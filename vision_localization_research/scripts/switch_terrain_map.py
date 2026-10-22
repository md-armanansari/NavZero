"""
Stress-Test & Terrain Switcher Script.
Allows you to switch between:
1. Real Ladakh Mountain Map (High features -> Green Lock)
2. Indian Ocean / Water Map (Zero features -> Shows genuine CV rejection!)
3. Custom Map (Any image you drag & drop into data folder)
"""

import sys
import shutil
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
data_dir = repo_root / "data"

def print_menu():
    print("=" * 68)
    print("  TERRAIN MAP SWITCHER & FAILURE MODE STRESS TEST")
    print("=" * 68)
    print("Choose which terrain map to load into your drone flight tracker:")
    print("  [1] Real Ladakh / Zanskar Mountain Map (High Contrast -> Green Lock)")
    print("  [2] Indian Ocean / Featureless Water Map (Zero Landmarks -> Failsafe Proof!)")
    print("  [3] Reset to Default Aerial Orthophoto")
    print("  [Q] Exit")
    print("=" * 68)

def switch_map():
    target_active = data_dir / "real_aerial_orthophoto.jpg"
    ladakh_img = data_dir / "ladakh_zanskar_map.jpg"
    ocean_img = data_dir / "ocean_test_map.jpg"

    while True:
        print_menu()
        choice = input("\nEnter choice [1, 2, 3 or Q]: ").strip().upper()

        if choice == '1':
            if ladakh_img.exists():
                shutil.copyfile(ladakh_img, target_active)
                print("\n[SUCCESS] Active map set to: REAL LADAKH & ZANSKAR MOUNTAINS.")
                print("Run 'run_interactive_map.bat' or 'run_real_aerial_tracker.bat' to see 300+ green inliers!\n")
            else:
                print(f"[ERROR] Could not find {ladakh_img}")
            break
        elif choice == '2':
            if ocean_img.exists():
                shutil.copyfile(ocean_img, target_active)
                print("\n[SUCCESS] Active map set to: INDIAN OCEAN (FEATURELESS WATER).")
                print("Now run 'run_interactive_map.bat' to PROVE to judges that inliers drop to 0 and")
                print("the system refuses to calculate fake coordinates!\n")
            else:
                print(f"[ERROR] Could not find {ocean_img}")
            break
        elif choice == '3':
            if ladakh_img.exists():
                shutil.copyfile(ladakh_img, target_active)
                print("\n[SUCCESS] Reset to default map.")
            break
        elif choice == 'Q':
            print("Exited.")
            break
        else:
            print("[WARN] Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    switch_map()
