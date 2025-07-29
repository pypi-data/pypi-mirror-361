from PySide6 import QtWidgets, QtCore, QtGui
import os


class LogTailer(QtCore.QObject):
    def __init__(
        self,
        file_path,
        text_browser: QtWidgets.QTextBrowser,
        interval=1000,
        parent=None,
        keep_log_file=False,
    ):
        super().__init__(parent)
        self.file_path = file_path
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        self.text_browser = text_browser
        self.text_browser.clear()
        self.interval = interval
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_log)
        self.last_position = 0
        self.keep_log_file = keep_log_file

    @QtCore.Slot()
    def start(self):
        self.timer.start(self.interval)

    @QtCore.Slot()
    def stop(self):
        # we update the log one last time
        self.update_log()
        # we stop the timer
        self.timer.stop()
        # we delete the log file, unless we configure not to
        if not self.keep_log_file and os.path.exists(self.file_path):
            os.remove(self.file_path)

    @QtCore.Slot()
    def update_log(self):
        if not os.path.exists(self.file_path):
            return
        with open(self.file_path, "r") as file:
            file.seek(self.last_position)
            content = file.read()
            self.last_position = file.tell()
            if content:
                self.text_browser.insertPlainText(content)
                self.text_browser.moveCursor(QtGui.QTextCursor.MoveOperation.End)
