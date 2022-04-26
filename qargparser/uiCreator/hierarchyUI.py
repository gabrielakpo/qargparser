import os
from qargparser import Array, Object
from .Qt import QtWidgets, QtCore
from . import utils
from . import envs 
from functools import partial
from .itemsUI import ItemsTree

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

    def add_arg(self, **data):
        return self.arg.add_arg(**data)

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
        self.currentItemChanged.connect(self.on_selection_changed)

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
        return self.parent().parent().ap


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
                        self.ap.pop_arg(source_item.arg)
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
            data = utils.get_properties_data(type, default=True)
            data["type"] = type
            data["name"] = self.search_name(data["type"])
        
        if target and target.arg("type") not in ["array", "object", "tab"]:
            target = target.parent()

        if not target: 
            target = self

        arg = target.add_arg(**data)
        return arg

    def add_arg(self, **data):
        return self.ap.add_arg(**data)

    def search_name(self, name):
        while(self.findItems(name, QtCore.Qt.MatchExactly 
                                 | QtCore.Qt.MatchRecursive, envs.NAME_IDX)):
            name = utils.get_next_name(name)
        return name


    def on_selection_changed(self):
        item = self.currentItem()
        if item:
            self.get_parent().sel_changed.emit(item.arg)

    def delete_item(self, item):
        parent = item.parent()
        if not parent:
            self.get_parent().ap.pop_arg(item.arg)
            self.takeTopLevelItem(self.indexOfTopLevelItem(item))
        else:
            parent.arg.pop_arg(item.arg)
            parent.takeChild(parent.indexOfChild(item))

    def get_parent(self):
        return self.parent().parent() 

class Hierarchy(utils.FrameLayout):
    to_delete = QtCore.Signal(object, object)
    sel_changed = QtCore.Signal(object)

    def __init__(self, ap, *args, **kwargs):
        self.ap = ap

        super(Hierarchy, self).__init__(collapsable=False, *args, **kwargs)  

        self.tree = HierarchyTree()
        self.up_button = QtWidgets.QPushButton("up")
        self.down_button = QtWidgets.QPushButton("down")

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(self.up_button)
        buttons_layout.addWidget(self.down_button)

        self.setContentsMargins(2, 2, 2, 2)
        self.addWidget(self.tree)
        self.addLayout(buttons_layout)

        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.up_button.clicked.connect(self.on_up_requested)
        self.down_button.clicked.connect(self.on_down_requested)

    def on_down_requested(self):
        item = self.tree.currentItem()
        parent_item = item.parent()
        if not parent_item:
            idx = self.ap._args.index(item.arg)
            if  (item.arg in self.ap._args 
                and idx != -1 
                and idx < len(self.ap._args)):
                self.ap.move_arg(item.arg, idx+1)
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
            idx = self.ap._args.index(item.arg)
            if  (item.arg in self.ap._args 
                and idx != -1 
                and idx > 0):
                self.ap.move_arg(item.arg, idx-1)
        else:
            children = parent_item.arg.get_children()
            idx = children.index(item.arg)
            if  (item.arg in children
                and idx != -1 
                and idx > 0):
                parent_item.arg.move_arg(item.arg, idx-1)

        self.load(item.arg)

    def load(self, current_arg=None):
        self.tree.clear()

        # Fill tree
        for arg in self.ap._args:
                name = arg.name
                item = HierarchyItem(name, arg=arg)
                self.tree.addTopLevelItem(item)

                for c_arg in arg.get_children():
                    item.add_children(name, c_arg)

        self.tree.expandAll()

        # Find current arg
        if current_arg:
            items = self.tree.findItems(current_arg.name, QtCore.Qt.MatchExactly 
                                      | QtCore.Qt.MatchRecursive, envs.NAME_IDX) or []
            for item in items:
                if item.arg == current_arg:
                    self.tree.setCurrentItem(item)
                    return
        
        # Select first item
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
        self.tree.delete_item(item)

    def add_item(self, *args, **kwargs):
        return self.tree.add_item(*args, **kwargs)