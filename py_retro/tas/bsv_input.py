"""
Read input from a bsnes movie file (*.bsv)
"""
import struct
import typing

from ..core import EmulatedSystem
from ..api.retro_constants import _retro_constant_lookup

BSV_MAGIC = b'BSV1'
HEADER_STRUCT = struct.Struct('<4s3I')
RECORD_STRUCT = struct.Struct('<h')

# Due to poorly-worded documentation, some versions of SSNES produce BSV files
# with the magic number reversed. Such files are otherwise fine, so we'll
# accept them.
BSV_SSNES_MAGIC = b'1VSB'


class CorruptFile(Exception):
    pass


class CartMismatch(Exception):
    pass


def extract_savestate_from_bsv(bsv_file: typing.BinaryIO) -> bytes:
    """
    Utility function to extract the savestate data from a .bsv movie.
    """
    magic, version, crc, state_size = HEADER_STRUCT.unpack(bsv_file.read(HEADER_STRUCT.size))
    if magic not in (BSV_MAGIC, BSV_SSNES_MAGIC):
        raise CorruptFile(f'File {bsv_file} has bad magic {magic}, expected {BSV_MAGIC}')
    return bsv_file.read(state_size)


class BsvPlayerInputMixin(EmulatedSystem):
    def __init__(self, libpath, bsv_file, restore=True, expected_cart_crc=None, **kw):
        """
        Sets the BSV file containing the log of input states.

        !!! Also restores the savestate contained in the file !!!
        !!! unless the argument 'restore' is set to False.    !!!
        """
        super().__init__(libpath, **kw)
        self.__handle = bsv_file

        # Read and sanity-check the header.
        magic, serializer_version, cart_crc, state_size = self.__extract(HEADER_STRUCT)

        if magic not in (BSV_MAGIC, BSV_SSNES_MAGIC):
            raise CorruptFile(f'File {bsv_file} has bad magic {magic}, expected {BSV_MAGIC}')

        self.__serializer_version = serializer_version
        self.__cart_crc = cart_crc
        self.__state_data = self.__handle.read(state_size)

        self.__debug = dict()

        if expected_cart_crc is not None and self.__cart_crc != expected_cart_crc:
            raise CartMismatch(f'Movie is for cart with CRC32 {self.__cart_crc}, expected {expected_cart_crc}')

        if restore:
            # retry loop for the multi-threaded ParaLLEl-N64,
            # which refuses to load state while 'initializing'
            for i in range(100):
                # noinspection PyBroadException
                try:
                    self.unserialize(self.__state_data)
                    break
                except:
                    if i == 99:
                        raise
                    self.run()

    def get_savestate(self) -> bytes:
        return self.__state_data

    def __extract(self, s: struct.Struct) -> tuple:
        """
        Read an instance of the given structure from the given file handle.
        """
        return s.unpack(self.__handle.read(s.size))

    def _input_state(self, port: int, device: int, index: int, id_: int) -> int:
        if self.__handle:
            try:
                val = self.__extract(RECORD_STRUCT)[0]
                old = self.__debug.setdefault((port, device, index, id_), val)
                if val != old:
                    self.__debug[(port, device, index, id_)] = val
                    dev_name = _retro_constant_lookup['DEVICE'][device][0]
                    index_name = _retro_constant_lookup['DEVICE_INDEX'][index][0]
                    id_name = [x for x in _retro_constant_lookup['DEVICE_ID'][id_]
                               if x.startswith(dev_name)]
                    print(port, dev_name, index_name, id_name, val)
                return val
            except struct.error:
                # end of the file
                self.__handle = None
        # else...
        return super()._input_state(port, device, index, id_)
