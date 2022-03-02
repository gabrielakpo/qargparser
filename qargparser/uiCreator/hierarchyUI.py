import os
from qargparser import Array, ArgParser, Object
from .Qt import QtWidgets, QtCore
from . import utils
from . import envs 
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
                                self.text(envs.TYPE_IDX), 
                                self.text(envs.NAME_IDX))

    @property
    def path(self):
        path = str(self)
        if self.parent():
            path = os.path.join(self.parent().path, path)
        return path

    def add_children(self, name, arg):
        item = HierarchyItem(arg("name"), arg=arg, parent=self)
        for c_arg in arg.get_children():
            item.add_children(name, c_arg)

class HierarchyParentItem(HierarchyItem):
    def __init__(self, *args, **kwargs):
        super(HierarchyParentItem, self).__init__(*args, **kwargs)
        flags = self.flags()
        flags |= QtCore.Qt.ItemIsDropEnabled
        self.setFlags(flags)

class HierarchyTree(QtWidgets.QTreeWidget):

    def __init__(self, *args, **kwargs):
        super(HierarchyTree, self).__init__(*args, **kwargs)
        self.setDragEnabled(True)
        self.setHeaderLabels(["name", "type"])
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.itemSelectionChanged.connect(self.on_item_changed)

        #Header
        header = self.header()
        header.setDefaultAlignment(QtCore.Qt.AlignCenter)
        header.setStretchLastSection(False)
        try:
            header.setSectionResizeMode(envs.NAME_IDX, QtWidgets.QHeaderView.Stretch) 
        except:
            header.setResizeMode(envs.NAME_IDX, QtWidgets.QHeaderView.Stretch) 
        header.resizeSection(envs.TYPE_IDX, 100)

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
            type = source_item.text(envs.NAME_IDX)
            new_item = self.add_item(type, target=item)

            self.setCurrentItem(new_item)

    def add_item(self, type, target=None):
        data = utils.get_properties_data(type)
        data = {d["name"]: d["default"] for d in data}
        data["type"] = type

        #Find unique name
        n = type
        n = self.search_name(n, target=target)
        data["name"] = n
        
        if target and target.arg("type") not in ["array", "object", "tab"]:
            target = target.parent()

        if target:
            arg = target.arg.add_arg(**data)
        else:
            arg = self.ap.add_arg(**data)

        if not arg:
            return 

        item = HierarchyItem(n, arg=arg)
        if target:
            target.addChild(item)
        else:
            self.addTopLevelItem(item)
        return item

    def search_name(self, name, target=None):
        #In top level
        if not target:
            while(self.findItems(name, QtCore.Qt.MatchExactly, envs.NAME_IDX)):
                name = utils.get_next_name(name)
        #In parent item children
        else:
            children = [target.child(i) for i in range(target.childCount())]
            while(name in [c.text(envs.NAME_IDX) for c in children]):
                name = utils.get_next_name(name)

        return name

    def on_item_changed(self):
        item = self.currentItem()

        if item:
            parent_item = item.parent()

            if not parent_item:
                #Item dropped
                idx = self.indexOfTopLevelItem(item)
                if  (item.arg in self.ap._args 
                    and idx != -1 
                    and idx != self.ap._args.index(item.arg)):
                    self.ap.move_arg(item.arg, idx)
            else:
                #Item dropped
                idx = parent_item.indexOfChild(item)
                children = parent_item.arg.get_children()
                if  (item.arg in children
                    and idx != -1 
                    and idx != children.index(item.arg)):
                    parent_item.arg.move_arg(item.arg, idx)

                parent_item.arg.reset()

            self.parent().item_changed.emit(item.arg)

class Hierarchy(QtWidgets.QGroupBox):
    to_delete = QtCore.Signal(object, object)
    item_changed = QtCore.Signal(object)

    def __init__(self, ap, *args, **kwargs):
        self.ap = ap

        super(Hierarchy, self).__init__(*args, **kwargs)  

        self.tree = HierarchyTree()
        layout = QtWidgets.QVBoxLayout(self)
        self.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.tree)

        self.tree.customContextMenuRequested.connect(self.show_context_menu)

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

    def edit_current_item(self):
        item = self.tree.selectedItems()[0]
        item.setText(envs.NAME_IDX, item.arg("name"))

    def show_context_menu(self, point):
        item = self.tree.itemAt(point)
        if not item:
            return

        menu = QtWidgets.QMenu()
        delete_action = menu.addAction("delete")
        delete_action.triggered.connect(partial(self.on_delete_item, item))
        menu.exec_(self.mapToGlobal(point))

    def on_delete_item(self, item):
        parent = item.parent()
        if not parent:
            self.ap.pop_arg(item.arg)
            self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(item))
        else:
            parent.arg.pop_arg(item.arg)
            parent.takeChild(parent.indexOfChild(item))

    def add_item(self, *args, **kwargs):
        return self.tree.add_item(*args, **kwargs)