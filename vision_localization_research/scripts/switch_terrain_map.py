"""
Terrain Map Switcher for Drone Navigation.
Instantly switches the active terrain between:
[1] Real Ladakh / Zanskar Mountain Map (High Altitude Mountains & Snow)
[2] Indian Ocean / Water Map (Featureless Water -> Inliers = 0 Fail-Safe Proof!)
[3] Punjab Plains & Farmland Map (Agricultural Fields, Roads & Canals)
"""

import sys
import shutil
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
data_dir = repo_root / "data"

def print_menu():
    print("=" * 70)
    print("       DRONE TERRAIN MAP SWITCHER & STRESS TEST")
    print("=" * 70)
    print("Choose which terrain map to load into your drone flight tracker:")
    print("  [1] Real Ladakh / Zanskar Mountain Map  (Mountain Ridges & Snow)")
    print("  [2] Indian Ocean / Water Map           (Zero Features -> Fail-Safe Proof!)")
    print("  [3] Punjab Plains & Farmland Map       (Green Fields, Roads & Canals)")
    print("  [Q] Exit")
    print("=" * 70)

def switch_map():
    target_active = data_dir / "real_aerial_orthophoto.jpg"
    ladakh_img = data_dir / "ladakh_zanskar_map.jpg"
    ocean_img = data_dir / "ocean_test_map.jpg"
    farmland_img = data_dir / "punjab_farmland_map.jpg"

    while True:
        print_menu()
        choice = input("\nEnter choice [1, 2, 3 or Q]: ").strip().upper()

        if choice == '1':
            if ladakh_img.exists():
                shutil.copyfile(ladakh_img, target_active)
                print("\n>>> [SUCCESS] Active map changed to: [1] REAL LADAKH & ZANSKAR MOUNTAINS.")
                print(">>> Now run 'run_interactive_map.bat' to fly over Ladakh ridges!\n")
            else:
                print(f"[ERROR] Could not find {ladakh_img}")
            break
        elif choice == '2':
            if ocean_img.exists():
                shutil.copyfile(ocean_img, target_active)
                print("\n>>> [SUCCESS] Active map changed to: [2] INDIAN OCEAN (FEATURELESS WATER).")
                print(">>> Now run 'run_interactive_map.bat' to see Inliers drop to 0 and prove real CV!\n")
            else:
                print(f"[ERROR] Could not find {ocean_img}")
            break
        elif choice == '3':
            if farmland_img.exists():
                shutil.copyfile(farmland_img, target_active)
                print("\n>>> [SUCCESS] Active map changed to: [3] PUNJAB PLAINS & FARMLAND.")
                print(">>> Now run 'run_interactive_map.bat' to fly over green fields and roads!\n")
            else:
                print(f"[ERROR] Could not find {farmland_img}")
            break
        elif choice == 'Q':
            print("Exited.")
            break
        else:
            print("[WARN] Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    switch_map()
