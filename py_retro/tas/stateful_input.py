import collections

from ..core import EmulatedSystem


def _recursive_defaultdict():
    return collections.defaultdict(_recursive_defaultdict)


class StatefulInputMixin(EmulatedSystem):
    def __init__(self, libpath: str, **kw):
        super().__init__(libpath, **kw)
        self.__storage = _recursive_defaultdict()

    def _input_state(self, port: int, device: int, index: int, id_: int) -> int:
        val = self.__storage[port][device][index][id_]
        if not isinstance(val, int):
            self.set_input_state(port, device, index, id_, 0)
            val = 0
        return val

    def set_input_state(self, port: int, device: int, index: int, id_: int, state: int):
        self.__storage[port][device][index][id_] = state
