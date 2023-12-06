import shutil
import os
import logging

# Try importing libraries, and if they are missing, install them using pip
try:
    import requests
except ImportError:
    print("requests library not found. Installing...")
    os.system("pip install requests")
    import requests

try:
    from py7zr import SevenZipFile
except ImportError:
    print("py7zr library not found. Installing...")
    os.system("pip install py7zr")
    from py7zr import SevenZipFile


class PCSX2QtUpdater:
    def __init__(self, github_repo_url, download_directory="./downloaded_pre_releases"):
        self.github_repo_url = github_repo_url
        self.download_directory = download_directory

        if not os.path.exists(self.download_directory):
            os.makedirs(self.download_directory)

    def find_pcsx2_qt_directory(self):
        users_path = "C:\\Users"
        emudeck_path = "emudeck\\EmulationStation-DE\\Emulators"
        target_folder = "PCSX2-Qt"

        for user_dir in os.listdir(users_path):
            target_path = os.path.join(
                users_path, user_dir, emudeck_path, target_folder)
            if os.path.exists(target_path):
                return target_path
        raise FileNotFoundError(
            f"Could not find the '{target_folder}' directory in {os.path.join(users_path, user_dir, emudeck_path)}.")

    def check_version_is_newer(self, local_version, remote_version):
        local_version = local_version.lstrip('v')
        remote_version = remote_version.lstrip('v')

        local_parts = [int(part) for part in local_version.split('.')]
        remote_parts = [int(part) for part in remote_version.split('.')]
        return local_parts < remote_parts

    def get_local_version(self, pcsx2_qt_directory):
        version_file_path = os.path.join(pcsx2_qt_directory, "version.txt")
        if os.path.exists(version_file_path):
            with open(version_file_path, 'r') as version_file:
                return version_file.read().strip()
        return None

    def download_and_extract_latest_pre_release(self):
        try:
            pcsx2_qt_directory = self.find_pcsx2_qt_directory()
            local_version = self.get_local_version(pcsx2_qt_directory)

            api_url = f"{self.github_repo_url}/releases"
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            releases = response.json()
            latest_pre_release = next(
                (release for release in releases if release['prerelease']), None)

            if latest_pre_release is None:
                raise RuntimeError("No pre-releases found.")

            remote_version = latest_pre_release['tag_name']

            if local_version is not None and not self.check_version_is_newer(local_version, remote_version):
                logging.info(
                    f"The local version ({local_version}) is already up to date.")
                return

            logging.info(f"Updating to version {remote_version}")

            desired_format = ".7z"
            desired_filename = f"pcsx2-{remote_version}-windows-x64-Qt{desired_format}"
            download_url = next((asset['browser_download_url']
                                for asset in latest_pre_release['assets'] if asset['name'] == desired_filename), None)

            if download_url is None:
                raise RuntimeError(
                    f"No matching file found in the latest pre-release.")

            file_path = os.path.join(
                self.download_directory, f"{remote_version}-{desired_format}")

            with requests.get(download_url, stream=True) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

            logging.info(f"Downloaded {remote_version} to {file_path}")

            extract_path = os.path.join(self.download_directory, "PCSX2-Qt")
            with SevenZipFile(file_path, mode='r') as seven_zip:
                seven_zip.extractall(extract_path)

            logging.info(f"Extracted contents to {extract_path}")

            exe_file_path = os.path.join(extract_path, "pcsx2-qt.exe")
            new_exe_file_path = os.path.join(extract_path, "pcsx2-qtx64.exe")
            if os.path.exists(exe_file_path):
                os.rename(exe_file_path, new_exe_file_path)
                logging.info(f"Renamed pcsx2-qt.exe to pcsx2-qtx64.exe")

            os.remove(file_path)
            logging.info(f"Deleted {file_path}")

            version_file_path = os.path.join(extract_path, "version.txt")
            with open(version_file_path, 'w') as version_file:
                version_file.write(remote_version)

            logging.info(f"Version information written to {version_file_path}")

            shutil.copytree(extract_path, os.path.join(
                pcsx2_qt_directory), dirs_exist_ok=True)
            logging.info(
                f"Successfully copied contents to {pcsx2_qt_directory}")

            shutil.rmtree(extract_path)
            logging.info(f"Deleted {extract_path}")

        except Exception as e:
            logging.error(f"Failed to update PCSX2-Qt: {str(e)}")


if __name__ == "__main__":
    # Add this line to delete existing log file
    if os.path.exists("pcsx2_qt_updater.log"):
        os.remove("pcsx2_qt_updater.log")

    logging.basicConfig(filename="pcsx2_qt_updater.log", level=logging.INFO)
    github_repo_url = "https://api.github.com/repos/PCSX2/pcsx2"
    updater = PCSX2QtUpdater(github_repo_url)
    updater.download_and_extract_latest_pre_release()
