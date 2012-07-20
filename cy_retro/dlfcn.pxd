
cdef extern from 'dlfcn.h':
	void *dlopen(char *filename, int flag)
	char *dlerror()
	void *dlsym(void *handle, char *symbol)
	int dlclose(void *handle)

	unsigned RTLD_LAZY
	unsigned RTLD_NOW
	unsigned RTLD_NOLOAD
	unsigned RTLD_DEEPBIND
	unsigned RTLD_GLOBAL
	unsigned RTLD_NODELETE

