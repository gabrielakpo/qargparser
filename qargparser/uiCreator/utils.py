import os
import json
import re

from qargparser.utils import (
    load_data_from_file,
    write_json,
    make_dir,
    read_json)

from . import envs


class ThemeManager(object):
    def __init__(self, app):
        self._app = app
        self._current_theme = "default"

    @property
    def current_theme(self):
        return self._current_theme

    def load_theme(self, theme_name=None):
        if not theme_name:
            theme_name = "default"

        if theme_name == "default":
            self._app.setStyleSheet("")
        else:
            style_file = os.path.join(envs.STYLE_ROOT, theme_name) + ".css"

            if not os.path.isfile(style_file):
                raise FileExistsError("Could not find : {}".format(style_file))

            with open(style_file, "r", encoding="utf-8") as f:
                style_data = f.read()

                self._app.setStyleSheet(style_data)

        self._current_theme = theme_name

    def get_theme_names(self):
        names = ["default"]
        for name in os.listdir(envs.STYLE_ROOT):
            names.append(os.path.splitext(name)[0])
        return names


class PreferenceManager(object):
    def __init__(self, app):
        self._app = app
        self.theme = ThemeManager(app)

    def _make_root(self, path):
        if not path or not os.path.exists(path):
            path = os.path.expanduser("~")

        if not path:
            return

        root = os.path.join(path, envs.PREFS_ROOT_NAME)
        make_dir(root)
        return root

    def save(self, path=None):
        """Saves package preferences

        :param data: The preference data to save
        :type data: dict
        :param path: The path to save the prefs, defaults to None
        :type path: str, optional
        """
        data = {
            "theme": self.theme.current_theme
        }

        root = self._make_root(path)
        if root:
            file_path = os.path.join(root, envs.PREFS_FILE_NAME)
            write_json(data, file_path)

    def load(self, path=None):
        """Reads package preferences

        :param path: The path to save the prefs, defaults to None
        :type path: str, optional
        """
        root = self._make_root(path)
        file_path = os.path.join(root, envs.PREFS_FILE_NAME)
        if os.path.isfile(file_path):
            data = read_json(file_path) or {}
            if "theme" in data:
                self.theme.load_theme(data["theme"])


def get_properties_data(name, default=False):
    #Get true file name
    name = envs.PROPERTIES_MAPPING_NAMES.get(name, name)
    #Get base data
    data = load_data_from_file(envs.BASE_PROPERTIES_FILE)
    #Update data
    path = os.path.join(envs.PROPERTIES_PATH, name+".json")
    if os.path.isfile(path):
        data.extend(load_data_from_file(path) or {})

    if default:
        data = {d["name"]: d["default"] for d in data}
    return data


def format_json(data, indent=4):
    return json.dumps(data, indent=indent)


def split_digits(string):
    match = re.match('.*?([0-9]+)$', string)
    if match is not None:
        split = [string.rpartition(match.group(1))[0], match.group(1)]
    else:
        split = [string, None]
    return split


def get_next_name(string):
    n, idx = split_digits(string)
    if not idx:
        idx = "0"
    idx = str(int(idx) + 1)
    return  n + idx


def get_example_path(name):
    dir_path = envs.EXAMPLES_DIR_PATH
    path = os.path.join(dir_path, name+envs.EXT)
    return path


def show_documentation():
    """Opens documentation file in browser
    """
    if not os.path.isfile(envs.DOC_FILE):
        raise RuntimeError("Could not find doumentation.")

    import webbrowser
    webbrowser.open(os.path.join('file:', envs.DOC_FILE))