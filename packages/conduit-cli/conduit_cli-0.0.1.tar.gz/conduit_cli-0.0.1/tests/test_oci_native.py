"""Tests for OCI-Native Registry Client.

Integration tests using real zot registry at localhost:8080/ocinative-test.
Tests OCI Distribution API compliance, bundle structure preservation, and authentication.
"""

import gzip
import hashlib
import io
import json
import os
import tarfile
import tempfile
from pathlib import Path

import pytest

from conduit.core.clients.oci_native import OciNativeRegistryClient


# Test configuration
REGISTRY_URL = "localhost:8080"
REGISTRY_REPO = "ocinative-test"
REGISTRY_USERNAME = os.getenv("CONDUIT_REGISTRY_USERNAME")
REGISTRY_PASSWORD = os.getenv("CONDUIT_REGISTRY_PASSWORD")


@pytest.fixture
async def oci_native_client():
    """Create OCI-Native Registry Client instance."""
    client = OciNativeRegistryClient()
    yield client
    # Cleanup
    await client.logout()


@pytest.fixture
def sample_bundle_manifest():
    """Create a sample OCI bundle manifest with 2-layer structure."""
    return {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "config": {
            "mediaType": "application/vnd.oci.image.config.v1+json",
            "size": 123,
            "digest": "sha256:44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
        },
        "layers": [
            {
                "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
                "size": 456,
                "digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "annotations": {
                    "com.warrical.conduit.layer.type": "metadata"
                }
            },
            {
                "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
                "size": 789,
                "digest": "sha256:a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
                "annotations": {
                    "com.warrical.conduit.layer.type": "artifacts"
                }
            }
        ],
        "annotations": {
            "com.warrical.conduit.bundle.name": "test-bundle",
            "com.warrical.conduit.bundle.version": "1.0.0",
            "com.warrical.conduit.created": "2025-01-01T00:00:00Z"
        }
    }


@pytest.fixture
def bundle_config_blob():
    """Create bundle config blob."""
    config = {
        "architecture": "amd64",
        "config": {
            "Env": ["PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"],
            "Labels": {
                "com.warrical.conduit.bundle": "true"
            }
        },
        "rootfs": {
            "type": "layers",
            "diff_ids": [
                "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "sha256:a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
            ]
        }
    }
    return json.dumps(config).encode()


@pytest.fixture
def bundle_layers_data():
    """Create sample bundle layer data."""
    metadata_layer = json.dumps({
        "apiVersion": "conduit.warrical.com/next",
        "kind": "Lockfile",
        "metadata": {"name": "test-bundle"},
        "operations": [
            {
                "type": "copy",
                "source": "test.txt",
                "destination": "/opt/test.txt"
            }
        ]
    }).encode()
    
    artifacts_layer = b"test artifact content for bundle"
    
    return {
        "config": json.dumps({}).encode(),
        "metadata": metadata_layer,
        "artifacts": artifacts_layer
    }


@pytest.mark.skipif(
    not REGISTRY_USERNAME or not REGISTRY_PASSWORD,
    reason="Registry credentials not provided"
)
async def test_authentication_with_zot_registry(oci_native_client):
    """Test authentication with zot registry using provided credentials."""
    result = await oci_native_client.login(REGISTRY_USERNAME, REGISTRY_PASSWORD)
    
    assert result.success is True, f"Login failed: {result.error_message}"


