import os
import logging
import sys
from configparser import ConfigParser
from subprocess import check_call

from auto_updater.updater.emulator_updater import EmulatorUpdater
from auto_updater.ppsspp.ppsspp_updater import PPSSPPUpdater
from auto_updater.dolphin.dolphin_updater import DolphinUpdater
from auto_updater.helpers.web_scrapper import WebScrapper

try:
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QTextEdit, QDesktopWidget
    from PyQt5.QtCore import pyqtSignal, QThread, QMetaObject, Qt, Q_ARG
except ImportError as e:
    print(f"Error importing required module: {e}")
    print("Installing necessary modules...")
    try:
        check_call(['pip', 'install', 'PyQt5'])
        from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QTextEdit, QDesktopWidget
        from PyQt5.QtCore import pyqtSignal, QThread, QMetaObject, Qt, Q_ARG
    except Exception as install_error:
        print(f"Error installing module: {install_error}")
        exit(1)


class UpdateThread(QThread):
    update_finished = pyqtSignal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.webscrapper = WebScrapper()
        self.update_finished.emit()

    def run(self):
        for idx, section_name in enumerate(self.config.sections(), start=1):
            try:
                if section_name == "Dolphin-x64":
                    updater = DolphinUpdater(self.webscrapper)
                elif section_name == "PPSSPP":
                    updater = PPSSPPUpdater(self.webscrapper)
                else:
                    updater = EmulatorUpdater(section_name)

                updater.update_emulator()
                self.update_finished.emit()

            except Exception as e:
                error_message = f"Error updating {section_name}: {e}"
                logging.error(error_message)
                self.update_finished.emit()

        self.webscrapper.quit()


class UpdateWindow(QWidget):
    def __init__(self, config, log_file_path):
        super().__init__()

        self.config = config
        self.log_file_path = log_file_path
        self.progress_bar = QProgressBar(self)
        self.log_text = QTextEdit(self)
        # Store the total number of sections
        self.total_sections = len(config.sections()) - 1
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_text)

        self.setWindowTitle("Updating Emulators")

        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry(desktop.primaryScreen())
        self.setGeometry(screen_rect.x(), screen_rect.y(
        ), (screen_rect.width() // 2), (screen_rect.height() // 2))

        self.configure_logger()

        self.update_thread = UpdateThread(self.config)
        self.update_thread.update_finished.connect(self.update_finished)
        self.update_thread.finished.connect(self.update_thread_finished)
        self.update_thread.start()

        # Set the maximum value of the progress bar based on the total number of sections
        self.progress_bar.setMaximum(self.total_sections)

    def configure_logger(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            filemode='w', filename=self.log_file_path)

        class WidgetHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget

            def emit(self, record):
                msg = self.format(record)
                QMetaObject.invokeMethod(
                    self.text_widget, "append", Qt.QueuedConnection, Q_ARG(str, msg + '\n'))
                self.flush()

        widget_handler = WidgetHandler(self.log_text)
        logging.getLogger().addHandler(widget_handler)

    def update_finished(self):
        QMetaObject.invokeMethod(self.progress_bar, "setValue", Qt.QueuedConnection, Q_ARG(
            int, self.progress_bar.value() + 1))
        QApplication.processEvents()  # Process events to update the GUI

    def update_thread_finished(self):
        self.progress_bar.setValue(
            self.progress_bar.maximum())  # Set progress to 100%
        QApplication.processEvents()  # Process events to update the GUI

        self.close()


def main():
    script_directory = os.path.dirname(os.path.realpath(sys.argv[0]))

    config = ConfigParser()
    config.read(os.path.join(script_directory, "config.ini"))

    app = QApplication([])

    log_file_path = os.path.join(script_directory, "scraper.log")

    window = UpdateWindow(config, log_file_path)
    window.show()

    app.exec_()


if __name__ == "__main__":
    main()
