from updater.emulator_updater import EmulatorUpdater
from ppsspp.ppsspp_updater import PPSSPPUpdater

if __name__ == "__main__":

    yuzu_updater = EmulatorUpdater("yuzu")
    yuzu_updater.update_emulator()

    RPCS3_updater = EmulatorUpdater("RPCS3")
    RPCS3_updater.update_emulator()

    PCSX2_updater = EmulatorUpdater("PCSX2-Qt")
    PCSX2_updater.update_emulator()

    duckstation_updater = EmulatorUpdater("duckstation")
    duckstation_updater.update_emulator()

    PPSSPP_updater = PPSSPPUpdater()
    PPSSPP_updater.update_emulator()
