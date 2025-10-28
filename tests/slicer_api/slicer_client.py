"""
3D Slicer API Client Library

Provides connection methods to interact with locally installed 3D Slicer:
- CLI Interface: Execute Slicer commands via subprocess
- Direct Import: Import Slicer Python modules when available
"""

import os
import json
import glob
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
import logging

logger = logging.getLogger(__name__)


class SlicerClient:
    """Client for connecting to 3D Slicer via different methods"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Slicer client
        
        Args:
            config_path: Path to configuration JSON file
        """
        self.config = self._load_config(config_path)
        self.slicer_path = self.config.get('slicer_path')
        self.timeout = self.config.get('timeout_seconds', 30)
        
        # Auto-detect Slicer if path not provided
        if not self.slicer_path:
            self.slicer_path = self._detect_slicer_path()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        if config_path is None:
            config_path = Path(__file__).parent / "slicer_config.json"
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
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
    
    def _detect_slicer_path(self) -> Optional[str]:
        """
        Auto-detect 3D Slicer installation path on Windows
        
        Returns:
            Path to Slicer.exe or None if not found
        """
        common_paths = self.config.get('common_paths', [])
        
        for pattern in common_paths:
            matches = glob.glob(pattern)
            for match in matches:
                slicer_exe = os.path.join(match, "Slicer.exe")
                if os.path.isfile(slicer_exe):
                    logger.info(f"Found Slicer at: {slicer_exe}")
                    return slicer_exe
        
        logger.warning("3D Slicer not found in common installation paths")
        return None
    
    def is_slicer_available(self) -> bool:
        """
        Check if Slicer is available for CLI operations
        
        Returns:
            True if Slicer executable found
        """
        return self.slicer_path is not None and os.path.isfile(self.slicer_path)
    
    def can_import_slicer(self) -> bool:
        """
        Check if Slicer Python modules can be imported directly
        
        Returns:
            True if slicer module can be imported
        """
        try:
            import slicer
            return True
        except ImportError:
            return False
    
    def execute_cli_command(self, python_code: str) -> Dict[str, Any]:
        """
        Execute Python code in Slicer via CLI
        
        Args:
            python_code: Python code to execute in Slicer
            
        Returns:
            Dictionary with execution results
        """
        if not self.is_slicer_available():
            raise RuntimeError("3D Slicer not available for CLI operations")
        
        try:
            # Escape quotes and prepare command
            escaped_code = python_code.replace('"', '\\"')
            cmd = [self.slicer_path, "--python-code", escaped_code]
            
            logger.debug(f"Executing CLI command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=os.path.dirname(self.slicer_path)
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {self.timeout} seconds",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def test_cli_connection(self) -> Dict[str, Any]:
        """
        Test CLI connection with simple Python code
        
        Returns:
            Test results dictionary
        """
        test_code = """
import sys
print("Slicer Python version:", sys.version)
print("Slicer available:", 'slicer' in sys.modules)
"""
        
        result = self.execute_cli_command(test_code)
        result["test_type"] = "cli_connection"
        return result
    
    def test_direct_import(self) -> Dict[str, Any]:
        """
        Test direct import of Slicer modules
        
        Returns:
            Test results dictionary
        """
        try:
            import slicer
            import vtk
            import qt
            
            return {
                "success": True,
                "test_type": "direct_import",
                "slicer_version": getattr(slicer, 'app', {}).get('applicationVersion', 'Unknown'),
                "vtk_version": vtk.vtkVersion.GetVTKVersion(),
                "qt_version": qt.QT_VERSION_STR if hasattr(qt, 'QT_VERSION_STR') else 'Unknown'
            }
        except ImportError as e:
            return {
                "success": False,
                "test_type": "direct_import",
                "error": str(e)
            }
    
    def load_volume(self, file_path: str) -> Dict[str, Any]:
        """
        Load a volume file in Slicer via CLI
        
        Args:
            file_path: Path to volume file (NRRD, NIfTI, etc.)
            
        Returns:
            Load results dictionary
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Volume file not found: {file_path}")
        
        python_code = f"""
import slicer
volumeNode = slicer.util.loadVolume('{file_path}')
if volumeNode:
    print("Volume loaded successfully:", volumeNode.GetName())
    print("Volume dimensions:", volumeNode.GetImageData().GetDimensions())
else:
    print("Failed to load volume")
"""
        
        result = self.execute_cli_command(python_code)
        result["test_type"] = "load_volume"
        result["file_path"] = file_path
        return result
    
    def create_segmentation(self, name: str = "TestSegmentation") -> Dict[str, Any]:
        """
        Create a segmentation node in Slicer via CLI
        
        Args:
            name: Name for the segmentation node
            
        Returns:
            Creation results dictionary
        """
        python_code = f"""
import slicer
segmentationNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode')
segmentationNode.SetName('{name}')
print("Segmentation created:", segmentationNode.GetName())
print("Scene node count:", slicer.mrmlScene.GetNumberOfNodes())
"""
        
        result = self.execute_cli_command(python_code)
        result["test_type"] = "create_segmentation"
        result["segmentation_name"] = name
        return result
    
    def get_scene_info(self) -> Dict[str, Any]:
        """
        Get information about the current MRML scene
        
        Returns:
            Scene information dictionary
        """
        python_code = """
import slicer
scene = slicer.mrmlScene
print("Scene node count:", scene.GetNumberOfNodes())
print("Scene modified time:", scene.GetMTime())

# List node types
node_types = {}
for i in range(scene.GetNumberOfNodes()):
    node = scene.GetNthNode(i)
    node_type = node.GetClassName()
    if node_type not in node_types:
        node_types[node_type] = 0
    node_types[node_type] += 1

print("Node types:", node_types)
"""
        
        result = self.execute_cli_command(python_code)
        result["test_type"] = "scene_info"
        return result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all available connection tests
        
        Returns:
            Comprehensive test results
        """
        results = {
            "slicer_path": self.slicer_path,
            "is_slicer_available": self.is_slicer_available(),
            "can_import_slicer": self.can_import_slicer(),
            "tests": {}
        }
        
        # Test CLI connection
        if self.config.get('enable_cli_tests', True):
            results["tests"]["cli_connection"] = self.test_cli_connection()
        
        # Test direct import
        if self.config.get('enable_direct_import_tests', True):
            results["tests"]["direct_import"] = self.test_direct_import()
        
        return results


def create_test_client() -> SlicerClient:
    """Create a SlicerClient instance for testing"""
    return SlicerClient()


if __name__ == "__main__":
    # Test the client
    client = SlicerClient()
    results = client.run_all_tests()
    
    print("3D Slicer Connection Test Results:")
    print("=" * 40)
    print(f"Slicer Path: {results['slicer_path']}")
    print(f"Slicer Available: {results['is_slicer_available']}")
    print(f"Can Import Slicer: {results['can_import_slicer']}")
    print()
    
    for test_name, test_result in results['tests'].items():
        print(f"{test_name.upper()}:")
        print(f"  Success: {test_result.get('success', False)}")
        if 'stdout' in test_result and test_result['stdout']:
            print(f"  Output: {test_result['stdout'].strip()}")
        if 'error' in test_result:
            print(f"  Error: {test_result['error']}")
        print()
