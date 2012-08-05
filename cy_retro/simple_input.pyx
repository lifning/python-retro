from core cimport *

cdef enum:
	MAX_PLAYERS = 8
	MAX_MAPPINGS = 20

cdef int16_t padcache[MAX_PLAYERS][MAX_MAPPINGS]

cdef void simple_input_poll() nogil:
	pass

cdef int16_t simple_input_state(unsigned port, unsigned device, unsigned index, unsigned id) nogil:
	global padcache
	return padcache[port][id]

cpdef set_input_internal(EmulatedSystem core):
	core.llw.set_input_poll(simple_input_poll)
	core.llw.set_input_state(simple_input_state)

cpdef set_state(unsigned port, unsigned device, unsigned index, unsigned id, int16_t state):
	# currently index and device go unused here...
	padcache[port][id] = state

cpdef set_state_digital(unsigned port, int16_t state):
	global padcache
	cdef unsigned id
	for id in xrange(16):
		padcache[port][id] = state & 1
		state >>= 1

