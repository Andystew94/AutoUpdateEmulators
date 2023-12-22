# Auto Update Emulators

Auto Update Emulators is a Python script for updating all your EmuDeck Emulators in one click!

NOTE: Windows Only.

## Building the EXE from the source

```bash
python setup_emulator_updater.py build
```

```bash
python setup_installer.py build
```

## Installing the script

Run the install.exe as an admin. This will both copy the EXE and all associated files to the local drive ('C:\EmulationTools\EmulatorUpdater'), as well as add the script to the Windows Task Scheduler.

Note: This script will run at PC logon or manually.

Alternative you can copy and paste both the Emulator Updater.exe and config.ini into their own folder, in a location you prefer. However if you do this, you will need to manually set up the script in the Windows Task Scheduler.
