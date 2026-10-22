"""
Terrain Map Switcher for Drone Navigation.
Instantly switches the active terrain between:
[1] Chandigarh University (CU) Campus Map (Blocks, Hostels, Sports Grounds)
[2] Real Ladakh / Zanskar Mountain Map (High Altitude Mountains & Snow)
[3] Indian Ocean / Water Map (Zero Features -> Fail-Safe Proof!)
[4] Punjab Farmland Map (Agricultural Fields, Roads & Canals)
"""

import sys
import shutil
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
data_dir = repo_root / "data"

def print_menu():
    print("=" * 72)
    print("       DRONE TERRAIN MAP SWITCHER & STRESS TEST")
    print("=" * 72)
    print("Choose which terrain map to load into your drone flight tracker:")
    print("  [1] Chandigarh University (CU) Campus Map (Real Campus Blocks & Ground!)")
    print("  [2] Real Ladakh / Zanskar Mountain Map   (High Altitude Mountains & Snow)")
    print("  [3] Indian Ocean / Water Map            (Zero Features -> Fail-Safe Proof!)")
    print("  [4] Punjab Farmland Map                (Green Fields, Roads & Canals)")
    print("  [Q] Exit")
    print("=" * 72)

def switch_map():
    target_active = data_dir / "real_aerial_orthophoto.jpg"
    cu_img = data_dir / "cu_campus_map.jpg"
    ladakh_img = data_dir / "ladakh_zanskar_map.jpg"
    ocean_img = data_dir / "ocean_test_map.jpg"
    farmland_img = data_dir / "punjab_farmland_map.jpg"

    while True:
        print_menu()
        choice = input("\nEnter choice [1, 2, 3, 4 or Q]: ").strip().upper()

        if choice == '1':
            if cu_img.exists():
                shutil.copyfile(cu_img, target_active)
                print("\n>>> [SUCCESS] Active map changed to: [1] CHANDIGARH UNIVERSITY CAMPUS.")
                print(">>> Now run 'run_interactive_map.bat' to fly your drone across CU campus!\n")
            else:
                print(f"[ERROR] Could not find {cu_img}")
            break
        elif choice == '2':
            if ladakh_img.exists():
                shutil.copyfile(ladakh_img, target_active)
                print("\n>>> [SUCCESS] Active map changed to: [2] REAL LADAKH & ZANSKAR MOUNTAINS.")
                print(">>> Now run 'run_interactive_map.bat' to fly over Ladakh ridges!\n")
            else:
                print(f"[ERROR] Could not find {ladakh_img}")
            break
        elif choice == '3':
            if ocean_img.exists():
                shutil.copyfile(ocean_img, target_active)
                print("\n>>> [SUCCESS] Active map changed to: [3] INDIAN OCEAN (FEATURELESS WATER).")
                print(">>> Now run 'run_interactive_map.bat' to see Inliers drop to 0 and prove real CV!\n")
            else:
                print(f"[ERROR] Could not find {ocean_img}")
            break
        elif choice == '4':
            if farmland_img.exists():
                shutil.copyfile(farmland_img, target_active)
                print("\n>>> [SUCCESS] Active map changed to: [4] PUNJAB FARMLAND.")
                print(">>> Now run 'run_interactive_map.bat' to fly over green fields and roads!\n")
            else:
                print(f"[ERROR] Could not find {farmland_img}")
            break
        elif choice == 'Q':
            print("Exited.")
            break
        else:
            print("[WARN] Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    switch_map()
