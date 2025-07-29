from ..common.keepalive import KeepAlive


class KeepAliveTask(KeepAlive):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(KeepAliveTask, cls).__new__(cls)
            cls.__instance.fn = None
        return cls.__instance

    @classmethod
    def set_fn(cls, fn=None):
        if cls.__instance is None:
            return
        cls.__instance.fn = fn

    @classmethod
    def task(cls):
        if cls.__instance is None:
            return
        if cls.__instance.fn is not None:
            cls.__instance.fn()
