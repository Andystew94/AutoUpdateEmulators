from setuptools import setup, find_packages
import os
from PyInstaller import __main__ as pyi
from shutil import copyfile

working_directory = os.path.join(os.getcwd())

setup(
    name='Emulator_Updater',
    version='1.0',
    description='Emulator Updater Script',
    author='Andrew S',
    packages=find_packages(),
    options={
        'build_exe': {
            'packages': ['updater', 'ppsspp', 'dolphin'],
            'include_files': [
                f'{working_directory}/auto_updater/updater/emulator_updater.py',
                f'{working_directory}/auto_updater/ppsspp/ppsspp_updater.py',
                f'{working_directory}/auto_updater/dolphin/dolphin_updater.py'
            ],
        },
    },
    executables=[
        pyi.run([
            'core.py',
            '--onefile',
            '--distpath', 'dist',
            '--name', 'Emulator_Updater.exe',
            '--noconsole'
        ])
    ]
)

# Copy the config.ini to the dist folder
copyfile(os.path.join(working_directory, 'config.ini'),
         os.path.join(working_directory, 'dist', 'config.ini'))
