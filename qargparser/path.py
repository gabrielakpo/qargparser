from .Qt import QtWidgets
from .arg import Arg
import os

class FileFolderDialog(QtWidgets.QFileDialog):
    def __init__(self, *args, **kwargs):
        super(FileFolderDialog, self).__init__(*args, **kwargs)
        self.selected_paths = []
        self.setOption(QtWidgets.QFileDialog.DontUseNativeDialog)
        self.setFileMode(QtWidgets.QFileDialog.Directory)

        for pushButton in self.findChildren(QtWidgets.QPushButton):
            if pushButton.text() == "&Open" or pushButton.text() == "&Choose" :
                self.openButton=pushButton
                break
        self.openButton.clicked.disconnect()
        self.openButton.clicked.connect(self.openClicked)
        self.treeview=self.findChild(QtWidgets.QTreeView)
        self.currentChanged.connect(self.change_mode)
        
    def change_mode(self, name):
        if os.path.isdir(name):
            self.setFileMode(QtWidgets.QFileDialog.Directory)
        else:
            self.setFileMode(QtWidgets.QFileDialog.ExistingFile)
 
    def selected(self):
        selected_path=''
        if len(self.selected_paths):
            selected_path=self.selected_paths[0]
        return selected_path

    def openClicked(self):
        self.selected_paths=[]
        self.treeview.selectionModel().selection()
        for modelIndex in self.treeview.selectionModel().selectedIndexes():
            col=modelIndex.column()
            if col == 0:
                self.selected_paths.append('/'.join([self.directory().path(), 
                                                    str(modelIndex.data())]))
        self.filesSelected.emit(self.selected_paths)
        self.hide()

class Path(Arg):

    def create(self):
        self.le = QtWidgets.QLineEdit()
        self.le.setText(self._data['default'])
        self.folder_button = QtWidgets.QPushButton(self._data['buttonLabel'])
        self.folder_button.clicked.connect(self.show_search_path_dialog)
        self.folder_button.setFixedSize(self.le.sizeHint().height(),
                                   self.le.sizeHint().height())
        wdg = QtWidgets.QWidget()
        wdg.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QGridLayout(wdg)
        layout.addWidget(self.le, 0, 0)
        layout.addWidget(self.folder_button, 0, 1)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        self._write = self.le.setText
        self._read = self.le.text
        self.le.textChanged.connect(self.on_changed)

        self.wdg = wdg
        return wdg

    def show_search_path_dialog(self):
        previous_path = self.le.text()
        dialog = FileFolderDialog(None,
                                  self._data['searchMessage'],
                                  previous_path)
        dialog.exec_()
        path = dialog.selected()
        if not path:
            path = previous_path
        self.le.setText(path)

    def reset(self):
        self._write(self._data['default'])

    def _update(self):
        super(Path, self)._update()
        self.folder_button.setText(self._data['buttonLabel'])