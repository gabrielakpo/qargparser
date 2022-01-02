from .Qt import QtWidgets
from .arg import Arg
from . import constants as cons

class Boolean(Arg):

    def create(self):
        wdg = QtWidgets.QCheckBox()
        wdg.setChecked(bool(self._data['default']))

        self._write = lambda x: wdg.setChecked(bool(x))
        self._read = wdg.isChecked

        wdg.stateChanged.connect(lambda x: self.on_changed(bool(x)))

        self.wdg = wdg
        return wdg

    def reset(self):
        self._write(self._data['default'])