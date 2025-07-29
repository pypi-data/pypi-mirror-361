class Run:
    def __init__(
            self,
            id,
            name=None,
            interval=60,
    ):
        self._id = id
        self._name = name
        self._interval = interval

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def interval(self):
        return self._interval
