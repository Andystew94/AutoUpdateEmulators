import os
import shutil
import subprocess

try:
    import psutil
except ImportError:
    subprocess.check_call(['pip', 'install', 'psutil'])
    import psutil

try:
    from winshell import desktop, CreateShortcut
except ImportError:
    subprocess.check_call(['pip', 'install', 'winshell'])
    from winshell import desktop, CreateShortcut


def task_exists(task_name):
    try:
        subprocess.check_output(['schtasks', '/query', '/tn', task_name])
        print("## Existing task found in Task Scheduler ##")
        return True
    except subprocess.CalledProcessError:
        return False


def remove_task(task_name):
    subprocess.call(['schtasks', '/delete', '/tn', task_name, '/f'])
    print("## Removing existing task found in Task Scheduler ##")


def terminate_process(process_name):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            try:
                process.terminate()
                print(
                    f"Terminated process {process_name} with PID {process.info['pid']}")
            except Exception as e:
                print(f"Error terminating process {process_name}: {e}")


def main():

    executable_name = 'Emulator Updater.exe'
    config_name = "config.ini"
    readme_name = "README.md"
    installation_path = 'C:\\EmulationTools\\EmulatorUpdater'
    task_name = 'EmulatorUpdaterTask'

    working_directory = os.getcwd()

    executable_path = os.path.join(working_directory, executable_name)
    config_path = os.path.join(working_directory, config_name)
    readme_path = os.path.join(working_directory, readme_name)

    terminate_process(executable_name)
    print("Terminated existing processes")

    # Remove existing task if it exists
    if task_exists(task_name):
        remove_task(task_name)

    # Create the destination directory if it doesn't exist
    os.makedirs(installation_path, exist_ok=True)
    print("Created installation directory")

    # Copy the executable, configuration and readme file to the installation directory
    shutil.copy(executable_path, os.path.join(
        installation_path, executable_name))
    shutil.copy(config_path, os.path.join(installation_path, config_name))
    shutil.copy(readme_path, os.path.join(installation_path, readme_name))
    print("Copied files to installation directory")

    # Create a shortcut on the desktop
    desktop_path = desktop()
    shortcut_name = "Emulator Updater.lnk"
    shortcut_target = os.path.join(installation_path, executable_name)
    shortcut_path = os.path.join(desktop_path, shortcut_name)

    CreateShortcut(Path=shortcut_path, Target=shortcut_target,
                   Description="Emulator Updater", StartIn=installation_path)

    # Prompt the user to add a scheduled task for the Emulator Updater
    add_scheduler_confirmation = input(
        "Installation complete. Do you want to add a scheduled task for the Emulator Updater? (y/n): ").lower()

    if add_scheduler_confirmation == 'y':
        # Add task to Windows Task Scheduler
        subprocess.call(['schtasks', '/create', '/tn', task_name, '/tr',
                         f'"{installation_path}\\{executable_name}"', '/sc', 'onlogon'])

        # Prompt the user to restart their PC
        restart_confirmation = input(
            "Emulator Updater has been added to the scheduler. Do you want to restart your PC now? (y/n): ").lower()

        if restart_confirmation == 'y':
            subprocess.call(['shutdown', '/r', '/t', '1'])
        else:
            print("Please restart your PC manually to apply changes.")


if __name__ == "__main__":
    main()
