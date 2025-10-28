"""
Generate a small sample NRRD volume for testing purposes (without numpy dependency)
"""

import os
from pathlib import Path


def create_sample_nrrd(output_path: str, size: tuple = (16, 16, 16)):
    """
    Create a small sample NRRD volume file for testing
    
    Args:
        output_path: Path where to save the NRRD file
        size: Dimensions of the volume (Z, Y, X)
    """
    z, y, x = size
    
    # Create a simple 3D volume with some structure
    volume_data = []
    
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
    
    # Write NRRD file
    with open(output_path, 'wb') as f:
        # NRRD header
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
space origin: (0,0,0)
"""
        f.write(header.encode('ascii'))
        f.write(b'\n')  # Empty line after header
        
        # Write volume data as bytes
        volume_bytes = bytes(volume_data)
        f.write(volume_bytes)
    
    print(f"Created sample NRRD volume: {output_path}")
    print(f"Dimensions: {size}")
    print(f"Data type: uint8")
    print(f"File size: {os.path.getsize(output_path)} bytes")


if __name__ == "__main__":
    # Create sample volume in fixtures directory
    fixtures_dir = Path(__file__).parent
    output_path = fixtures_dir / "sample_volume.nrrd"
    
    create_sample_nrrd(str(output_path))