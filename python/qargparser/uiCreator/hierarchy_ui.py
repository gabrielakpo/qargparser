import os
from qargparser import Array, Object, TYPES as ITEMS_TYPES
from Qt import QtWidgets, QtCore
from . import utils, envs
from functools import partial
from .items_ui import ItemsTree
from .customs_ui import CustomTree, CustomToolbar
from .properties_manager import PropertiesManager

TYPE_IDX = 1
NAME_IDX = 0


class HierarchyItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, argument, parent=None):
        self.arg = argument

        super(HierarchyItem, self).__init__(parent)

        self.setText(NAME_IDX, argument.name)
        self.setText(TYPE_IDX, argument.type)

        self.setIcon(NAME_IDX, envs.ICONS["type_%s" % argument("type")])

        self.setFlags(self.flags() | (QtCore.Qt.ItemIsDragEnabled |
                                      QtCore.Qt.ItemIsDropEnabled))

    @property
    def path(self):
        path = str(self)
        if self.parent():
            path = os.path.join(self.parent().path, path)
        return path

    @property
    def type(self):
        return self.arg.type

    def add_arg(self, **data):
        return self.arg.add_arg(**data)

    def is_block(self):
        return self.arg.is_block()

    def accept_children(self):
        return (self.arg.is_block() and self.arg.accept())

    def accept_drop(self, source_item):
        return (self.accept_children()
                and self.arg.accept_type(source_item.type))

    def get_accepted_children_types(self):
        if self.accept_children():
            return sorted(self.arg.get_accepted_types())
        
    def update_name(self):
        self.setText(NAME_IDX, self.arg.name)


class HierarchyTree(CustomTree):
    reload_requested = QtCore.Signal(object)
    add_argument_requested = QtCore.Signal(object, object, object)

    def dragMoveEvent(self, event):
        source_tree = event.source()

        # check sources
        if not isinstance(source_tree, (ItemsTree, HierarchyTree)):
            event.ignore()
            return

        # manage parenting drop
        target_item = self.itemAt(event.pos())
        if target_item:
            source_item = source_tree.currentItem()

            # check accepted
            if not target_item.accept_drop(source_item):
                event.ignore()
                return

        super(HierarchyTree, self).dragMoveEvent(event)

    def dropEvent(self, event):
        source_tree = event.source()

        # check sources
        if not isinstance(source_tree, (ItemsTree, HierarchyTree)):
            event.ignore()
            return

        source_item = source_tree.currentItem()
        target_item = self.itemAt(event.pos())
        target = target_item.arg if target_item else None

        # move and reparent current argument
        if isinstance(source_tree, HierarchyTree):
            parent_item = source_item.parent()
            source = source_item.arg
            source_parent = parent_item.arg if parent_item else None

            self.add_argument_requested.emit(source, target, source_parent)

        # source is items tree
        elif isinstance(source_tree, ItemsTree):
            source_item = source_tree.currentItem()
            self.add_argument_requested.emit(source_item.name, target, None)


