"""
Pytest configuration and fixtures for 3D Slicer API tests
"""

import pytest
import os
import tempfile
import json
from pathlib import Path
from tests.slicer_api.slicer_client import SlicerClient


@pytest.fixture(scope="session")
def slicer_config():
    """Session-scoped fixture for Slicer configuration"""
    config_path = Path(__file__).parent / "slicer_config.json"
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "slicer_path": None,
            "timeout_seconds": 30,
            "enable_cli_tests": True,
            "enable_direct_import_tests": True,
            "common_paths": [
                "C:\\ProgramData\\NA-MIC\\Slicer*",
                "C:\\Program Files\\Slicer*",
                "C:\\Program Files (x86)\\Slicer*",
                "C:\\Users\\*\\AppData\\Local\\Slicer*"
            ]
        }


@pytest.fixture(scope="session")
def slicer_client(slicer_config):
    """Session-scoped fixture for SlicerClient instance"""
    return SlicerClient()


@pytest.fixture(scope="session")
def slicer_available(slicer_client):
    """Session-scoped fixture to check if Slicer is available"""
    return slicer_client.is_slicer_available()


@pytest.fixture(scope="session")
def slicer_can_import(slicer_client):
    """Session-scoped fixture to check if Slicer can be imported"""
    return slicer_client.can_import_slicer()


@pytest.fixture
def temp_config_file():
    """Fixture for temporary configuration file"""
    config = {
        "slicer_path": "/test/path/Slicer.exe",
        "timeout_seconds": 60,
        "enable_cli_tests": False,
        "enable_direct_import_tests": True,
        "common_paths": ["/test/path/*"]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def sample_nrrd_data():
    """Fixture for sample NRRD volume data"""
    import numpy as np
    
    # Create a simple 3D volume
    volume_data = np.random.randint(0, 255, (16, 16, 16), dtype=np.uint8)
    
    return volume_data


@pytest.fixture
def sample_nrrd_file(sample_nrrd_data):
    """Fixture for temporary sample NRRD file"""
    with tempfile.NamedTemporaryFile(suffix='.nrrd', delete=False) as f:
        temp_path = f.name
    
    # Write simple NRRD header and data
    with open(temp_path, 'wb') as f:
        # Simple NRRD header
        header = f"""NRRD0004
# Complete NRRD file format specification at:
# http://teem.sourceforge.net/nrrd/format.html
type: uint8
dimension: 3
space: left-posterior-superior
sizes: 16 16 16
space directions: (1,0,0) (0,1,0) (0,0,1)
kinds: domain domain domain
endian: little
encoding: raw
"""
        f.write(header.encode('ascii'))
        f.write(b'\n')  # Empty line after header
        f.write(sample_nrrd_data.tobytes())
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def mock_slicer_responses():
    """Fixture providing mock Slicer responses for testing"""
    return {
        "cli_connection_success": {
            "success": True,
            "stdout": "Slicer Python version: 3.9.0\nSlicer available: True",
            "stderr": "",
            "returncode": 0
        },
        "cli_connection_failure": {
            "success": False,
            "stdout": "",
            "stderr": "Error: Invalid command",
            "returncode": 1
        },
        "load_volume_success": {
            "success": True,
            "stdout": "Volume loaded successfully: test_volume\nVolume dimensions: (16, 16, 16)",
            "stderr": "",
            "returncode": 0
        },
        "create_segmentation_success": {
            "success": True,
            "stdout": "Segmentation created: TestSegmentation\nScene node count: 1",
            "stderr": "",
            "returncode": 0
        },
        "scene_info_success": {
            "success": True,
            "stdout": "Scene node count: 3\nScene modified time: 12345\nNode types: {'vtkMRMLVolumeNode': 1, 'vtkMRMLSegmentationNode': 2}",
            "stderr": "",
            "returncode": 0
        }
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slicer_required: mark test as requiring 3D Slicer installation"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Add markers based on test file names
        if "test_slicer_connection" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "test_slicer_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add slicer_required marker for integration tests
        if "integration" in item.nodeid and "skipif" not in item.nodeid:
            item.add_marker(pytest.mark.slicer_required)


def pytest_runtest_setup(item):
    """Setup for each test item"""
    # Skip integration tests if Slicer not available
    if item.get_closest_marker("slicer_required"):
        slicer_client = SlicerClient()
        if not slicer_client.is_slicer_available():
            pytest.skip("3D Slicer not available on system")


# Custom pytest hooks for better test reporting
def pytest_report_header(config):
    """Add custom header to pytest report"""
    slicer_client = SlicerClient()
    header = []
    
    header.append("3D Slicer API Test Configuration:")
    header.append(f"  Slicer Path: {slicer_client.slicer_path or 'Not found'}")
    header.append(f"  Slicer Available: {slicer_client.is_slicer_available()}")
    header.append(f"  Can Import Slicer: {slicer_client.can_import_slicer()}")
    header.append(f"  Timeout: {slicer_client.timeout}s")
    
    return header


def pytest_sessionstart(session):
    """Called after the Session object has been created"""
    print("\n" + "="*60)
    print("Starting 3D Slicer API Tests")
    print("="*60)


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished"""
    print("\n" + "="*60)
    print("3D Slicer API Tests Completed")
    print(f"Exit Status: {exitstatus}")
    print("="*60)
