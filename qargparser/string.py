from .Qt import QtWidgets, QtCore
from .arg import Arg

class String(Arg):

    def create(self):
        default = self._data['default']

        if "enum" in self._data:
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

        else:   
            if self._data['default'] is None:
                self._data['default'] = ''
            wdg = QtWidgets.QLineEdit()
            wdg.setText(self._data['default'])

            #Info
            if isinstance(self, Info):
                wdg.setReadOnly(True)

            self._write = wdg.setText
            self._read = wdg.text
            wdg.editingFinished.connect(lambda: self.on_editing_finished(wdg))

        self.wdg = wdg
        return wdg

    def reset(self):
        self._write(self._data['default'])

    def on_editing_finished(self, wdg):
        text = wdg.text()
        self.on_changed(text)

class Info(String):
    pass