from auto_updater.updater.emulator_updater import EmulatorUpdater
from auto_updater.ppsspp.ppsspp_updater import PPSSPPUpdater
from auto_updater.dolphin.dolphin_updater import DolphinUpdater

if __name__ == "__main__":

    try:
        yuzu_updater = EmulatorUpdater("yuzu")
        yuzu_updater.update_emulator()
    except Exception as e:
        print(f"Error updating yuzu: {e}")

    try:
        RPCS3_updater = EmulatorUpdater("RPCS3")
        RPCS3_updater.update_emulator()
    except Exception as e:
        print(f"Error updating RPCS3: {e}")

    try:
        PCSX2_updater = EmulatorUpdater("PCSX2-Qt")
        PCSX2_updater.update_emulator()
    except Exception as e:
        print(f"Error updating PCSX2: {e}")

    try:
        duckstation_updater = EmulatorUpdater("duckstation")
        duckstation_updater.update_emulator()
    except Exception as e:
        print(f"Error updating duckstation: {e}")

    try:
        PPSSPP_updater = PPSSPPUpdater()
        PPSSPP_updater.update_emulator()
    except Exception as e:
        print(f"Error updating PPSSPP: {e}")

    try:
        cemu_updater = EmulatorUpdater("cemu")
        cemu_updater.update_emulator()
    except Exception as e:
        print(f"Error updating cemu: {e}")

    try:
        citra_updater = EmulatorUpdater("citra")
        citra_updater.update_emulator()
    except Exception as e:
        print(f"Error updating citra: {e}")

    try:
        Dolphin_updater = DolphinUpdater()
        Dolphin_updater.update_emulator()
    except Exception as e:
        print(f"Error updating Dolphin: {e}")

    try:
        melonDS_updater = EmulatorUpdater("melonDS")
        melonDS_updater.update_emulator()
    except Exception as e:
        print(f"Error updating melonDS: {e}")

    try:
        xemu_updater = EmulatorUpdater("xemu")
        xemu_updater.update_emulator()
    except Exception as e:
        print(f"Error updating xemu: {e}")

    try:
        Vita3K_updater = EmulatorUpdater("Vita3K")
        Vita3K_updater.update_emulator()
    except Exception as e:
        print(f"Error updating Vita3K: {e}")

    try:
        flycast_updater = EmulatorUpdater("flycast")
        flycast_updater.update_emulator()
    except Exception as e:
        print(f"Error updating flycast: {e}")

    try:
        xenia_updater = EmulatorUpdater("xenia")
        xenia_updater.update_emulator()
    except Exception as e:
        print(f"Error updating xenia: {e}")

    try:
        mgba_updater = EmulatorUpdater("mgba")
        mgba_updater.update_emulator()
    except Exception as e:
        print(f"Error updating mgba: {e}")

    try:
        PrimeHack_updater = EmulatorUpdater("PrimeHack")
        PrimeHack_updater.update_emulator()
    except Exception as e:
        print(f"Error updating PrimeHack: {e}")
