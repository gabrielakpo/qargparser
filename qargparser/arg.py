from Qt import QtCore
from . import utils, envs


class ArgData(dict):

    def __init__(self, *args, **kwargs):
        super(ArgData, self).__init__(*args, **kwargs)
        ref = args[0]
        if ref["type"] in envs.DEFAULT_DATA:
            for key in envs.DEFAULT_DATA[ref["type"]]:
                if not key in self or self[key] is None:
                    super(ArgData, self).__setitem__(
                        key, envs.DEFAULT_DATA[ref["type"]][key])

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                super(ArgData, self).__repr__())


class Arg(QtCore.QObject):
    """ Base of argument widgets.

        :param name: The name of the widget, defaults to None
        :type name: str, optional
        :param default: The widget default value. Depends widget type,
                        defaults to None
        :type default: type, optional
        :param description: The description of the widget, defaults to ""
        :type description: str, optional

        :return: The new instance
        :rtype: :class:`~qargparser.array.Array` ,
                :class:`~qargparser.boolean.Boolean`,
                :class:`~qargparser.enum.Enum` ,
                :class:`~qargparser.number.Integer`,
                :class:`~qargparser.number.Float`,
                :class:`~qargparser.object.Object`,
                :class:`~qargparser.path.Path`,
                :class:`~qargparser.string.String`,
                :class:`~qargparser.string.Info`,
                :class:`~qargparser.text.Text`,
                :class:`~qargparser.text.Doc`,
                :class:`~qargparser.text.Python`
                or
                :class:`~qargparser.text.Mel` instance
    """
    changed = QtCore.Signal(tuple)
    reset_requested = QtCore.Signal()

    def __init__(self, name=None, default=None, **kwargs):
        super(Arg, self).__init__(kwargs.pop('parent', None))

        kwargs['name'] = name
        kwargs['type'] = self.__class__.__name__.lower()
        kwargs['default'] = default
        kwargs['description'] = kwargs.get('description', "")

        self.wdg = None
        self._data = ArgData(kwargs)
        self._write = None
        self._read = None

    @property
    def name(self):
        return self._data['name']

    def __repr__(self):
        return '<%s( %s )>' % (self.__class__.__name__,
                               self._data.items())

    def __call__(self, key, default=None):
        return self._data.get(key, default)

    def __eq__(self, other):
        return self._data == other._data

    def create(self):
        pass

    def is_block(self):
        return isinstance(self, BlockArg)

    def set_data(self, name, value):
        """Sets its data with new from a name and a value.

        :param name: The data key
        :type name: str
        :param value: The data value
        :type value: type
        """
        self._data[name] = value
        self._update()

    def update_data(self, data):
        """Updates its data

        :param data: The new data
        :type data: dict
        """
        self._data.update(data)
        self._update()

    def _update(self):
        desc = self._data['description']
        if desc.strip():
            self.wdg.setToolTip(utils.pretty_description(desc))
        self.reset()

    def delete(self):
        """Deletes itself.
        """
        utils.clear_layout(self.wdg.layout())
        self.wdg.deleteLater()

    def get_children(self):
        """Gets all its children.

        :return: The list of its children
        :rtype: list of :class:`~qargparser.array.Array` ,
                :class:`~qargparser.boolean.Boolean`,
                :class:`~qargparser.enum.Enum`,
                :class:`~qargparser.number.Integer`,
                :class:`~qargparser.number.Float`,
                :class:`~qargparser.object.Object`,
                :class:`~qargparser.path.Path`,
                :class:`~qargparser.string.String`,
                :class:`~qargparser.string.Info`,
                :class:`~qargparser.text.Text`,
                :class:`~qargparser.text.Doc`,
                :class:`~qargparser.text.Python`
                or
                :class:`~qargparser.text.Mel` instance
        """
        return []

    def write(self, value):
        """Writes the value

        :param value: The value
        :type value: type
        """
        return self._write(value)

    def read(self):
        """Reads the value.

        :return: The value
        :rtype: type
        """
        return self._read()

    def reset(self):
        """Resets itself
        """
        self.changed.emit(None)

    def is_edited(self):
        return self.read() != self._data["default"]

    def on_changed(self, *args):
        if not args:
            args = (None, )
        self.changed.emit(*args)

    def to_data(self):
        """Gets its data.

        :return: The data
        :rtype: dict
        """
        data = utils.OrderedDict(
            sorted([item for item in self._data.items()
                    if item[1] is not None],
                   key=lambda x: envs.NAMES_ORDER.index(x[0])
                   if x[0] in envs.NAMES_ORDER else 0))
        return data

    def erase_data(self):
        value = self.read()
        self._data["default"] = value
        for child in self.get_children():
            child.erase_data()
        self.reset()

    def overwrite(self):
        self.erase_data()

    def disable(self, disable):
        self.wdg.setDisabled(disable)


class BlockArg(Arg):
    pass
