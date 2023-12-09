from updater.emulator_updater import EmulatorUpdater

if __name__ == "__main__":

    yuzu_updater = EmulatorUpdater("yuzu")
    yuzu_updater.update_emulator()

    RPCS3_updater = EmulatorUpdater("RPCS3")
    RPCS3_updater.update_emulator()

    PCSX2_updater = EmulatorUpdater("PCSX2-Qt")
    PCSX2_updater.update_emulator()
