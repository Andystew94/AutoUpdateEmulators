from setuptools import setup, find_packages
from PyInstaller import __main__ as pyi
from shutil import copyfile
import os
import sys

working_directory = os.path.dirname(os.path.realpath(sys.argv[0]))

setup(
    name='Emulator_Updater',
    version='1.0',
    description='Emulator Updater Script',
    author='Andrew S',
    packages=find_packages(),
    options={
        'build_exe': {
            'packages': ['updater', 'ppsspp', 'dolphin'],
        },
    },
)

# After setup, copy necessary files to the release directory
release_directory = os.path.join(working_directory, 'release')
if not os.path.exists(release_directory):
    os.makedirs(release_directory)

copyfile(os.path.join(working_directory, 'config.ini'),
         os.path.join(release_directory, 'config.ini'))

copyfile(os.path.join(working_directory, 'README.md'),
         os.path.join(release_directory, 'README.md'))

# Build the executable using PyInstaller
pyi.run([
    'core.py',
    '--onefile',
    '--distpath', release_directory,
    '--name', 'Emulator Updater.exe',
    '--noconsole'
])
