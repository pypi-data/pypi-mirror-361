import os
import subprocess
import sys

def main():
    # Get the path to scrcpy.exe inside your package
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scrcpy_path = os.path.join(current_dir, "bin", "scrcpy.exe")

    if not os.path.exists(scrcpy_path):
        print("scrcpy.exe not found in internal bin folder.")
        sys.exit(1)

    # Run the local scrcpy version
    subprocess.run([scrcpy_path])
