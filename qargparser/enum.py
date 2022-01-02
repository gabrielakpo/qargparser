from .Qt import QtWidgets, QtCore
from .arg import Arg

class Enum(Arg):

    def create(self):
        #Widget
        wdg = QtWidgets.QComboBox()
        self.wdg = wdg

        #Init
        self._init()
        
        #Connections
        self._write = lambda x: wdg.setCurrentIndex(wdg.findText(x, QtCore.Qt.MatchExactly))
        self._read =  lambda: wdg.itemText(wdg.currentIndex())
        wdg.currentIndexChanged.connect(lambda x: self.on_changed(wdg.itemText(x)))

        return wdg

    def _init(self):
        self.wdg.addItems(self._data["enums"])
        
        if (self._data['default'] is not None 
        and self._data['default'] in self._data["enums"]):
            idx = self.wdg.findText(self._data['default'], QtCore.Qt.MatchExactly)
            self.wdg.setCurrentIndex(idx)
        else:
            idx = self.wdg.currentIndex()
            text = self.wdg.itemText(idx)
            self._data['default'] = text

        #Descriptions
        descs = self._data['enumsDescriptions']
        for i in range(len(self._data["enums"])):
            if i < len(descs):
                self.wdg.setItemData(i, descs[i], QtCore.Qt.ToolTipRole)

    def reset(self):
        self._write(self._data['default'])

    def _update(self):
        super(Enum, self)._update()
        self.wdg.clear()
        self._init()


        
