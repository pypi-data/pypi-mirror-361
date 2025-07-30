import webbrowser

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QDockWidget,
)

from rbeesoft.ui.constants import Constants

from rbeesoft.ui.settings import Settings
from rbeesoft.ui.panels.stackedpanel import StackedPanel
from rbeesoft.core.utils.logmanager import LogManager

LOG = LogManager()


class MainPanel(QDockWidget):
    def __init__(self, parent):
        super(MainPanel, self).__init__(parent)
        self._settings = None
        self._title_label = None
        self._donate_button = None
        self._stacked_panel = None
        self._panels = {}
        self.init_layout()

    def init_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.title_label())
        # layout.addWidget(self.donate_button())
        layout.addWidget(self.stacked_panel())
        container = QWidget()
        container.setLayout(layout)
        self.setObjectName(Constants.RBEESOFT_MAIN_PANEL_NAME)
        self.setWidget(container)

    # GETTERS

    def settings(self):
        if not self._settings:
            self._settings = Settings()
        return self._settings
    
    def title_label(self):
        if not self._title_label:
            self._title_label = QLabel('')
            self._title_label.setStyleSheet(Constants.RBEESOFT_MAIN_PANEL_NAME_TITLE_LABEL_STYLESHEET)
        return self._title_label
    
    def donate_button(self):
        if not self._donate_button:
            self._donate_button = QPushButton(Constants.RBEESOFT_DONATE_BUTTON_TEXT)
            self._donate_button.setStyleSheet(Constants.RBEESOFT_DONATE_BUTTON_STYLESHEET)
            self._donate_button.clicked.connect(self.handle_donate_button)
        return self._donate_button
    
    def stacked_panel(self):
        if not self._stacked_panel:
            self._stacked_panel = StackedPanel()
        return self._stacked_panel
    
    def panels(self):
        return self._panels

    # ADDING PANELS

    def add_panel(self, panel, name):
        self.panels()[name] = panel.title()
        self.stacked_panel().add_panel(panel, name)

    def select_panel(self, name):
        self.title_label().setText(self.panels().get(name))
        self.stacked_panel().switch_to(name)

    # EVENT HANDLERS

    def handle_donate_button(self):
        webbrowser.open(Constants.RBEESOFT_DONATE_URL)