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
    def __init__(self, name, arg, parent=None):
        super(HierarchyItem, self).__init__(parent, [name, arg("type")])
        self.setIcon(NAME_IDX, envs.ICONS["type_%s" % arg("type")])

        flags = self.flags()
        flags |= QtCore.Qt.ItemIsDragEnabled
        flags |= QtCore.Qt.ItemIsDropEnabled
        # if isinstance(arg, (Array, Object)):
        #     flags ^= QtCore.Qt.ItemIsDropEnabled
        self.setFlags(flags)

        self.arg = arg

    def __repr__(self):
        return "<%s( %s, %s)>" % (self.__class__.__name__,
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
    reload_requested = QtCore.Signal(object)

    def dragMoveEvent(self, event):
        target_item = self.itemAt(event.pos())
        if target_item:
            if not target_item.is_block() or not target_item.arg.accept():
                event.ignore()
                return

        super(HierarchyTree, self).dragMoveEvent(event)

    def dropEvent(self, event):
        source_tree = event.source()

        # source is hierarchy tree
        if isinstance(source_tree, HierarchyTree):
            source_item = source_tree.currentItem()
            parent_item = source_item.parent()
            target_item = self.itemAt(event.pos())

            data = source_item.arg.to_data()

            arg = self.add_item(target=target_item, data=data)

            if arg:
                if not parent_item:
                    envs.CURRENT_AP.pop_arg(source_item.arg)
                else:
                    parent_item.arg.pop_arg(source_item.arg)
            else:
                event.ignore()
                return

        # source is items tree
        elif isinstance(source_tree, ItemsTree):
            source_item = source_tree.currentItem()

            arg = self.add_item(type=source_item.name,
                                target=self.itemAt(event.pos()))
        else:
            event.ignore()
            return

        self.reload_requested.emit(arg)

    def add_item(self, type=None, target=None, data=None):
        if not data:
            data = PropertiesManager().get_data(type, default=True)
            data["type"] = type
            data["name"] = self.get_unique_name(data["type"])

        if target and not target.arg.is_block():
            target = target.parent()

        if not target:
            target = self

        arg = target.add_arg(**data)
        return arg

    def add_arg(self, **data):
        return envs.CURRENT_AP.add_arg(**data)

    def get_unique_name(self, name):
        names = self.findItems(name,
                               QtCore.Qt.MatchExactly
                               | QtCore.Qt.MatchRecursive, NAME_IDX)
        name = utils.get_unique_name(name, names)

        return name


class HierarchyWidget(QtWidgets.QWidget):
    selection_changed = QtCore.Signal(object)
    clear_requested = QtCore.Signal()
    delete_requested = QtCore.Signal(object, object)

    def __init__(self, *args, **kwargs):

        super(HierarchyWidget, self).__init__(*args, **kwargs)

        # widgets
        self.tree = HierarchyTree()
        self.tree.setDragEnabled(True)
        self.tree.setHeaderLabels(["name", "type"])
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.setIconSize(QtCore.QSize(25, 25))
        self.tree.setSectionResizeMode(NAME_IDX, QtWidgets.QHeaderView.Stretch)
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

    def reload(self, current_arg=None):
        self.tree.blockSignals(True)
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
            for item in self.tree.iter_all_items():
                if item.arg is current_arg:
                    self.tree.setCurrentItem(item)
                    return

        self.tree.blockSignals(False)
        
        # Select first item
        if self.tree.childCount():
            self.tree.setCurrentItem(self.tree.child(0))

    def edit_current_item(self):
        item = self.tree.selectedItems()[0]
        item.setText(NAME_IDX, item.arg("name"))

    def show_context_menu(self, point):
        item = self.tree.itemAt(point)
        if not item:
            return

        menu = QtWidgets.QMenu()
        menu.addAction(envs.ICONS["delete"],
                       "delete",
                       self.on_delete_requested)

        if item.is_block() and item.arg.accept():
            children_menu = menu.addMenu("add child")
            accepted_types = sorted(item.arg.get_accepted_types())

            for name in accepted_types:
                children_menu.addAction(envs.ICONS["type_%s" % name],
                                        name,
                                        partial(self.on_add_child_requested,
                                                item,
                                                name))

        menu.exec_(self.tree.mapToGlobal(point))

    def add_item(self, *args, **kwargs):
        return self.tree.add_item(*args, **kwargs)

    def on_reload_requested(self):
        self.reload()

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

    def on_add_child_requested(self, item, name):
        self.add_item(type=name, target=item)
        self.reload()
