import os
from qargparser import Array, ArgParser, Object
from .Qt import QtWidgets, QtCore
from . import utils
from . import constants as cons
from functools import partial

class HierarchyItem(QtWidgets.QTreeWidgetItem):
    def __new__(cls, *args, **kwargs):
        if isinstance(kwargs["arg"], (Array, Object) ) and cls is HierarchyItem:
            cls = HierarchyParentItem
        return super(HierarchyItem, cls).__new__(cls, *args, **kwargs)

    def __init__(self, name, arg, parent=None):
        super(HierarchyItem, self).__init__(parent, [name, arg("type")])
        flags = self.flags()
        flags ^= QtCore.Qt.ItemIsDropEnabled
        flags |= QtCore.Qt.ItemIsDragEnabled
        self.setFlags(flags)

        self.arg = arg

    def __repr__(self):
        return "<%s( %s, %s)>"%(self.__class__.__name__, 
                                self.text(cons.TYPE_IDX), 
                                self.text(cons.NAME_IDX))

    @property
    def path(self):
        path = str(self)
        if self.parent():
            path = os.path.join(self.parent().path, path)
        return path

    def add_children(self, name, arg):
        item = HierarchyItem(arg("type"), arg=arg, parent=self)
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
        self.setHeaderLabels(["name", "type"])
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        #Header
        header = self.header()
        header.setDefaultAlignment(QtCore.Qt.AlignCenter)
        header.setStretchLastSection(False)
        try:
            header.setSectionResizeMode(cons.NAME_IDX, QtWidgets.QHeaderView.Stretch) 
        except:
            header.setResizeMode(cons.NAME_IDX, QtWidgets.QHeaderView.Stretch) 
        header.resizeSection(cons.TYPE_IDX, 120)

    @property
    def ap(self):
        return self.parent().ap

    def dragEnterEvent (self, event):
        source_tree = event.source()

        if isinstance(source_tree, QtWidgets.QTreeWidget):
            if self != source_tree:
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
                source_item = source_tree.currentItem()
                is_found = False

                for column in range(0, self.columnCount()):
                    source_string = source_item.text(column)
                    found_items = self.findItems(source_string, QtCore.Qt.MatchExactly, column)
                    if found_items:
                        is_found = True
                        break

                if not is_found:
                    (source_item.parent() or source_tree.invisibleRootItem()).removeChild(source_item)
                    self.invisibleRootItem().addChild(source_item)
            else:
                source_tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
                source_item = source_tree.currentItem()
                super(HierarchyTree, self).dropEvent(event)
                self.setCurrentItem(source_item)
        else:
            event.ignore()
            source_item = source_tree.currentItem()

            item = self.itemAt(event.pos())
            type = source_item.text(cons.NAME_IDX)
            new_item = self.add_item(type, item)

            self.setCurrentItem(new_item)

    def add_item(self, type, parent=None):
        data = utils.get_properties_data(type)
        data = {d["name"]: d["default"] for d in data}
        data["type"] = type

        #Find unique name
        n = type
        while(self.findItems(n, QtCore.Qt.MatchExactly, cons.NAME_IDX)):
            n = utils.get_next_name(n)

        data["name"] = n

        if parent and type in ["array", "item"]:
            arg = parent.arg.add_arg(**data)
        else:
            arg = self.ap.add_arg(**data)

        if not arg:
            return 

        item = HierarchyItem(n, arg=arg)
        if parent:
            parent.addChild(item)
        else:
            self.addTopLevelItem(item)
        return item

class Hierarchy(QtWidgets.QGroupBox):
    to_delete = QtCore.Signal(object, object)
    item_changed = QtCore.Signal(object)
    item_added = QtCore.Signal(object)

    def __init__(self, ap, *args, **kwargs):
        self.ap = ap

        super(Hierarchy, self).__init__(*args, **kwargs)  

        self.tree = HierarchyTree()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.tree)

        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.itemSelectionChanged.connect(self.on_item_changed)

    def load(self):
        self.tree.clear()
            
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
        
        found_item.setText(cons.NAME_IDX, arg("name"))

    def on_item_changed(self):
        item = self.tree.currentItem()
        if item:
            parent_item = item.parent()
            if not parent_item:
                #Item dropped
                idx = self.tree.indexOfTopLevelItem(item)
                if  idx != -1 and idx != self.ap._args.index(item.arg):
                    self.ap.move_arg(item.arg, idx)
            else:
                print(parent_item)

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
        delete_action.triggered.connect(partial(self.on_delete_item, item, item.parent()))
        menu.exec_(self.mapToGlobal(point))

    def on_delete_item(self, item, parent):
        if not parent:
            self.ap.pop_arg(item.arg)
            self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(item))

    def add_item(self, *args, **kwargs):
        return self.tree.add_item(*args, **kwargs)