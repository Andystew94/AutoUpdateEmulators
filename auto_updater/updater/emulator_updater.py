import os
import shutil
from subprocess import check_call

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

from configparser import ConfigParser
from helpers.seven_zip import SevenZip


class EmulatorUpdater:
    def __init__(self, emulator_name):
        self.emulator_name = emulator_name
        self.config = ConfigParser()
        self.config.read(os.path.join(
            os.getcwd(), "auto_updater", "config.ini"))
        self.github_repo_url = self.config.get(
            emulator_name, "github_repo_url")
        self.github_version_identifier = self.config.get(
            emulator_name, "github_version_identifier")
        self.has_sub_folder = self.config.getboolean(
            emulator_name, "has_sub_folder")
        self.sub_folder_name = self.config.get(
            emulator_name, "sub_folder_name") if self.has_sub_folder else None
        self.release_asset_name_identifier = self.config.get(
            emulator_name, "release_asset_name_identifier")
        self.exe_rename_required = self.config.getboolean(
            emulator_name, "exe_rename_required")
        self.exe_rename_filenames = self.config.get(emulator_name, "exe_rename_filenames").split(
            ", ") if self.exe_rename_required else None
        self.emulator_directory = self.find_emulator_directory()
        if self.has_sub_folder:
            self.emulator_directory = f"{self.emulator_directory}\\{self.sub_folder_name}"
        self.release_info = self.fetch_latest_release_info()
        self.download_directory = os.path.join(
            os.getcwd(), "downloads", self.emulator_name)
        self.SevenZip = SevenZip()

    def fetch_latest_release_info(self):
        response = requests.get(self.github_repo_url)

        try:
            response = next(
                (release for release in response.json() if release['prerelease']), None)
        except:
            response = response.json()

        return response

    def download_and_extract_release(self, download_url, file_name):
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

    def find_emulator_directory(self):
        users_path = "C:\\Users"
        for user_dir in os.listdir(users_path):
            target_path = os.path.join(
                users_path, user_dir, "emudeck", "EmulationStation-DE", "Emulators", self.emulator_name)
            if os.path.exists(target_path):
                return target_path
        raise FileNotFoundError(
            f"Could not find the 'Emulators\\{self.emulator_name}' directory in C:\\Users.")

    def rename_file(self, directory_path, original_name, new_name):
        original_file_path = os.path.join(directory_path, original_name)
        new_file_path = os.path.join(directory_path, new_name)
        if os.path.exists(original_file_path):
            os.rename(original_file_path, new_file_path)
            print(f"Renamed {original_name} to {new_name}")

    def update_emulator(self):
        existing_version_file_path = os.path.join(
            self.emulator_directory, "version.txt")

        if os.path.exists(existing_version_file_path):
            with open(existing_version_file_path, 'r') as existing_version_file:
                existing_version = existing_version_file.read().strip()
                if existing_version == str(self.release_info[self.github_version_identifier]):
                    print(
                        f"Latest version of {self.emulator_name} is already downloaded. Exiting.")
                    return False

        if not os.path.exists(self.download_directory):
            os.makedirs(self.download_directory)

        download_url = next(
            (asset['browser_download_url'] for asset in self.release_info['assets']
             if asset['name'].endswith((".zip", ".7z")) and self.release_asset_name_identifier in asset['name']),
            None
        )

        if download_url is None:
            raise RuntimeError(
                f"No matching file found in the latest release.")

        file_name = os.path.basename(download_url)

        print(f"Downloading {file_name} to {self.emulator_directory}...")
        self.download_and_extract_release(download_url, file_name)

        extracted_folder_name = os.listdir(self.download_directory)[0]
        extracted_folder_directory = os.path.join(
            self.download_directory, extracted_folder_name)

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

        if self.sub_folder_name == "True":
            shutil.copytree(extracted_folder_directory,
                            self.emulator_directory, dirs_exist_ok=True)
            shutil.rmtree(extracted_folder_directory)
        else:
            shutil.copytree(self.download_directory,
                            self.emulator_directory, dirs_exist_ok=True)
            shutil.rmtree(self.download_directory)

        print("Download, extraction, and version information written to 'version.txt' complete.")
        return True
