from .Qt import QtWidgets, QtCore
from .arg import Arg

class Enum(Arg):
    default = ""

    def create(self):
        default = self._data['default']

        descs = self._data.get('enumDescriptions', [])
        enum = self._data['enum']
        wdg = QtWidgets.QComboBox()
        wdg.addItems(enum)
        
        if default is not None and default in enum:
            idx = wdg.findText(default, QtCore.Qt.MatchExactly)
            wdg.setCurrentIndex(idx)
        else:
            idx = wdg.currentIndex()
            text = wdg.itemText(idx)
            self._data['default'] = text

        self._write = lambda x: wdg.setCurrentIndex(wdg.findText(x, QtCore.Qt.MatchExactly))
        self._read =  lambda: wdg.itemText(wdg.currentIndex())
        wdg.currentIndexChanged.connect(lambda x: self.on_changed(wdg.itemText(x)))

        self.wdg = wdg
        return wdg

    def reset(self):
        self._write(self._data['default'])

    def _update(self):
        super(Enum, self)._update()
        self.wdg.clear()
        self.wdg.addItems(self._data["enum"])