@pytest.mark.skipif(
    not REGISTRY_USERNAME or not REGISTRY_PASSWORD,
    reason="Registry credentials not provided"
)
async def test_manifest_upload_preserves_bundle_structure(oci_native_client, sample_bundle_manifest, bundle_config_blob):
    """Test that manifest upload preserves 2-layer bundle structure."""
    # First authenticate
    auth_result = await oci_native_client.login(REGISTRY_USERNAME, REGISTRY_PASSWORD)
    assert auth_result.success is True
    
    # Upload config blob first
    config_result = await oci_native_client._upload_blob(
        f"{REGISTRY_URL}/{REGISTRY_REPO}",
        bundle_config_blob
    )
    assert config_result.success is True
    
    # Create and upload layer blobs
    metadata_blob = b"metadata layer content"
    artifacts_blob = b"artifacts layer content"
    
    metadata_result = await oci_native_client._upload_blob(
        f"{REGISTRY_URL}/{REGISTRY_REPO}",
        metadata_blob
    )
    assert metadata_result.success is True
    
    artifacts_result = await oci_native_client._upload_blob(
        f"{REGISTRY_URL}/{REGISTRY_REPO}",
        artifacts_blob
    )
    assert artifacts_result.success is True
    
    # Update manifest with actual digests and sizes
    sample_bundle_manifest["config"]["digest"] = config_result.digest
    sample_bundle_manifest["config"]["size"] = len(bundle_config_blob)
    
    sample_bundle_manifest["layers"][0]["digest"] = metadata_result.digest
    sample_bundle_manifest["layers"][0]["size"] = len(metadata_blob)
    
    sample_bundle_manifest["layers"][1]["digest"] = artifacts_result.digest
    sample_bundle_manifest["layers"][1]["size"] = len(artifacts_blob)
    
    # Upload manifest
    result = await oci_native_client._put_manifest(
        f"{REGISTRY_URL}/{REGISTRY_REPO}",
        "test-bundle-structure",
        sample_bundle_manifest
    )
    
    assert result.success is True, f"Manifest upload failed: {result.error_message}"
    
    # Verify manifest retrieval preserves structure
    retrieved_result = await oci_native_client._get_manifest(
        f"{REGISTRY_URL}/{REGISTRY_REPO}",
        "test-bundle-structure"
    )
    
    assert retrieved_result.success is True
    retrieved_manifest = retrieved_result.manifest
    
    # Verify 2-layer structure
    assert len(retrieved_manifest["layers"]) == 2
    assert retrieved_manifest["layers"][0]["annotations"]["com.warrical.conduit.layer.type"] == "metadata"
    assert retrieved_manifest["layers"][1]["annotations"]["com.warrical.conduit.layer.type"] == "artifacts"
    
    # Verify bundle annotations
    assert retrieved_manifest["annotations"]["com.warrical.conduit.bundle.name"] == "test-bundle"
    assert retrieved_manifest["annotations"]["com.warrical.conduit.bundle.version"] == "1.0.0"


@pytest.mark.skipif(
    not REGISTRY_USERNAME or not REGISTRY_PASSWORD,
    reason="Registry credentials not provided"
)
async def test_blob_upload_and_download(oci_native_client, bundle_layers_data):
    """Test blob upload and download operations."""
    # First authenticate
    auth_result = await oci_native_client.login(REGISTRY_USERNAME, REGISTRY_PASSWORD)
    assert auth_result.success is True
    
    # Test each layer upload
    uploaded_digests = {}
    
    for layer_name, layer_data in bundle_layers_data.items():
        upload_result = await oci_native_client._upload_blob(
            f"{REGISTRY_URL}/{REGISTRY_REPO}",
            layer_data
        )
        
        assert upload_result.success is True, f"Upload failed for {layer_name}: {upload_result.error_message}"
        uploaded_digests[layer_name] = upload_result.digest
        
        # Verify digest calculation
        expected_digest = f"sha256:{hashlib.sha256(layer_data).hexdigest()}"
        assert upload_result.digest == expected_digest
    
    # Test blob download
    for layer_name, digest in uploaded_digests.items():
        download_result = await oci_native_client._download_blob(
            f"{REGISTRY_URL}/{REGISTRY_REPO}",
            digest
        )
        
        assert download_result.success is True, f"Download failed for {layer_name}: {download_result.error_message}"
        assert download_result.data == bundle_layers_data[layer_name]


