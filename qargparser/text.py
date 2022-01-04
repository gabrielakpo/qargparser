from .Qt import QtWidgets
from .arg import Arg

class Text(Arg):
    """ Text argument widget. 

        :param default: The default value, defaults to ""
        :type default: str, optional

        :return: The new instance
        :rtype: :class:`~qargparser.text.Text` instance
    """
    def create(self):
        wdg = QtWidgets.QPlainTextEdit()
        wdg.setPlainText(self._data['default'])

        self._write = wdg.setPlainText
        self._read = wdg.toPlainText
        wdg.textChanged.connect(self.on_changed)

        if isinstance(self, Doc):
            wdg.setReadOnly(True)

        self.wdg = wdg
        return wdg

    def reset(self):
        self._write(self._data['default'])

class Doc(Text):
    """ Doc argument widget. 
        The value is on read-only mode.

        :param default: The default value, defaults to ""
        :type default: str, optional

        :return: The new instance
        :rtype: :class:`~qargparser.text.Doc` instance
    """

class Code(Text):
    pass

class Python(Code):
    """ Python argument widget. 

        :param default: The default value, defaults to ""
        :type default: str, optional

        :return: The new instance
        :rtype: :class:`~qargparser.text.Python` instance
    """

class Mel(Code):
    """ Mel argument widget. 

        :param default: The default value, defaults to ""
        :type default: str, optional

        :return: The new instance
        :rtype: :class:`~qargparser.text.Mel` instance
    """