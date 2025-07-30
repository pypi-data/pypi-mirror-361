import sys

from PySide6 import QtWidgets

import rbeesoft.ui.constants as constants

from rbeesoft.ui.settings import Settings
from rbeesoft.ui.mainwindow import MainWindow


def main():
    settings = Settings()
    application_name = settings.get(constants.RBEESOFT_WINDOW_TITLE)
    QtWidgets.QApplication.setApplicationName(application_name)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(application_name)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()