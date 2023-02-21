import os  
from functools import partial
from .Qt import QtWidgets, QtCore
from . import utils
from .__version__ import __title__, __version__
from .editor_ui import EditorWidget
from . import envs 

class MainUI(QtWidgets.QDialog):
    WINDOW_TITLE = "%s v-%s"%(__title__, __version__)

    def __init__(self, path=None, *args, **kwargs):
        #Init data
        self.data = None
        self.path = None

        #Init UI
        super(MainUI, self).__init__(*args, **kwargs)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        if path:
            self.load_file(path)

        self.resize(envs.WIN_WIDTH, envs.WIN_HEIGHT)

    def create_widgets(self):
        # Menu 
        self.menuBar = QtWidgets.QMenuBar()
        self.menuBar.setFixedHeight(25)
        menu = self.menuBar.addMenu("File")
        menu.addAction("New", self.on_new_file_requested)
        self.open_action = menu.addAction("Open", self.on_open_file_requested)
        self.save_action = menu.addAction("Save", self.on_save_file_requested)
        self.saveAs_action = menu.addAction("Save as...", self.on_save_as_file_requested)
        self.clear_action = menu.addAction("Clear", self.on_clear_file_requested)
        loadExamples_menu = menu.addMenu("Load examples...")
        for name in envs.EXAMPLES_NAMES:
            loadExamples_menu.addAction(name, partial(self.open_example, name))

        self.editor_wdg = EditorWidget()

        # File
        self.file_le = QtWidgets.QLineEdit()
        self.file_le.setReadOnly(True)

    def create_layouts(self):
        file_layout = QtWidgets.QHBoxLayout()
        file_layout.setContentsMargins(2, 2, 2, 2)
        file_layout.setSpacing(2)
        file_layout.addWidget(QtWidgets.QLabel("Path: "))
        file_layout.addWidget(self.file_le)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.layout().addWidget(self.menuBar)
        self.layout().addLayout(file_layout)
        self.layout().addWidget(self.editor_wdg)

    def create_connections(self):
        pass

    def on_properties_edited(self):
        self.hierarchy_wdg.edit_current_item()

    def on_clear_file_requested(self):
        self.editor_wdg.clear()

    def on_new_file_requested(self):
        self.editor_wdg.clear()
        self.file_le.setText("")

    def on_save_file_requested(self):
        path =  self.file_le.text()

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
        path = self.file_le.text()
        dir_path = ""
        if os.path.isfile(path):
            dir_path = os.path.dirname(path)
        path = QtWidgets.QFileDialog.getOpenFileName(self, "Open file", dir_path, filter="JSON (**.json)")[0]
        if not path:
            return 
        #Update path test
        self.load_file(path)

    def load_file(self, path):
        self.editor_wdg.edit(path=path)
        self.file_le.setText(path)
    
    def open_example(self, name):
        path = utils.get_example_path(name)
        self.load_file(path)

    def on_save_as_file_requested(self):
        path = self.file_le.text()
        if os.path.isfile(path):
            path = os.path.dirname(path)
        path = QtWidgets.QFileDialog.getSaveFileName(self, "Save as...", path, filter="JSON (**.json)")[0]
        if not path:
            return 
        self.file_le.setText(path)
        envs.CURRENT_AP.save_data(path)

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
