import sys
from qargparser import utils as qargp_utils, \
                       ArgParser

from .Qt import QtWidgets, QtCore
from . import utils
from .__version__ import __title__, __version__

from .propertiesUI import Properties
from .hierarchyUI import Hierarchy
from .previewUI import Preview
from .itemsUI import Items

from . import constants as cons

class ReadPreview(QtWidgets.QWidget):
    def __init__(self, data, *args, **kwargs):
        super(ReadPreview, self).__init__(*args, **kwargs)
        self.setWindowTitle("Read Preview")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)

        wdg = QtWidgets.QPlainTextEdit()
        wdg.setReadOnly(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(wdg)

        data = utils.format_json(data)
        wdg.appendPlainText(data)

        self.resize(cons.READPREVIEW_WIN_WIDTH, 
                    cons.READPREVIEW_WIN_HEIGHT)

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

        self.resize(cons.WIN_WIDTH, cons.WIN_HEIGHT)
        self.h_splitter.setSizes([self.width()*v for v in cons.SPLITTER_RATIOS])

        self.setStyleSheet(utils.load_style())

    def create_widgets(self):
        #Menu 
        self.menuBar = QtWidgets.QMenuBar()
        self.menuBar.setFixedHeight(50)
        menu = self.menuBar.addMenu("File")
        self.new_action = menu.addAction("New")
        self.load_action = menu.addAction("Load")
        self.save_action = menu.addAction("Save")
        self.saveAs_action = menu.addAction("Save as...")
        self.readPreview_action = self.menuBar.addAction("Read preview")

        #File
        self.file_le = QtWidgets.QLineEdit()
        self.file_le.setReadOnly(True)


        #Splitters
        self.h_splitter = QtWidgets.QSplitter()
        self.v_splitter = QtWidgets.QSplitter(self.h_splitter)
        self.v_splitter.setOrientation(QtCore.Qt.Vertical)

        #Sections
        self.items_wdg = Items("Items", parent=self.v_splitter)
        self.hierarchy_wdg = Hierarchy(self.ap, "Hierarchy", parent=self.v_splitter)
        self.preview_wdg = Preview(self.ap, "Preview", parent=self.h_splitter)
        self.properties_wdg = Properties("Properties", parent=self.h_splitter)

        self.h_splitter.setStretchFactor(0, 0)
        self.h_splitter.setStretchFactor(1, 1)
        self.h_splitter.setStretchFactor(2, 0)

    def create_layouts(self):
        file_layout = QtWidgets.QHBoxLayout()
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.setSpacing(2)
        file_layout.addWidget(QtWidgets.QLabel("Path: "))
        file_layout.addWidget(self.file_le)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.menuBar)
        main_layout.addLayout(file_layout)
        main_layout.addWidget(self.h_splitter)

    def create_connections(self):
        self.new_action.triggered.connect(self.on_new_file_clicked)
        self.load_action.triggered.connect(self.on_load_file_clicked)
        self.save_action.triggered.connect(self.save_file)
        self.saveAs_action.triggered.connect(self.save_as_file)
        self.readPreview_action.triggered.connect(self.readPreview_file_clicked)
        self.hierarchy_wdg.item_changed.connect(self.on_hierarchy_item_changed)
        self.hierarchy_wdg.item_added.connect(self.on_hierarchy_item_added)
        self.items_wdg.add_requested.connect(self.on_add_requested)
        self.properties_wdg.edited.connect(self.on_properties_edited)

    def reload(self):
        self.items_wdg.load()
        self.hierarchy_wdg.load()

    def on_properties_edited(self, arg):
        self.hierarchy_wdg.edit_item(arg)

    def add_arg(self, **data):
        self.ap.add_arg(**data)

    def on_hierarchy_item_changed(self, arg):
        self.properties_wdg.load(arg)

    def on_hierarchy_item_added(self, arg):
        self.ap.add_arg(**data)

    def on_add_requested(self, name):
        self.hierarchy_wdg.add_item(name)

    def on_new_file_clicked(self):
        self.ap.delete_children()
        self.file_le.setText("")
        self.hierarchy_wdg.load()
        self.properties_wdg.load()

    def on_load_file_clicked(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, "Load", "", filter="JSON (**.json)")[0]
        
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

    def save_file(self):
        data = self.ap.to_data()
        path = r"A:\packages\perso\qargparser\dev\examples\uiCreator\test.json"
        utils.write_json(data, path)

    def save_as_file(self):
        print('TODO: Save as file')

    def readPreview_file_clicked(self):
        data = self.ap.export_data()
        ReadPreview(data, parent=self)


def show(path=None):
    app = QtWidgets.QApplication(sys.argv)
    win_dow = MainUI(path)
    win_dow.show()
    sys.exit(app.exec_())
