import subprocess
import sys

def compile_script(input_file, output_name="output", icon=None, console=True):
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole" if not console else "",
        f"--name={output_name}",
        f"--icon={icon}" if icon else "",
        input_file
    ]
    subprocess.run([arg for arg in cmd if arg])