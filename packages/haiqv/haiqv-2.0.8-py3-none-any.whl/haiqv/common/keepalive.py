from abc import ABC, abstractmethod
import time
from threading import Thread


class KeepAlive(ABC):
    def __init__(self):
        self.thd = None
        self.stop_requested = False

    def __del__(self):
        self.stop()

    @abstractmethod
    def task(self):
        pass

    def keepalive(self, interval):
        remain_interval = interval
        while self.stop_requested is False:
            time.sleep(1)
            remain_interval -= 1
            if remain_interval == 0:
                try:
                    self.task()
                except Exception as e:
                    print('keepalive ' + str(e))
                remain_interval = interval

    def start(self, interval):
        if self.thd is not None:
            return
        self.stop_requested = False
        self.thd = Thread(target=self.keepalive, args=(interval,), daemon=True)
        if self.thd:
            self.thd.start()

    def stop(self):
        if self.thd is None:
            return
        self.stop_requested = True
        self.thd.join()
        self.thd = None