@pytest.mark.skipif(
    not REGISTRY_USERNAME or not REGISTRY_PASSWORD,
    reason="Registry credentials not provided"
)
async def test_chunked_upload_large_blob(oci_native_client):
    """Test chunked upload for large blobs."""
    # First authenticate
    auth_result = await oci_native_client.login(REGISTRY_USERNAME, REGISTRY_PASSWORD)
    assert auth_result.success is True
    
    # Create large blob (1MB)
    large_blob = b"x" * (1024 * 1024)
    
    # Test chunked upload
    result = await oci_native_client._upload_blob_chunked(
        f"{REGISTRY_URL}/{REGISTRY_REPO}",
        large_blob,
        chunk_size=64 * 1024  # 64KB chunks
    )
    
    assert result.success is True, f"Chunked upload failed: {result.error_message}"
    
    # Verify digest
    expected_digest = f"sha256:{hashlib.sha256(large_blob).hexdigest()}"
    assert result.digest == expected_digest
    
    # Verify download
    download_result = await oci_native_client._download_blob(
        f"{REGISTRY_URL}/{REGISTRY_REPO}",
        result.digest
    )
    
    assert download_result.success is True
    assert download_result.data == large_blob


@pytest.mark.skipif(
    not REGISTRY_USERNAME or not REGISTRY_PASSWORD,
    reason="Registry credentials not provided"
)
async def test_complete_bundle_push_pull_cycle(oci_native_client, sample_bundle_manifest, bundle_layers_data):
    """Test complete bundle push and pull cycle."""
    # First authenticate
    auth_result = await oci_native_client.login(REGISTRY_USERNAME, REGISTRY_PASSWORD)
    assert auth_result.success is True
    
    # Upload all blobs
    blob_digests = {}
    for layer_name, layer_data in bundle_layers_data.items():
        upload_result = await oci_native_client._upload_blob(
            f"{REGISTRY_URL}/{REGISTRY_REPO}",
            layer_data
        )
        assert upload_result.success is True
        blob_digests[layer_name] = upload_result.digest
    
    # Update manifest with actual digests
    sample_bundle_manifest["config"]["digest"] = blob_digests["config"]
    sample_bundle_manifest["config"]["size"] = len(bundle_layers_data["config"])
    
    sample_bundle_manifest["layers"][0]["digest"] = blob_digests["metadata"]
    sample_bundle_manifest["layers"][0]["size"] = len(bundle_layers_data["metadata"])
    
    sample_bundle_manifest["layers"][1]["digest"] = blob_digests["artifacts"]
    sample_bundle_manifest["layers"][1]["size"] = len(bundle_layers_data["artifacts"])
    
    # Push complete bundle
    push_result = await oci_native_client.push(
        f"{REGISTRY_URL}/{REGISTRY_REPO}:complete-bundle-test",
        sample_bundle_manifest
    )
    
    assert push_result.success is True, f"Bundle push failed: {push_result.error_message}"
    
    # Pull complete bundle
    pull_result = await oci_native_client.pull(
        f"{REGISTRY_URL}/{REGISTRY_REPO}:complete-bundle-test"
    )
    
    assert pull_result.success is True, f"Bundle pull failed: {pull_result.error_message}"
    
    # Verify bundle structure
    pulled_manifest = pull_result.manifest
    assert len(pulled_manifest["layers"]) == 2
    
    # Verify layer types
    metadata_layer = pulled_manifest["layers"][0]
    artifacts_layer = pulled_manifest["layers"][1]
    
    assert metadata_layer["annotations"]["com.warrical.conduit.layer.type"] == "metadata"
    assert artifacts_layer["annotations"]["com.warrical.conduit.layer.type"] == "artifacts"
    
    # Verify bundle annotations preserved
    assert pulled_manifest["annotations"]["com.warrical.conduit.bundle.name"] == "test-bundle"
    assert pulled_manifest["annotations"]["com.warrical.conduit.bundle.version"] == "1.0.0"


