import os  
from functools import partial
from .Qt import QtWidgets, QtCore
from . import utils
from .__version__ import __title__, __version__
from .editor_ui import EditorWidget
from . import envs


class MainUI(QtWidgets.QMainWindow):

    def __init__(self, path=None, *args, **kwargs):
        self._current_file = ""
        self._preference = utils.PreferenceManager(self)

        # Init UI
        super(MainUI, self).__init__(*args, **kwargs)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        # init
        if path:
            self.load_file(path)

        self.resize(envs.WIN_WIDTH, envs.WIN_HEIGHT)

        # theme
        self.populate_themes_actions()
        self._preference.load()
        self.set_theme(self._preference.theme.current_theme)

        # title
        self.update_window_title()

    def create_widgets(self):
        # Menu
        self.menuBar = QtWidgets.QMenuBar()
        self.menuBar.setFixedHeight(25)

        file_menu = self.menuBar.addMenu("File")

        file_menu.addAction("New", self.on_new_file_requested)
        file_menu.addAction("Open", self.on_open_file_requested)
        file_menu.addAction("Save", self.on_save_file_requested)
        file_menu.addAction("Save as...", self.on_save_as_file_requested)
        file_menu.addAction("Clear", self.on_clear_file_requested)

        setting_menu = self.menuBar.addMenu("Settings")

        self.theme_menu = setting_menu.addMenu("theme")
        self.theme_action_grp = QtWidgets.QActionGroup(self)
        self.theme_action_grp.setExclusive(True)
        
        help_menu = self.menuBar.addMenu("Help")
        help_menu.addAction("About qarparser...", self.on_show_documentation_requested)

        loadExamples_menu = file_menu.addMenu("Load examples...")
        for name in envs.EXAMPLES_NAMES:
            loadExamples_menu.addAction(name, partial(self.open_example, name))

        self.editor_wdg = EditorWidget()

        # central widget
        self.setCentralWidget(QtWidgets.QWidget())

    def create_layouts(self):
        self.centralWidget().setLayout(QtWidgets.QVBoxLayout())
        self.centralWidget().layout().setContentsMargins(10, 10, 10, 10)
        self.centralWidget().layout().addWidget(self.menuBar)
        self.centralWidget().layout().addWidget(self.editor_wdg)

    def create_connections(self):
        pass

    def update_window_title(self):
        title = "%s v-%s"%(__title__, __version__)
        path = self._current_file

        if not path:
            path = "untitled"

        title += "  -  "
        title += path
        self.setWindowTitle(title)

    def populate_themes_actions(self):
        self.theme_menu.clear()

        for action in self.theme_action_grp.actions():
            self.theme_action_grp.removeAction(action)

        theme_names = self._preference.theme.get_theme_names()

        for theme_name in theme_names:
            action = self.theme_menu.addAction(theme_name)
            action.setCheckable(True)
            action.triggered.connect(partial(self.on_theme_requested, theme_name))
            self.theme_action_grp.addAction(action)

    def set_theme(self, theme_name=None):
        self._preference.theme.load_theme(theme_name)
        theme_name = self._preference.theme.current_theme

        for action in self.theme_action_grp.actions():
            if action.text() == theme_name:
                action.setChecked(True)
                break

    def load_file(self, path):
        self._current_file = path
        self.editor_wdg.edit(path=path)
        self.update_window_title()
    
    def open_example(self, name):
        path = utils.get_example_path(name)
        self.load_file(path)

    def on_theme_requested(self, theme_name):
        self.set_theme(theme_name)

    def on_properties_edited(self):
        self.hierarchy_wdg.edit_current_item()

    def on_clear_file_requested(self):
        self.editor_wdg.clear()

    def on_new_file_requested(self):
        self.editor_wdg.clear()
        self._current_file = ""
        self.update_window_title()

    def on_save_file_requested(self):
        path = self.file_le.text()

        if os.path.isfile(path):
            awns = QtWidgets.QMessageBox.question(
                None,
                "This file already exists.",
                "Do you want to save your changes?",
                QtWidgets.QMessageBox.Save | 
                QtWidgets.QMessageBox.Cancel)
            if awns == QtWidgets.QMessageBox.Cancel:
                return

        envs.CURRENT_AP.save_data(path)

    def on_open_file_requested(self):
        path = self._current_file
        dir_path = ""
        if os.path.isfile(path):
            dir_path = os.path.dirname(path)
        path = QtWidgets.QFileDialog.getOpenFileName(self, "Open file", dir_path, filter="JSON (**.json)")[0]
        if not path:
            return 
        #Update path test
        self.load_file(path)

    def on_save_as_file_requested(self):
        path = self._current_file
        if os.path.isfile(path):
            path = os.path.dirname(path)
        path = QtWidgets.QFileDialog.getSaveFileName(self, "Save as...", path, filter="JSON (**.json)")[0]
        if not path:
            return 
        self._current_file = path
        self.update_window_title()
        envs.CURRENT_AP.save_data(path)

    def on_show_documentation_requested(self):
        utils.show_documentation()
        
    def closeEvent(self, event):
        self._preference.save()
        super(MainUI, self).closeEvent(event)


def show(path=None):
    try:
        import sys
        app = QtWidgets.QApplication(sys.argv)
    except:
        app = QtWidgets.QApplication.instance()

    win_dow = MainUI(path)
    win_dow.show()
    try:
        sys.exit(app.exec_())
    except:
        pass
