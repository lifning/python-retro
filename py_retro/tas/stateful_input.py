import collections

from ..core import EmulatedSystem


def _recursive_defaultdict():
    return collections.defaultdict(_recursive_defaultdict)


class StatefulInputMixin(EmulatedSystem):
    def __init__(self, libpath, **kw):
        super().__init__(libpath, **kw)
        self.__storage = _recursive_defaultdict()

    def _input_state(self, port: int, device: int, index: int, id_: int) -> int:
        return self.__storage[port][device][index][id_]

    def set_input_state(self, port: int, device: int, index: int, id_: int, state: int):
        self.__storage[port][device][index][id_] = state