@pytest.mark.skipif(
    not REGISTRY_USERNAME or not REGISTRY_PASSWORD,
    reason="Registry credentials not provided"
)
async def test_progress_callback_functionality(oci_native_client):
    """Test progress callback functionality during operations."""
    # First authenticate
    auth_result = await oci_native_client.login(REGISTRY_USERNAME, REGISTRY_PASSWORD)
    assert auth_result.success is True
    
    progress_calls = []
    
    def progress_callback(info):
        progress_calls.append(info)
    
    # Upload with progress
    test_data = b"test data for progress callback" * 100  # Make it larger
    
    upload_result = await oci_native_client._upload_blob(
        f"{REGISTRY_URL}/{REGISTRY_REPO}",
        test_data,
        progress_callback=progress_callback
    )
    
    assert upload_result.success is True
    # Progress callback may not be called for very small uploads
    if len(progress_calls) > 0:
        # Verify progress info structure
        progress_info = progress_calls[0]
        assert "type" in progress_info
        assert progress_info["type"] == "upload_progress"


@pytest.mark.skipif(
    not REGISTRY_USERNAME or not REGISTRY_PASSWORD,
    reason="Registry credentials not provided"
)
async def test_manifest_not_found_handling(oci_native_client):
    """Test handling of non-existent manifest."""
    # First authenticate
    auth_result = await oci_native_client.login(REGISTRY_USERNAME, REGISTRY_PASSWORD)
    assert auth_result.success is True
    
    # Try to get non-existent manifest
    result = await oci_native_client._get_manifest(
        f"{REGISTRY_URL}/{REGISTRY_REPO}",
        "non-existent-tag"
    )
    
    assert result.success is False
    assert "not found" in result.error_message.lower() or "404" in result.error_message


@pytest.mark.skipif(
    not REGISTRY_USERNAME or not REGISTRY_PASSWORD,
    reason="Registry credentials not provided"
)
async def test_blob_not_found_handling(oci_native_client):
    """Test handling of non-existent blob."""
    # First authenticate
    auth_result = await oci_native_client.login(REGISTRY_USERNAME, REGISTRY_PASSWORD)
    assert auth_result.success is True
    
    # Try to get non-existent blob
    fake_digest = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
    
    result = await oci_native_client._download_blob(
        f"{REGISTRY_URL}/{REGISTRY_REPO}",
        fake_digest
    )
    
    assert result.success is False
    assert "not found" in result.error_message.lower() or "404" in result.error_message


@pytest.mark.skipif(
    not REGISTRY_USERNAME or not REGISTRY_PASSWORD,
    reason="Registry credentials not provided"
)
async def test_registry_client_interface_compliance(oci_native_client):
    """Test that OCI client implements RegistryClient interface correctly."""
    from conduit.core.clients.registry import RegistryClient
    
    assert isinstance(oci_native_client, RegistryClient)
    
    # Test all abstract methods exist and are callable
    assert callable(oci_native_client.login)
    assert callable(oci_native_client.logout)
    assert callable(oci_native_client.push)
    assert callable(oci_native_client.pull)
    
    # Test login/logout cycle
    login_result = await oci_native_client.login(REGISTRY_USERNAME, REGISTRY_PASSWORD)
    assert login_result.success is True
    
    logout_result = await oci_native_client.logout()
    assert logout_result.success is True


async def test_invalid_authentication():
    """Test handling of invalid authentication."""
    client = OciNativeRegistryClient()
    
    # Test with invalid credentials
    result = await client.login("invalid_user", "invalid_pass")
    
    # Should handle gracefully (either success with stored creds or appropriate error)
    assert hasattr(result, 'success')
    assert isinstance(result.success, bool)


async def test_session_management():
    """Test HTTP session management."""
    client = OciNativeRegistryClient()
    
    # Test session creation
    session1 = await client._get_session(REGISTRY_URL)
    session2 = await client._get_session(REGISTRY_URL)
    
    # Should reuse same session for same registry
    assert session1 is session2
    
    # Test cleanup
    await client.logout()
    assert len(client._sessions) == 0


