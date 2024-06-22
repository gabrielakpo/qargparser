from .arg import Arg
from Qt import QtWidgets, QtCore


class DoubleSlider(QtWidgets.QSlider):

    doubleValueChanged = QtCore.Signal(float)

    def __init__(self, orient=QtCore.Qt.Horizontal, parent=None, decimals=3):
        super(DoubleSlider, self).__init__(orient, parent)
        self._multi = 10 ** decimals

        self.valueChanged.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = float(super(DoubleSlider, self).value()) / self._multi
        self.doubleValueChanged.emit(value)

    def value(self):
        return float(super(DoubleSlider, self).value()) / self._multi

    def setMinimum(self, value):
        super(DoubleSlider, self).setMinimum(value * self._multi)

    def setMaximum(self, value):
        return super(DoubleSlider, self).setMaximum(value * self._multi)

    def setSingleStep(self, value):
        super(DoubleSlider, self).setSingleStep(value * self._multi)

    def singleStep(self):
        return float(super(DoubleSlider, self).singleStep()) / self._multi

    def setValue(self, value):
        super(DoubleSlider, self).setValue(int(value * self._multi))


class AbstractSliderSpinBox(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(int)

    def __init__(self, min=0.0, max=1.0, step=1.0, default=0.0, *args, **kwargs):
        use_slider = kwargs.pop("slider", False)

        super(AbstractSliderSpinBox, self).__init__(*args, **kwargs)

        if isinstance(self, SliderSpinBox):
            self.spin_box = QtWidgets.QSpinBox()
            self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            self.slider.valueChanged.connect(self.spin_box.setValue)
        else:
            self.spin_box = QtWidgets.QDoubleSpinBox()
            self.slider = DoubleSlider(QtCore.Qt.Horizontal)
            self.slider.doubleValueChanged.connect(self.spin_box.setValue)

        self.setMinimum(min)
        self.setMaximum(max)
        self.setSingleStep(step)
        self.setValue(default)

        self.spin_box.valueChanged.connect(self.slider.setValue)
        self.spin_box.valueChanged.connect(self.valueChanged.emit)

        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.slider)
        lay.addWidget(self.spin_box)

        self.set_slider_visible(use_slider)

    def value(self):
        return self.spin_box.value()

    def singleStep(self):
        return self.spin_box.singleStep()

    def setValue(self, value):
        self.spin_box.setValue(value)
        self.slider.setValue(value)

    def setMinimum(self, value):
        self.spin_box.setMinimum(value)
        self.slider.setMinimum(value)

    def setMaximum(self, value):
        self.spin_box.setMaximum(value)
        self.slider.setMaximum(value)

    def setSingleStep(self, value):
        self.spin_box.setSingleStep(value)
        self.slider.setSingleStep(value)
        self.slider.setTickInterval(value)

    def set_slider_visible(self, show):
        self.slider.setVisible(show)


class SliderSpinBox(AbstractSliderSpinBox):
    pass


class SliderDoubleSpinBox(AbstractSliderSpinBox):
    pass


class Number(Arg):

    def create(self):
        # Widget
        if isinstance(self, Float):
            _cls = SliderDoubleSpinBox
        else:
            _cls = SliderSpinBox

        wdg = _cls(slider=self._data["slider"],
                   step=self._data["step"],
                   min=self._data['min'],
                   max=self._data['max'],
                   default=self._data['default'])

        self._write = wdg.setValue
        self._read = wdg.value

        wdg.valueChanged.connect(self.on_changed)

        self.wdg = wdg
        return wdg

    def reset(self):
        self._write(self._data['default'])

    def _update(self):
        super(Number, self)._update()
        self.wdg.setMaximum(self._data["max"])
        self.wdg.setMinimum(self._data["min"])
        self.wdg.setSingleStep(self._data["step"])
        self.wdg.set_slider_visible(self._data["slider"])


class Integer(Number):
    """ Integer argument widget.

        :param default: The default value, defaults to 0
        :type default: int, optional
        :param step: The step, defaults to 0
        :type step: int, optional
        :param min: The minimum value, defaults to -10000
        :type min: int, optional
        :param max: The maximum value, defaults to 10000
        :type max: int, optional
        :param slider: Add a slider if True, defaults to False
        :type slider: bool, optional

        :return: The new instance
        :rtype: :class:`~qargparser.number.Integer` instance
    """
    pass


class Float(Number):
    """ Float argument widget.

        :param default: The default value, defaults to 0.0
        :type default: float, optional
        :param step: The step, defaults to 0.1
        :type step: float, optional
        :param min: The minimum value, defaults to -10000.0
        :type min: float, optional
        :param max: The maximum value, defaults to 10000.0
        :type max: float, optional
        :param slider: Add a slider if True, defaults to False
        :type slider: bool, optional

        :return: The new instance
        :rtype: :class:`~qargparser.number.Float` instance
    """
    pass
