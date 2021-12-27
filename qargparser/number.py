from .arg import Arg
from .Qt import QtWidgets, QtCore

class DoubleSlider(QtWidgets.QSlider):

    doubleValueChanged = QtCore.Signal(float)

    def __init__(self, orient=QtCore.Qt.Horizontal , parent=None, decimals=3):
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
    default = 0

    def create(self):
        #Widget
        if isinstance(self, Float):
            _cls = SliderDoubleSpinBox
            self._data["step"] = self._data.get("step", 0.1)
        else:
            _cls = SliderSpinBox
            self._data["step"] = self._data.get("step", 1)

        #Min
        if self._data.get("min") is None:
            self._data['min'] = -100000
            
        #Max
        if self._data.get("max") is None:
            self._data['max'] = 100000

        #Slider
        self._data["slider"] = self._data.get("slider", False)

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

class Float(Number):
    pass

class Integer(Number):
    pass
