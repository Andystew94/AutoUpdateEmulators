from yuzu_update import YuzuUpdater

if __name__ == "__main__":
    updater = YuzuUpdater("pineappleEA/pineapple-src")
    success = updater.update_yuzu()
    
    if success:
        print("Yuzu updated successfully.")
    else:
        print("Yuzu update failed.")
