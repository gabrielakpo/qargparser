from .arg import Arg

class Object(Arg):
    def create(self):
        from .argparser import ArgParser
        wdg = ArgParser(description=self._data['description'])
        default = self._data["default"]

        if 'items' in self._data:
            for _data in self._data.get('items')[:]:
                #Update default
                if _data["name"] in default:
                    _data["default"] = default[_data["name"]]

                wdg.add_arg(**_data)

        wdg.changed.connect(self.on_changed)
        self._read = wdg._read
        self.wdg = wdg
        self._data.pop("default")
        return wdg

    def is_edited(self):
        return any(child.is_edited() for child in self.get_children())

    def reset(self):
        for child in self.get_children():
            child.reset()
            child.changed.emit(None)
        self.changed.emit(None)

    def _update(self):
        super(Object, self)._update()
        self.reset()

    def add_arg(self, *args, **kwargs):
        return self.wdg.add_arg(*args, **kwargs)

    def pop_arg(self, *args, **kwargs):
        self.wdg.pop_arg(*args, **kwargs)
        self._update()

    def move_arg(self, *args, **kwargs):
        self.wdg.move_arg(*args, **kwargs)
        self._update()
        self.reset_requested.emit()

    def get_children(self):
        return self.wdg._args

    def to_data(self):
        data = super(Object, self).to_data()
        children = self.get_children()
        if children:
            data["items"] = [child.to_data() for child in self.get_children()]
        
        return data

    