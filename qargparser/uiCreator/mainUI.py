import sys
import os
from qargparser import utils as qargp_utils, \
                       ArgParser
                       
from functools import partial
from .Qt import QtWidgets, QtCore
from . import utils
from .__version__ import __title__, __version__

from .propertiesUI import Properties
from .hierarchyUI import Hierarchy
from .previewUI import Preview
from .itemsUI import Items

from . import envs 

class ReadPreview(QtWidgets.QWidget):
    def __init__(self, data, *args, **kwargs):
        super(ReadPreview, self).__init__(*args, **kwargs)
        self.setWindowTitle("Read Preview")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)

        wdg = QtWidgets.QPlainTextEdit()
        wdg.setReadOnly(True)

        layout = QtWidgets.QVBoxLayout(self)
        # layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(wdg)

        data = utils.format_json(data)
        wdg.appendPlainText(data)

        self.resize(envs.READPREVIEW_WIN_WIDTH, 
                    envs.READPREVIEW_WIN_HEIGHT)

        self.show()
        self.move(self.parent().x(), self.parent().y())

class MainUI(QtWidgets.QWidget):
    WINDOW_TITLE = "%s v-%s"%(__title__, __version__)

    def __init__(self, path=None, *args, **kwargs):
        #Init data
        self.data = None
        self.path = None
        self.ap = ArgParser(label_suffix=":")

        #Init UI
        super(MainUI, self).__init__(*args, **kwargs)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        #Start
        self.reload()
        if path:
            self.load_file(path)

        self.resize(envs.WIN_WIDTH, envs.WIN_HEIGHT)
        self.h_splitter.setSizes([self.width()*v for v in envs.SPLITTER_RATIOS])

        self.setStyleSheet(utils._load_style())

    def create_widgets(self):
        #Menu 
        self.menuBar = QtWidgets.QMenuBar()
        self.menuBar.setFixedHeight(25)
        menu = self.menuBar.addMenu("File")
        self.new_action = menu.addAction("New")
        self.open_action = menu.addAction("Open")
        self.save_action = menu.addAction("Save")
        self.saveAs_action = menu.addAction("Save as...")
        self.clear_action = menu.addAction("Clear")
        loadExamples_menu = menu.addMenu("Load examples...")
        for name in envs.EXAMPLES_NAMES:
            action = loadExamples_menu.addAction(name)
            action.triggered.connect(partial(self.open_example, name))
        self.readPreview_action = self.menuBar.addAction("Read preview")

        #File
        self.file_le = QtWidgets.QLineEdit()
        self.file_le.setReadOnly(True)

        #Sections
        self.items_wdg = Items("Items")
        self.hierarchy_wdg = Hierarchy(self.ap, "Hierarchy")
        self.preview_wdg = Preview(self.ap, "Preview")
        self.properties_wdg = Properties("Properties")

        #Splitters
        self.v_splitter = QtWidgets.QSplitter()
        self.v_splitter.setOrientation(QtCore.Qt.Vertical)
        self.v_splitter.addWidget(self.items_wdg)
        self.v_splitter.addWidget(self.hierarchy_wdg)

        self.h_splitter = QtWidgets.QSplitter()
        self.h_splitter.addWidget(self.v_splitter)
        self.h_splitter.addWidget(self.preview_wdg)
        self.h_splitter.addWidget(self.properties_wdg)
        self.h_splitter.setStretchFactor(0, 0)
        self.h_splitter.setStretchFactor(1, 1)
        self.h_splitter.setStretchFactor(2, 0)
        self.h_splitter.setContentsMargins(10, 10, 10, 10)

    def create_layouts(self):
        file_layout = QtWidgets.QHBoxLayout()
        file_layout.setContentsMargins(2, 2, 2, 2)
        file_layout.setSpacing(2)
        file_layout.addWidget(QtWidgets.QLabel("Path: "))
        file_layout.addWidget(self.file_le)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.addWidget(self.menuBar)
        main_layout.addLayout(file_layout)
        main_layout.addWidget(self.h_splitter)

    def create_connections(self):
        self.clear_action.triggered.connect(self.on_clear_file_clicked)
        self.new_action.triggered.connect(self.on_new_file_clicked)
        self.open_action.triggered.connect(self.on_open_file_clicked)
        self.save_action.triggered.connect(self.save_file)
        self.saveAs_action.triggered.connect(self.save_as_file)
        self.readPreview_action.triggered.connect(self.readPreview_file_clicked)
        self.hierarchy_wdg.item_changed.connect(self.on_hierarchy_item_changed)
        self.items_wdg.add_requested.connect(self.on_add_requested)
        self.properties_wdg.edited.connect(self.on_properties_edited)

    def reload(self):
        self.items_wdg.load()
        self.hierarchy_wdg.load()

    def on_properties_edited(self):
        self.hierarchy_wdg.edit_current_item()

    def add_arg(self, **data):
        self.ap.add_arg(**data)

    def on_hierarchy_item_changed(self, arg):
        self.properties_wdg.load(arg)

    def on_add_requested(self, name):
        self.hierarchy_wdg.add_item(name)

    def on_clear_file_clicked(self):
        self.ap.delete_children()
        self.hierarchy_wdg.load()
        self.properties_wdg.load()

    def on_new_file_clicked(self):
        self.ap.delete_children()
        self.file_le.setText("")
        self.hierarchy_wdg.load()
        self.properties_wdg.load()

    def on_open_file_clicked(self):
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
        data = qargp_utils.load_data_from_file(path)
        self.path = path
        self.data = data

        #Rebuild preview
        self.ap.delete_children()
        self.ap.build(data)

        self.hierarchy_wdg.load()

        self.file_le.setText(path)
    
    def open_example(self, name):
        path = utils.get_example_path(name)
        self.load_file(path)

    def save_file(self):
        path =  self.file_le.text()

        if os.path.isfile(path):
            awns = QtWidgets.QMessageBox.question(None,
                                           "This file already exists.", 
                                           "Do you want to save your changes?",
                                           QtWidgets.QMessageBox.Save | 
                                           QtWidgets.QMessageBox.Cancel)
            if awns == QtWidgets.QMessageBox.Cancel:
                return

        self.ap.save_data(path)

    def save_as_file(self):
        path = self.file_le.text()
        if os.path.isfile(path):
            path = os.path.dirname(path)
        path = QtWidgets.QFileDialog.getSaveFileName(self, "Save as...", path, filter="JSON (**.json)")[0]
        if not path:
            return 
        self.file_le.setText(path)
        self.ap.save_data(path)

    def readPreview_file_clicked(self):
        data = self.ap.export_data()
        ReadPreview(data, parent=self)

def show(path=None):
    app = QtWidgets.QApplication(sys.argv)
    win_dow = MainUI(path)
    win_dow.show()
    sys.exit(app.exec_())
