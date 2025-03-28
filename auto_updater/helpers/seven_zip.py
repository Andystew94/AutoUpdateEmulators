import subprocess
import os
from subprocess import check_call
import logging

try:
    import psutil
except ImportError as e:
    logging.error(f"Error importing required module: {e}")
    logging.info("Installing necessary modules...")
    try:
        check_call(['pip', 'install', 'psutil'])
        import psutil
    except Exception as install_error:
        logging.error(f"Error installing module: {install_error}")
        exit(1)


class SevenZip:
    def __init__(self):
        self.seven_zip_executable = self.find_7zip_executable()

    def find_7zip_executable(self):
        # Get a list of all connected drives
        connected_drives = [drive.device for drive in psutil.disk_partitions()]

        # Search for 7z.exe on each drive
        for drive in connected_drives:
            for dirpath, dirnames, filenames in os.walk(drive):
                for filename in filenames:
                    if filename.lower() == "7z.exe":
                        return os.path.join(dirpath, filename)

        # If the executable is not found, you can raise an exception or return None
        logging.error("7-Zip executable not found")
        raise FileNotFoundError("7-Zip executable not found")

    def extract_with_7zip(self, archive_path, extract_path):
        try:
            # Use the found executable in the command
            command = [self.seven_zip_executable, "x",
                       archive_path, f"-o{extract_path}", "-y"]

            # Subprocess will run in headless
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            # Run the command
            subprocess.run(command, check=True, startupinfo=startupinfo)
            logging.info("Extraction successful...")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error during extraction: {e}")
        except FileNotFoundError as e:
            logging.error(f"Error: {e}")
