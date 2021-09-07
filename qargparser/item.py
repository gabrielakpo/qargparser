from .Qt import QtWidgets, QtCore
from functools import partial
from .arg import Arg

class Item(Arg):

    deleted = QtCore.Signal()

    def create(self):
        wdg = QtWidgets.QWidget()
        wdg.setContentsMargins(0, 0, 0, 0)

        le = QtWidgets.QLineEdit()
        le.setText(self._data['default'])
        del_button = QtWidgets.QPushButton('X')
        del_button.clicked.connect(partial(self.delete, wdg))

        layout = QtWidgets.QGridLayout(wdg)
        layout.addWidget(le, 0, 0)
        layout.addWidget(del_button, 0, 1)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        self.wdg = wdg
        self._write = le.setText
        self._read = le.text
        le.textChanged.connect(self.on_changed)

        return wdg

    def delete(self, wdg):
        parent_wdg = wdg.parent()
        parent_wdg.delete_argument(self._data['name'], wdg)
        self.deleted.emit()
        self.changed.emit(None)

    def add_item(self, **kwargs):
        idx = len(self.wdg._arguments)
        name = self._data['name']
        self.wdg.add_argument(name + str(idx), **kwargs)

    def reset(self):
        self._write(self._data['default'])
        self.changed.emit(None)