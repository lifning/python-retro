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
PACKET_TYPE_SAVESTATE = 1
INPUT_POLL_SET = struct.Struct('<4sh')


class TilRecorder:
    def __init__(self, emu, destination_file, validation_state=True):
        self.emu = emu
        self.handle = destination_file
        self._validation_state = validation_state
        self._first_poll = True

    def __enter__(self):
        self._wrapped_poll_cb = self.emu._input_poll_wrapper
        self._wrapped_state_cb = self.emu._input_state_wrapper
        self.emu.set_input_poll_cb(self.input_poll)
        self.emu.set_input_state_cb(self.input_state)
        self.handle.write(TIL_MAGIC)
        try:
            self.insert_savestate()
            pass
        except:  # TODO: make core throw something specific...
            print(f'{self.__class__.__name__}: could not save initial state.',
                  file=sys.stderr)
        self._current_poll = collections.OrderedDict()
        self._last_inputs = dict()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.emu.set_input_state_cb(self._wrapped_state_cb)
        self.emu.set_input_poll_cb(self._wrapped_poll_cb)
        self._wrapped_poll_cb = lambda: None
        self._wrapped_state_cb = lambda *args: 0
        self.input_poll()  # write last input packet
        if self._validation_state:
            try:
                self.insert_savestate()
            except:
                print(f'{self.__class__.__name__}: could not save validation state.',
                      file=sys.stderr)

    def insert_savestate(self):
        state = self.emu.serialize()
        self.handle.write(PACKET_HEADER.pack(PACKET_TYPE_SAVESTATE, len(state)))
        self.handle.write(state)

    def input_poll(self):
        if self._first_poll:
            assert not self._current_poll
            self._first_poll = False
        else:
            data = bytearray()
            for key, val in self._current_poll.items():
                if self._last_inputs.get(key, 0) != val:
                    data.extend(INPUT_POLL_SET.pack(key, val))
            self.handle.write(PACKET_HEADER.pack(PACKET_TYPE_INPUT, len(data)))
            self.handle.write(data)
            self._last_inputs.update(self._current_poll)
            self._current_poll.clear()
            self._wrapped_poll_cb()

    def input_state(self, port, device, index, id_):
        val = self._wrapped_state_cb(port, device, index, id_)
        key = bytes((port, device, index, id_))
        if key in self._current_poll:
            if self._current_poll[key] != val:
                print(f'{self.__class__.__name__}: Inconsistent input_state({key}): '
                      f'{val} vs. {self._current_poll[key]}', file=sys.stderr)
        self._current_poll[key] = val
        return val


class TilPlayer:
    def __init__(self, emu, source_file, fix_desyncs=False):
        self.handle = source_file
        self.emu = emu
        self.emu.set_input_poll_cb(self.input_poll)
        self.emu.set_input_state_cb(self.input_state)
        self.finished = False
        self._fix_desyncs = fix_desyncs
        self._inputs = dict()

        self._peek_first_packet()

    def _peek_first_packet(self):
        assert self.handle.read(len(TIL_MAGIC)) == TIL_MAGIC
        pos = self.handle.tell()
        header = self.handle.read(PACKET_HEADER.size)
        packet_type, size = PACKET_HEADER.unpack(header)
        if packet_type == PACKET_TYPE_SAVESTATE:
            self._load_savestate(self.handle.read(size))
        else:
            print(f'{self.__class__.__name__}: No initial savestate present.')
            self.handle.seek(pos)

    def _load_savestate(self, data):
        try:
            self.emu.unserialize(data)
        except:
            print(f'{self.__class__.__name__}: could not unserialize savestate.',
                  file=sys.stderr)

    def _validate_savestate(self, data):
        try:
            if self.emu.serialize() != data:
                print(f'{self.__class__.__name__}: savestate mismatch, possible desync.',
                      file=sys.stderr)
                if self._fix_desyncs:
                    self._load_savestate(data)
        except:
            print(f'{self.__class__.__name__}: error in (un)serialization.')

    def input_poll(self):
        packet_type = None
        while packet_type != PACKET_TYPE_INPUT and not self.finished:
            header = self.handle.read(PACKET_HEADER.size)
            if len(header) < PACKET_HEADER.size:
                self.finished = True
                self._inputs.clear()
                break
            else:
                packet_type, size = PACKET_HEADER.unpack(header)
                data = self.handle.read(size)
                if packet_type == PACKET_TYPE_INPUT:
                    self._inputs.update(INPUT_POLL_SET.iter_unpack(data))
                elif packet_type == PACKET_TYPE_SAVESTATE:
                    self._validate_savestate(data)
                else:
                    print(f'{self.__class__.__name__}: unknown tag: {packet_type}.')

    def input_state(self, port, device, index, id_):
        val = self._inputs.get(bytes((port, device, index, id_)), 0)
        return val
