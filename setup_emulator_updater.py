from setuptools import setup, find_packages
from shutil import copyfile
import os
import sys
import subprocess

# Required packages for core.py
try:
    from PyInstaller import __main__ as pyi
except ImportError:
    subprocess.check_call(['pip', 'install', 'PyInstaller'])
    from PyInstaller import __main__ as pyi

try:
    import requests
except ImportError as e:
    try:
        subprocess.check_call(['pip', 'install', 'requests'])
        import requests
    except Exception as install_error:
        print(f"Error installing module: {install_error}")

try:
    import selenium
except ImportError as e:
    try:
        subprocess.check_call(['pip', 'install', 'selenium'])
        subprocess.check_call(["pip", "install", "--upgrade", "selenium"])
        import selenium
    except Exception as install_error:
        print(f"Error installing module: {install_error}")

try:
    import psutil
except ImportError as e:
    try:
        subprocess.check_call(['pip', 'install', 'psutil'])
        import psutil
    except Exception as install_error:
        print(f"Error installing module: {install_error}")

try:
    import PyQt5
except ImportError as e:
    try:
        subprocess.check_call(['pip', 'install', 'PyQt5'])
        import PyQt5
    except Exception as install_error:
        print(f"Error installing module: {install_error}")

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
