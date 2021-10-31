import collections

from ..core import EmulatedSystem


def _recursive_defaultdict(depth, last_factory):
    factory = (last_factory if depth <= 1
               else lambda: _recursive_defaultdict(depth - 1, last_factory))
    return collections.defaultdict(factory)


class StatefulInputMixin(EmulatedSystem):
    """ This mixin trivially returns in _input_state(...) whatever value has been set for the given gamepad button by
    `set_input_state(..., state)`, or 0 if there hasn't been a state set for that button.
    This exists as a convenience for programmatically setting the controller state from code that's not necessarily
    a part of this object's class hierarchy."""
    def __init__(self, libpath: str, **kw):
        super().__init__(libpath, **kw)
        self.__storage = _recursive_defaultdict(4, int)

    def _input_state(self, port: int, device: int, index: int, id_: int) -> int:
        val = self.__storage[port][device][index][id_]
        return val

    def set_input_state(self, port: int, device: int, index: int, id_: int, state: int):
        self.__storage[port][device][index][id_] = state
