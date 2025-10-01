# ============================================================
# Project: CLARA_VISIO
# File: main.py
# Date: 2025.08.25
# ------------------------------------------------------------
# Description:
# TODO
# ============================================================

from __future__ import annotations
import sys
from Stimulus.Light.photon import Photon
from PrimaryVisualPathway.NeuralRetina.MaculaLutea import input_layer 

# ============================================================
# MENU
# ============================================================

APP_TITLE = "CLARA_VISIO — Main Menu"

def print_menu() -> None:
    print("\n" + "=" * 56)
    print(APP_TITLE)
    print("=" * 56)
    print("1) Light Detection")
    print("0) Exit")
    print("-" * 56)

def read_choice(prompt: str = "Select an option: ") -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        # Gracefully handle Ctrl+D / Ctrl+C
        print("\nExiting...")
        sys.exit(0)

def main() -> None:
    while True:
        print_menu()
        choice = read_choice()

        if choice == "1":
            light_detection_stub()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose 1 or 0.")

# ============================================================
# METHODS
# ============================================================

def light_detection_stub() -> None:
    """
    Placeholder for the Light Detection pipeline.
    Later this will:
      - load an image
      - compute luminance
      - threshold to light/dark
      - print/save results
    """
    print("\n[Light Detection]")
    
    photon = Photon(550, 0, 0, 0)
    photons = [photon]
    print("Photon list:", photons)

    profile = input_layer.photoreceptor_profile(2000)
    print(profile)

if __name__ == "__main__":
    main()