"""
Integration tests for 3D Slicer API operations

These tests perform real operations with Slicer via CLI and require
Slicer to be installed on the system.
"""

import pytest
import os
import tempfile
from pathlib import Path
from tests.slicer_api.slicer_client import SlicerClient


@pytest.fixture
def slicer_client():
    """Create a SlicerClient instance for testing"""
    return SlicerClient()


@pytest.fixture
def sample_nrrd_path():
    """Create a small sample NRRD volume for testing"""
    # Create a simple 3D volume without numpy
    volume_data = []
    size = (16, 16, 16)
    z, y, x = size
    
    # Create a sphere-like structure in the center
    center_z, center_y, center_x = z//2, y//2, x//2
    radius = min(z, y, x) // 4
    
    for i in range(z):
        for j in range(y):
            for k in range(x):
                # Calculate distance from center
                dist_sq = (i - center_z)**2 + (j - center_y)**2 + (k - center_x)**2
                dist = dist_sq ** 0.5
                
                if dist <= radius:
                    # Create gradient from center to edge
                    intensity = int(128 + 64 * (1 - dist/radius))
                    intensity = max(0, min(255, intensity))
                else:
                    intensity = 0
                
                volume_data.append(intensity)
    
    # Save as temporary NRRD file
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
sizes: {x} {y} {z}
space directions: (1,0,0) (0,1,0) (0,0,1)
kinds: domain domain domain
endian: little
encoding: raw
"""
        f.write(header.encode('ascii'))
        f.write(b'\n')  # Empty line after header
        f.write(bytes(volume_data))
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass


class TestSlicerIntegration:
    """Integration tests for Slicer operations"""
    
    @pytest.mark.skipif(True, reason="Requires Slicer installation")
    def test_slicer_availability(self, slicer_client):
        """Test that Slicer is available on the system"""
        assert slicer_client.is_slicer_available(), "3D Slicer not found on system"
        assert slicer_client.slicer_path is not None
        assert os.path.isfile(slicer_client.slicer_path)
    
    @pytest.mark.skipif(True, reason="Requires Slicer installation")
    def test_cli_connection(self, slicer_client):
        """Test basic CLI connection to Slicer"""
        result = slicer_client.test_cli_connection()
        
        assert result["success"] == True
        assert "Slicer Python version" in result["stdout"]
        assert "Slicer available" in result["stdout"]
    
    @pytest.mark.skipif(True, reason="Requires Slicer installation")
    def test_load_volume_integration(self, slicer_client, sample_nrrd_path):
        """Test loading a volume file in Slicer"""
        result = slicer_client.load_volume(sample_nrrd_path)
        
        assert result["success"] == True
        assert result["test_type"] == "load_volume"
        assert result["file_path"] == sample_nrrd_path
        assert "Volume loaded successfully" in result["stdout"]
        assert "Volume dimensions" in result["stdout"]
    
    @pytest.mark.skipif(True, reason="Requires Slicer installation")
    def test_create_segmentation_integration(self, slicer_client):
        """Test creating a segmentation node in Slicer"""
        result = slicer_client.create_segmentation("IntegrationTestSeg")
        
        assert result["success"] == True
        assert result["test_type"] == "create_segmentation"
        assert result["segmentation_name"] == "IntegrationTestSeg"
        assert "Segmentation created" in result["stdout"]
        assert "Scene node count" in result["stdout"]
    
    @pytest.mark.skipif(True, reason="Requires Slicer installation")
    def test_scene_operations_integration(self, slicer_client):
        """Test scene information retrieval"""
        result = slicer_client.get_scene_info()
        
        assert result["success"] == True
        assert result["test_type"] == "scene_info"
        assert "Scene node count" in result["stdout"]
        assert "Scene modified time" in result["stdout"]
    
    @pytest.mark.skipif(True, reason="Requires Slicer installation")
    def test_complete_workflow_integration(self, slicer_client, sample_nrrd_path):
        """Test a complete workflow: load volume, create segmentation, get scene info"""
        # Load volume
        load_result = slicer_client.load_volume(sample_nrrd_path)
        assert load_result["success"] == True
        
        # Create segmentation
        seg_result = slicer_client.create_segmentation("WorkflowTest")
        assert seg_result["success"] == True
        
        # Get scene info
        scene_result = slicer_client.get_scene_info()
        assert scene_result["success"] == True
        
        # Verify scene has nodes
        assert "Scene node count" in scene_result["stdout"]
    
    @pytest.mark.skipif(True, reason="Requires Slicer installation")
    def test_error_handling_integration(self, slicer_client):
        """Test error handling with invalid operations"""
        # Test loading non-existent file
        with pytest.raises(FileNotFoundError):
            slicer_client.load_volume("/nonexistent/file.nrrd")
        
        # Test invalid Python code
        result = slicer_client.execute_cli_command("invalid_python_syntax")
        assert result["success"] == False
        assert result["returncode"] != 0
    
    @pytest.mark.skipif(True, reason="Requires Slicer installation")
    def test_timeout_handling_integration(self, slicer_client):
        """Test timeout handling with long-running operations"""
        # Create a command that will take longer than timeout
        long_running_code = """
