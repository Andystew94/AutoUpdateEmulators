from updater.emulator_updater import EmulatorUpdater
from ppsspp.ppsspp_updater import PPSSPPUpdater
from dolphin.dolphin_updater import DolphinUpdater

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

    duckstation_updater = EmulatorUpdater("cemu")
    duckstation_updater.update_emulator()

    citra_updater = EmulatorUpdater("citra")
    citra_updater.update_emulator()

    Dolphin_updater = DolphinUpdater()
    Dolphin_updater.update_emulator()

    melonDS_updater = EmulatorUpdater("melonDS")
    melonDS_updater.update_emulator()

    xemu_updater = EmulatorUpdater("xemu")
    xemu_updater.update_emulator()

    Vita3K_updater = EmulatorUpdater("Vita3K")
    Vita3K_updater.update_emulator()
