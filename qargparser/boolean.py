from .Qt import QtWidgets
from .arg import Arg

class Boolean(Arg):
    default = False

    def create(self):
        wdg = QtWidgets.QCheckBox()
        wdg.setChecked(bool(self._data['default']))
        return wdg