from .arg import Arg
from .Qt import QtWidgets, QtCore, QtGui
from . import envs

class ColorButton(QtWidgets.QPushButton):
    _style = """
            QPushButton{background-color: rgba(%(r)s, %(g)s, %(b)s, %(a)s)} 
    """

    def __init__(self, color=None, *args, **kwargs):
        super(ColorButton, self).__init__(*args, **kwargs)
        if not color: color = (0, 0, 0, 1.0)
        self.set_color(color)

    def set_color(self, color):
        if len(color) < 4:
            color.append(1.0)
        self._color = [c*255 for c in color]
        self.update()

    def paintEvent(self, event):
        super(ColorButton, self).paintEvent(event)
        self.setStyleSheet(self._style%({"r":self._color[0], 
                                         "g": self._color[1], 
                                         "b": self._color[2], 
                                         "a": self._color[3]}))

class ColorSliderSpinBox(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(object)

    def __init__(self, default=[0.0, 0.0, 0.0], slider=False, spinbox=True, alpha=False, **kwargs):

        super(ColorSliderSpinBox, self).__init__()

        self.alpha = alpha

        # color
        self.color_button = ColorButton()
        self.color_button.setFixedSize(60, 20)
        self.color_button.clicked.connect(self.on_color_clicked)

        # slider
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(envs.IDX_COLORS)-1)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(self.on_slider_value_changed)
        
        # spinboxes
        self.spinbox = []
        if len(default) < 4:
            default.append(1.0)

        spinbox_layout = QtWidgets.QHBoxLayout()
        spinbox_layout.setContentsMargins(0, 0, 0, 0)
        spinbox_layout.setSpacing(0)
        for i in range(4):
            self.spinbox.append(QtWidgets.QDoubleSpinBox())
            spinbox_layout.addWidget(self.spinbox[i])
            self.spinbox[i].setMinimum(0.0)
            self.spinbox[i].setMaximum(1.0)
            self.spinbox[i].setSingleStep(0.01)
            self.spinbox[i].valueChanged.connect(self.on_spinbox_value_changed)

        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.color_button)
        lay.addStretch(0)
        lay.addWidget(self.slider, QtCore.Qt.AlignLeft)
        lay.addLayout(spinbox_layout, QtCore.Qt.AlignLeft)

        self.set_slider_visible(slider)
        self.set_spinbox_visible(spinbox)
        self.use_alpha(alpha)
        self.setValue(default)

    def value(self):
        value =  [sb.value() for sb in self.spinbox]
        if not self.alpha:
            value.pop(-1)
        return value

    def setValue(self, value):
        for i in range(len(value)):
            self.spinbox[i].setValue(value[i])

    def set_slider_visible(self, show):
        self.slider.setVisible(show)

    def set_spinbox_visible(self, show):
        for i in range(4):
            self.spinbox[i].setVisible(show)

    def use_alpha(self, use):
        self.alpha = use
        self.spinbox[-1].setVisible(use)

    def on_color_clicked(self):
        color = QtGui.QColor(*[255*c for c in self.value()])
        color_wdg = QtWidgets.QColorDialog(color)
        color_wdg.setOption(QtWidgets.QColorDialog.ShowAlphaChannel, self.alpha)
        response = color_wdg.exec_()
        if not response:
            return
        color = color_wdg.selectedColor()
        color = [color.red()/255.0, color.green()/255.0, color.blue()/255.0, color.alpha()/255.0]
        if not self.alpha:
            color.pop(-1)
        self.setValue(color)

    def on_spinbox_value_changed(self):
        self.color_button.set_color(self.value())
        self.valueChanged.emit(self.value())

    def on_slider_value_changed(self, idx):
        color = envs.IDX_COLORS[idx]
        self.setValue(color)

class Color(Arg):
    """ Color argument widget.

        :param default: The default value, defaults to [0.0, 0.0, 0.0]
        :type default: color, optional
        :param slider: Add a slider if True, defaults to True
        :type slider: bool, optional
        :param spinbox: Add a 3 double spinbox if True, defaults to True
        :type spinbox: bool, optional
        :param alpha: Add a double spinbox for alpha if True, defaults to False
        :type alpha: bool, optional

        :return: The new instance
        :rtype: :class:`~qargparser.number.Color` instance
    """
    def create(self):
        #Widget
        if not self._data["alpha"] and len(self._data["default"]) > 3:
            self._data["default"].pop(-1)

        wdg = ColorSliderSpinBox(slider=self._data["slider"],
                                 spinbox=self._data["spinbox"],
                                 alpha=self._data["alpha"],
                                 default=self._data['default'])

        self._write = wdg.setValue
        self._read = wdg.value

        wdg.valueChanged.connect(self.on_changed)

        self.wdg = wdg
        return wdg

    def reset(self):
        self._write(self._data['default'])

    def _update(self):
        if self._data["alpha"] and len(self._data["default"]) < 4:
            self._data["default"].append(1.0)
        self.wdg.set_slider_visible(self._data["slider"])
        self.wdg.set_spinbox_visible(self._data["spinbox"])
        self.wdg.use_alpha(self._data["alpha"])
        super(Color, self)._update()