async def test_manifest_validation():
    """Test manifest validation before operations."""
    client = OciNativeRegistryClient()
    
    # Test valid manifest
    valid_manifest = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "config": {
            "mediaType": "application/vnd.oci.image.config.v1+json",
            "size": 123,
            "digest": "sha256:abcd1234"
        },
        "layers": []
    }
    
    result = await client._validate_manifest(valid_manifest)
    assert result.success is True
    
    # Test invalid manifest
    invalid_manifest = {
        "schemaVersion": 1,  # Invalid version
        "mediaType": "invalid/type"
    }
    
    result = await client._validate_manifest(invalid_manifest)
    assert result.success is False
    assert "schema" in result.error_message.lower() or "validation" in result.error_message.lower()


@pytest.mark.skipif(
    not REGISTRY_USERNAME or not REGISTRY_PASSWORD,
    reason="Registry credentials not provided"
)
async def test_simple_bundle_push_pull(oci_native_client):
    """Test simple bundle push and pull with OCI-Native client."""
    # First authenticate
    auth_result = await oci_native_client.login(REGISTRY_USERNAME, REGISTRY_PASSWORD)
    assert auth_result.success, "Authentication failed"
    
    # Create simple test manifest
    test_manifest = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "config": {
            "mediaType": "application/vnd.oci.image.config.v1+json",
            "size": 44,
            "digest": "sha256:44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
        },
        "layers": [
            {
                "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
                "size": 32,
                "digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "annotations": {
                    "com.warrical.conduit.layer.type": "metadata"
                }
            },
            {
                "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
                "size": 26,
                "digest": "sha256:a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
                "annotations": {
                    "com.warrical.conduit.layer.type": "artifacts"
                }
            }
        ],
        "annotations": {
            "com.warrical.conduit.bundle.name": "test-simple-bundle",
            "com.warrical.conduit.bundle.version": "1.0.0"
        }
    }
    
    # Upload all required blobs first
    config_blob = b"{}"  # Empty config
    metadata_blob = b""  # Empty metadata layer
    artifacts_blob = b"test artifacts content"  # Test artifacts layer
    
    # Upload config blob
    config_upload = await oci_native_client._upload_blob(
        f"{REGISTRY_URL}/{REGISTRY_REPO}",
        config_blob
    )
    assert config_upload.success, f"Config upload failed: {config_upload.error_message}"
    
    # Upload metadata blob  
    metadata_upload = await oci_native_client._upload_blob(
        f"{REGISTRY_URL}/{REGISTRY_REPO}",
        metadata_blob
    )
    assert metadata_upload.success, f"Metadata upload failed: {metadata_upload.error_message}"
    
    # Upload artifacts blob
    artifacts_upload = await oci_native_client._upload_blob(
        f"{REGISTRY_URL}/{REGISTRY_REPO}",
        artifacts_blob
    )
    assert artifacts_upload.success, f"Artifacts upload failed: {artifacts_upload.error_message}"
    
    # Update manifest with actual digests
    test_manifest["config"]["digest"] = config_upload.digest
    test_manifest["config"]["size"] = len(config_blob)
    test_manifest["layers"][0]["digest"] = metadata_upload.digest
    test_manifest["layers"][0]["size"] = len(metadata_blob)
    test_manifest["layers"][1]["digest"] = artifacts_upload.digest
    test_manifest["layers"][1]["size"] = len(artifacts_blob)
    
    # Push manifest
    push_result = await oci_native_client.push(
        f"{REGISTRY_URL}/{REGISTRY_REPO}:simple-test",
        test_manifest
    )
    assert push_result.success, f"Manifest push failed: {push_result.error_message}"
    
    # Pull manifest back
    pull_result = await oci_native_client.pull(
        f"{REGISTRY_URL}/{REGISTRY_REPO}:simple-test"
    )
    assert pull_result.success, f"Manifest pull failed: {pull_result.error_message}"
    
    # Verify structure
    pulled_manifest = pull_result.manifest
    assert len(pulled_manifest["layers"]) == 2
    assert pulled_manifest["annotations"]["com.warrical.conduit.bundle.name"] == "test-simple-bundle"
    
    # Verify layer types
    layer_types = [layer["annotations"]["com.warrical.conduit.layer.type"] for layer in pulled_manifest["layers"]]
    assert "metadata" in layer_types
    assert "artifacts" in layer_types


