import os
from qargparser import Array, Object, TYPES as ITEMS_TYPES
from Qt import QtWidgets, QtCore
from . import utils
from . import envs 
from functools import partial
from .items_ui import ItemsTree
from .customs_ui import CustomTree, CustomToolbar
from .properties_manager import PropertiesManager

TYPE_IDX = 1
NAME_IDX = 0

class HierarchyItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, name, arg, parent=None):
        super(HierarchyItem, self).__init__(parent, [name, arg("type")])
        self.setIcon(NAME_IDX, envs.ICONS["type_%s" % arg("type")])

        flags = self.flags()
        flags |= QtCore.Qt.ItemIsDragEnabled
        flags |= QtCore.Qt.ItemIsDropEnabled
        if isinstance(arg, (Array, Object)):
            flags ^= QtCore.Qt.ItemIsDropEnabled
        self.setFlags(flags)

        self.arg = arg

    def __repr__(self):
        return "<%s( %s, %s)>"%(self.__class__.__name__, 
                                self.text(TYPE_IDX), 
                                self.text(NAME_IDX))
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

    def add_arg(self, **data):
        return self.arg.add_arg(**data)
    
    def is_block(self):
        return self.arg.is_block()

class HierarchyTree(CustomTree):
    def __init__(self, *args, **kwargs):
        super(HierarchyTree, self).__init__(*args, **kwargs)
        self.setDragEnabled(True)
        self.setHeaderLabels(["name", "type"])
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.currentItemChanged.connect(self.on_selection_changed)
        self.setIconSize(QtCore.QSize(25, 25))
        self.setSectionResizeMode(NAME_IDX, QtWidgets.QHeaderView.Stretch) 
        self.header().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.header().setStretchLastSection(False)
        self.header().resizeSection(TYPE_IDX, 100)
        self.header().hideSection(TYPE_IDX)

    def dropEvent(self, event):
        arg = None
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
                source_item = source_tree.currentItem()
                data  = source_item.arg.to_data() 
                parent = source_item.parent()
                arg = self.add_item(target=self.itemAt(event.pos()), 
                                         data=data)
                if arg:
                    if not parent:
                        envs.CURRENT_AP.pop_arg(source_item.arg)
                    else:
                        parent.arg.pop_arg(source_item.arg)
                else:
                    event.ignore()

        elif isinstance(source_tree, ItemsTree):
            source_item = source_tree.currentItem()

            arg = self.add_item(type=source_item.name, 
                                target=self.itemAt(event.pos()))

        self.get_parent().load(arg)

    def add_item(self, type=None, target=None, data=None):
        if not data:
            data = PropertiesManager().get_data(type, default=True)
            data["type"] = type
            data["name"] = self.search_name(data["type"])
        
        if target and not target.arg.is_block():
            target = target.parent()

        if not target: 
            target = self

        arg = target.add_arg(**data)
        return arg

    def add_arg(self, **data):
        return envs.CURRENT_AP.add_arg(**data)

    def search_name(self, name):
        while(self.findItems(name, QtCore.Qt.MatchExactly 
                                 | QtCore.Qt.MatchRecursive, NAME_IDX)):
            name = utils.get_next_name(name)
        return name

    def on_selection_changed(self):
        arg = None
        item = self.currentItem()
        if item:
            arg = item.arg
        self.get_parent().sel_changed.emit(arg)

    def delete_item(self, item):
        parent = item.parent()
        if not parent:
            envs.CURRENT_AP.pop_arg(item.arg)
            self.takeTopLevelItem(self.indexOfTopLevelItem(item))
        else:
            parent.arg.pop_arg(item.arg)
            parent.takeChild(parent.indexOfChild(item))

    def get_parent(self):
        return self.parent()


