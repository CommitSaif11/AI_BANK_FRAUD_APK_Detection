import os
import platform
import subprocess
import tempfile
import shutil
from pathlib import Path

# Define paths to the tools, assuming this script is in backend/app/extraction
# and the tools are in backend/tools
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
TOOLS_DIR = BACKEND_DIR / "tools"
APKTOOL_PATH = TOOLS_DIR / "apktool.jar"
JADX_DIR = TOOLS_DIR / "jadx"

def decompile_apk(apk_path: str):
    """
    Decompiles an APK file using apktool and jadx.

    Args:
        apk_path: The absolute path to the APK file.

    Returns:
        A tuple containing the paths to the apktool and jadx output folders.
        Returns (None, None) if decompilation fails.
    """
    if not Path(apk_path).exists():
        print(f"Error: APK file not found at {apk_path}")
        return None, None

    # Check for Java
    if not shutil.which("java"):
        print("Error: Java is not installed or not in the system's PATH.")
        print("apktool and jadx require Java to run.")
        return None, None

    # Create a temporary directory to store all outputs
    temp_dir = tempfile.mkdtemp(prefix="apk_analysis_", dir=str(BACKEND_DIR))
    print(f"Created temporary directory: {temp_dir}")

    apktool_output_path = Path(temp_dir) / "apktool_output"
    jadx_output_path = Path(temp_dir) / "jadx_output"

    try:
        # 1. Run apktool
        print("Running apktool...")
        apktool_cmd = [
            "java", "-jar", str(APKTOOL_PATH),
            "d",  # decode
            apk_path,
            "-o", str(apktool_output_path),
            "-f"  # force overwrite
        ]
        apktool_result = subprocess.run(apktool_cmd, capture_output=True, text=True, check=True)
        print("apktool finished successfully.")
        print(f"apktool output in: {apktool_output_path}")

        # 2. Run JADX
        print("Running JADX...")
        jadx_executable = "jadx.bat" if platform.system() == "Windows" else "jadx"
        jadx_bin_path = JADX_DIR / "bin" / jadx_executable

        if not jadx_bin_path.exists():
            print(f"Error: JADX executable not found at {jadx_bin_path}")
            raise FileNotFoundError(f"JADX executable not found at {jadx_bin_path}")

        jadx_cmd = [
            str(jadx_bin_path),
            "-d", str(jadx_output_path),
            apk_path
        ]
        jadx_result = subprocess.run(jadx_cmd, capture_output=True, text=True, check=True)
        print("JADX finished successfully.")
        print(f"JADX output in: {jadx_output_path}")

        return str(apktool_output_path), str(jadx_output_path)

    except subprocess.CalledProcessError as e:
        print(f"Error during decompilation process:")
        print(f"Command: {' '.join(e.cmd)}")
        print(f"Return code: {e.returncode}")
        print(f"Output:\n{e.stdout}\n{e.stderr}")
        # Clean up the temp directory on failure
        shutil.rmtree(temp_dir)
        return None, None
    except FileNotFoundError as e:
        print(f"Error: {e}")
        shutil.rmtree(temp_dir)
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        shutil.rmtree(temp_dir)
        return None, None

if __name__ == '__main__':
    # Example usage for testing
    # Create a dummy APK file for testing if it doesn't exist
    test_apk_path = BACKEND_DIR / "dummy_test.apk"
    if not test_apk_path.exists():
        print("Creating a dummy APK file for testing...")
        with open(test_apk_path, "w") as f:
            f.write("This is not a real APK.")

    print(f"Testing decompilation with: {test_apk_path}")
    apktool_out, jadx_out = decompile_apk(str(test_apk_path))

    if apktool_out and jadx_out:
        print("\nDecompilation Test Successful!")
        print(f"  - Apktool output: {apktool_out}")
        print(f"  - JADX output: {jadx_out}")
        # Clean up generated files for the test
        shutil.rmtree(Path(apktool_out).parent)
        print("Cleaned up temporary directory.")
    else:
        print("\nDecompilation Test Failed.")

    if test_apk_path.exists():
        os.remove(test_apk_path)
        print("Removed dummy APK file.")

