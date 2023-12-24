import os
import shutil
from subprocess import check_call
import logging
import sys

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

from configparser import ConfigParser
from auto_updater.helpers.seven_zip import SevenZip


class EmulatorUpdater:
    def __init__(self, section_name):
        self.config = ConfigParser()
        self.SevenZip = SevenZip()
        self.emulator_name = section_name
        script_directory = os.path.dirname(os.path.realpath(sys.argv[0]))

        try:
            self.config.read(os.path.join(
                script_directory, "config.ini"))

            # Mandatory Fields
            self.emudeck_folder_name = self.config.get(
                section_name, "emudeck_folder_name")
            self.github_repo_url = self.config.get(
                section_name, "github_repo_url")
            self.github_version_identifier = self.config.get(
                section_name, "github_version_identifier")
            self.release_asset_name_identifier = self.config.get(
                section_name, "release_asset_name_identifier")

            # Optional Fields
            try:
                self.has_sub_folder = self.config.getboolean(
                    section_name, "has_sub_folder")
            except:
                self.has_sub_folder = False

            self.sub_folder_name = self.config.get(
                section_name, "sub_folder_name") if self.has_sub_folder else None

            try:
                self.release_asset_name_ignore = self.config.get(
                    section_name, "release_asset_name_ignore")
            except:
                self.release_asset_name_ignore = None

            try:
                self.exe_rename_required = self.config.getboolean(
                    section_name, "exe_rename_required")
            except:
                self.exe_rename_required = False

            self.exe_rename_filenames = self.config.get(section_name, "exe_rename_filenames").split(
                ", ") if self.exe_rename_required else None

            try:
                self.copy_folder_contents_only = self.config.getboolean(
                    section_name, "copy_folder_contents_only")
            except:
                self.copy_folder_contents_only = False

            try:
                self.assest_file_extension = self.config.get(
                    section_name, "custom_assest_file_extension")
            except:
                self.assest_file_extension = (".zip", ".7z")

        except:
            logging.error(
                f"config.ini not configured correctly for {self.emulator_name}...")
            exit()

        else:
            self.emulator_directory = self.find_emulator_directory()
            if self.has_sub_folder:
                self.emulator_directory = f"{self.emulator_directory}\\{self.sub_folder_name}"

            self.release_info = self.fetch_latest_release_info()
            self.download_directory = os.path.join(
                script_directory, "downloads", self.emudeck_folder_name)

    def fetch_latest_release_info(self):
        logging.info(
            f"Fetching latest {self.emulator_name} release assets info from github api...")
        response = requests.get(self.github_repo_url)

        try:
            response = next(
                (release for release in response.json() if release['prerelease']))
        except StopIteration:
            response = next(
                (release for release in response.json() if not release['prerelease']))
        except:
            response = response.json()

        return response

    def download_and_extract_release(self, download_url, file_name):
        downloads_file_path = os.path.join(self.download_directory, file_name)

        logging.info(f"Downloading...")

        with requests.get(download_url, stream=True) as response:
            response.raise_for_status()
            with open(downloads_file_path, "wb") as file:
                shutil.copyfileobj(response.raw, file)

        logging.info(f"Extracting...")

        self.SevenZip.extract_with_7zip(
            downloads_file_path, self.download_directory)
        os.remove(downloads_file_path)

    def write_version_file(self, version_file_path, version_identifier):

        logging.info(
            f"Updating version.txt file with the following Version ID: {version_identifier}")
        with open(version_file_path, 'w') as version_file:
            version_file.write(version_identifier)

    def find_emulator_directory(self):
        users_path = "C:\\Users"
        for user_dir in os.listdir(users_path):
            target_path = os.path.join(
                users_path, user_dir, "emudeck", "EmulationStation-DE", "Emulators", self.emudeck_folder_name)
            if os.path.exists(target_path):
                return target_path
        logging.error(
            f"Could not find the 'Emulators\\{self.emudeck_folder_name}' directory in C:\\Users.")
        raise FileNotFoundError(
            f"Could not find the 'Emulators\\{self.emudeck_folder_name}' directory in C:\\Users.")

    def rename_file(self, directory_path, original_name, new_name):
        original_file_path = os.path.join(directory_path, original_name)
        new_file_path = os.path.join(directory_path, new_name)
        if os.path.exists(original_file_path):
            os.rename(original_file_path, new_file_path)
        else:
            logging.error(
                f"Failed to rename {original_file_path} to {new_file_path}")

    def delete_files_with_extension(self, directory, extension):
        try:
            # Iterate over all items (files and directories) in the directory
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)

                # Check if the item is a file and has the specified extension
                if os.path.isfile(item_path) and item.endswith(extension):
                    # Delete the file
                    os.remove(item_path)

        except Exception as e:
            logging.error(
                f"Error deleting files with requested extension/s: {e}")

    def update_emulator(self):
        existing_version_file_path = os.path.join(
            self.emulator_directory, "version.txt")

        if os.path.exists(existing_version_file_path):
            with open(existing_version_file_path, 'r') as existing_version_file:
                existing_version = existing_version_file.read().strip()
                if existing_version == str(self.release_info[self.github_version_identifier]):
                    logging.info(
                        f"Latest version of {self.emulator_name} is already installed - No Update Required")
                    return False

        logging.info(
            f"Newer version of {self.emulator_name} found...")

        if not os.path.exists(self.download_directory):
            os.makedirs(self.download_directory)

        if self.release_info is not None and 'assets' in self.release_info and self.release_info['assets'] is not None:
            download_url = next(
                (
                    asset['browser_download_url']
                    for asset in self.release_info['assets']
                    if (
                        asset['name'].endswith(self.assest_file_extension)
                        and self.release_asset_name_identifier in asset['name']
                        and (self.release_asset_name_ignore is None or self.release_asset_name_ignore not in asset['name'])
                    )
                ),
                None
            )
        else:
            # Handle the case where assets or release_info is None
            logging.error(
                f"Error: Release information or assets are not available for {self.emulator_name}. Check github_repo_url in config.ini")
            exit()

        if download_url is None:
            logging.error(f"No matching file found in the latest release.")
            raise RuntimeError(
                f"No matching file found in the latest release.")

        file_name = os.path.basename(download_url)

        self.download_and_extract_release(download_url, file_name)

        extracted_folder_name = os.listdir(self.download_directory)[0]
        extracted_folder_directory = os.path.join(
            self.download_directory, extracted_folder_name)

        # Check if there is exactly one item in the directory
        items = os.listdir(self.download_directory)

        if len(items) == 1:
            # Check if the single item is a folder
            item_path = os.path.join(self.download_directory, items[0])
            if os.path.isdir(item_path):
                self.has_sub_folder = True
            else:
                self.has_sub_folder = False
        else:
            self.has_sub_folder = False

        # Remove any source code found in the downloaded extract
        if self.has_sub_folder:
            self.delete_files_with_extension(
                extracted_folder_directory, ".tar.xz")
        else:
            self.delete_files_with_extension(
                self.download_directory, ".tar.xz")

        if self.exe_rename_required:
            self.rename_file(
                self.download_directory, self.exe_rename_filenames[0], self.exe_rename_filenames[1])

        if self.exe_rename_required and self.has_sub_folder:
            self.rename_file(
                extracted_folder_name, self.exe_rename_filenames[0], self.exe_rename_filenames[1])

        version_file_path = os.path.join(
            self.download_directory, extracted_folder_name, "version.txt") if self.has_sub_folder else os.path.join(
            self.download_directory, "version.txt")

        self.write_version_file(
            version_file_path, str(self.release_info[self.github_version_identifier]))

        if not os.path.exists(self.emulator_directory):
            os.makedirs(self.emulator_directory)

        logging.info(
            f"Moving extracted files to {self.emulator_name} directory...")

        if self.copy_folder_contents_only:
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

        else:
            if self.has_sub_folder:
                shutil.copytree(extracted_folder_directory,
                                self.emulator_directory, dirs_exist_ok=True)
                shutil.rmtree(extracted_folder_directory)
            else:
                shutil.copytree(self.download_directory,
                                self.emulator_directory, dirs_exist_ok=True)
                shutil.rmtree(self.download_directory)

        logging.info(f"Updated {self.emulator_name} successfully.")
        return True
