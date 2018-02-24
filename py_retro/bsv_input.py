"""
Read input from a bsnes movie file (*.bsv)
"""
import struct

from py_retro.core import EmulatedSystem
from py_retro.retro_constants import _retro_constant_lookup

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


class BSV(EmulatedSystem):
    """
    Iterate the contents of the given BSV file.

    filenameOrHandle should either be a string containing the path to a BSV
    file, or a file-like object containing a BSV file.

    Once we've reached the end of the input recorded in the BSV file, we just
    yield an infinite stream of zeroes.
    """

    def __init__(self, libpath, bsv_file, restore=True, expected_cart_crc=None, **kw):
        """
        Sets the BSV file containing the log of input states.

        !!! Also restores the savestate contained in the file !!!
        !!! unless the argument 'restore' is set to False.    !!!
        """
        super().__init__(libpath, **kw)
        if isinstance(bsv_file, str):
            self.handle = open(bsv_file, 'rb')
        else:
            self.handle = bsv_file

        # Read and sanity-check the header.
        magic, serializer_version, cart_crc, state_size = self._extract(HEADER_STRUCT)

        if magic not in (BSV_MAGIC, BSV_SSNES_MAGIC):
            raise CorruptFile(f'File {bsv_file} has bad magic {magic}, expected {BSV_MAGIC}')

        self.serializer_version = serializer_version
        self.cart_crc = cart_crc
        self.state_data = self.handle.read(state_size)

        self.active = True
        self.__debug = dict()

        if expected_cart_crc is not None and self.cart_crc != expected_cart_crc:
            raise CartMismatch(f'Movie is for cart with CRC32 {self.cart_crc}, expected {expected_cart_crc}')

        if restore:
            # retry loop for the multi-threaded ParaLLEl-N64,
            # which refuses to load state while 'initializing'
            for i in range(100):
                # noinspection PyBroadException
                try:
                    self.unserialize(self.state_data)
                    break
                except:
                    if i == 99:
                        raise
                    self.run()

    def _extract(self, s: struct.Struct) -> tuple:
        """
        Read an instance of the given structure from the given file handle.
        """
        return s.unpack(self.handle.read(s.size))

    def _input_state(self, port: int, device: int, index: int, id_: int) -> int:
        if self.active:
            try:
                val = self._extract(RECORD_STRUCT)[0]
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
                self.active = False
        # else...
        return super()._input_state(port, device, index, id_)
