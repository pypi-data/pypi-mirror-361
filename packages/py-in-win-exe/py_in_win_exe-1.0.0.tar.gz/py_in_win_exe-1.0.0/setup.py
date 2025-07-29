from setuptools import setup, find_packages
import os
from pathlib import Path

# Пути к файлам
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
package_dir = current_dir / "py_in_win_exe"

# Копирование Beta.exe
beta_exe_src = src_dir / "Beta.exe"
beta_exe_dst = package_dir / "Beta.exe"

if beta_exe_src.exists():
    with open(beta_exe_src, 'rb') as src_file:
        with open(beta_exe_dst, 'wb') as dst_file:
            dst_file.write(src_file.read())
else:
    raise FileNotFoundError(f"Файл {beta_exe_src} не найден!")

setup(
    name="py-in-win-exe",
    version="1.0.0",
    packages=find_packages(),
    package_data={
        "py_in_win_exe": ["Beta.exe"],
    },
    include_package_data=True,
    install_requires=[
        "pyinstaller>=5.0",
    ],
    entry_points={
        "console_scripts": [
            "py-in-win-exe=py_in_win_exe.gui:main",
        ],
    },
)