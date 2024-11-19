from .arg import BlockArg
from Qt import QtCore, QtWidgets


class FrameWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, title: str = "", icon=None, collapsed=True):
        super().__init__(parent)

        # Create the header frame
        self.header_frame = QtWidgets.QFrame()
        self.header_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.header_frame.setObjectName("headerFrame")
        self.header_frame.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        
        self.title_label = QtWidgets.QLabel()
        self.title_label.setStyleSheet("font-weight: bold;")

        self.icon_label = QtWidgets.QLabel()
    
        # Add the toggle button (still needed to show the arrow)
        self.toggle_button = QtWidgets.QToolButton()
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.setArrowType(QtCore.Qt.DownArrow)
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.clicked.connect(self.toggle_content)

        # Create the content frame
        self.content_frame = QtWidgets.QFrame()
        
        self.header_layout = QtWidgets.QHBoxLayout(self.header_frame)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(5)
        self.header_layout.addWidget(self.toggle_button)
        self.header_layout.addWidget(self.icon_label)
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch()

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.header_frame)
        main_layout.addWidget(self.content_frame)

        # Connections
        self.header_frame.mousePressEvent = self.header_clicked

        # Set initial state
        self.content_frame.setVisible(True)

        # Add the icon
        if icon:
            self.set_icon(icon)
            
        if collapsed:
            self.collapse()
            
        if title:
            self.set_title(title)
            
    def set_title(self, title):
        self.title_label.setText(title)
            
    def set_icon(self, icon):
        self.icon_label.setPixmap(icon.pixmap(16, 16))

    def layout(self):
        return self.content_frame.layout()
        
    def setLayout(self, layout):
        # layout.setContentsMargins(30, 0, 0, 0)
        self.content_frame.setLayout(layout)

    def expand(self, expanded=True):
        self.toggle_button.setArrowType(
            QtCore.Qt.DownArrow if expanded else QtCore.Qt.RightArrow)
        self.content_frame.setVisible(expanded)
        self.toggle_button.setChecked(expanded)

    def collapse(self, collapsed=True):
        self.expand(not collapsed)

    def toggle_content(self):
        is_expanded = self.toggle_button.isChecked()
        self.expand(is_expanded)

    def header_clicked(self, event):
        # Simulate a button click
        self.toggle_button.setChecked(not self.toggle_button.isChecked())
        self.toggle_content()


class Frame(BlockArg):
    """ Frame argument widget. 
        You an can add all sub-argument types.

        :param default: The default value, defaults to {}
        :type default: dict, optional
        :param items: the list of child data, defaults to False
        :type items: list of dict, optional

        :return: The new instance
        :rtype: :class:`~qargparser.object.Frame` instance
    """

    def create(self):
        from .argparser import ArgParser
        
        self.wdg = ArgParser(description=self._data['description'])
    
        default = self._data["default"]

        if 'items' in self._data:
            for _data in self._data.get('items')[:]:
                # Update default
                if _data["name"] in default:
                    _data["default"] = default[_data["name"]]

                arg = self.wdg.add_arg(**_data)
                self._data["default"][arg._data["name"]] = arg.read()

        self.wdg.changed.connect(self.on_changed)

        self._read = self.wdg._read
        self.frame_wdg = FrameWidget(title=self._data["name"], collapsed=self._data["collapsed"])
        self.frame_wdg.setLayout(QtWidgets.QVBoxLayout())
        self.frame_wdg.layout().addWidget(self.wdg)

        return self.frame_wdg

    def is_edited(self):
        return (any(child.is_edited() for child in self.get_children())
                or super(Frame, self).is_edited()
                if self._data["default"] else False)

    def reset(self):
        for child in self.get_children():
            child_name = child._data["name"]
            if child_name in self._data["default"]:
                child._data["default"] = self._data["default"][child_name]
            child.reset()
            child.changed.emit(None)
        self.changed.emit(None)

    def _update(self):
        super(Frame, self)._update()
        self.frame_wdg.set_title(self._data["name"])
        self.reset()

    def add_arg(self, *args, **kwargs):
        arg = self.wdg.add_arg(*args, **kwargs)
        self._data["default"][arg._data["name"]] = arg.read()
        return arg

    def pop_arg(self, arg):
        self.wdg.pop_arg(arg)
        self._data["default"].pop(arg._data["name"])
        self._update()

    def move_arg(self, *args, **kwargs):
        self.wdg.move_arg(*args, **kwargs)
        self._update()
        self.reset_requested.emit()

    def get_children(self):
        return self.wdg._args

    def to_data(self):
        data = super(Frame, self).to_data()
        children = self.get_children()
        if children:
            data["items"] = [child.to_data() for child in self.get_children()]

        return data
