from qargparser import utils as qargp_utils, \
                       ArgParser, \
                       TYPES as items_types

from .Qt import QtWidgets, QtCore
from . import utils
from .__version__ import __title__, __version__
import TBM_UI
import sys
from functools import partial

NAME = 0
TYPE = 1

def clear_layout(layout):
    """Delete all UI children recurcively

    :param layout: layout parent, defaults to None
    :type layout: QLayout, optional
    """
    while layout.count():
        item = layout.takeAt(0)
        if item:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            lay = item.layout()
            if lay:
                clear_layout(lay) 

class Items(QtWidgets.QGroupBox):
    def __init__(self, *args, **kwargs):
        super(Items, self).__init__(*args, **kwargs)  
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.tree.setHeaderHidden(True)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.tree)

    def load(self):
        self.tree.clear()
        names = items_types.keys() 

        for name in names:
            item = QtWidgets.QTreeWidgetItem([name])
            self.tree.addTopLevelItem(item)

class HierarchyItem(QtWidgets.QTreeWidgetItem):
    def __new__(cls, *args, **kwargs):
        if kwargs['data']['type'] == "array" and cls is HierarchyItem:
            cls = HierarchyParentItem
        return super(HierarchyItem, cls).__new__(cls, *args, **kwargs)

    def __init__(self, name, data):
        type = data['type']
        super(HierarchyItem, self).__init__([name, type])
        flags = self.flags()
        flags ^= QtCore.Qt.ItemIsDropEnabled
        flags |= QtCore.Qt.ItemIsDragEnabled
        self.setFlags(flags)

        self._data = data

    def add_children(self, name, data):
        item = HierarchyItem(name+"_"+data["type"], data=data)
        self.addChild(item)
        if "items" in data:
            item.add_children(name, data["items"])

class HierarchyParentItem(HierarchyItem):
    def __init__(self, *args, **kwargs):
        super(HierarchyParentItem, self).__init__(*args, **kwargs)
        flags = self.flags()
        flags |= QtCore.Qt.ItemIsDropEnabled
        flags ^= QtCore.Qt.ItemIsDragEnabled
        self.setFlags(flags)

class HierarchyTree(QtWidgets.QTreeWidget):

    def __init__(self, *args, **kwargs):
        super(HierarchyTree, self).__init__(*args, **kwargs)
        self.setDragEnabled(True)

    def dragEnterEvent (self, event):
        source_tree = event.source()

        if isinstance(source_tree, HierarchyTree):
            if self != source_tree:
                source_tree.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
                event.accept()
            else:
                source_tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
                super(HierarchyTree, self).dragEnterEvent(event)
        else:
            super(HierarchyTree, self).dragEnterEvent(event)

    def dropEvent (self, event):
        source_tree = event.source()

        if isinstance(source_tree, HierarchyTree):
            if self != source_tree:
                source_tree.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
                source_item = source_tree.currentItem()
                isFound = False

                for column in range(0, self.columnCount()):
                    sourceQString = source_item.text(column)
                    found_items = self.findItems(sourceQString, QtCore.Qt.MatchExactly, column)
                    if found_items:
                        isFound = True
                        break

                if not isFound:
                    (source_item.parent() or source_tree.invisibleRootItem()).removeChild(source_item)
                    self.invisibleRootItem().addChild(source_item)
            else:
                source_tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
                super(HierarchyTree, self).dropEvent(event)
        else:
            event.ignore()
            source_item = source_tree.currentItem()
            item = self.itemAt(event.pos())

            type = source_item.text(NAME)
            new_item = HierarchyItem("", data={"type": type})

            if not item:
                self.addTopLevelItem(new_item)
            elif isinstance(item, HierarchyParentItem):
                item.addChild(new_item)

class Hierarchy(QtWidgets.QGroupBox):
    to_delete = QtCore.Signal(object)
    item_changed = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        super(Hierarchy, self).__init__(*args, **kwargs)  

        self.tree = HierarchyTree()
        self.tree.setHeaderLabels(["name", "type"])
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

        #Header
        header = self.tree.header()
        header.setDefaultAlignment(QtCore.Qt.AlignCenter)
        header.setStretchLastSection(False)
        try:
            header.setSectionResizeMode(NAME, QtWidgets.QHeaderView.Stretch) 
        except:
            header.setResizeMode(NAME, QtWidgets.QHeaderView.Stretch) 
        header.resizeSection(TYPE, 120)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.tree)

        self.tree.itemSelectionChanged.connect(self.on_item_changed)

    def load(self, data=None):
        self.tree.clear()
        layout = self.layout()

        if not data:
            return

        for name, _data in data.items():
            item = HierarchyItem(name, data=_data)
            self.tree.addTopLevelItem(item)

            if "items" in _data:
                item.add_children(name, _data["items"])

        self.tree.expandAll()

    def on_item_changed(self):
        item = self.tree.currentItem()
        self.item_changed.emit(item._data)

    # def delete_item(self, item):
        # parent = item.parent()

        # for idx in range(item.childCount()):
        #     child = item.child(idx)
        #     self.delete_item(child)

        # if parent:
        #     index = parent.indexOfChild(item)
        #     parent.takeChild(index)
        # else:
        #     index = self.tree.indexOfTopLevelItem(item)
        #     self.tree.takeTopLevelItem(index)
        
    def show_context_menu(self, point):
        item = self.tree.itemAt(point)
        if not item:
            return

        menu = QtWidgets.QMenu()
        delete_action = menu.addAction("delete")
        delete_action.triggered.connect(partial(self.to_delete.emit, item))
        menu.exec_(self.mapToGlobal(point))

