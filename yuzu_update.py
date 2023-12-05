import os
import shutil
import zipfile
from subprocess import check_call

try:
    import requests
except ImportError:
    print("Installing requests module...")
    check_call(['pip', 'install', 'requests'])
    import requests

class YuzuUpdater:
    def __init__(self, repo, version_subdirectory="yuzu-windows-msvc-early-access"):
        self.repo = repo
        self.version_subdirectory = version_subdirectory
        self.release_info = self.fetch_latest_release_info()
        self.windows_directory = self.find_yuzu_directory()

    def fetch_latest_release_info(self):
        api_url = f"https://api.github.com/repos/{self.repo}/releases/latest"
        response = requests.get(api_url)
        return response.json()

    def download_and_extract_release(self, download_url, file_name, temp_dir):
        response = requests.get(download_url, stream=True)
        with open(file_name, "wb") as file:
            shutil.copyfileobj(response.raw, file)

        with zipfile.ZipFile(file_name, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        os.remove(file_name)

    def write_version_file(self, version_file_path, tag_name):
        with open(version_file_path, 'w') as version_file:
            version_file.write(tag_name)

    def find_yuzu_directory(self):
        users_path = "C:\\Users"
        for user_dir in os.listdir(users_path):
            target_path = os.path.join(users_path, user_dir, "emudeck", "EmulationStation-DE", "Emulators", "yuzu")
            if os.path.exists(target_path):
                return target_path
        raise FileNotFoundError("Could not find the 'Emulators\\yuzu' directory in C:\\Users.")

    def update_yuzu(self):
        existing_version_file_path = os.path.join(self.windows_directory, self.version_subdirectory, "version.txt")

        if os.path.exists(existing_version_file_path):
            with open(existing_version_file_path, 'r') as existing_version_file:
                existing_version = existing_version_file.read().strip()
                if existing_version == self.release_info["tag_name"]:
                    print("Latest version is already downloaded. Exiting.")
                    return False

        zip_assets = [asset for asset in self.release_info["assets"] if asset["name"].endswith(".zip")]

        if not zip_assets:
            print("No ZIP file found in the release assets.")
            return False

        download_url = zip_assets[0]["browser_download_url"]
        file_name = os.path.basename(download_url)
        temp_dir = os.path.join(self.windows_directory, "temp_extracted")

        print(f"Downloading {file_name} to {self.windows_directory}...")
        self.download_and_extract_release(download_url, file_name, temp_dir)

        extracted_folder_name = os.listdir(temp_dir)[0]
        version_file_path = os.path.join(temp_dir, extracted_folder_name, "version.txt")

        self.write_version_file(version_file_path, self.release_info["tag_name"])

        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            target_path = os.path.join(self.windows_directory, item)

            if os.path.exists(target_path):
                print(f"Destination path '{target_path}' already exists. Removing existing contents...")
                shutil.rmtree(target_path)

            shutil.move(item_path, self.windows_directory)

        shutil.rmtree(temp_dir)

        print("Download, extraction, and version information written to 'version.txt' complete.")
        return True

if __name__ == "__main__":
    updater = YuzuUpdater("pineappleEA/pineapple-src")
    updater.update_yuzu()