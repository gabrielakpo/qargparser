from .Qt import QtWidgets, QtCore
from qargparser import TYPES as ITEMS_TYPES
from functools import partial
from . import envs
from .customs_ui import CustomTree, set_widget_font

ADD_IDX = 1
NAME_IDX = 0


class ItemsTreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, name):
        super(ItemsTreeItem, self).__init__([name])  
        self.setIcon(NAME_IDX, envs.ICONS["type_%s" % name])

    @property
    def name(self):
        return self.text(NAME_IDX)


class ItemsTree(CustomTree):
    pass


class ItemsWidget(QtWidgets.QWidget):
    add_requested = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        super(ItemsWidget, self).__init__(*args, **kwargs)  

        self.tree = ItemsTree()
        self.tree.setDragEnabled(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setHeaderHidden(True)
        self.tree.setColumnCount(2)
        self.tree.setResizeMode(NAME_IDX, QtWidgets.QHeaderView.Stretch) 
        self.tree.setResizeMode(ADD_IDX, QtWidgets.QHeaderView.ResizeToContents) 
        self.tree.setIconSize(QtCore.QSize(35, 35))
        self.tree.setSectionMinimumSize(10)
        self.tree.header().setStretchLastSection(False)
        self.tree.header().resizeSection(ADD_IDX, 60)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setSpacing(1)
        self.layout().addWidget(self.tree)

    def load(self):
        self.tree.clear()
        names = sorted(ITEMS_TYPES.keys())
        for name in names:
            item = ItemsTreeItem(name)
            self.tree.addChild(item)
            add_button = QtWidgets.QPushButton("+", parent=self)
            add_button.setFixedSize(35, 35)
            set_widget_font(add_button, size=14)
            add_button.clicked.connect(partial(self.add_requested.emit, name))
            self.tree.setItemWidget(item, ADD_IDX, add_button)
