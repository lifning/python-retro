IF UNAME_SYSNAME != "Windows":
	cdef extern from 'dlfcn.h' nogil:
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
ELIF UNAME_SYSNAME == "Windows": # for some reason "ELSE" alone didn't cut it?
	cdef extern from "windows.h" nogil:
		ctypedef void* HMODULE
		void *LoadLibrary(char*)
		void *GetProcAddress(void*, char*)
		int FreeLibrary(void*)
		int GetLastError()
	cdef inline void* dlopen(char* filename, int flag) nogil:  return LoadLibrary(filename)
	cdef inline void* dlsym(void* handle, char* symbol) nogil:  return GetProcAddress(<HMODULE>handle, symbol)
	cdef inline int dlclose(void* handle) nogil:  return FreeLibrary(<HMODULE>handle)
	cdef inline char* dlerror() nogil:  return <char*>'Windows DLL error' if GetLastError() else NULL
	cdef enum:
		RTLD_LAZY = 0
		RTLD_NOW = 0
		RTLD_NOLOAD = 0
		RTLD_DEEPBIND = 0
		RTLD_GLOBAL = 0
		RTLD_NODELETE = 0

