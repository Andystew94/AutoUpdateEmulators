from setuptools import setup, find_packages
import os
import sys
import subprocess

# Required packages for install.py
try:
    from PyInstaller import __main__ as pyi
except ImportError:
    subprocess.check_call(['pip', 'install', 'PyInstaller'])
    from PyInstaller import __main__ as pyi

try:
    from winshell import desktop, CreateShortcut
except ImportError:
    subprocess.check_call(['pip', 'install', 'winshell'])
    subprocess.check_call(['pip', 'install', 'pywin32'])
    from winshell import desktop, CreateShortcut

try:
    import psutil
except ImportError:
    subprocess.check_call(['pip', 'install', 'psutil'])
    import psutil

working_directory = os.path.dirname(os.path.realpath(sys.argv[0]))

setup(
    name='Emulator_Updater_Installer',
    version='1.0',
    description='Emulator Updater Installer',
    author='Andrew S',
    packages=find_packages(),
)

# After setup, copy necessary files to the release directory
release_directory = os.path.join(working_directory, 'release')

# Build the installer executable using PyInstaller
pyi.run([
    'install.py',
    '--onefile',
    '--distpath', release_directory,
    '--name', 'install.exe',
    '--console'
])
