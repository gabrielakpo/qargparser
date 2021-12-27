from .Qt import QtWidgets
from qargparser import TYPES as items_types

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