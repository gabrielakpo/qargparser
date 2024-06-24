import os
from functools import partial
from qargparser import ArgParser
from Qt import QtWidgets, QtCore
from . import utils
from .__version__ import __title__, __version__
from .preferences_manager import PreferencesManager
from .properties_ui import PropertiesWidget
from .hierarchy_ui import HierarchyWidget
from .preview_ui import PreviewWidget
from .items_ui import ItemsWidget
from . import envs
from .customs_ui import CustomDockWidget, ThrobberWidget


class MainUI(QtWidgets.QMainWindow):

    def __init__(self, path=None, *args, **kwargs):
        self._current_file = ""
        self._preferences_manager = PreferencesManager(self)

        envs.CURRENT_AP = ArgParser(label_suffix=":")

        super(MainUI, self).__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        # init
        self.items_wdg.load()
        self.populate_examples_actions()

        if path:
            self.load_file(path)

        self.resize(envs.WIN_WIDTH, envs.WIN_HEIGHT)

        # theme
        self.call_throbber(self._preferences_manager.load, raise_error=False)

        # title
        self.update_window_title()

    def create_widgets(self):
        # Menu
        menubar = QtWidgets.QMenuBar()
        self.setMenuBar(menubar)

        menubar.setFixedHeight(25)

        # file
        file_menu = menubar.addMenu("File")

        # reload
        file_menu.addAction("reload", self.on_reload_requested)

        # new / open
        file_menu.addSeparator()

        file_menu.addAction("new", self.on_new_file_requested)
        file_menu.addAction("open", self.on_open_file_requested)
        self.examples_menu = file_menu.addMenu("examples")

        # save / save as
        file_menu.addSeparator()

        file_menu.addAction("save", self.on_save_file_requested)
        file_menu.addAction("save as...", self.on_save_as_file_requested)

        # clear
        file_menu.addSeparator()

        file_menu.addAction("Clear", self.on_clear_file_requested)

        # workspace
        workspace_menu = menubar.addMenu("Workspace")
        workspace_menu.addAction("reset", self.on_reset_workspace_requested)
        self.workspace_edit_menu = workspace_menu.addMenu("edit")

        # settings
        setting_menu = menubar.addMenu("Settings")

        # theme
        self.theme_menu = setting_menu.addMenu("theme")

        # help
        help_menu = menubar.addMenu("Help")
        help_menu.addAction(
            "About qarparser...",
            self.on_show_documentation_requested)

        # central widget
        self.setCentralWidget(QtWidgets.QWidget())

        # Sections
        self.items_wdg = ItemsWidget()
        self.hierarchy_wdg = HierarchyWidget()
        self.preview_wdg = PreviewWidget()
        self.properties_wdg = PropertiesWidget()

        self.create_dock("Items", self.items_wdg, QtCore.Qt.LeftDockWidgetArea)
        self.create_dock("Hierarchy", self.hierarchy_wdg,
                         QtCore.Qt.LeftDockWidgetArea)
        self.create_dock("Properties", self.properties_wdg,
                         QtCore.Qt.RightDockWidgetArea)

    def create_dock(self, name, widget, area):
        dock = CustomDockWidget(name)
        dock.layout().addWidget(widget)
        self.addDockWidget(area, dock)
        return dock

    def create_layouts(self):
        self.centralWidget().setLayout(QtWidgets.QVBoxLayout())
        self.centralWidget().layout().setContentsMargins(5, 5, 5, 5)
        self.centralWidget().layout().addWidget(self.preview_wdg)

    def create_connections(self):
        self.workspace_edit_menu.aboutToShow.connect(
            self.on_show_workspace_menu_requested)
        self.theme_menu.aboutToShow.connect(self.populate_themes_actions)
        self.examples_menu.aboutToShow.connect(self.populate_examples_actions)

        self.hierarchy_wdg.selection_changed.connect(
            self.on_hierarchy_selection_changed)

        self.hierarchy_wdg.clear_requested.connect(
            self.on_hierarchy_clear_requested)

        self.hierarchy_wdg.delete_requested.connect(
            self.on_hierarchy_delete_requested)

        self.items_wdg.add_requested.connect(self.on_add_item_requested)
        self.properties_wdg.edited.connect(self.on_properties_edited)
        self.preview_wdg.reset_requested.connect(self.on_reset_requested)

    def call_throbber(self,
                      callback=None,
                      raise_error=True,
                      loading_message=None):

        throbber_wdg = ThrobberWidget(parent=self,
                                      loading_message=loading_message)
        throbber_wdg.show()

        QtWidgets.QApplication.processEvents()

        if callback:
            try:
                result = callback()

            except Exception:
                import traceback
                msg = traceback.format_exc()
                QtWidgets.QMessageBox.critical(
                    self,
                    "%s - error" % self.windowTitle(),
                    "%s" % msg)
                if raise_error:
                    raise
            finally:
                throbber_wdg.deleteLater()

        QtWidgets.QApplication.processEvents()

        return result

    def update_window_title(self):
        title = "{} v-{}" .format(__title__, __version__)
        path = self._current_file

        if not path:
            path = "untitled"

        title += "  -  "
        title += path
        self.setWindowTitle(title)

    def populate_themes_actions(self):
        self.theme_menu.clear()

        theme_names = self._preferences_manager.theme.get_theme_names()

        for theme_name in theme_names:
            action = self.theme_menu.addAction(theme_name)
            action.setCheckable(True)

            if theme_name == self._preferences_manager.theme.current_theme:
                action.setChecked(True)

            action.triggered.connect(
                partial(self.on_theme_requested, theme_name))

    def populate_examples_actions(self):
        self.examples_menu.clear()
        for name in utils.get_example_names():
            self.examples_menu.addAction(
                name, partial(self.on_open_example_requested, name))

    def reload_ui(self):
        if self._current_file:
            self.load_file(self._current_file)

    def clear(self):
        self.hierarchy_wdg.clear()

    def reset(self):
        envs.CURRENT_AP.reset()

    def new_file(self):
        self.clear()
        self._current_file = ""
        self.update_window_title()

    def set_theme(self, theme_name=None):
        self._preferences_manager.theme.load_theme(theme_name)
        theme_name = self._preferences_manager.theme.current_theme

    def add_item(self, name):
        self.hierarchy_wdg.add_item(name)
        self.hierarchy_wdg.reload()

    def load_file(self, path):
        self._current_file = path
        envs.CURRENT_AP.build_from_path(path)
        self.hierarchy_wdg.reload()
        self.update_window_title()

    def open_example(self, name):
        path = utils.get_example_path(name)
        if path:
            self.load_file(path)

    def request_save_file(self):
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

    def request_save_as_file(self):
        path = self._current_file

        if os.path.isfile(path):
            path = os.path.dirname(path)

        path = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save as...",
            path,
            filter=envs.FILE_FILTERS)[0]

        if not path:
            return

        self._current_file = path
        self.update_window_title()
        envs.CURRENT_AP.save_data(path)

    def request_open_file(self):
        path = self._current_file
        dir_path = ""

        if os.path.isfile(path):
            dir_path = os.path.dirname(path)

        path = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open file",
            dir_path,
            filter=envs.FILE_FILTERS)[0]

        if not path:
            return

        # Update path test
        self.load_file(path)

    def on_properties_edited(self):
        self.hierarchy_wdg.edit_current_item()

    def on_hierarchy_selection_changed(self, arg):
        self.properties_wdg.load(arg)

    def on_hierarchy_clear_requested(self):
        envs.CURRENT_AP.delete_children()
        self.hierarchy_wdg.reload()

    def on_hierarchy_delete_requested(self, parent, child):
        if not parent:
            parent = envs.CURRENT_AP
        parent.pop_arg(child)

    def on_add_item_requested(self, name):
        self.call_throbber(partial(self.add_item, name))

    def on_theme_requested(self, theme_name):
        self.call_throbber(partial(self.set_theme, theme_name))

    def on_reload_requested(self):
        self.call_throbber(self.reload_ui)

    def on_reset_requested(self):
        self.call_throbber(self.reset)

    def on_clear_file_requested(self):
        self.call_throbber(self.clear)

    def on_reset_workspace_requested(self):
        self._preferences_manager.settings.restore()

    def on_show_workspace_menu_requested(self):
        self.workspace_edit_menu.clear()
        menu = self.createPopupMenu()
        if menu:
            action = QtWidgets.QWidgetAction(self)
            action.setDefaultWidget(menu)
            self.workspace_edit_menu.addAction(action)

    def on_new_file_requested(self):
        self.call_throbber(self.new_file)

    def on_save_file_requested(self):
        self.call_throbber(self.request_save_file)

    def on_open_file_requested(self):
        self.call_throbber(self.request_open_file)

    def on_save_as_file_requested(self):
        self.call_throbber(self.request_save_as_file)

    def on_show_documentation_requested(self):
        self.call_throbber(utils.show_documentation)

    def on_open_example_requested(self, name):
        self.call_throbber(partial(self.open_example, name))

    def closeEvent(self, event):
        self._preferences_manager.save()
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