import time
time.sleep(60)  # Sleep for 60 seconds
print("This should timeout")
"""
        
        # Set short timeout
        original_timeout = slicer_client.timeout
        slicer_client.timeout = 5
        
        try:
            result = slicer_client.execute_cli_command(long_running_code)
            assert result["success"] == False
            assert "timed out" in result["stderr"]
        finally:
            slicer_client.timeout = original_timeout


class TestSlicerMockIntegration:
    """Mock integration tests that don't require actual Slicer"""
    
    def test_mock_load_volume(self, slicer_client, sample_nrrd_path):
        """Test volume loading with mocked Slicer response"""
        from unittest.mock import patch
        
        mock_result = {
            "success": True,
            "stdout": "Volume loaded successfully: test_volume\nVolume dimensions: (16, 16, 16)",
            "stderr": "",
            "returncode": 0
        }
        
        with patch.object(slicer_client, 'execute_cli_command', return_value=mock_result):
            result = slicer_client.load_volume(sample_nrrd_path)
            
            assert result["success"] == True
            assert result["test_type"] == "load_volume"
            assert result["file_path"] == sample_nrrd_path
            assert "Volume loaded successfully" in result["stdout"]
    
    def test_mock_complete_workflow(self, slicer_client, sample_nrrd_path):
        """Test complete workflow with mocked Slicer responses"""
        from unittest.mock import patch
        
        mock_load_result = {
            "success": True,
            "stdout": "Volume loaded successfully: test_volume",
            "stderr": "",
            "returncode": 0
        }
        
        mock_seg_result = {
            "success": True,
            "stdout": "Segmentation created: WorkflowTest\nScene node count: 2",
            "stderr": "",
            "returncode": 0
        }
        
        mock_scene_result = {
            "success": True,
            "stdout": "Scene node count: 2\nScene modified time: 12345",
            "stderr": "",
            "returncode": 0
        }
        
        with patch.object(slicer_client, 'execute_cli_command') as mock_execute:
            mock_execute.side_effect = [mock_load_result, mock_seg_result, mock_scene_result]
            
            # Load volume
            load_result = slicer_client.load_volume(sample_nrrd_path)
            assert load_result["success"] == True
            
            # Create segmentation
            seg_result = slicer_client.create_segmentation("WorkflowTest")
            assert seg_result["success"] == True
            
            # Get scene info
            scene_result = slicer_client.get_scene_info()
            assert scene_result["success"] == True
            
            # Verify all commands were called
            assert mock_execute.call_count == 3


class TestSlicerConfiguration:
    """Tests for Slicer configuration and setup"""
    
    def test_config_loading(self):
        """Test configuration file loading"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                "slicer_path": "/test/path/Slicer.exe",
                "timeout_seconds": 45,
                "enable_cli_tests": False,
                "enable_direct_import_tests": True
            }
            import json
            json.dump(config, f)
            config_path = f.name
        
        try:
            client = SlicerClient(config_path)
            assert client.slicer_path == "/test/path/Slicer.exe"
            assert client.timeout == 45
            assert client.config["enable_cli_tests"] == False
            assert client.config["enable_direct_import_tests"] == True
        finally:
            os.unlink(config_path)
    
    def test_config_defaults(self):
        """Test default configuration values"""
        client = SlicerClient()
        
        assert client.timeout == 30
        assert client.config["enable_cli_tests"] == True
        assert client.config["enable_direct_import_tests"] == True
        assert "common_paths" in client.config
        assert len(client.config["common_paths"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