class HierarchyWidget(QtWidgets.QWidget):
    selection_changed = QtCore.Signal(object)
    clear_requested = QtCore.Signal()
    delete_requested = QtCore.Signal(object, object)
    duplicate_requested = QtCore.Signal(object, object)
    add_argument_requested = QtCore.Signal(object, object, object)

    def __init__(self, *args, **kwargs):

        super(HierarchyWidget, self).__init__(*args, **kwargs)

        # widgets
        self.tree = HierarchyTree()
        self.tree.setDragEnabled(True)
        self.tree.setHeaderLabels(["name", "type"])
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.setIconSize(QtCore.QSize(25, 25))
        self.tree.setSectionResizeMode(NAME_IDX,
                                       QtWidgets.QHeaderView.Stretch)

        self.tree.setSectionResizeMode(TYPE_IDX,
                                       QtWidgets.QHeaderView.ResizeToContents)

        self.tree.header().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.tree.header().setStretchLastSection(False)
        self.tree.header().resizeSection(TYPE_IDX, 100)
        self.tree.header().hideSection(TYPE_IDX)

        toolbar = CustomToolbar()
        toolbar.addAction(envs.ICONS["move_up"],
                          "up",
                          self.on_up_requested)

        toolbar.addAction(envs.ICONS["move_down"],
                          "down",
                          self.on_down_requested)

        toolbar.addAction(envs.ICONS["delete"],
                          "delete",
                          self.on_delete_requested)

        toolbar.addAction(envs.ICONS["clear"],
                          "clear",
                          self.on_clear_requested)

        # layouts
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setSpacing(1)
        self.layout().addWidget(self.tree)
        self.layout().addWidget(toolbar)

        # connections
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.currentItemChanged.connect(self.on_selection_changed)
        self.tree.reload_requested.connect(self.on_reload_requested)
        self.tree.add_argument_requested.connect(self.on_add_argument_requested)

    def reload(self, current_arg=None):

        def _populate_items(parent, parent_item):
            for child in parent.get_children():
                child_item = HierarchyItem(child, parent=parent_item)
                _populate_items(child, child_item)

        self.tree.blockSignals(True)
        self.tree.clear()

        # Fill tree
        _populate_items(envs.CURRENT_AP, self.tree)

        self.tree.expandAll()

        self.tree.blockSignals(False)

        # Find current arg
        if current_arg:
            for item in self.tree.iter_all_items():
                if item.arg is current_arg:
                    self.tree.setCurrentItem(item)
                    return

        # Select first item
        elif self.tree.childCount():
            self.tree.setCurrentItem(self.tree.child(0))

    def update_current_item(self):
        item = self.tree.selectedItems()[0]
        item.update_name()

    def show_context_menu(self, point):
        item = self.tree.itemAt(point)
        if not item:
            return

        menu = QtWidgets.QMenu()
        menu.addAction(
            envs.ICONS["duplicate"],
            "duplicate",
            self.on_duplicate_requested)

        menu.addAction(
            envs.ICONS["delete"],
            "delete",
            self.on_delete_requested)

        # check if arguement can have children
        accepted_children_types = item.get_accepted_children_types()
        if accepted_children_types:
            children_menu = menu.addMenu("add child")
            for name in accepted_children_types:
                children_menu.addAction(
                    envs.ICONS["type_%s" % name],
                    name,
                    partial(self.on_add_argument_requested,
                            target=item.arg,
                            source=name))

        menu.exec_(self.tree.mapToGlobal(point))

    def on_reload_requested(self, argument):
        self.reload(argument)

    def on_selection_changed(self):
        arg = None
        item = self.tree.currentItem()
        if item:
            arg = item.arg
        self.selection_changed.emit(arg)

    def on_delete_requested(self):
        item = self.tree.currentItem()

        if not item:
            return

        # get child to delete and its parent
        parent_item = item.parent() or self.tree

        parent = None if parent_item is self.tree else parent_item.arg
        child = item.arg

        # send request to delete
        self.delete_requested.emit(parent, child)

        # update ui
        parent_item.removeChild(item)
        
    def on_duplicate_requested(self):
        item = self.tree.currentItem()

        if not item:
            return
        
        # get child to delete and its parent
        parent_item = item.parent() or self.tree

        parent = None if parent_item is self.tree else parent_item.arg
        child = item.arg

        # send request to delete
        self.duplicate_requested.emit(parent, child)

    def on_clear_requested(self):
        self.clear_requested.emit()

    def on_down_requested(self):
        item = self.tree.currentItem()
        parent_item = item.parent()

        if not parent_item:
            idx = envs.CURRENT_AP._args.index(item.arg)
            if (item.arg in envs.CURRENT_AP._args
                and idx != -1
                    and idx < len(envs.CURRENT_AP._args)):
                envs.CURRENT_AP.move_arg(item.arg, idx+1)
        else:
            children = parent_item.arg.get_children()
            idx = children.index(item.arg)
            if (item.arg in children
                and idx != -1
                    and idx < len(children)):
                parent_item.arg.move_arg(item.arg, idx+1)

        self.reload(item.arg)

    def on_up_requested(self):
        item = self.tree.currentItem()
        parent_item = item.parent()
        if not parent_item:
            idx = envs.CURRENT_AP._args.index(item.arg)
            if (item.arg in envs.CURRENT_AP._args
                and idx != -1
                    and idx > 0):
                envs.CURRENT_AP.move_arg(item.arg, idx-1)
        else:
            children = parent_item.arg.get_children()
            idx = children.index(item.arg)
            if (item.arg in children
                and idx != -1
                    and idx > 0):
                parent_item.arg.move_arg(item.arg, idx-1)

        self.reload(item.arg)

    def on_add_argument_requested(self, source, target, source_parent=None):
        self.add_argument_requested.emit(source, target, source_parent)