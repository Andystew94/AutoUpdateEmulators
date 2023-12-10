from setuptools import setup, find_packages
import os
from PyInstaller import __main__ as pyi

working_directory = os.path.join(os.getcwd())

setup(
    name='emulator_updater',
    version='1.0',
    description='Emulator updater script',
    author='Your Name',
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
            '--name', 'emulator_updater.exe',
            '--console'
        ])
    ]
)
