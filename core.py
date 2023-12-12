import os
from configparser import ConfigParser
from auto_updater.updater.emulator_updater import EmulatorUpdater
from auto_updater.ppsspp.ppsspp_updater import PPSSPPUpdater
from auto_updater.dolphin.dolphin_updater import DolphinUpdater

if __name__ == "__main__":

    # Load configuration from config.ini
    config = ConfigParser()
    config.read(os.path.join(os.getcwd(), "config.ini"))

    # Iterate over sections in the configuration
    for section in config.sections():
        try:
            if section == "Dolphin-x64":
                updater = DolphinUpdater()
            elif section == "PPSSPP":
                updater = PPSSPPUpdater()
            else:
                emulator_name = section
                updater = EmulatorUpdater(emulator_name)

            updater.update_emulator()
        except Exception as e:
            print(f"Error updating {section}: {e}")

    exit()
