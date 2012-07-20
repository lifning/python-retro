from SDL cimport *
from pygame cimport *
from cy_retro cimport *

cdef enum:
	MAP_NONE = 0
	MAP_BTN  = 1
	MAP_AXIS = 2
	MAP_HAT  = 3

cdef struct joymapping:
	int map_type  # see enum above
	int map_index # index within the device of the button/axis/hat
	int extra     # the SDL_HAT_x map for hats.
	              # for axes, +1 or -1 for positive or negative only.

cdef dict maptypes = {
	'a': MAP_AXIS,
	'b': MAP_BTN,
	'h': MAP_HAT,
	'n': MAP_NONE,
}

cdef dict hatdirs = {
	'c': SDL_HAT_CENTERED,
	'u': SDL_HAT_UP,
	'r': SDL_HAT_RIGHT,
	'd': SDL_HAT_DOWN,
	'l': SDL_HAT_LEFT,
	'ru': SDL_HAT_RIGHTUP,
	'ur': SDL_HAT_RIGHTUP,
	'rd': SDL_HAT_RIGHTDOWN,
	'dr': SDL_HAT_RIGHTDOWN,
	'lu': SDL_HAT_LEFTUP,
	'ul': SDL_HAT_LEFTUP,
	'ld': SDL_HAT_LEFTDOWN,
	'dl': SDL_HAT_LEFTDOWN,
}

cdef enum:
	MAX_PLAYERS = 8
	MAX_MAPPINGS = 20

cdef int16_t padcache[MAX_PLAYERS][MAX_MAPPINGS]
cdef joymapping joy_mappings[MAX_PLAYERS][MAX_MAPPINGS]
cdef SDL_Joystick* sdl_joy[MAX_PLAYERS]
cdef unsigned num_players = 0

cdef void sdl_input_poll() nogil:
	global padcache, joy_mappings, sdl_joy, num_players
	cdef int player, m, idx, hat

	SDL_JoystickUpdate()
	for player in xrange(num_players):
		if sdl_joy[player]:
			for m in xrange(MAX_MAPPINGS):
				if joy_mappings[player][m].map_type == MAP_NONE:
					continue
				elif joy_mappings[player][m].map_type == MAP_BTN:
					padcache[player][m] = SDL_JoystickGetButton(
						sdl_joy[player],
						joy_mappings[player][m].map_index
					)
				elif joy_mappings[player][m].map_type == MAP_AXIS:
					padcache[player][m] = SDL_JoystickGetAxis(
						sdl_joy[player],
						joy_mappings[player][m].map_index
					)
					if padcache[player][m] * joy_mappings[player][m].extra < 0:
						padcache[player][m] = 0
				elif joy_mappings[player][m].map_type == MAP_HAT:
					hat = SDL_JoystickGetHat(sdl_joy[player], 0)
					padcache[player][m] = <bool>(hat & joy_mappings[player][m].extra)

cdef int16_t sdl_input_state(unsigned port, unsigned device, unsigned index, unsigned id) nogil:
	global padcache
	return padcache[port][id]


cpdef set_input_poll_joystick(
	EmulatedSystem core,
	# default map suitable for xpad on linux,
	dict mapping = {
		RETRO_DEVICE_ID_JOYPAD_B:      ('b', 0),
		RETRO_DEVICE_ID_JOYPAD_Y:      ('b', 2),
		RETRO_DEVICE_ID_JOYPAD_SELECT: ('b', 6),
		RETRO_DEVICE_ID_JOYPAD_START:  ('b', 7),
		RETRO_DEVICE_ID_JOYPAD_UP:     ('h', 0, 'u'),
		RETRO_DEVICE_ID_JOYPAD_DOWN:   ('h', 0, 'd'),
		RETRO_DEVICE_ID_JOYPAD_LEFT:   ('h', 0, 'l'),
		RETRO_DEVICE_ID_JOYPAD_RIGHT:  ('h', 0, 'r'),
		RETRO_DEVICE_ID_JOYPAD_A:      ('b', 1),
		RETRO_DEVICE_ID_JOYPAD_X:      ('b', 3),
		RETRO_DEVICE_ID_JOYPAD_L:      ('b', 4),
		RETRO_DEVICE_ID_JOYPAD_R:      ('b', 5),
		RETRO_DEVICE_ID_JOYPAD_L2:     ('a', 2, +1),
		RETRO_DEVICE_ID_JOYPAD_R2:     ('a', 5, +1),
		RETRO_DEVICE_ID_JOYPAD_L3:     ('b', 9),
		RETRO_DEVICE_ID_JOYPAD_R3:     ('b', 10),
		(RETRO_DEVICE_INDEX_ANALOG_LEFT, RETRO_DEVICE_ID_ANALOG_X): ('a', 0, 0), 
		(RETRO_DEVICE_INDEX_ANALOG_LEFT, RETRO_DEVICE_ID_ANALOG_Y): ('a', 1, 0),
		(RETRO_DEVICE_INDEX_ANALOG_RIGHT,RETRO_DEVICE_ID_ANALOG_X): ('a', 3, 0),
		(RETRO_DEVICE_INDEX_ANALOG_RIGHT,RETRO_DEVICE_ID_ANALOG_Y): ('a', 4, 0),
	},
	unsigned joyindex = 0,
	unsigned player = 0
):
	global joy_mappings, sdl_joy, num_players

	if player >= MAX_PLAYERS: return

	for k,v in mapping.items():
		if type(k) is tuple:
			stick, axis = k
			k = 16 | (stick<<1) | axis  # hack!
		joy_mappings[player][k].map_type = maptypes[v[0]]
		joy_mappings[player][k].map_index = v[1]
		joy_mappings[player][k].extra = 0
		if len(v) > 2:
			if v[0] == 'h':
				joy_mappings[player][k].extra = hatdirs[v[2]]
			else:
				joy_mappings[player][k].extra = v[2]

	SDL_Init(SDL_INIT_JOYSTICK)
	sdl_joy[player] = SDL_JoystickOpen(joyindex)

	# if this is the first call
	if not num_players:
		core.llw.set_input_poll(sdl_input_poll)
		core.llw.set_input_state(sdl_input_state)

	if num_players <= player:
		num_players = player + 1

