"""Tests for CLI progress display functionality."""

import pytest
import yaml

from conduit.cli.progress import ProgressDisplay, create_progress_callback, format_bytes
from conduit.services.lock import LockService

from .conftest import API_VERSION

# delay_num = 3
#     number_of_requests = 5
#     base_url = concurrent_httpbin.url or "https://httpbin.org"
#     bin_url = f"{base_url}/delay/{delay_num}"

#     list_comp_fetch_commands = [
#         FetchArtifactCommand(
#             origin_url=bin_url,
#             target_path=str(tmp_path / f"delay{i}.json")
#         ) for i in range(1, number_of_requests + 1)
#     ]


@pytest.mark.asyncio
async def test_progress_display_with_concurrent_downloads(concurrent_httpbin, tmp_path):
    """Test progress display with real concurrent HTTP downloads."""
    number_of_artifacts = 3
    # Create test manifest with multiple HTTP artifacts
    artifacts_str = "\n".join(
        f"  - name: artifact{i}\n    origin: {concurrent_httpbin.url}/stream-bytes/2097152?chunk_size=131072\n    target: {tmp_path / f'artifact{i}.bin'!s}"
        for i in range(1, number_of_artifacts + 1)
    )

    manifest_content = f"""
apiVersion: {API_VERSION}
kind: Manifest
metadata:
  name: progress-test
  version: 1.0.0
artifacts:
{artifacts_str}
"""

    # Write manifest to temp file
    manifest_file = tmp_path / "manifest.yaml"
    manifest_file.write_text(manifest_content)

    # Track progress events
    progress_events = []

    # Create services
    generate_service = LockService()

    # Generate lockfile with progress tracking
    with ProgressDisplay() as display:
        callback = create_progress_callback(display)

        # Wrap callback to capture events
        def wrapped_callback(event):
            progress_events.append(event)
            callback(event)

        # Generate lockfile asynchronously
        _, lockfile = await generate_service.generate_lockfile_async(
            str(manifest_file), progress_callback=wrapped_callback
        )

    # Verify progress events were received
    assert len(progress_events) > 0

    # Check for download start events (one per artifact)
    start_events = [
        e for e in progress_events if e["type"] == "download_start" and "name" in e
    ]
    assert len(start_events) == number_of_artifacts

    # Check for progress events
    progress_updates = [e for e in progress_events if e["type"] == "download_progress"]
    assert len(progress_updates) > 0

    # Verify each artifact got progress updates
    artifacts_with_progress = {e["name"] for e in progress_updates}
    for i in range(1, number_of_artifacts + 1):
        assert f"artifact{i}" in artifacts_with_progress, (
            f"Missing progress for artifact{i}"
        )

    # Check complete events
    complete_events = [
        e for e in progress_events if e["type"] == "download_complete" and "name" in e
    ]
    assert len(complete_events) == number_of_artifacts

    # Verify artifacts were actually downloaded
    assert lockfile is not None
    assert len(lockfile.artifacts) == number_of_artifacts
    for artifact in lockfile.artifacts:
        assert artifact.checksum.startswith("sha256:")
        assert artifact.size > 0


@pytest.mark.asyncio
async def test_progress_callback_event_structure(concurrent_httpbin, tmp_path):
    """Test that progress events have the correct structure."""
    manifest_content = f"""
apiVersion: {API_VERSION}
kind: Manifest
metadata:
  name: event-test
  version: 1.0.0
artifacts:
  - name: test-artifact
    origin: {concurrent_httpbin.url}/stream-bytes/102400
    target: {tmp_path}/test.bin
"""

    # Write manifest to temp file
    manifest_file = tmp_path / "manifest.yaml"
    manifest_file.write_text(manifest_content)

    events = []

    # Create services
    generate_service = LockService()

    with ProgressDisplay() as display:
        callback = create_progress_callback(display)

        def capture_callback(event):
            events.append(event)
            callback(event)

        await generate_service.generate_lockfile_async(
            str(manifest_file), progress_callback=capture_callback
        )

    # Check start event
    start_events = [e for e in events if e["type"] == "download_start" and "name" in e]
    assert len(start_events) == 1
    start = start_events[0]
    assert "name" in start
    assert "url" in start
    assert start["name"] == "test-artifact"

    # Check progress events
    progress_events = [e for e in events if e["type"] == "download_progress"]
    assert len(progress_events) > 0
    for event in progress_events:
        assert "name" in event
        assert "bytes_downloaded" in event
        assert "total_bytes" in event
        assert "progress_percent" in event
        assert event["bytes_downloaded"] >= 0
        assert event["total_bytes"] > 0
        assert 0 <= event["progress_percent"] <= 100

    # Check complete event
    complete_events = [
        e for e in events if e["type"] == "download_complete" and "name" in e
    ]
    assert len(complete_events) == 1
    complete = complete_events[0]
    assert "name" in complete
    assert "bytes_downloaded" in complete
    assert "total_bytes" in complete
    assert complete["bytes_downloaded"] == 102400  # Matches requested size


def test_format_bytes():
    """Test byte formatting function."""
    test_cases = [
        (0, "0.0 B"),
        (1, "1.0 B"),
        (1023, "1023.0 B"),
        (1024, "1.0 KB"),
        (1536, "1.5 KB"),
        (1048576, "1.0 MB"),
        (1572864, "1.5 MB"),
        (1073741824, "1.0 GB"),
        (1610612736, "1.5 GB"),
        (1099511627776, "1.0 TB"),
    ]

    for bytes_val, expected in test_cases:
        assert format_bytes(bytes_val) == expected


def test_progress_display_context_manager():
    """Test ProgressDisplay works as context manager."""
    with ProgressDisplay() as display:
        assert display is not None
        assert hasattr(display, "progress")
        assert hasattr(display, "tasks")
        # Verify it's properly initialized
        assert display.tasks == {}


def test_progress_display_manual_start_stop():
    """Test ProgressDisplay can be manually started and stopped."""
    display = ProgressDisplay()

    # Should be able to start
    display.start()
    assert display.progress is not None

    # Should be able to stop
    display.stop()

    # Should handle multiple stop calls gracefully
    display.stop()  # Should not raise


@pytest.mark.asyncio
async def test_progress_display_with_local_files(manifest_data_factory, tmp_path):
    """Test progress display handles local files (no download progress)."""
    # Create a local test file
    test_file = tmp_path / "local.txt"
    test_file.write_text("local content")

    manifest_data = manifest_data_factory(
        manifest_name="local-test",
        artifacts=[
            {
                "name": "local-artifact",
                "origin": str(test_file),
                "target": str(tmp_path / "output.txt"),
            }
        ],
    )

    # Write manifest to temp file
    manifest_file = tmp_path / "local-test.yaml"
    manifest_file.write_text(
        yaml.dump(manifest_data, default_flow_style=True, indent=4)
    )
    events = []

    # Create services
    lockfile_service = LockService()

    with ProgressDisplay() as display:
        callback = create_progress_callback(display)

        def capture_callback(event):
            events.append(event)
            callback(event)

        await lockfile_service.generate_lockfile_async(
            str(manifest_file), progress_callback=capture_callback
        )

    # Local files shouldn't generate download events
    download_events = [e for e in events if "download" in e.get("type", "")]
    assert len(download_events) == 0
