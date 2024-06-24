class SingletonDecorator:
    """Decorator to make class unique, so each time called same object returned
    """
    all_instances = []

    @staticmethod
    def delete_all():
        for instance in SingletonDecorator.all_instances:
            instance.delete()

    def __init__(self, cls):
        self.cls = cls
        self.instance = None
        self.all_instances.append(self)

    def delete(self):
        del self.instance
        self.instance = None

    def __call__(self, *args, **kwds):
        if self.instance is None:
            self.instance = self.cls(*args, **kwds)

        return self.instance