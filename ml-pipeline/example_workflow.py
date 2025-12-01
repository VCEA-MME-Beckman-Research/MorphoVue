#!/usr/bin/env python3
"""
Example workflow for MorphoVue Local MVP
Demonstrates how to run the pipeline on a sample TIFF file
"""

import os
import sys
import shutil
import numpy as np
from PIL import Image

# Import local pipeline
from run_local_segmentation import run_pipeline

def create_dummy_tiff(path: str, shape=(10, 128, 128)):
    """Create a dummy multi-page TIFF for testing"""
    print(f"Creating dummy TIFF at {path}...")
    
    frames = []
    for i in range(shape[0]):
        # Create a noisy image with some structure
        img_data = np.random.randint(0, 50, (shape[1], shape[2]), dtype=np.uint8)
        
        # Add a bright circle (tick body)
        cy, cx = shape[1]//2, shape[2]//2
        y, x = np.ogrid[:shape[1], :shape[2]]
        mask = ((y - cy)**2 + (x - cx)**2) <= (shape[1]//4)**2
        img_data[mask] = np.random.randint(150, 255, mask.sum(), dtype=np.uint8)
        
        frames.append(Image.fromarray(img_data))
    
    # Save as multi-page TIFF
    frames[0].save(
        path, 
        save_all=True, 
        append_images=frames[1:], 
        compression="tiff_deflate"
    )
    print("Dummy TIFF created successfully.")

def main():
    # Setup directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "input")
    results_dir = os.path.join(base_dir, "results")
    
    os.makedirs(input_dir, exist_ok=True)
    
    # 1. Check for input file or create dummy
    tiff_filename = "test_tick_scan.tiff"
    tiff_path = os.path.join(input_dir, tiff_filename)
    
    if len(sys.argv) > 1:
        # Use provided file
        user_file = sys.argv[1]
        if os.path.exists(user_file):
            print(f"Using input file: {user_file}")
            # Copy to input dir if not already there
            if os.path.abspath(user_file) != os.path.abspath(tiff_path):
                shutil.copy(user_file, tiff_path)
        else:
            print(f"File not found: {user_file}")
            return
    elif not os.path.exists(tiff_path):
        # Create dummy file
        create_dummy_tiff(tiff_path)
    else:
        print(f"Using existing test file: {tiff_path}")
    
    print("\n" + "="*50)
    print("MORPHOVUE LOCAL PIPELINE DEMO")
    print("="*50)
    print(f"Input: {tiff_path}")
    print(f"Output: {results_dir}")
    print("\nRunning pipeline...")
    
    try:
        # 2. Run pipeline
        scan_results_dir = run_pipeline(tiff_path, results_dir)
        
        print("\n" + "="*50)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("="*50)
        print(f"\nResults saved to: {scan_results_dir}")
        print("\nFiles generated:")
        for f in os.listdir(scan_results_dir):
            print(f" - {f}")
            
        print("\nNEXT STEPS:")
        print("1. Open 3D Slicer")
        print("2. Switch to 'Tick Segmentation Review' module")
        print("3. Click 'Load from Local'")
        print(f"4. Select TIFF: {tiff_path}")
        print(f"5. Select Mask: {os.path.join(scan_results_dir, 'mask.nrrd')}")
        
    except Exception as e:
        print(f"\nPipeline failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

