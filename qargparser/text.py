from .Qt import QtWidgets
from .arg import Arg

class Text(Arg):
    default = '#'
    
    def create(self):
        wdg = QtWidgets.QPlainTextEdit()
        wdg.setPlainText(self._data['default'])

        self._write = wdg.setPlainText
        self._read = wdg.toPlainText
        wdg.textChanged.connect(self.on_changed)

        if isinstance(self, Doc):
            wdg.setReadOnly(True)

        return wdg

    def reset(self):
        self._write(self._data['default'])

class Doc(Text):
    default = '#Documentation'

class Code(Text):
    default = '#Code'

class Python(Code):
    default = '#Python'

class Mel(Code):
    default = '#Mel'