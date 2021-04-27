from .Qt import QtWidgets, QtCore
from .arg import Arg

class String(Arg):

    def create(self):
        default = self._data['default']
        if "enum" in self._data:
            descriptions = self._data.get('enumDescriptions', [])
            enum = self._data['enum']
            wdg = QtWidgets.QComboBox()
            wdg.addItems(enum)
            if default is not None and default not in enum:
                idx = wdg.findText(default, QtCore.Qt.MatchExactly)
                wdg.setCurrentIndex(idx)
            else:
                idx = wdg.currentIndex()
                text = wdg.itemText(idx)
                self._data['default'] = text
        else:   
            if self._data['default'] is None:
                self._data['default'] = ''
            wdg = QtWidgets.QLineEdit()
            wdg.setText(self._data['default'])

            self._write = wdg.setText
            self._read = wdg.text
            wdg.textChanged.connect(self.on_changed)

        return wdg

    def reset(self):
        self._write(self._data['default'])