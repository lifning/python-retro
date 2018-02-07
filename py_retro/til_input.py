"""
Read input from or record inputs to a "tagged input log" file.

Structure of such a file (all integers are little-endian):
- the string "TIL0"
- packets, repeated until EOF:
    - type: u16. 0 = input poll set, 1 = savestate, more tbd.
    - size: u32. size of the packet in bytes.
    - data

unknown types are currently empty/ignored, but may eventually contain information
pertaining to "retro_controller_info", "ENVIRONMENT_SET_SERIALIZATION_QUIRKS",
the emulator name and version, etc.

a savestate is the result of retro_serialize().
*savestates can occur mid-input-stream,* though we can choose to ignore them.

an input poll set consists of:
- port: u8
- device: u8
- index: u8
- id: u8
- value: s16
which are the args and returns of calls to input_state() between calls to input_poll().
the port, device, index, and id should be considered a unique key in such a packet;
until we discover otherwise, it should be incorrect behavior to have two different values
for the same input_state() query within the same polling period.
it is *not* incorrect behavior to have the same value queried multiple times, but only
the first should be logged to file for size's sake.
if a given (port, device, index, id) key doesn't appear in a poll set, consider its
value to be that of the last one in which it *did* appear, or zero if it hasn't.
(the writer may optimize file size by omitting states that haven't changed.)
"""

import collections
import struct
import sys

TIL_MAGIC = b'TIL0'
PACKET_HEADER = struct.Struct('<HI')
PACKET_TYPE_INPUT = 0
PACKET_TYPE_STATE = 1
INPUT_POLL_SET = struct.Struct('<4sh')


class TILRecorder:
    def __init__(self, emu, destination_filename):
        self.emu = emu
        self.filename = destination_filename

    def __enter__(self):
        self._wrapped_poll_cb = self.emu._input_poll_wrapper
        self._wrapped_state_cb = self.emu._input_state_wrapper
        self.emu.set_input_poll_cb(self.input_poll)
        self.emu.set_input_state_cb(self.input_state)
        self.handle = open(self.filename, 'wb')
        self.handle.write(TIL_MAGIC)
        try:
            self.insert_savestate()
        except Exception:  # TODO: make core throw something specific...
            print('TILRecorder: could not serialize initial state; only writing inputs.',
                  file=sys.stderr)
        self._current_poll = collections.OrderedDict()
        self._last_state = dict()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.emu.set_input_state_cb(self._wrapped_state_cb)
        self.emu.set_input_poll_cb(self._wrapped_poll_cb)
        self._wrapped_poll_cb = lambda: None
        self._wrapped_state_cb = lambda *args: 0
        self.input_poll()  # write last packet
        try:
            self.insert_savestate()
        except:
            print('TILRecorder: could not serialize a validation state.', file=sys.stderr)
        self.handle.close()

    def insert_savestate(self):
        state = self.emu.serialize()
        self.handle.write(PACKET_HEADER.pack(PACKET_TYPE_STATE, len(state)))
        self.handle.write(state)

    def input_poll(self):
        self.handle.write(PACKET_HEADER.pack(PACKET_TYPE_INPUT,
                                             INPUT_POLL_SET.size * len(self._current_poll)))
        for pair in self._current_poll.items():
            if self._last_state.get(pair[0], 0) != pair[1]:
                self.handle.write(INPUT_POLL_SET.pack(*pair))
        self._last_state.update(self._current_poll)
        self._current_poll.clear()
        self._wrapped_poll_cb()

    def input_state(self, port, device, index, id_):
        val = self._wrapped_state_cb(port, device, index, id_)
        key = bytes((port, device, index, id_))
        if key in self._current_poll:
            assert self._current_poll[key] == val, \
                f'Inconsistent input_state({key}): {val} vs. {self._current_poll[key]}'
        self._current_poll[key] = val
        return val


# TODO: implement playback
