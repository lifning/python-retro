import pygame

from ..api.retro_constants import *
from ..core import EmulatedSystem

# xinput mappings because lazy
# TODO: can we steal SDL2's GameController database for reasonable defaults?
g_stick_map = {
    DEVICE_INDEX_ANALOG_LEFT: {
        DEVICE_ID_ANALOG_X: lambda j: 32767 * j.get_axis(0),
        DEVICE_ID_ANALOG_Y: lambda j: 32767 * j.get_axis(1),
    },
    DEVICE_INDEX_ANALOG_RIGHT: {
        DEVICE_ID_ANALOG_X: lambda j: 32767 * j.get_axis(3),
        DEVICE_ID_ANALOG_Y: lambda j: 32767 * j.get_axis(4),
    },
}
g_button_map = {
    DEVICE_ID_JOYPAD_B: lambda j: j.get_button(0),
    DEVICE_ID_JOYPAD_Y: lambda j: j.get_button(2),
    DEVICE_ID_JOYPAD_SELECT: lambda j: j.get_button(6),
    DEVICE_ID_JOYPAD_START: lambda j: j.get_button(7),
    DEVICE_ID_JOYPAD_UP: lambda j: j.get_hat(0)[1] > 0,
    DEVICE_ID_JOYPAD_DOWN: lambda j: j.get_hat(0)[1] < 0,
    DEVICE_ID_JOYPAD_LEFT: lambda j: j.get_hat(0)[0] < 0,
    DEVICE_ID_JOYPAD_RIGHT: lambda j: j.get_hat(0)[0] > 0,
    DEVICE_ID_JOYPAD_A: lambda j: j.get_button(1),
    DEVICE_ID_JOYPAD_X: lambda j: j.get_button(3),
    DEVICE_ID_JOYPAD_L: lambda j: j.get_button(4),
    DEVICE_ID_JOYPAD_R: lambda j: j.get_button(5),
    DEVICE_ID_JOYPAD_L2: lambda j: max(0, 32767 * j.get_axis(2)),
    DEVICE_ID_JOYPAD_R2: lambda j: max(0, 32767 * j.get_axis(5)),
    DEVICE_ID_JOYPAD_L3: lambda j: j.get_button(9),
    DEVICE_ID_JOYPAD_R3: lambda j: j.get_button(10),
}


class PygameJoystickMixin(EmulatedSystem):
    """ This mixin provides inputs from a connected HID gamepad via the pygame.joystick API.
    The mappings it uses are appropriate for an XInput device's button layout.
    """
    def __init__(self, libpath, **kw):
        super().__init__(libpath, **kw)
        self.__joystick = None
        pygame.joystick.init()

        joystick_index = kw.get("joystick", None)
        joystick_count = pygame.joystick.get_count()

        if joystick_index is not None:
            if joystick_index >= joystick_count:
                print(f'Joystick index out of range ({joystick_count} joysticks detected)')
            else:
                self.__joystick = pygame.joystick.Joystick(joystick_index)
                self.__joystick.init()

        self.__joy_states = dict()

    def _input_poll(self):
        if not self.__joystick:
            return
        # TODO: multi support, per-pad configurable mappings.
        port = 0
        device = DEVICE_JOYPAD
        index = 0
        for id_, fn in g_button_map.items():
            key = bytes((port, device, index, id_))
            val = int(fn(self.__joystick))
            self.__joy_states[key] = val
        device = DEVICE_ANALOG
        for index in (DEVICE_INDEX_ANALOG_LEFT, DEVICE_INDEX_ANALOG_RIGHT):
            for id_, fn in g_stick_map[index].items():
                key = bytes((port, device, index, id_))
                val = int(fn(self.__joystick))
                self.__joy_states[key] = val

    def _input_state(self, port, device, index, id_):
        if not self.__joystick:
            return super()._input_state(port, device, index, id_)
        key = bytes((port, device, index, id_))
        val = self.__joy_states.get(key, 0)
        return val
