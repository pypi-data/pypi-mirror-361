from PySide6.QtCore import QSettings

from rbeesoft.ui.constants import Constants


class Settings(QSettings):
    def __init__(self):
        super(Settings, self).__init__(
            QSettings.IniFormat, 
            QSettings.UserScope, 
            Constants.RBEESOFT_BUNDLE_IDENTIFIER, 
            Constants.RBEESOFT_NAME,
        )

    def prepend_bundle_identifier_and_name(self, name):
        return '{}.{}.{}'.format(
            Constants.RBEESOFT_BUNDLE_IDENTIFIER, 
            Constants.RBEESOFT_NAME,
            name,
        )

    def get(self, name, default=None):
        if not name.startswith(Constants.RBEESOFT_BUNDLE_IDENTIFIER):
            name = self.prepend_bundle_identifier_and_name(name)
        value = self.value(name)
        if value is None or value == '':
            return default
        return value
    
    def set(self, name, value):
        name = self.prepend_bundle_identifier_and_name(name)
        self.setValue(name, value)