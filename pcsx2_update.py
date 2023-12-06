import requests
import os
from py7zr import SevenZipFile
import shutil


def find_pcsx2_qt_directory():
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


def check_version_is_newer(local_version, remote_version):
    # Remove 'v' prefix if present
    local_version = local_version.lstrip('v')
    remote_version = remote_version.lstrip('v')

    local_parts = [int(part) for part in local_version.split('.')]
    remote_parts = [int(part) for part in remote_version.split('.')]
    return local_parts < remote_parts


def get_local_version(pcsx2_qt_directory):
    version_file_path = os.path.join(
        pcsx2_qt_directory, "version.txt")
    print(version_file_path)
    if os.path.exists(version_file_path):
        with open(version_file_path, 'r') as version_file:
            return version_file.read().strip()
    return None


def download_and_extract_latest_pre_release(repo_url, download_path):
    pcsx2_qt_directory = find_pcsx2_qt_directory()
    local_version = get_local_version(pcsx2_qt_directory)
    print(local_version)

    # Get the releases from the GitHub API
    api_url = f"{repo_url}/releases"
    response = requests.get(api_url)

    if response.status_code != 200:
        print(f"Failed to fetch releases. Status code: {response.status_code}")
        return

    releases = response.json()

    # Find the latest pre-release
    latest_pre_release = next(
        (release for release in releases if release['prerelease']), None)

    if latest_pre_release is None:
        print("No pre-releases found.")
        return

    remote_version = latest_pre_release['tag_name']

    # Check if the remote version is newer than the local version
    if local_version is not None and not check_version_is_newer(local_version, remote_version):
        print(f"The local version ({local_version}) is already up to date.")
        return

    print(f"Updating to version {remote_version}")

    # Find the asset with the desired format (e.g., .7z)
    desired_format = ".7z"
    desired_filename = f"pcsx2-{remote_version}-windows-x64-Qt{desired_format}"

    # Construct the download URL
    download_url = None
    for asset in latest_pre_release['assets']:
        if asset['name'] == desired_filename:
            download_url = asset['browser_download_url']
            break

    if download_url is None:
        print(f"No matching file found in the latest pre-release.")
        return

    # Download the file
    file_path = os.path.join(
        download_path, f"{remote_version}-{desired_format}")

    with requests.get(download_url, stream=True) as response:
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    print(f"Downloaded {remote_version} to {file_path}")

    # Extract the contents of the archive (if it's a 7z file)
    extract_path = os.path.join(download_path, "PCSX2-Qt")
    try:
        with SevenZipFile(file_path, mode='r') as seven_zip:
            seven_zip.extractall(extract_path)
        print(f"Extracted contents to {extract_path}")

        # Check if pcsx2-qt.exe exists and rename it if needed
        exe_file_path = os.path.join(extract_path, "pcsx2-qt.exe")
        new_exe_file_path = os.path.join(extract_path, "pcsx2-qtx64.exe")
        if os.path.exists(exe_file_path):
            os.rename(exe_file_path, new_exe_file_path)
            print(f"Renamed pcsx2-qt.exe to pcsx2-qtx64.exe")

        # Delete the downloaded .7z file
        os.remove(file_path)
        print(f"Deleted {file_path}")

        # Write version information to version.txt
        version_file_path = os.path.join(extract_path, "version.txt")
        with open(version_file_path, 'w') as version_file:
            version_file.write(remote_version)
        print(f"Version information written to {version_file_path}")

        # Copy the entire contents of the extracted PCSX2-Qt folder to pcsx2_qt_directory
        shutil.copytree(extract_path, os.path.join(
            pcsx2_qt_directory), dirs_exist_ok=True)
        print(f"Successfully copied contents to {pcsx2_qt_directory}")

        # Delete the extract_path and everything below it
        shutil.rmtree(extract_path)
        print(f"Deleted {extract_path}")

    except Exception as e:
        print(f"Failed to extract/copy contents: {str(e)}")


if __name__ == "__main__":
    github_repo_url = "https://api.github.com/repos/PCSX2/pcsx2"
    download_directory = "./downloaded_pre_releases"

    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    download_and_extract_latest_pre_release(
        github_repo_url, download_directory)
