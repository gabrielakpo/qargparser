from .arg import BlockArg
from .object import Object
from Qt import QtWidgets


class Tab(BlockArg):
    """ Tab argument widget.
        You an can add all sub-argument types.

        :param default: The default value, defaults to {}
        :type default: dict, optional
        :param items: the list of child data, defaults to False
        :type items: list of dict, optional

        :return: The new instance
        :rtype: :class:`~qargparser.tab.Tab` instance
    """

    def create(self):
        self._args = []

        default = self._data["default"]

        self.wdg = QtWidgets.QTabWidget()
        self.wdg.setMovable(self._data["movable"])
        self.wdg.setTabsClosable(self._data["closable"])

        if 'items' in self._data:
            for _data in self._data.get('items')[:]:
                # Update default
                if _data["name"] in default:
                    _data["default"] = default[_data["name"]]

                self.add_arg(**_data)

        self._read = lambda: {self.wdg.tabText(
            i): c._read() for i, c in enumerate(self._args)}

        return self.wdg

    def is_edited(self):
        return any(child.is_edited() for child in self._args)

    def reset(self):
        self.wdg.setMovable(self._data["movable"])
        self.wdg.setTabsClosable(self._data["closable"])

        for i, child in enumerate(self._args):
            child.reset()
            child.changed.emit(None)
            self.wdg.setTabText(i, child._data["name"])

        self.changed.emit(None)

    def _update(self):
        super(Tab, self)._update()
        self.reset()

    def add_arg(self, name, *args, **kwargs):
        obj = Object(name, *args, **kwargs)
        obj.create()
        self.wdg.addTab(obj.wdg, name)
        self._args.append(obj)
        obj.changed.connect(self.on_changed)
        return obj

    def pop_arg(self, arg):
        idx = self._args.index(arg)
        self._args.remove(arg)
        self.wdg.removeTab(idx)
        arg.delete()
        self._update()

    def move_arg(self, *args, **kwargs):
        # self.wdg.move_arg(*args, **kwargs)
        self._update()
        self.reset_requested.emit()

    def get_children(self):
        return self._args

    def to_data(self):
        data = super(Tab, self).to_data()
        if self._args:
            data["items"] = [child.to_data() for child in self._args]

        return data

    def get_accepted_types(self):
        return ["object"]