class HierarchyWidget(QtWidgets.QWidget):
    sel_changed = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):

        super(HierarchyWidget, self).__init__(*args, **kwargs)  

        self.tree = HierarchyTree()

        toolbar = CustomToolbar()
        toolbar.addAction(envs.ICONS["move_up"], "up", self.on_up_requested)
        toolbar.addAction(envs.ICONS["move_down"], "down", self.on_down_requested)
        toolbar.addAction(envs.ICONS["delete"], "delete", self.on_delete_requested)
        toolbar.addAction(envs.ICONS["clear"], "clear", self.on_clear_requested)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setSpacing(1)
        self.layout().addWidget(self.tree)
        self.layout().addWidget(toolbar)

        self.tree.customContextMenuRequested.connect(self.show_context_menu)

    def load(self, current_arg=None):
        self.tree.clear()

        # Fill tree
        for arg in envs.CURRENT_AP._args:
                name = arg.name
                item = HierarchyItem(name, arg=arg)
                self.tree.addTopLevelItem(item)

                for c_arg in arg.get_children():
                    item.add_children(name, c_arg)

        self.tree.expandAll()

        # Find current arg
        if current_arg:
            items = self.tree.findItems(current_arg.name, QtCore.Qt.MatchExactly 
                                      | QtCore.Qt.MatchRecursive, NAME_IDX) or []
            for item in items:
                if item.arg == current_arg:
                    self.tree.setCurrentItem(item)
                    return
        
        # Select first item
        if self.tree.topLevelItemCount():
            self.tree.setCurrentItem(self.tree.topLevelItem(0))

    def clear(self):
        envs.CURRENT_AP.delete_children()
        self.load()

    def edit_current_item(self):
        item = self.tree.selectedItems()[0]
        item.setText(NAME_IDX, item.arg("name"))

    def show_context_menu(self, point):
        item = self.tree.itemAt(point)
        if not item:
            return

        menu = QtWidgets.QMenu()
        menu.addAction(envs.ICONS["delete"], "delete", partial(self.on_delete_item, item))

        if item.is_block():
            children_menu = menu.addMenu("add child")
            for name in ITEMS_TYPES:
                children_menu.addAction(envs.ICONS["type_%s" % name], name, partial(self.on_add_child_requested, item, name))
        menu.exec_(self.tree.mapToGlobal(point))

    def add_item(self, *args, **kwargs):
        return self.tree.add_item(*args, **kwargs)

    def on_delete_item(self, item):
        self.tree.delete_item(item)

    def on_delete_requested(self):
        item = self.tree.currentItem()
        if item:
            self.tree.delete_item(item)

    def on_clear_requested(self):
        self.clear()

    def on_down_requested(self):
        item = self.tree.currentItem()
        parent_item = item.parent()
        if not parent_item:
            idx = envs.CURRENT_AP._args.index(item.arg)
            if  (item.arg in envs.CURRENT_AP._args 
                and idx != -1 
                and idx < len(envs.CURRENT_AP._args)):
                envs.CURRENT_AP.move_arg(item.arg, idx+1)
        else:
            children = parent_item.arg.get_children()
            idx = children.index(item.arg)
            if  (item.arg in children
                and idx != -1 
                and idx < len(children)):
                parent_item.arg.move_arg(item.arg, idx+1)

        self.load(item.arg)

    def on_up_requested(self):
        item = self.tree.currentItem()
        parent_item = item.parent()
        if not parent_item:
            idx = envs.CURRENT_AP._args.index(item.arg)
            if  (item.arg in envs.CURRENT_AP._args 
                and idx != -1 
                and idx > 0):
                envs.CURRENT_AP.move_arg(item.arg, idx-1)
        else:
            children = parent_item.arg.get_children()
            idx = children.index(item.arg)
            if  (item.arg in children
                and idx != -1 
                and idx > 0):
                parent_item.arg.move_arg(item.arg, idx-1)

        self.load(item.arg)

    def on_add_child_requested(self, item, name):
        self.add_item(type=name, target=item)
        self.load()