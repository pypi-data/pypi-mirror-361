from setuptools import setup, find_packages

setup(
    name="py-in-win-exe",
    version="1.0.2",
    packages=find_packages(),
    install_requires=[
        'pyinstaller>=5.0',
        'tkinter>=0.1.0'
    ],
    entry_points={
        'console_scripts': [
            'py-in-win-exe=py_in_win_exe.cli:main',
            'py-in-win-exe-gui=py_in_win_exe.gui:run_gui'
        ],
    },
    author="Vadim M.",
    author_email="somerare22@gmail.com",
    description="GUI и CLI инструмент для компиляции Python в EXE",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="pyinstaller gui exe compiler",
    url="https://github.com/ваш-репозиторий/py-in-win-exe",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.6",
)