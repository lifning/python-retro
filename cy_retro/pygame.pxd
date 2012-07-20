from SDL cimport *

cdef extern from "Python.h":
	ctypedef struct PyObject

cdef extern from "pygame/pygame.h":

	ctypedef struct GAME_Rect:
		int x, y
		int w, h

	ctypedef struct PyRectObject:
		GAME_Rect r

	ctypedef struct PyCDObject:
		int id

	ctypedef struct PyJoystickObject:
		int id

	cdef struct SubSurface_Data:
		int pixeloffset
		int offsetx, offsety

	ctypedef struct PySurfaceObject:
		SDL_Surface* surf
		SubSurface_Data* subsurface

	ctypedef struct PyEventObject:
		int type

	ctypedef struct PyBufferProxy:
		void *buffer        # Pointer to the buffer of the parent object.
		Py_ssize_t length   # Length of the buffer.

	cdef inline SDL_Surface* PySurface_AsSurface(x)
	cdef inline object PySurface_New(SDL_Surface* surf)

cdef extern from "pygame/mixer.h":
	ctypedef struct PySoundObject:
		Mix_Chunk *chunk
		Uint8 *mem
		PyObject *weakreflist

	ctypedef struct PyChannelObject:
		int chan

	cdef inline Mix_Chunk* PySound_AsChunk(x)
	cdef inline object PySound_New(Mix_Chunk* chunk)

