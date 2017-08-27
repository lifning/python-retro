from sys import argv
import core as C

for l in argv[1:]:
    es = C.EmulatedSystem(l)
    print l, es.get_library_info()['name']
