# File: tests/plugins/concurrent_httpbin.py

import asyncio
import base64
import secrets
import socket
from contextlib import closing

import pytest
from aiohttp import web


def find_free_port():
    """Find a free port on localhost"""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


class ConcurrentHttpBin:
    """A concurrent httpbin-like service"""

    def __init__(self, host="127.0.0.1", port=None):
        self.host = host
        self.port = port or find_free_port()
        self.server = None
        self.runner = None
        self.url = f"http://{self.host}:{self.port}"

    async def start(self):
        """Start the server"""
        app = web.Application()

        # Basic httpbin endpoints
        app.router.add_get("/delay/{seconds}", self.handle_delay)
        app.router.add_get("/get", self.handle_get)
        app.router.add_post("/post", self.handle_post)
        app.router.add_get("/status/{status}", self.handle_status)
        app.router.add_get("/headers", self.handle_headers)
        app.router.add_get("/base64/{encoded_data}", self.handle_base64)

        # New endpoints for progress tracking tests
        app.router.add_get("/stream-bytes/{nbytes}", self.handle_stream_bytes)
        app.router.add_get("/drip", self.handle_drip)

        # Start the server
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()

        return self

    async def stop(self):
        """Stop the server"""
        if self.runner:
            await self.runner.cleanup()
            self.runner = None

    # Original handlers...
    async def handle_delay(self, request):
        """Simulate delay like httpbin's /delay/{seconds}"""
        try:
            seconds = float(request.match_info["seconds"])
            seconds = min(seconds, 10)
            await asyncio.sleep(seconds)
            data = {
                "args": dict(request.query),
                "headers": dict(request.headers),
                "url": str(request.url),
                "origin": request.remote,
                "delay": seconds,
            }
            return web.json_response(data)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_get(self, request):
        """Similar to httpbin's /get"""
        data = {
            "args": dict(request.query),
            "headers": dict(request.headers),
            "url": str(request.url),
            "origin": request.remote,
        }
        return web.json_response(data)

    async def handle_post(self, request):
        """Similar to httpbin's /post"""
        try:
            body = await request.text()
            try:
                json_data = await request.json()
            except Exception:
                json_data = None

            form_data = None
            if (
                request.headers.get("Content-Type")
                == "application/x-www-form-urlencoded"
            ):
                form_data = dict(await request.post())

            data = {
                "args": dict(request.query),
                "headers": dict(request.headers),
                "url": str(request.url),
                "origin": request.remote,
                "json": json_data,
                "data": body,
                "form": form_data,
            }
            return web.json_response(data)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_status(self, request):
        """Similar to httpbin's /status/{status}"""
        try:
            status = int(request.match_info["status"])
            return web.Response(status=status)
        except ValueError:
            return web.Response(status=400, text="Invalid status code")

    async def handle_headers(self, request):
        """Similar to httpbin's /headers"""
        data = {"headers": dict(request.headers)}
        return web.json_response(data)

    async def handle_base64(self, request):
        """Decode and return base64 encoded data"""
        try:
            encoded_data = request.match_info["encoded_data"]
            try:
                decoded_data = base64.b64decode(encoded_data)
            except Exception:
                # Try URL-safe base64 decoding if standard fails
                decoded_data = base64.urlsafe_b64decode(encoded_data)

            return web.Response(body=decoded_data, content_type="text/plain")
        except Exception as e:
            return web.Response(status=400, text=f"Error decoding base64 data: {e!s}")

    # New handlers for progress tracking tests
    async def handle_stream_bytes(self, request):
        """Stream a specified number of bytes in chunks"""
        try:
            nbytes = int(request.match_info["nbytes"])
            chunk_size = int(
                request.query.get("chunk_size", 10240)
            )  # Default 10KB chunks

            # Limit maximum file size to prevent abuse (100MB)
            nbytes = min(nbytes, 100 * 1024 * 1024)

            # Optional delay between chunks (in ms)
            chunk_delay_ms = float(request.query.get("chunk_delay_ms", 0))

            # Create a streaming response
            resp = web.StreamResponse(
                status=200,
                reason="OK",
                headers={
                    "Content-Type": "application/octet-stream",
                    "Content-Length": str(nbytes),
                },
            )

            await resp.prepare(request)

            bytes_sent = 0
            while bytes_sent < nbytes:
                # Calculate next chunk size
                current_chunk_size = min(chunk_size, nbytes - bytes_sent)

                # Generate random bytes - use secrets instead of list comprehension for efficiency
                chunk = secrets.token_bytes(current_chunk_size)

                # Send chunk
                await resp.write(chunk)
                bytes_sent += current_chunk_size

                # Delay between chunks if requested
                if chunk_delay_ms > 0:
                    await asyncio.sleep(chunk_delay_ms / 1000)  # Convert ms to seconds

            await resp.write_eof()
            return resp

        except Exception as e:
            return web.Response(status=400, text=f"Error streaming bytes: {e!s}")

    async def handle_drip(self, request):
        """Drip data over a duration with specified number of chunks"""
        try:
            # Parse parameters
            duration = float(request.query.get("duration", 2))
            numbytes = int(
                request.query.get("numbytes", 10 * 1024 * 1024)
            )  # Default 10MB
            chunks = int(request.query.get("numchunks", 10))

            # Limit maximum duration and size to prevent abuse
            duration = min(duration, 30)  # Max 30 seconds
            numbytes = min(numbytes, 100 * 1024 * 1024)  # Max 100MB

            # Calculate chunk size
            bytes_per_chunk = numbytes // chunks

            # Calculate delay between chunks
            delay_per_chunk = duration / chunks

            # Create response
            resp = web.StreamResponse(
                status=200,
                reason="OK",
                headers={
                    "Content-Type": "application/octet-stream",
                    "Content-Length": str(numbytes),
                },
            )

            await resp.prepare(request)

            for i in range(chunks):
                # Generate chunk data
                if i == chunks - 1:  # Last chunk
                    # Make sure we send exactly numbytes
                    remaining = numbytes - (i * bytes_per_chunk)
                    chunk = secrets.token_bytes(remaining)
                else:
                    chunk = secrets.token_bytes(bytes_per_chunk)

                # Send chunk
                await resp.write(chunk)

                # Delay before next chunk (except after the last chunk)
                if i < chunks - 1:
                    await asyncio.sleep(delay_per_chunk)

            await resp.write_eof()
            return resp

        except Exception as e:
            return web.Response(status=400, text=f"Error in drip response: {e!s}")


@pytest.fixture
async def concurrent_httpbin():
    """Pytest fixture that provides a concurrent httpbin-like server"""
    server = ConcurrentHttpBin()
    await server.start()
    yield server
    await server.stop()
