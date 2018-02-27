import collections

from ..core import EmulatedSystem


def _recursive_defaultdict(depth, last_factory):
    factory = (last_factory if depth <= 1
               else lambda: _recursive_defaultdict(depth - 1, last_factory))
    return collections.defaultdict(factory)


class StatefulInputMixin(EmulatedSystem):
    def __init__(self, libpath: str, **kw):
        super().__init__(libpath, **kw)
        self.__storage = _recursive_defaultdict(4, int)

    def _input_state(self, port: int, device: int, index: int, id_: int) -> int:
        val = self.__storage[port][device][index][id_]
        return val

    def set_input_state(self, port: int, device: int, index: int, id_: int, state: int):
        self.__storage[port][device][index][id_] = state
