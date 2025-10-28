"""
Unit tests for 3D Slicer API connection methods
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from tests.slicer_api.slicer_client import SlicerClient


class TestSlicerClient:
    """Test cases for SlicerClient class"""
    
    def test_init_with_default_config(self):
        """Test client initialization with default config"""
        client = SlicerClient()
        assert client.timeout == 30
        assert client.config is not None
        assert 'common_paths' in client.config
    
    def test_init_with_custom_config(self):
        """Test client initialization with custom config"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                "slicer_path": "/custom/path/Slicer.exe",
                "timeout_seconds": 60,
                "enable_cli_tests": False
            }
            import json
            json.dump(config, f)
            config_path = f.name
        
        try:
            client = SlicerClient(config_path)
            assert client.slicer_path == "/custom/path/Slicer.exe"
            assert client.timeout == 60
            assert client.config["enable_cli_tests"] == False
        finally:
            os.unlink(config_path)
    
    @patch('glob.glob')
    def test_detect_slicer_path_success(self, mock_glob):
        """Test successful Slicer path detection"""
        mock_glob.return_value = ["C:\\Program Files\\Slicer-5.2.2"]
        
        with patch('os.path.isfile', return_value=True):
            client = SlicerClient()
            client.slicer_path = None
            detected_path = client._detect_slicer_path()
            
            assert detected_path == "C:\\Program Files\\Slicer-5.2.2\\Slicer.exe"
    
    @patch('glob.glob')
    def test_detect_slicer_path_not_found(self, mock_glob):
        """Test Slicer path detection when not found"""
        mock_glob.return_value = []
        
        client = SlicerClient()
        client.slicer_path = None
        detected_path = client._detect_slicer_path()
        
        assert detected_path is None
    
    def test_is_slicer_available_true(self):
        """Test is_slicer_available when Slicer is available"""
        with patch('os.path.isfile', return_value=True):
            client = SlicerClient()
            client.slicer_path = "/path/to/Slicer.exe"
            assert client.is_slicer_available() == True
    
    def test_is_slicer_available_false(self):
        """Test is_slicer_available when Slicer is not available"""
        with patch('os.path.isfile', return_value=False):
            client = SlicerClient()
            client.slicer_path = "/path/to/Slicer.exe"
            assert client.is_slicer_available() == False
    
    def test_is_slicer_available_no_path(self):
        """Test is_slicer_available when no path is set"""
        client = SlicerClient()
        client.slicer_path = None
        assert client.is_slicer_available() == False
    
    def test_can_import_slicer_true(self):
        """Test can_import_slicer when import succeeds"""
        client = SlicerClient()
        
        with patch('builtins.__import__', return_value=MagicMock()):
            assert client.can_import_slicer() == True
    
    def test_can_import_slicer_false(self):
        """Test can_import_slicer when import fails"""
        client = SlicerClient()
        
        with patch('builtins.__import__', side_effect=ImportError("No module named 'slicer'")):
            assert client.can_import_slicer() == False
    
    @patch('subprocess.run')
    def test_execute_cli_command_success(self, mock_run):
        """Test successful CLI command execution"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Test output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        client = SlicerClient()
        client.slicer_path = "/path/to/Slicer.exe"
        
        # Mock the is_slicer_available check
        with patch.object(client, 'is_slicer_available', return_value=True):
            result = client.execute_cli_command("print('test')")
        
        assert result["success"] == True
        assert result["stdout"] == "Test output"
        assert result["returncode"] == 0
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_execute_cli_command_failure(self, mock_run):
        """Test CLI command execution failure"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error message"
        mock_run.return_value = mock_result
        
        client = SlicerClient()
        client.slicer_path = "/path/to/Slicer.exe"
        
        # Mock the is_slicer_available check
        with patch.object(client, 'is_slicer_available', return_value=True):
            result = client.execute_cli_command("invalid_code")
        
        assert result["success"] == False
        assert result["stderr"] == "Error message"
        assert result["returncode"] == 1
    
    @patch('subprocess.run')
    def test_execute_cli_command_timeout(self, mock_run):
        """Test CLI command execution timeout"""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)
        
        client = SlicerClient()
        client.slicer_path = "/path/to/Slicer.exe"
        client.timeout = 30
        
        # Mock the is_slicer_available check
        with patch.object(client, 'is_slicer_available', return_value=True):
            result = client.execute_cli_command("print('test')")
        
        assert result["success"] == False
        assert "timed out" in result["stderr"]
        assert result["returncode"] == -1
    
    def test_execute_cli_command_no_slicer(self):
        """Test CLI command execution when Slicer not available"""
        client = SlicerClient()
        client.slicer_path = None
        
        with pytest.raises(RuntimeError, match="3D Slicer not available"):
            client.execute_cli_command("print('test')")
    
    @patch.object(SlicerClient, 'execute_cli_command')
    def test_test_cli_connection(self, mock_execute):
        """Test CLI connection test"""
        mock_execute.return_value = {
            "success": True,
            "stdout": "Slicer Python version: 3.9.0\nSlicer available: True",
            "stderr": "",
            "returncode": 0
        }
        
        client = SlicerClient()
        client.slicer_path = "/path/to/Slicer.exe"
        
        result = client.test_cli_connection()
        
        assert result["test_type"] == "cli_connection"
        assert result["success"] == True
        assert "Slicer Python version" in result["stdout"]
    
    @patch('builtins.__import__')
    def test_test_direct_import_success(self, mock_import):
        """Test successful direct import test"""
        # Mock slicer module
        mock_slicer = MagicMock()
        mock_slicer.app = {"applicationVersion": "5.2.2"}
        mock_vtk = MagicMock()
        mock_vtk.vtkVersion.GetVTKVersion.return_value = "9.2.0"
        mock_qt = MagicMock()
        mock_qt.QT_VERSION_STR = "5.15.0"
        
        def import_side_effect(name, *args, **kwargs):
            if name == 'slicer':
                return mock_slicer
            elif name == 'vtk':
                return mock_vtk
            elif name == 'qt':
                return mock_qt
            else:
                return MagicMock()
        
        mock_import.side_effect = import_side_effect
        
        client = SlicerClient()
        result = client.test_direct_import()
        
        assert result["success"] == True
        assert result["test_type"] == "direct_import"
        assert result["slicer_version"] == "5.2.2"
        assert result["vtk_version"] == "9.2.0"
        assert result["qt_version"] == "5.15.0"
    
    @patch('builtins.__import__')
    def test_test_direct_import_failure(self, mock_import):
        """Test direct import test failure"""
        mock_import.side_effect = ImportError("No module named 'slicer'")
        
        client = SlicerClient()
        result = client.test_direct_import()
        
        assert result["success"] == False
        assert result["test_type"] == "direct_import"
        assert "No module named 'slicer'" in result["error"]
    
    @patch.object(SlicerClient, 'execute_cli_command')
    def test_load_volume_success(self, mock_execute):
        """Test successful volume loading"""
        mock_execute.return_value = {
            "success": True,
            "stdout": "Volume loaded successfully: test_volume\nVolume dimensions: (64, 64, 64)",
            "stderr": "",
            "returncode": 0
        }
        
        client = SlicerClient()
        client.slicer_path = "/path/to/Slicer.exe"
        
        with tempfile.NamedTemporaryFile(suffix='.nrrd', delete=False) as f:
            f.write(b"dummy data")
            temp_path = f.name
        
        try:
            result = client.load_volume(temp_path)
            
            assert result["test_type"] == "load_volume"
            assert result["file_path"] == temp_path
            assert result["success"] == True
            assert "Volume loaded successfully" in result["stdout"]
        finally:
            os.unlink(temp_path)
    
    def test_load_volume_file_not_found(self):
        """Test volume loading with non-existent file"""
        client = SlicerClient()
        
        with pytest.raises(FileNotFoundError):
            client.load_volume("/nonexistent/file.nrrd")
    
    @patch.object(SlicerClient, 'execute_cli_command')
    def test_create_segmentation(self, mock_execute):
        """Test segmentation creation"""
        mock_execute.return_value = {
            "success": True,
            "stdout": "Segmentation created: TestSegmentation\nScene node count: 1",
            "stderr": "",
            "returncode": 0
        }
        
        client = SlicerClient()
        client.slicer_path = "/path/to/Slicer.exe"
        
        result = client.create_segmentation("TestSegmentation")
        
        assert result["test_type"] == "create_segmentation"
        assert result["segmentation_name"] == "TestSegmentation"
        assert result["success"] == True
        assert "Segmentation created" in result["stdout"]
    
    @patch.object(SlicerClient, 'execute_cli_command')
    def test_get_scene_info(self, mock_execute):
        """Test scene info retrieval"""
        mock_execute.return_value = {
            "success": True,
            "stdout": "Scene node count: 3\nScene modified time: 12345\nNode types: {'vtkMRMLVolumeNode': 1, 'vtkMRMLSegmentationNode': 2}",
            "stderr": "",
            "returncode": 0
        }
        
        client = SlicerClient()
        client.slicer_path = "/path/to/Slicer.exe"
        
        result = client.get_scene_info()
        
        assert result["test_type"] == "scene_info"
        assert result["success"] == True
        assert "Scene node count" in result["stdout"]
    
    @patch.object(SlicerClient, 'test_cli_connection')
    @patch.object(SlicerClient, 'test_direct_import')
    def test_run_all_tests(self, mock_direct_import, mock_cli_connection):
        """Test running all available tests"""
        mock_cli_connection.return_value = {"success": True, "test_type": "cli_connection"}
        mock_direct_import.return_value = {"success": False, "test_type": "direct_import", "error": "Import failed"}
        
        client = SlicerClient()
        client.slicer_path = "/path/to/Slicer.exe"
        
        # Mock the availability checks
        with patch.object(client, 'is_slicer_available', return_value=True):
            results = client.run_all_tests()
        
        assert results["slicer_path"] == "/path/to/Slicer.exe"
        assert results["is_slicer_available"] == True
        assert "tests" in results
        assert "cli_connection" in results["tests"]
        assert "direct_import" in results["tests"]
        
        mock_cli_connection.assert_called_once()
        mock_direct_import.assert_called_once()


class TestSlicerClientIntegration:
    """Integration tests that may require actual Slicer installation"""
    
    @pytest.mark.skipif(not os.path.exists("C:\\Program Files\\Slicer*"), reason="Slicer not installed")
    def test_real_slicer_detection(self):
        """Test actual Slicer detection on system"""
        client = SlicerClient()
        # This test will only run if Slicer is actually installed
        if client.is_slicer_available():
            assert client.slicer_path is not None
            assert os.path.isfile(client.slicer_path)
    
    @pytest.mark.skipif(True, reason="Requires actual Slicer installation")
    def test_real_cli_execution(self):
        """Test actual CLI execution with real Slicer"""
        client = SlicerClient()
        if client.is_slicer_available():
            result = client.test_cli_connection()
            assert result["success"] == True
            assert "Slicer Python version" in result["stdout"]


if __name__ == "__main__":
    pytest.main([__file__])