class Preview(QtWidgets.QGroupBox):
    def __init__(self, ap, *args, **kwargs):
        super(Preview, self).__init__(*args, **kwargs)   
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(ap)
        layout.addWidget(scroll_area)

class Properties(QtWidgets.QGroupBox):
    def __init__(self, *args, **kwargs):
        super(Properties, self).__init__(*args, **kwargs)   
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

    def clear(self, layout=None):
        """Delete all UI children recurcively

        :param layout: layout parent, defaults to None
        :type layout: QLayout, optional
        """
        if not layout:
            layout = self.layout()

        while layout.count():
            item = layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                lay = item.layout()
                if lay:
                    self.clear(lay) 

    def load(self, data):
        clear_layout(self.layout())

        if not data: 
            return

        data.update(utils.get_base_properties())
        data.pop("items", None)

        ap = ArgParser(label_suffix=':',
                        data=data,
                        description='')

        self.layout().addWidget(ap)


class MainUI(TBM_UI.Window):
    WINDOW_TITLE = "%s v-%s"%(__title__, __version__)

    def __init__(self, path=None, *args, **kwargs):
        self.data = None
        self.path = None

        super(MainUI, self).__init__(*args, **kwargs)

        self.reload()

        self.resize(2500, 1800)
        self.h_splitter.setSizes([self.width()*0.25, 
                                  self.width()*0.5, 
                                  self.width()*0.25])

        if path:
            self.load_file(path)

    def create_widgets(self):
        self.file_le = QtWidgets.QLineEdit()
        self.file_le.setReadOnly(True)
        self.load_file_button = QtWidgets.QPushButton("Load")
        self.load_file_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                            QtWidgets.QSizePolicy.Fixed)
        self.save_file_button = QtWidgets.QPushButton("Save")
        self.save_file_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                            QtWidgets.QSizePolicy.Fixed)
        self.save_as_file_button = QtWidgets.QPushButton("Save As")
        self.save_as_file_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                               QtWidgets.QSizePolicy.Fixed)

        self.h_splitter = QtWidgets.QSplitter()
        self.v_splitter = QtWidgets.QSplitter(self.h_splitter)
        self.v_splitter.setOrientation(QtCore.Qt.Vertical)

        self.preview_ap = ArgParser(label_suffix=':',
                            description='')

        self.items_wdg = Items("Items", parent=self.v_splitter)
        self.hierarchy_wdg = Hierarchy("Hierarchy", parent=self.v_splitter)
        self.preview_wdg = Preview(self.preview_ap, "Preview", parent=self.h_splitter)
        self.properties_wdg = Properties("Properties", parent=self.h_splitter)

        self.h_splitter.setStretchFactor(0, 0)
        self.h_splitter.setStretchFactor(1, 1)
        self.h_splitter.setStretchFactor(2, 0)

    def create_layouts(self):
        file_layout = QtWidgets.QHBoxLayout()
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.setSpacing(2)
        file_layout.addWidget(QtWidgets.QLabel("File: "))
        file_layout.addWidget(self.file_le)
        file_layout.addWidget(self.load_file_button)
        file_layout.addWidget(self.save_file_button)
        file_layout.addWidget(self.save_as_file_button)

        main_layout = self.main_layout
        main_layout.addLayout(file_layout)
        main_layout.addWidget(self.h_splitter)

    def create_connections(self):
        self.load_file_button.clicked.connect(self.on_load_file_clicked)
        self.save_file_button.clicked.connect(self.save_file)
        self.save_as_file_button.clicked.connect(self.save_as_file)
        self.hierarchy_wdg.to_delete.connect(self.delete_item)
        self.hierarchy_wdg.item_changed.connect(self.on_hierarchy_item_changed)

    def reload(self):
        self.items_wdg.load()
        self.hierarchy_wdg.load()

    def on_hierarchy_item_changed(self, data):
        self.properties_wdg.load(data)

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
        self.preview_ap.delete_children()
        self.preview_ap.build(data)

        self.hierarchy_wdg.load(data)

        self.file_le.setText(path)

    def save_file(self):
        print('TODO: Save file')

    def save_as_file(self):
        print('TODO: Save as file')

    def delete_item(self, item):
        print(item)

def show(path=None):
    app = QtWidgets.QApplication(sys.argv)
    win_dow = MainUI(path)
    win_dow.show()
    sys.exit(app.exec_())
