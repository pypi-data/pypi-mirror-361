import os

from PySide6.QtWidgets import (
    QMainWindow,
)
from PySide6.QtGui import (
    QGuiApplication,
    QIcon,
)
from PySide6.QtCore import Qt, QByteArray

from rbeesoft.ui.constants import Constants
from rbeesoft.ui.settings import Settings
from rbeesoft.ui.utils import resource_path, version


class MainWindow(QMainWindow):
    def __init__(self, title, app_name, icon):
        super(MainWindow, self).__init__()
        self._title = title
        self._app_name = app_name
        self._icon = icon
        self._settings = None
        self.init_window()

    def init_window(self):
        self.setWindowTitle(f'{self.title()} {version(self.app_name())}')
        # self.setWindowIcon(QIcon(resource_path(os.path.join(
        #     Constants.RBEESOFT_RESOURCES_IMAGES_ICONS_DIR, Constants.RBEESOFT_RESOURCES_ICON))))
        self.setWindowIcon(self.icon())
        if not self.load_geometry_and_state():
            self.set_default_size_and_position()

    # GETTERS

    def title(self):
        return self._title
    
    def app_name(self):
        return self._app_name
    
    def icon(self):
        return self._icon

    def settings(self):
        if not self._settings:
            self._settings = Settings()
        return self._settings
    
    def closeEvent(self, event):
        self.save_geometry_and_state()
        return super().closeEvent(event)
    
    # MISCELLANEOUS

    def load_geometry_and_state(self):
        geometry = self.settings().get(Constants.RBEESOFT_WINDOW_GEOMETRY_KEY)
        state = self.settings().get(Constants.RBEESOFT_WINDOW_STATE_KEY)
        if isinstance(geometry, QByteArray) and self.restoreGeometry(geometry):
            if isinstance(state, QByteArray):
                self.restoreState(state)
            return True
        return False

    def save_geometry_and_state(self):
        self.settings().set(
            Constants.RBEESOFT_WINDOW_GEOMETRY_KEY, self.saveGeometry())
        self.settings().set(
            Constants.RBEESOFT_WINDOW_STATE_KEY, self.saveState())

    def set_default_size_and_position(self):
        self.resize(Constants.RBEESOFT_WINDOW_W, Constants.RBEESOFT_WINDOW_H)
        self.center_window()

    def center_window(self):
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.geometry().width()) / 2
        y = (screen.height() - self.geometry().height()) / 2
        self.move(int(x), int(y))