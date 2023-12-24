import re
import os
import shutil
import logging
import sys
from subprocess import check_call
from configparser import ConfigParser
from auto_updater.helpers.seven_zip import SevenZip

try:
    import requests
except ImportError as e:
    logging.error(f"Error importing required module: {e}")
    logging.info("Installing necessary modules...")
    try:
        check_call(['pip', 'install', 'requests'])
        import requests
    except Exception as install_error:
        logging.error(f"Error installing module: {install_error}")
        exit(1)


class UpdaterScrapper:
    CONFIG_FILE = "config.ini"
    DOWNLOADS_PATH = "downloads"

    def __init__(self, section_name, webscrapper):
        self.config = ConfigParser()
        self.SevenZip = SevenZip()
        self.webscrapper = webscrapper
        self.emulator_name = section_name
        self._load_and_validate_config()
        self.zip_file_link = self._get_download_url()
        self.version = self._extract_version_from_url(self.zip_file_link)
        self.emulator_directory = self.find_emulator_directory()
        self.download_directory = os.path.join(os.path.dirname(
            os.path.realpath(sys.argv[0])), self.DOWNLOADS_PATH, self.emulator_name)

    def _load_and_validate_config(self):
        script_directory = os.path.dirname(os.path.realpath(sys.argv[0]))
        config_path = os.path.join(script_directory, self.CONFIG_FILE)

        try:
            self.config.read(config_path)
            self.emudeck_folder_name = self.config.get(
                self.emulator_name, "emudeck_folder_name")
            self.url = self.config.get(self.emulator_name, "url")
            self.version_identifier = self.config.get(
                self.emulator_name, "version_identifier")
            self.exe_file_name = self.config.get(
                self.emulator_name, "exe_file_name")
        except Exception as e:
            logging.error(
                f"Error loading configuration for {self.emulator_name}: {e}")
            exit()

    def _get_download_url(self):
        try:
            logging.info(
                f"Scrapping {self.url} for latest version of {self.emulator_name}...")
            self.webscrapper.get_URL(self.url)
            download_links = self.webscrapper.find_elements()

            highest_value = 0
            matched_link = None

            for link in download_links:
                href = link.get_attribute("href")
                match = re.search(self.version_identifier, href)
                if match:
                    value = re.sub(r'\D', '', match.group(1))
                    try:
                        current_value = int(value)
                        if current_value > highest_value:
                            highest_value = current_value
                            matched_link = href
                    except ValueError:
                        continue

            return matched_link
        except Exception as e:
            logging.error(f"Error fetching download URL: {e}")
            return None

    def _extract_version_from_url(self, url):
        match = re.search(self.version_identifier, url)
        return match.group(1) if match else None

    def find_emulator_directory(self):
        users_path = "C:\\Users"
        for user_dir in os.listdir(users_path):
            target_path = os.path.join(
                users_path, user_dir, "emudeck", "EmulationStation-DE", "Emulators", self.emulator_name)
            if os.path.exists(target_path):
                return target_path
        raise FileNotFoundError(
            f"Directory 'Emulators\\{self.emulator_name}' not found in C:\\Users.")

    def download_and_extract_release(self, download_url):
        file_name = os.path.basename(download_url)
        downloads_file_path = os.path.join(self.download_directory, file_name)

        logging.info("Downloading...")
        with requests.get(download_url, stream=True) as response:
            response.raise_for_status()
            with open(downloads_file_path, "wb") as file:
                shutil.copyfileobj(response.raw, file)

        logging.info("Extracting...")
        self.SevenZip.extract_with_7zip(
            downloads_file_path, self.download_directory)
        os.remove(downloads_file_path)

    def write_version_file(self, version_file_path, version_identifier):
        logging.info(
            f"Updating version.txt with Version ID: {version_identifier}")
        with open(version_file_path, 'w') as version_file:
            version_file.write(version_identifier)

    def update_emulator(self):
        existing_version_file_path = os.path.join(
            self.emulator_directory, "version.txt")
        repo_version = self._extract_version_from_url(self.zip_file_link)

        if os.path.exists(existing_version_file_path):
            with open(existing_version_file_path, 'r') as existing_version_file:
                existing_version = existing_version_file.read().strip()
                if existing_version == str(repo_version):
                    logging.info(
                        f"Latest version of {self.emulator_name} is already installed - No Update Required")
                    return

        logging.info(f"Newer version of {self.emulator_name} found.")
        os.makedirs(self.download_directory, exist_ok=True)
        self.download_and_extract_release(self.zip_file_link)
        self._update_emulator_files()

        logging.info(f"Successfully updated {self.emulator_name}.")

    def _update_emulator_files(self):
        if self.exe_file_name in os.listdir(self.download_directory):
            version_file_path = os.path.join(
                self.download_directory, "version.txt")
            self.write_version_file(version_file_path, str(self.version))
            self._update_files_in_emulator_dir(self.download_directory)
        else:
            extracted_folder_name = os.listdir(self.download_directory)[0]
            extracted_folder_directory = os.path.join(
                self.download_directory, extracted_folder_name)
            version_file_path = os.path.join(
                self.download_directory, extracted_folder_name, "version.txt")
            self.write_version_file(version_file_path, str(self.version))
            self._update_files_in_emulator_dir(extracted_folder_directory)

    def _update_files_in_emulator_dir(self, source_directory):
        if not os.path.exists(self.emulator_directory):
            os.makedirs(self.emulator_directory)

        for item in os.listdir(source_directory):
            source_item = os.path.join(source_directory, item)
            destination_item = os.path.join(self.emulator_directory, item)
            if os.path.isdir(source_item):
                shutil.copytree(source_item, destination_item,
                                dirs_exist_ok=True)
            else:
                shutil.copy2(source_item, destination_item)

        shutil.rmtree(self.download_directory)
