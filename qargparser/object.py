from .arg import Arg

class Object(Arg):
    def create(self):
        from .argparser import ArgParser
        wdg = ArgParser(description=self._data['description'])

        if 'items' in self._data:
            for _data in self._data.get('items'):
                wdg.add_arg(**_data)

        self._read = wdg._read
        self.wdg = wdg
        return wdg

    def is_edited(self):
        return False

    def add_arg(self, *args, **kwargs):
        return self.wdg.add_arg(*args, **kwargs)