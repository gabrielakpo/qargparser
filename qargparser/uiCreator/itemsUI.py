from .Qt import QtWidgets, QtCore
from qargparser import TYPES as items_types
from functools import partial
from . import envs 

class Items(QtWidgets.QGroupBox):
    add_requested = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        super(Items, self).__init__(*args, **kwargs)  
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setDragEnabled(True)
        self.tree.setHeaderHidden(True)
        self.tree.setColumnCount(2)

        header = self.tree.header()
        header.setStretchLastSection(False)
        try:
            header.setSectionResizeMode(envs.NAME_IDX, QtWidgets.QHeaderView.Stretch) 
        except:
            header.setResizeMode(envs.NAME_IDX, QtWidgets.QHeaderView.Stretch) 
        header.resizeSection(envs.ADD_IDX, 20)

        layout = QtWidgets.QVBoxLayout(self)
        # layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.tree)

    def load(self):
        self.tree.clear()
        names = sorted(items_types.keys())
        names.remove("item")

        for name in names:
            item = QtWidgets.QTreeWidgetItem([name])
            self.tree.addTopLevelItem(item)
            add_button = QtWidgets.QPushButton("+", parent=self)
            add_button.setFixedSize(20, 20)
            add_button.clicked.connect(partial(self.add_requested.emit, name))
            self.tree.setItemWidget(item, envs.ADD_IDX, add_button)