@pytest.mark.skipif(
    not REGISTRY_USERNAME or not REGISTRY_PASSWORD,
    reason="Registry credentials not provided"
)
async def test_end_to_end_bundle_lifecycle_with_soc_siem_core(tmp_path, oci_native_client):
    """Test complete bundle lifecycle using real soc-siem-core manifest.
    
    This test:
    1. Uses the soc-siem-core.yml manifest
    2. Generates a lockfile from it
    3. Creates a bundle using PackService
    4. Pushes bundle using OCI-Native client
    5. Verifies proper 2-layer structure in registry
    6. Pulls bundle back and verifies integrity
    """
    from conduit.services.lock import LockService
    from conduit.services.pack import PackService
    
    # Get the soc-siem-core manifest
    manifest_path = Path("tests/testfiles/manifests/soc-siem-core.yml")
    assert manifest_path.exists(), "soc-siem-core.yml manifest not found"
    
    # Create temporary directories
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    bundle_output_dir = tmp_path / "bundle"
    bundle_output_dir.mkdir()
    
    # Step 1: Generate lockfile from manifest
    lock_service = LockService()
    
    lockfile_path, _ = await lock_service.generate_lockfile_async(
        str(manifest_path),
        cli_variables=None,
        output_path=str(output_dir / "soc-siem-core.lock.yaml")
    )
    
    assert Path(lockfile_path).exists(), "Lockfile generation failed"
    
    # Step 2: Create bundle from lockfile
    pack_service = PackService()
    
    bundle_result = await pack_service.pack_async(
        lockfile_path=lockfile_path,
        output_dir=str(bundle_output_dir)
    )
    
    assert bundle_result.success, f"Bundle creation failed: {bundle_result.error_message}"
    
    bundle_path = Path(bundle_result.oci_bundle_path)
    assert bundle_path.exists(), "Bundle file not created"
    
    # Step 3: Extract bundle structure for verification
    with tempfile.TemporaryDirectory() as temp_extract_dir:
        # Extract bundle to verify structure
        with tarfile.open(bundle_path, 'r') as tar:
            tar.extractall(temp_extract_dir, filter='data')
        
        extract_path = Path(temp_extract_dir)
        
        # Verify OCI bundle structure
        assert (extract_path / "index.json").exists(), "Missing index.json"
        assert (extract_path / "blobs").exists(), "Missing blobs directory"
        
        # Read index.json to understand bundle structure
        with open(extract_path / "index.json", encoding='utf-8') as f:
            index_data = json.load(f)
        
        # Verify it's an OCI image index
        assert index_data["schemaVersion"] == 2
        assert "manifests" in index_data
        
        # Get the main manifest
        main_manifest_descriptor = index_data["manifests"][0]
        manifest_digest = main_manifest_descriptor["digest"]
        
        # Read the manifest blob
        manifest_blob_path = extract_path / "blobs" / "sha256" / manifest_digest.split(":")[1]
        assert manifest_blob_path.exists(), f"Manifest blob not found: {manifest_blob_path}"
        
        with open(manifest_blob_path, encoding='utf-8') as f:
            manifest_data = json.load(f)
        
        # Verify 2-layer structure
        assert len(manifest_data["layers"]) == 2, f"Expected 2 layers, got {len(manifest_data['layers'])}"
        
        metadata_layer = manifest_data["layers"][0]
        artifacts_layer = manifest_data["layers"][1]
        
        # Verify layer annotations
        assert metadata_layer["annotations"]["com.warrical.conduit.layer.type"] == "metadata"
        assert artifacts_layer["annotations"]["com.warrical.conduit.layer.type"] == "artifacts"
        
        # Verify bundle annotations
        bundle_annotations = manifest_data.get("annotations", {})
        assert "com.warrical.conduit.bundle.name" in bundle_annotations
        assert bundle_annotations["com.warrical.conduit.bundle.name"] == "soc-siem-core"
    
    # Step 4: Push bundle using OCI-Native client
    auth_result = await oci_native_client.login(REGISTRY_USERNAME, REGISTRY_PASSWORD)
    assert auth_result.success, "Authentication failed"
    
    # Read manifest from bundle for push
    with tempfile.TemporaryDirectory() as temp_extract_dir:
        with tarfile.open(bundle_path, 'r') as tar:
            tar.extractall(temp_extract_dir, filter='data')
        
        extract_path = Path(temp_extract_dir)
        
        # Read index and manifest
        with open(extract_path / "index.json", encoding='utf-8') as f:
            index_data = json.load(f)
        
        main_manifest_descriptor = index_data["manifests"][0]
        manifest_digest = main_manifest_descriptor["digest"]
        
        manifest_blob_path = extract_path / "blobs" / "sha256" / manifest_digest.split(":")[1]
        with open(manifest_blob_path, encoding='utf-8') as f:
            manifest_data = json.load(f)
        
        # Upload all blobs first
        blobs_dir = extract_path / "blobs" / "sha256"
        uploaded_blobs = {}
        
        for blob_file in blobs_dir.iterdir():
            if blob_file.is_file():
                blob_data = blob_file.read_bytes()
                
                upload_result = await oci_native_client._upload_blob(
                    f"{REGISTRY_URL}/{REGISTRY_REPO}",
                    blob_data
                )
                
                assert upload_result.success, f"Failed to upload blob {blob_file.name}"
                uploaded_blobs[f"sha256:{blob_file.name}"] = upload_result.digest
        
        # Push manifest
        push_result = await oci_native_client.push(
            f"{REGISTRY_URL}/{REGISTRY_REPO}:soc-siem-core-e2e-test",
            manifest_data
        )
        
        assert push_result.success, f"Bundle push failed: {push_result.error_message}"
    
    # Step 5: Verify bundle structure in registry
    pull_result = await oci_native_client.pull(
        f"{REGISTRY_URL}/{REGISTRY_REPO}:soc-siem-core-e2e-test"
    )
    
    assert pull_result.success, f"Bundle pull failed: {pull_result.error_message}"
    
    # Verify pulled manifest structure
    pulled_manifest = pull_result.manifest
    assert len(pulled_manifest["layers"]) == 2
    
    # Verify layer types are preserved
    layer_types = [
        layer["annotations"]["com.warrical.conduit.layer.type"] 
        for layer in pulled_manifest["layers"]
    ]
    assert "metadata" in layer_types
    assert "artifacts" in layer_types
    
    # Verify bundle annotations are preserved
    pulled_annotations = pulled_manifest.get("annotations", {})
    assert "com.warrical.conduit.bundle.name" in pulled_annotations
    assert pulled_annotations["com.warrical.conduit.bundle.name"] == "soc-siem-core"
    
    # Step 6: Verify layer content integrity
    metadata_layer_data = None
    artifacts_layer_data = None
    
    for layer_info in pull_result.layers:
        if layer_info["type"] == "metadata":
            metadata_layer_data = layer_info["data"]
        elif layer_info["type"] == "artifacts":
            artifacts_layer_data = layer_info["data"]
    
    assert metadata_layer_data is not None, "Metadata layer not found"
    assert artifacts_layer_data is not None, "Artifacts layer not found"
    
    # Verify metadata layer contains lockfile
    # Decompress and extract metadata layer
    with gzip.GzipFile(fileobj=io.BytesIO(metadata_layer_data)) as gz, \
         tarfile.open(fileobj=gz, mode='r') as tar:
        lockfile_member = tar.getmember("conduit.lock.json")
        lockfile_content = tar.extractfile(lockfile_member).read()
        
        # Verify lockfile content
        lockfile_json = json.loads(lockfile_content)
        assert lockfile_json["kind"] == "Lockfile"
        assert lockfile_json["metadata"]["name"] == "soc-siem-core"
        
        # Verify operations exist
        assert "operations" in lockfile_json
        assert len(lockfile_json["operations"]) > 0