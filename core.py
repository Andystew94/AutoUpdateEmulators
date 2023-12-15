import os
from configparser import ConfigParser
import logging
from auto_updater.updater.emulator_updater import EmulatorUpdater
from auto_updater.ppsspp.ppsspp_updater import PPSSPPUpdater
from auto_updater.dolphin.dolphin_updater import DolphinUpdater

if __name__ == "__main__":
    # Configure logging to write to a log file
    log_file_path = os.path.join(os.getcwd(), "update_log.txt")
    logging.basicConfig(filename=log_file_path, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

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
                section_name = section
                updater = EmulatorUpdater(section_name)

            updater.update_emulator()

        except Exception as e:
            error_message = f"Error updating {section}: {e}"
            logging.error(error_message)
            print(error_message)
