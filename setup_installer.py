from setuptools import setup, find_packages
from PyInstaller import __main__ as pyi
import os
import sys

working_directory = os.path.dirname(os.path.realpath(sys.argv[0]))

setup(
    name='Emulator_Updater_Installer',
    version='1.0',
    description='Emulator Updater Installer',
    author='Andrew S',
    packages=find_packages(),
)

# Build the installer executable using PyInstaller
pyi.run([
    'install.py',
    '--onefile',
    '--distpath', 'release',
    '--name', 'install.exe',
    '--console'
])
