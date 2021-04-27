from .Qt import QtWidgets
from .arg import Arg

class Code(Arg):
    default = '#'
    
    def create(self):
        wdg = QtWidgets.QPlainTextEdit()
        wdg.setPlainText(self._data['default'])

        self._write = wdg.setPlainText
        self._read = wdg.toPlainText
        wdg.textChanged.connect(self.on_changed)

        return wdg

    def reset(self):
        self._write(self._data['default'])

class Python(Code):
    default = '#Python'

class Mel(Code):
    default = '#Mel'