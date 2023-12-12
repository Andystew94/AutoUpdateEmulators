import re
import os
import shutil
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

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
except ImportError as e:
    print(f"Error importing required module: {e}")
    print("Installing necessary modules...")
    try:
        check_call(['pip', 'install', 'selenium'])
        from selenium import webdriver
        from selenium.webdriver.common.by import By
    except Exception as install_error:
        print(f"Error installing module: {install_error}")
        exit(1)


class PPSSPPUpdater:
    def __init__(self):
        self.url = "https://www.ppsspp.org/download"
        self.download_name_contains = "ppsspp_win.zip"
        self.emulator_name = "PPSSPP"
        self.driver = self._configure_headless_chrome()
        self.ppsspp_win_zip_link = self._get_ppsspp_download_url()
        self.version = self._extract_version_from_url(self.ppsspp_win_zip_link)
        self.emulator_directory = self.find_emulator_directory()
        self.download_directory = os.path.join(
            os.getcwd(), "downloads", self.emulator_name)
        self.SevenZip = SevenZip()

    def _configure_headless_chrome(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        return webdriver.Chrome(options=options)

    def _get_ppsspp_download_url(self):
        try:
            self.driver.get(self.url)
            self.driver.implicitly_wait(10)
            download_links = self.driver.find_elements(By.XPATH, "//a[@href]")

            for link in download_links:
                href = link.get_attribute("href")
                if self.download_name_contains in href:
                    return href  # Return the first matching link

            return None  # Return None if no matching link is found
        except Exception as e:
            print(f"Error: {e}")
            return None

    def _extract_version_from_url(self, url):
        # https://www.ppsspp.org/files/1_16_6/ppsspp_win.zip
        pattern = r'files/([^/]+)/ppsspp_win\.zip'
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
        repo_version = self._extract_version_from_url(self.ppsspp_win_zip_link)

        if os.path.exists(existing_version_file_path):
            with open(existing_version_file_path, 'r') as existing_version_file:
                existing_version = existing_version_file.read().strip()
                if existing_version == str(repo_version):
                    print(
                        f"Latest version of {self.emulator_name} is already downloaded. Exiting.")
                    return False

        if not os.path.exists(self.download_directory):
            os.makedirs(self.download_directory)

        print(f"Downloading PPSSPP to {self.emulator_directory}...")
        self.download_and_extract_release(self.ppsspp_win_zip_link)

        version_file_path = os.path.join(
            self.download_directory, "version.txt")
        self.write_version_file(version_file_path, str(self.version))

        shutil.copytree(self.download_directory,
                        self.emulator_directory, dirs_exist_ok=True)
        shutil.rmtree(self.download_directory)

        # Close the browser
        self.driver.quit()
