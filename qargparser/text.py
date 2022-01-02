from .Qt import QtWidgets
from .arg import Arg

class Text(Arg):

    def create(self):
        wdg = QtWidgets.QPlainTextEdit()
        wdg.setPlainText(self._data['default'])

        self._write = wdg.setPlainText
        self._read = wdg.toPlainText
        wdg.textChanged.connect(self.on_changed)

        if isinstance(self, Doc):
            wdg.setReadOnly(True)

        self.wdg = wdg
        return wdg

    def reset(self):
        self._write(self._data['default'])

class Doc(Text):
    pass

class Code(Text):
    pass

class Python(Code):
    pass

class Mel(Code):
    pass