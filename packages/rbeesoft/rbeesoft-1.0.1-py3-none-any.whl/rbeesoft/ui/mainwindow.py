import os

from PySide6.QtWidgets import (
    QMainWindow,
)
from PySide6.QtGui import (
    QGuiApplication,
    QAction,
    QIcon,
)
from PySide6.QtCore import Qt, QByteArray

import rbeesoft.ui.constants as constants

from rbeesoft.ui.settings import Settings
from rbeesoft.ui.panels.mainpanel import MainPanel
from rbeesoft.ui.panels.logpanel import LogPanel
from rbeesoft.ui.panels.settingspanel import SettingsPanel
from rbeesoft.ui.utils import resource_path, version, is_macos
from rbeesoft.core.utils.logmanager import LogManager

LOG = LogManager()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self._settings = None
        self._main_panel = None
        self._settings_panel = None
        self._log_panel = None
        self.init_window()

    def init_window(self):
        self.setWindowTitle(f'{constants.RBEESOFT_WINDOW_TITLE} {version(constants.RBEESOFT_NAME)}')
        self.setWindowIcon(QIcon(resource_path(os.path.join(
            constants.RBEESOFT_RESOURCES_IMAGES_ICONS_DIR, constants.RBEESOFT_RESOURCES_ICON))))
        if not self.load_geometry_and_state():
            self.set_default_size_and_position()
        self.init_menus()
        self.init_status_bar()
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.main_panel())
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_panel())

    def init_menus(self):
        self.init_app_menu()
        if is_macos():            
            self.menuBar().setNativeMenuBar(False)

    def init_app_menu(self):
        open_settings_action = QAction(constants.RBEESOFT_APP_MENU_OPEN_SETTINGS_PANEL_ACTION_TEXT, self)
        open_settings_action.triggered.connect(self.handle_open_settings_panel_action)
        exit_action = QAction(constants.RBEESOFT_APP_MENU_EXIT_ACTION_TEXT, self)
        exit_action.triggered.connect(self.close)
        app_menu = self.menuBar().addMenu(constants.RBEESOFT_APP_MENU_TEXT)
        app_menu.addAction(open_settings_action)
        app_menu.addAction(exit_action)

    def init_status_bar(self):
        self.set_status(constants.RBEESOFT_STATUS_READY)

    # GETTERS

    def settings(self):
        if not self._settings:
            self._settings = Settings()
        return self._settings
    
    def main_panel(self):
        if not self._main_panel:
            self._main_panel = MainPanel(self)
            self._main_panel.add_panel(
                self.settings_panel(), constants.RBEESOFT_SETTINGS_PANEL_NAME)
            self._main_panel.select_panel(constants.RBEESOFT_SETTINGS_PANEL_NAME)
        return self._main_panel
    
    def settings_panel(self):
        if not self._settings_panel:
            self._settings_panel = SettingsPanel()
        return self._settings_panel
    
    def log_panel(self):
        if not self._log_panel:
            self._log_panel = LogPanel()
            LOG.add_listener(self._log_panel)
        return self._log_panel
    
    # SETTERS

    def set_status(self, message):
        self.statusBar().showMessage(message)

    # EVENT HANDLERS

    def handle_open_settings_panel_action(self):
        self.main_panel().select_panel(constants.RBEESOFT_SETTINGS_PANEL_NAME)

    def closeEvent(self, event):
        self.save_geometry_and_state()
        return super().closeEvent(event)
    
    # MISCELLANEOUS

    def load_geometry_and_state(self):
        geometry = self.settings().get(constants.RBEESOFT_WINDOW_GEOMETRY_KEY)
        state = self.settings().get(constants.RBEESOFT_WINDOW_STATE_KEY)
        if isinstance(geometry, QByteArray) and self.restoreGeometry(geometry):
            if isinstance(state, QByteArray):
                self.restoreState(state)
            return True
        return False

    def save_geometry_and_state(self):
        self.settings().set(
            constants.RBEESOFT_WINDOW_GEOMETRY_KEY, self.saveGeometry())
        self.settings().set(
            constants.RBEESOFT_WINDOW_STATE_KEY, self.saveState())

    def set_default_size_and_position(self):
        self.resize(constants.RBEESOFT_WINDOW_W, constants.RBEESOFT_WINDOW_H)
        self.center_window()

    def center_window(self):
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.geometry().width()) / 2
        y = (screen.height() - self.geometry().height()) / 2
        self.move(int(x), int(y))