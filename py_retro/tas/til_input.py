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
from contextlib import contextmanager

from ..core import EmulatedSystem, SerializationError

TIL_MAGIC = b'TIL0'
PACKET_HEADER = struct.Struct('<HI')
PACKET_TYPE_INPUT = 0
PACKET_TYPE_SAVESTATE = 1
INPUT_POLL_SET = struct.Struct('<4sh')


class TilRecorderInputMixin(EmulatedSystem):
    def __init__(self, libpath, **kw):
        super().__init__(libpath, **kw)
        self.__handle = None
        self.__first_poll = True
        self.__current_poll = collections.OrderedDict()
        self.__last_inputs = dict()

    @contextmanager
    def til_record(self, destination_file, validation_state=True):
        self.__handle = destination_file
        self.__handle.write(TIL_MAGIC)
        try:
            self.til_insert_savestate()
            pass
        except SerializationError:
            print(f'TilRecorder: could not save initial state.',
                  file=sys.stderr)
        self.__first_poll = True
        self.__current_poll = collections.OrderedDict()
        self.__last_inputs = dict()

        yield

        self._input_poll()  # write last input packet
        if validation_state:
            try:
                self.til_insert_savestate()
            except SerializationError:
                print(f'TilRecorder: could not save validation state.',
                      file=sys.stderr)
        self.__handle = None

    def til_insert_savestate(self):
        state = self.serialize()
        self.__handle.write(PACKET_HEADER.pack(PACKET_TYPE_SAVESTATE, len(state)))
        self.__handle.write(state)

    def _input_poll(self):
        if self.__first_poll:
            assert not self.__current_poll
            self.__first_poll = False
        elif self.__handle:
            data = bytearray()
            for key, val in self.__current_poll.items():
                if self.__last_inputs.get(key, 0) != val:
                    data.extend(INPUT_POLL_SET.pack(key, val))
            self.__handle.write(PACKET_HEADER.pack(PACKET_TYPE_INPUT, len(data)))
            self.__handle.write(data)
            self.__last_inputs.update(self.__current_poll)
            self.__current_poll.clear()
        super()._input_poll()

    def _input_state(self, port: int, device: int, index: int, id_: int) -> int:
        val = super()._input_state(port, device, index, id_)
        if self.__handle:
            key = bytes((port, device, index, id_))
            if key in self.__current_poll:
                if self.__current_poll[key] != val:
                    print(f'TilRecorder: Inconsistent input_state({key}): '
                          f'{val} vs. {self.__current_poll[key]}', file=sys.stderr)
            self.__current_poll[key] = val
        return val


class TilPlayerInputMixin(EmulatedSystem):
    def __init__(self, libpath, **kw):
        super().__init__(libpath, **kw)
        self.__handle = None
        self.__fix_desyncs = False
        self.__inputs = dict()

    @contextmanager
    def til_playback(self, source_file, fix_desyncs=False):
        self.__handle = source_file
        self.__fix_desyncs = fix_desyncs
        self.__inputs.clear()

        self.__peek_first_packet()

        yield

        self.__handle = None

    def til_stop(self):
        self.__handle = None

    def __peek_first_packet(self):
        assert self.__handle.read(len(TIL_MAGIC)) == TIL_MAGIC
        pos = self.__handle.tell()
        header = self.__handle.read(PACKET_HEADER.size)
        packet_type, size = PACKET_HEADER.unpack(header)
        if packet_type == PACKET_TYPE_SAVESTATE:
            self.__load_savestate(self.__handle.read(size))
        else:
            print(f'TilPlayer: No initial savestate present.')
            self.__handle.seek(pos)

    def __load_savestate(self, data):
        try:
            self.unserialize(data)
        except SerializationError:
            print(f'TilPlayer: could not unserialize savestate.',
                  file=sys.stderr)

    def __validate_savestate(self, data):
        try:
            if self.serialize() != data:
                print(f'TilPlayer: savestate mismatch, possible desync.',
                      file=sys.stderr)
                if self.__fix_desyncs:
                    self.__load_savestate(data)
        except SerializationError:
            print(f'TilPlayer: error in (un)serialization.')

    def _input_poll(self):
        if not self.__handle:
            super()._input_poll()
            return

        packet_type = None
        while self.__handle and packet_type != PACKET_TYPE_INPUT:
            header = self.__handle.read(PACKET_HEADER.size)
            if len(header) < PACKET_HEADER.size:
                self.__handle = None
                print('TilPlayer: finished playback.')
            else:
                packet_type, size = PACKET_HEADER.unpack(header)
                data = self.__handle.read(size)
                if len(data) < size:
                    print('TilPlayer: incomplete packet, maybe corrupt file?'
                          f'packet type {packet_type}, expected {size} bytes, got {len(data)}.',
                          file=sys.stderr)
                    self.__handle = None
                elif packet_type == PACKET_TYPE_INPUT:
                    self.__inputs.update(INPUT_POLL_SET.iter_unpack(data))
                elif packet_type == PACKET_TYPE_SAVESTATE:
                    self.__validate_savestate(data)
                else:
                    print(f'TilPlayer: unknown tag: {packet_type}.')

    def _input_state(self, port: int, device: int, index: int, id_: int) -> int:
        if not self.__handle:
            return super()._input_state(port, device, index, id_)

        val = self.__inputs.get(bytes((port, device, index, id_)), 0)
        return val
