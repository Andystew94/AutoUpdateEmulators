from setuptools import setup, find_packages
import os
import sys
from PyInstaller import __main__ as pyi
from shutil import copyfile

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
    executables=[
        pyi.run([
            'core.py',
            '--onefile',
            '--distpath', 'release',
            '--name', 'Emulator Updater.exe',
            '--noconsole'
        ])
    ]
)

# Copy the config.ini and README.md to the release folder
copyfile(os.path.join(working_directory, 'config.ini'),
         os.path.join(working_directory, 'release', 'config.ini'))
copyfile(os.path.join(working_directory, 'README.md'),
         os.path.join(working_directory, 'release', 'README.md'))

setup(
    name='Emulator_Updater_Installer',
    version='1.0',
    description='Emulator Updater Installer',
    author='Andrew S',
    packages=find_packages(),
    executables=[
        pyi.run([
            'install.py',
            '--onefile',
            '--distpath', 'release',
            '--name', 'install.exe',
            '--console'
        ])
    ]
)
