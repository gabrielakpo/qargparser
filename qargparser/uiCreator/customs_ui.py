from .Qt import QtWidgets, QtCore, QtGui
from . import envs
from functools import partial


def set_widget_font(wdg, size=None, weight=None):
    font = wdg.font()
    if size:
        font.setPointSize(size)
    if weight:
        font.setWeight(weight)
    wdg.setFont(font)


class ThrobberWidget(QtWidgets.QDialog):
    def __init__(self, parent=None, loading_message="Loading...", *args, **kwargs):
        super(ThrobberWidget, self).__init__(parent, *args, **kwargs)
        self.setWindowFlags(QtCore.Qt.Window
                            | QtCore.Qt.FramelessWindowHint
                            | QtCore.Qt.CustomizeWindowHint)
        self.setWindowTitle(loading_message)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        pixmap = QtGui.QPixmap(envs.FILES["throbber"])
        label = QtWidgets.QLabel()
        label.setPixmap(pixmap.scaled(200,
                                      200,
                                      QtCore.Qt.KeepAspectRatio,
                                      QtCore.Qt.SmoothTransformation))
        label.setScaledContents(True)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(label)

        self.setFixedSize(200, 200)

        if self.parent():
            center = self.parent().rect().center()
            point = self.parent().mapToGlobal(center)
            point = self.mapFromGlobal(point)
            point.setX(point.x()-self.width()/2)
            point.setY(point.y()-self.height()/2)
            self.move(point.x(), point.y())


class CustomToolbar(QtWidgets.QToolBar):
    def __init__(self, style=QtCore.Qt.ToolButtonTextUnderIcon, icon_size=(25, 25), *args, **kwargs):
        super(CustomToolbar, self).__init__(*args, **kwargs)
        self.setToolButtonStyle(style)
        self.setIconSize(QtCore.QSize(*icon_size))

    def add_menu(self, icon=None, text="", menu=None, mode=QtWidgets.QToolButton.InstantPopup):
        button = QtWidgets.QToolButton()
        button.setPopupMode(mode)
        button.setToolButtonStyle(self.toolButtonStyle())
        button.setText(text)
        if icon:
            button.setIcon(icon)
        if not menu:
            menu = QtWidgets.QMenu()
        action = QtWidgets.QWidgetAction(button)
        action.setDefaultWidget(menu)
        button.addAction(action)
        self.addWidget(button)

        return menu


class CustomTree(QtWidgets.QTreeWidget):
    delete_item_requested = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        self.hide_ignores = []  # Ignore indexes when hide requested
        self.itemWidgets = set()

        super(CustomTree, self).__init__(*args, **kwargs)
        self.header().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.header().customContextMenuRequested.connect(self.show_header_context_menu)

    def setItemWidget(self, item, column, widget):
        self.itemWidgets.add(widget)
        widget.destroyed.connect(lambda: self.itemWidgets.discard(widget))
        super(CustomTree, self).setItemWidget(item, column, widget)

    def updateGeometries(self):
        hidden = [w for w in self.itemWidgets if w.isHidden()]
        super(CustomTree, self).updateGeometries()
        for widget in hidden:
            widget.setVisible(False)

    def show_header_context_menu(self, point):
        menu = QtWidgets.QMenu(self.header())
        for i in range(self.header().count()):
            if i in self.hide_ignores:
                continue
            name = self.headerItem().text(i)
            action = menu.addAction(name)
            action.setCheckable(True)
            action.setChecked(not self.header().isSectionHidden(i))
            action.toggled.connect(partial(self.on_hide_section_requested, i))
        menu.exec_(self.mapToGlobal(point))

    def on_hide_section_requested(self, idx, value):
        if (not value
                and (self.header().count() - self.header().hiddenSectionCount() < 2)):
            return
        self.header().setSectionHidden(idx, not value)

    def childCount(self):
        return self.topLevelItemCount()

    def child(self, idx):
        return self.topLevelItem(idx)

    def insertChild(self, *args, **kwargs):
        return self.insertTopLevelItem(*args, **kwargs)

    def addChild(self, item, deletable=False):
        self.addTopLevelItem(item)
        if deletable:
            del_button = QtWidgets.QPushButton("x")
            del_button.setFixedWidth(20)
            del_button.clicked.connect(
                partial(self.on_delete_item_requested, item))
            del_wdg = QtWidgets.QWidget(self)
            del_wdg.setLayout(QtWidgets.QHBoxLayout())
            del_wdg.layout().setContentsMargins(0, 0, 0, 0)
            del_wdg.layout().addStretch(0)
            del_wdg.layout().addWidget(del_button)
            del_wdg.layout().addStretch(0)
            self.setItemWidget(item, self.columnCount()-1, del_wdg)

    def on_delete_item_requested(self, item):
        self.delete_item_requested.emit(item)

    def takeChild(self, idx):
        return self.takeTopLevelItem(idx)

    def indexOfChild(self, item):
        return self.indexOfTopLevelItem(item)

    def setSectionResizeMode(self, *args, **kwargs):
        try:
            self.header().setSectionResizeMode(*args, **kwargs)
        except:
            self.header().setResizeMode(*args, **kwargs)

    def setResizeMode(self, *args, **kwargs):
        self.setSectionResizeMode(*args, **kwargs)

    def setSectionMinimumSize(self, size):
        try:
            self.header().setSectionMinimumSize(size)
        except:
            self.header().setMinimumSectionSize(size)

    def iter_all_items(self):
        def _iter(parent):
            for i in range(parent.childCount()):
                child = parent.child(i)
                yield child
                if child.childCount():
                    for item in _iter(child):
                        yield item
        return _iter(self)

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())

        if index.isValid():
            super(CustomTree, self).mousePressEvent(event)

            if event.button() == QtCore.Qt.LeftButton and \
               event.modifiers() == QtCore.Qt.ShiftModifier:
                self.expandChildren(index, self.isExpanded(index))
        else:
            super(CustomTree, self).mousePressEvent(event)

    def expandChildren(self, index, state):
        if not index.isValid():
            return
        childCount = index.model().rowCount(index)
        for i in range(childCount):
            child = index.child(i, 0)
            self.expandChildren(child, state)
        if state:
            self.expand(index)
        else:
            self.collapse(index)

    def collapse_all(self):
        for item in self.iter_all_items():
            item.setExpanded(False)


class CustomDockWidget(QtWidgets.QDockWidget):
    def __init__(self, title=None, *args, **kwargs):
        super(CustomDockWidget, self).__init__(*args, **kwargs)
        self.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable |
                         QtWidgets.QDockWidget.DockWidgetFloatable |
                         QtWidgets.QDockWidget.DockWidgetClosable)
        if title:
            title_label = QtWidgets.QLabel(title)
            title_label.setAlignment(QtCore.Qt.AlignCenter)
            set_widget_font(title_label, size=10, weight=QtGui.QFont.Bold)
            self.setTitleBarWidget(title_label)
            self.setWindowTitle(title)
            self.setObjectName(title.replace("", "_"))

        wdg = QtWidgets.QWidget()
        wdg.setLayout(QtWidgets.QVBoxLayout())
        self.setWidget(wdg)

    def layout(self):
        return self.widget().layout()