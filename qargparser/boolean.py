from .Qt import QtWidgets
from .arg import Arg

class Boolean(Arg):
    default = False

    def create(self):
        wdg = QtWidgets.QCheckBox()
        wdg.setChecked(bool(self._data['default']))

        self._write = wdg.setChecked
        self._read = bool(wdg.isChecked)

        wdg.stateChanged.connect(self.on_changed)

        return wdg

    def reset(self):
        self._write(self._data['default'])