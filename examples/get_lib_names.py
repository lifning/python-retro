from sys import argv
from py_retro import core

for l in argv[1:]:
    es = core.EmulatedSystem(l)
    print(l, es.get_library_info()['name'])
