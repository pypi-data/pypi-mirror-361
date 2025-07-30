from PySide6.QtWidgets import QStyle

from rbeesoft.ui.utils import is_macos


class Constants:
    # MAIN APPLICATION
    RBEESOFT_WINDOW_TITLE = 'Rbeesoft'
    RBEESOFT_NAME = 'rbeesoft'
    RBEESOFT_BUNDLE_IDENTIFIER = 'com.rbeesoft'
    RBEESOFT_WINDOW_W = 1024
    RBEESOFT_WINDOW_H = 600
    RBEESOFT_WINDOW_GEOMETRY_KEY = 'window/geometry'
    RBEESOFT_WINDOW_STATE_KEY = 'window/state'
    RBEESOFT_STATUS_READY = 'Ready'
    RBEESOFT_DONATE_URL = 'https://rbeesoft.nl/wordpress/'
    RBEESOFT_DONATE_BUTTON_TEXT = 'If you wish to support us, please consider a donation by clicking here!'
    RBEESOFT_DONATE_BUTTON_STYLESHEET = 'background-color: blue; color: white; font-weight: bold;'
    RBEESOFT_LAST_DIRECTORY_KEY = 'last_directory'
    # https://www.pythonguis.com/faq/built-in-qicons-pyqt/#qt-standard-icons
    RBEESOFT_ICON_EXIT = QStyle.SP_MessageBoxCritical
    RBEESOFT_ICON_SETTINGS = QStyle.SP_VistaShield

    # RESOURCES
    RBEESOFT_RESOURCES_DIR = 'rbeesoft/resources'
    RBEESOFT_RESOURCES_IMAGES_DIR = 'rbeesoft/resources/images'
    RBEESOFT_RESOURCES_IMAGES_ICONS_DIR = 'rbeesoft/resources/images/icons'
    RBEESOFT_RESOURCES_ICON = 'rbeesoft.icns' if is_macos() else 'rbeesoft.ico'

    # MENUS
    RBEESOFT_APP_MENU_TEXT = 'Application'
    RBEESOFT_APP_MENU_OPEN_SETTINGS_PANEL_ACTION_TEXT = 'Settings...'
    RBEESOFT_APP_MENU_EXIT_ACTION_TEXT = 'Exit'

    # PANELS
    RBEESOFT_MAIN_PANEL_NAME = 'mainpanel'
    RBEESOFT_MAIN_PANEL_NAME_TITLE_LABEL_STYLESHEET = 'color: black; font-weight: bold; font-size: 14pt;'
    RBEESOFT_LOG_PANEL_TITLE = 'Output log'
    RBEESOFT_LOG_PANEL_NAME = 'logpanel'
    RBEESOFT_LOG_PANEL_CLEAR_LOGS_BUTTON = 'Clear logs'
    RBEESOFT_SETTINGS_PANEL_TITLE = 'Settings'
    RBEESOFT_SETTINGS_PANEL_NAME ='settingspanel'
    RBEESOFT_SETTINGS_PANEL_NAME_COLUMN_NAME = 'NAME'
    RBEESOFT_SETTINGS_PANEL_VALUE_COLUMN_NAME = 'VALUE'
    RBEESOFT_SETTINGS_PANEL_CANNOT_DISPLAY_MESSAGE = 'Cannot display (binary data)'