from Qt import QtWidgets
from .arg import Arg
import os


class FileFolderDialog(QtWidgets.QFileDialog):
    def __init__(self, *args, **kwargs):
        self.mode = kwargs.pop("mode", "all")

        super(FileFolderDialog, self).__init__(*args, **kwargs)
        self.selected_paths = []
        self.setOption(QtWidgets.QFileDialog.DontUseNativeDialog)

        if self.mode == "directory":
            self.setFileMode(QtWidgets.QFileDialog.Directory)
        else:
            self.setFileMode(QtWidgets.QFileDialog.ExistingFile)

        for pushButton in self.findChildren(QtWidgets.QPushButton):
            if pushButton.text() == "&Open" or pushButton.text() == "&Choose":
                self.open_button = pushButton
                break
        self.open_button.clicked.disconnect()
        self.open_button.clicked.connect(self.on_open_clicked)
        self.treeview = self.findChild(QtWidgets.QTreeView)

        self.currentChanged.connect(self.on_current_changed)

    def on_current_changed(self, name):
        if self.mode == "file":
            self.setFileMode(QtWidgets.QFileDialog.ExistingFile)
            self.open_button.setDisabled(not os.path.isfile(name))

        elif self.mode == "directory":
            self.setFileMode(QtWidgets.QFileDialog.Directory)
            self.open_button.setDisabled(not os.path.isdir(name))
        else:
            if os.path.isdir(name):
                self.setFileMode(QtWidgets.QFileDialog.Directory)
            else:
                self.setFileMode(QtWidgets.QFileDialog.ExistingFile)

    def selected(self):
        selected_path = ''
        if len(self.selected_paths):
            selected_path = self.selected_paths[0]
        return selected_path

    def accept(self):
        self.selected_paths = []
        self.treeview.selectionModel().selection()
        for modelIndex in self.treeview.selectionModel().selectedIndexes():
            col = modelIndex.column()
            if col == 0:
                path = '/'.join([self.directory().path(),
                                str(modelIndex.data())])
                if self.mode == "file" and not os.path.isfile(path):
                    return
                self.selected_paths.append(path)
        super(FileFolderDialog, self).accept()

    def on_open_clicked(self):
        self.accept()


class Path(Arg):
    """ Path argument widget. 
        A button open an explorer window to choose a path.

        :param default: The default value, defaults to ""
        :type default: str, optional
        :param buttonLabel: The label of the button, defaults to "..."
        :type buttonLabel: str, optional
        :param searchMessage: The title message of the explorer window,
                              defaults to "choose a path"
        :type searchMessage: str, optional

        :return: The new instance
        :rtype: :class:`~qargparser.path.Path` instance
    """

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
                                  previous_path,
                                  self._data["filters"],
                                  mode=self._data["mode"])
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
