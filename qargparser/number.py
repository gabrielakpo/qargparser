from .arg import Arg
from .Qt import QtWidgets

class Number(Arg):
    default = 0

    def create(self):
        if isinstance(self, Float):
            wdg = QtWidgets.QDoubleSpinBox()
            wdg.setSingleStep(0.1)
        else:
            wdg = QtWidgets.QSpinBox()

        min = self._data.get('min')
        if min is not None:
            wdg.setMinimum(min)

        max = self._data.get("max")
        if max is not None:
            wdg.setMaximum(max)

        wdg.setValue(self._data['default'])

        self._write = wdg.setValue
        self._read = wdg.value

        wdg.valueChanged.connect(self.on_changed)

        return wdg

    def reset(self):
        self._write(self._data['default'])

class Float(Number):
    pass

class Integer(Number):
    pass