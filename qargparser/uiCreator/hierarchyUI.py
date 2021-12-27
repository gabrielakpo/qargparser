import os
from qargparser import Array, ArgParser
from .Qt import QtWidgets, QtCore
from . import utils
from . import constants as cons
from functools import partial

class HierarchyItem(QtWidgets.QTreeWidgetItem):
    def __new__(cls, *args, **kwargs):
        if isinstance(kwargs["arg"], Array) and cls is HierarchyItem:
            cls = HierarchyParentItem
        return super(HierarchyItem, cls).__new__(cls, *args, **kwargs)

    def __init__(self, name, arg, parent=None):
        self.name = name
        super(HierarchyItem, self).__init__(parent, [name, arg.__class__.__name__])
        flags = self.flags()
        flags ^= QtCore.Qt.ItemIsDropEnabled
        flags |= QtCore.Qt.ItemIsDragEnabled
        self.setFlags(flags)

        self.arg = arg

    def __repr__(self):
        return "<%s( %s )>"%(self.__class__.__name__, self.name)

    @property
    def path(self):
        path = str(self)
        if self.parent():
            path = os.path.join(self.parent().path, path)
        return path

    def add_children(self, name, arg):
        item = HierarchyItem(arg.__class__.__name__.lower(), arg=arg, parent=self)
        for c_arg in arg.get_children():
            item.add_children(name, c_arg)

    def search_from_arg(self, arg):
        if self.arg is arg:
            return self

        for j in range(self.childCount()):
            item = self.child(j)
            return item.search_from_arg(arg)

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

            type = source_item.text(cons.NAME_IDX)

            if type == "item" and (not item or not item.text(cons.NAME_IDX) == "array"):
                return

            n = type

            #Find unique name
            while(self.findItems(n, QtCore.Qt.MatchExactly, cons.NAME_IDX)):
                n = utils.get_next_name(n)

            data = utils.get_properties(type)
            data = {k: data[k]["default"] for k in data}
            data["type"] = type
            arg = self.parent().ap.add_arg(n, **data)
            new_item = HierarchyItem(n, arg=arg)

            if not item:
                self.addTopLevelItem(new_item)
            elif isinstance(item, HierarchyParentItem):
                item.addChild(new_item)

            # data["name"] = new_item.text(cons.NAME_IDX)
            # self.parent().item_added.emit(data)
            self.setCurrentItem(new_item)

class Hierarchy(QtWidgets.QGroupBox):
    to_delete = QtCore.Signal(object, object)
    item_changed = QtCore.Signal(object)
    item_added = QtCore.Signal(object)
    # item_deleted = QtCore.Signal(object)

    def __init__(self, ap, *args, **kwargs):
        self.ap = ap

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
            header.setSectionResizeMode(cons.NAME_IDX, QtWidgets.QHeaderView.Stretch) 
        except:
            header.setResizeMode(cons.NAME_IDX, QtWidgets.QHeaderView.Stretch) 
        header.resizeSection(cons.TYPE_IDX, 120)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.tree)

        self.tree.itemSelectionChanged.connect(self.on_item_changed)

    def load(self):
        self.tree.clear()
        layout = self.layout()
            
        for arg in self.ap._args:
                name = arg.name
                item = HierarchyItem(name, arg=arg)
                self.tree.addTopLevelItem(item)

                for c_arg in arg.get_children():
                    item.add_children(name, c_arg)

        self.tree.expandAll()

        #Select first item
        if self.tree.topLevelItemCount():
            self.tree.setCurrentItem(self.tree.topLevelItem(0))

    def edit_item(self, arg):
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            found_item = item.search_from_arg(arg)
            if found_item:
                break
        
        found_item.setText(cons.NAME_IDX, arg("label"))

    def on_item_changed(self):
        item = self.tree.currentItem()
        if item:
            self.item_changed.emit(item.arg)

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
        delete_action.triggered.connect(partial(self.to_delete.emit, item, item.parent()))
        menu.exec_(self.mapToGlobal(point))