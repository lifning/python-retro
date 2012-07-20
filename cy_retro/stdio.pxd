
cdef extern from 'stdio.h':
	int puts(char* s) nogil
	int printf(char *format, ...) nogil
	int snprintf(char *str, size_t size, char *format, ...) nogil

