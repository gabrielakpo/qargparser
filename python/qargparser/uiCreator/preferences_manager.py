import os

from . import envs, utils

from Qt import QtCore


class ThemeManager(object):
    def __init__(self, app):
        self._app = app
        self._current_theme = "default"
        self._themes_root = envs.THEME_ROOT
        self._theme_exts = envs.THEME_EXTS

    @property
    def current_theme(self):
        return self._current_theme

    def load_theme(self, theme_name=None):
        if not theme_name:
            theme_name = "default"

        self._current_theme = theme_name

        # default
        if theme_name == "default":
            self._app.setStyleSheet("")
            return

        # find theme in files
        for ext in self._theme_exts:
            theme_dir = os.path.join(self._themes_root, theme_name)
            theme_file = os.path.join(theme_dir, "style") + ext
            if os.path.isfile(theme_file):
                break
        else:
            print("Could not find style file for : {}".format(theme_name))
            return

        theme_data = utils.read_file(theme_file)

        os.chdir(theme_dir)
        self._app.setStyleSheet("")
        self._app.setStyleSheet(theme_data)

    def get_theme_names(self):
        names = ["default"]
        for name in os.listdir(self._themes_root):
            if os.path.isdir(os.path.join(self._themes_root, name)):
                names.append(os.path.splitext(name)[0])
        return names


class SettingsManager(object):
    def __init__(self, app, root_path):
        self._root_path = root_path
        self._app = app
        self._settings = None

    def initialize(self):
        file = self.get_file()
        self._settings = QtCore.QSettings(file, QtCore.QSettings.IniFormat)
        self.save(version=0)
        self.restore(version=1)

    def get_file(self):
        return os.path.join(self._root_path, envs.SETTINGS_FILE_NAME)

    def save(self, version=0):
        if version == 0:
            key = "defaultWindowState"
        else:
            key = "customWindowState"
        self._settings.setValue(key, self._app.saveState())
        self._settings.sync()

    def save_current(self):
        self.save(version=1)

    def restore(self, version=0):
        self._settings.sync()
        if version == 0:
            key = "defaultWindowState"
        else:
            key = "customWindowState"
        if self._settings.contains(key):
            self._app.restoreState(self._settings.value(key))


class PreferencesManager(object):
    def __init__(self, app):
        self._app = app
        self._root_path = os.path.join(os.path.expanduser("~"),
                                       envs.PREFS_ROOT_NAME)

        self._file_name = envs.PREFS_FILE_NAME
        self.theme = ThemeManager(app)
        self.settings = SettingsManager(app, self._root_path)

    def _make_root(self):
        root = self._root_path
        utils.make_dir(root)
        return root

    def get_data(self):
        return {
            envs.THEME_KEY: self.theme.current_theme
        }

    def set_from_data(self, data):
        # set from data
        if envs.THEME_KEY in data:
            self.theme.load_theme(data[envs.THEME_KEY])

    def reset(self):
        data = envs.PREFS_DEFAULT
        self.set_from_data(data)

    def save(self):
        """Saves package preferences

        :param data: The preference data to save
        :type data: dict
        :param path: The path to save the prefs, defaults to None
        :type path: str, optional
        """
        root = self._make_root()

        if not root:
            print("Could not save preferences.")
            return

        data = self.get_data()

        file_path = os.path.join(root, self._file_name)
        utils.write_json(data, file_path)

        self.settings.save_current()

    def load(self):
        """Loads package preferences

        :param path: The path to save the prefs, defaults to None
        :type path: str, optional
        """

        root = self._make_root()
        file_path = os.path.join(root, self._file_name)

        data = None
        if os.path.isfile(file_path):
            data = utils.read_json(file_path)

        if not data:
            data = envs.PREFS_DEFAULT.copy()

        self.set_from_data(data)

        self.settings.initialize()