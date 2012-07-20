
cdef extern from 'stdlib.h':
	void free(void* ptr) nogil
	void* malloc(size_t size) nogil
	void* realloc(void* ptr, size_t size) nogil

cdef extern from 'string.h':
	void *memcpy(void *dest, void *src, size_t n) nogil

