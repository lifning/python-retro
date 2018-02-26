#!/usr/bin/env python3.6
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from py_retro.tas.bsv_input import extract_savestate_from_bsv

if __name__ == '__main__':
    for name in sys.argv[1:]:
        open(f'{name}.state', 'wb').write(
            extract_savestate_from_bsv(open(name, 'rb')))
