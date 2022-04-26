from .Qt import QtWidgets, QtCore
from qargparser import TYPES as items_types
from functools import partial
from . import utils

ADD_IDX = 0
NAME_IDX = 1

class ItemsTreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, name):
        super(ItemsTreeItem, self).__init__(['', name])  

    @property
    def name(self):
        return self.text(NAME_IDX)

class ItemsTree(QtWidgets.QTreeWidget):
    pass

class Items(utils.FrameLayout):
    add_requested = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        super(Items, self).__init__(collapsable=False, *args, **kwargs)  
        self.tree = ItemsTree()
        self.tree.setDragEnabled(True)
        self.tree.setHeaderHidden(True)
        self.tree.setColumnCount(2)

        header = self.tree.header()
        header.setStretchLastSection(True)
        try:
            header.setSectionResizeMode(NAME_IDX, QtWidgets.QHeaderView.Stretch) 
        except:
            header.setResizeMode(NAME_IDX, QtWidgets.QHeaderView.Stretch) 
        header.resizeSection(ADD_IDX, 60)

        self.addWidget(self.tree)

    def load(self):
        self.tree.clear()
        names = sorted(items_types.keys())
        names.remove("item")

        for name in names:
            item = ItemsTreeItem(name)
            self.tree.addTopLevelItem(item)
            add_button = QtWidgets.QPushButton("+", parent=self)
            add_button.setFixedSize(20, 20)
            add_button.clicked.connect(partial(self.add_requested.emit, name))
            self.tree.setItemWidget(item, ADD_IDX, add_button)
