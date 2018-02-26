import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from py_retro import core

for l in sys.argv[1:]:
    es = core.EmulatedSystem(l)
    print(l, es.get_library_info()['name'])
