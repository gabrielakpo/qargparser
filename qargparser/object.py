from .arg import BlockArg

class Object(BlockArg):
    """ Object argument widget. 
        You an can add all sub-argument types.

        :param default: The default value, defaults to {}
        :type default: dict, optional
        :param items: the list of child data, defaults to False
        :type items: list of dict, optional

        :return: The new instance
        :rtype: :class:`~qargparser.object.Object` instance
    """

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
        return wdg

    def is_edited(self):
        return (any(child.is_edited() for child in self.get_children()) 
            or super(Object, self).is_edited() if self._data["default"] else False)

    def reset(self):
        for child in self.get_children():
            child.reset()
            child.changed.emit(None)
            if child._data["name"] in self._data["default"]:
                child._data["default"] = self._data["default"][child._data["name"]]     
        self.changed.emit(None)

    def _update(self):
        super(Object, self)._update()
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
        data = super(Object, self).to_data()
        children = self.get_children()
        if children:
            data["items"] = [child.to_data() for child in self.get_children()]
        
        return data

    