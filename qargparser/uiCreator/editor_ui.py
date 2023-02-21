import os
from qargparser import utils as qargp_utils, \
                       ArgParser
                       
from .Qt import QtWidgets, QtCore
from . import utils
from .__version__ import __title__, __version__

from .properties_ui import PropertiesWidget
from .hierarchy_ui import HierarchyWidget
from .preview_ui import PreviewWidget
from .items_ui import ItemsWidget

from . import envs 

class EditorWidget(QtWidgets.QDialog):
    def __init__(self, path=None, data=None, *args, **kwargs):
        #Init data
        self.data = None
        self.path = None
        envs.CURRENT_AP = ArgParser(label_suffix=":")

        #Init UI
        super(EditorWidget, self).__init__(*args, **kwargs)
        self.setWindowTitle("qargparser - Editor")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        #Start
        self.items_wdg.load()
        self.edit(data=data, path=path)

        self.resize(envs.WIN_WIDTH, envs.WIN_HEIGHT)
        
    def create_widgets(self):
        #Sections
        self.items_wdg = ItemsWidget()
        self.hierarchy_wdg = HierarchyWidget()
        self.preview_wdg = PreviewWidget()
        self.properties_wdg = PropertiesWidget()

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
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.addWidget(self.h_splitter)

    def create_connections(self):
        self.hierarchy_wdg.sel_changed.connect(self.on_hierarchy_sel_changed)
        self.items_wdg.add_requested.connect(self.on_add_requested)
        self.properties_wdg.edited.connect(self.on_properties_edited)

    def edit(self, data=None, path=None):
        if path:
            data = qargp_utils.load_data_from_file(path)
        self.data = data
        envs.CURRENT_AP.clear()
        if data:
            envs.CURRENT_AP.build(data)
            self.hierarchy_wdg.load()

    def read(self):
        return envs.CURRENT_AP

    def clear(self):
        self.hierarchy_wdg.clear()
        self.hierarchy_wdg.load()

    def on_properties_edited(self):
        self.hierarchy_wdg.edit_current_item()

    def add_arg(self, **data):
        envs.CURRENT_AP.add_arg(**data)

    def on_hierarchy_sel_changed(self, arg):
        self.properties_wdg.load(arg)

    def on_add_requested(self, name):
        self.hierarchy_wdg.add_item(name)
        self.hierarchy_wdg.load()

    def on_clear_file_clicked(self):
        envs.CURRENT_AP.delete_children()
        self.hierarchy_wdg.load()
        self.properties_wdg.load()

    def load_file(self, path):
        data = qargp_utils.load_data_from_file(path)
        self.path = path
        self.data = data

        #Rebuild preview
        envs.CURRENT_AP.clear()
        envs.CURRENT_AP.build(data)
        self.hierarchy_wdg.load()
        self.file_le.setText(path)
    
    def open_example(self, name):
        path = utils.get_example_path(name)
        self.load_file(path)

    def save_as_file(self):
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

    try:
        win.close()
        win.deleteLater()
    except:
        pass

    win = EditorWidget(path)
    win.show()
    try:
        sys.exit(app.exec_())
    except:
        pass
