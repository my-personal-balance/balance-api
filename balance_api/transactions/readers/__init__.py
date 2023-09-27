import abc


class BaseReader(metaclass=abc.ABCMeta):
    def __init__(self, filename):
        self.filename = filename
        self._head = None
        self._tail = None

    @abc.abstractmethod
    def parse(self):
        pass

    def set_head(self, head):
        self._head = head

    def set_tail(self, tail):
        self._tail = tail

    @property
    def head(self):
        return self._head

    @property
    def tail(self):
        return self._tail
