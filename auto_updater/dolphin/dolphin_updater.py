import re
import os
import shutil
import logging
import sys
from subprocess import check_call
from auto_updater.helpers.seven_zip import SevenZip

try:
    import requests
except ImportError as e:
    print(f"Error importing required module: {e}")
    print("Installing necessary modules...")
    try:
        check_call(['pip', 'install', 'requests'])
        import requests
    except Exception as install_error:
        print(f"Error installing module: {install_error}")
        exit(1)


class DolphinUpdater:
    def __init__(self, webscrapper):
        self.url = "https://dolphin-emu.org/download/"
        self.download_name_contains = "dolphin-master"
        self.emulator_name = "Dolphin-x64"
        self.webscrapper = webscrapper
        self.dolphin_win_zip_link = self._get_download_url()
        self.version = self._extract_version_from_url(
            self.dolphin_win_zip_link)
        self.emulator_directory = self.find_emulator_directory()
        script_directory = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.download_directory = os.path.join(
            script_directory, "downloads", self.emulator_name)
        self.SevenZip = SevenZip()

    def _get_download_url(self):
        try:
            self.webscrapper.get_URL(self.url)
            download_links = self.webscrapper.find_elements()

            pattern = r'dolphin-master-([^/]+)-x64\.7z'
            highest_value = 0
            matched_link = None

            for link in download_links:
                href = link.get_attribute("href")
                match = re.search(pattern, href)
                if match:
                    # Extract the value from the regex match
                    value = match.group(1)
                    # Convert the extracted value to an integer for comparison
                    try:
                        cleaned_str = ''.join(filter(str.isdigit, value))
                        # Convert the cleaned string into an integer
                        current_value = int(cleaned_str)
                        # If the current value is higher than the previous highest, update the values
                        if current_value > highest_value:
                            highest_value = current_value
                            matched_link = href
                    except ValueError:
                        # If the extracted value cannot be converted to an integer, continue to the next link
                        continue

            return matched_link

        except Exception as e:
            print(f"Error: {e}")
            return None

    def _extract_version_from_url(self, url):
        # https://dl.dolphin-emu.org/builds/c8/35/dolphin-master-5.0-20347-x64.7z
        pattern = r'dolphin-master-([^/]+)-x64.7z'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def find_emulator_directory(self):
        users_path = "C:\\Users"
        for user_dir in os.listdir(users_path):
            target_path = os.path.join(
                users_path, user_dir, "emudeck", "EmulationStation-DE", "Emulators", self.emulator_name)
            if os.path.exists(target_path):
                return target_path
        raise FileNotFoundError(
            f"Could not find the 'Emulators\\{self.emulator_name}' directory in C:\\Users.")

    def download_and_extract_release(self, download_url):
        file_name = os.path.basename(download_url)
        downloads_file_path = os.path.join(self.download_directory, file_name)

        with requests.get(download_url, stream=True) as response:
            response.raise_for_status()
            with open(downloads_file_path, "wb") as file:
                shutil.copyfileobj(response.raw, file)

        self.SevenZip.extract_with_7zip(
            downloads_file_path, self.download_directory)
        os.remove(downloads_file_path)

    def write_version_file(self, version_file_path, version_identifier):
        with open(version_file_path, 'w') as version_file:
            version_file.write(version_identifier)

    def update_emulator(self):
        existing_version_file_path = os.path.join(
            self.emulator_directory, "version.txt")
        repo_version = self._extract_version_from_url(
            self.dolphin_win_zip_link)

        if os.path.exists(existing_version_file_path):
            with open(existing_version_file_path, 'r') as existing_version_file:
                existing_version = existing_version_file.read().strip()
                if existing_version == str(repo_version):
                    print(
                        f"Latest version of {self.emulator_name} is already downloaded. Exiting.")
                    logging.info(
                        f"Latest version of {self.emulator_name} is already downloaded. Exiting.")
                    return False

        if not os.path.exists(self.download_directory):
            os.makedirs(self.download_directory)

        print(
            f"Downloading {self.emulator_name} to {self.emulator_directory}...")
        self.download_and_extract_release(self.dolphin_win_zip_link)

        extracted_folder_name = os.listdir(self.download_directory)[0]
        extracted_folder_directory = os.path.join(
            self.download_directory, extracted_folder_name)

        version_file_path = os.path.join(
            self.download_directory, extracted_folder_name, "version.txt")
        self.write_version_file(version_file_path, str(self.version))

        contents = os.listdir(extracted_folder_directory)

        # Copy each item in the source directory to the destination directory
        for item in contents:
            source_item = os.path.join(extracted_folder_directory, item)
            destination_item = os.path.join(self.emulator_directory, item)

            if os.path.isdir(source_item):
                shutil.copytree(
                    source_item, destination_item, dirs_exist_ok=True)
            else:
                # Use copy2 to preserve metadata if needed
                shutil.copy2(source_item, destination_item)
        shutil.rmtree(self.download_directory)

        logging.info(f"Updated {self.emulator_name} successfully.")
