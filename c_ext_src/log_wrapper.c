#include <stdio.h>
#include <stdarg.h>
#include <Python.h>
#include "libretro.h"

typedef void (*wrapped_retro_log_print_t)(enum retro_log_level level, const char* msg);

static wrapped_retro_log_print_t g_wrapped_log_cb;

void retro_log_snprintf(enum retro_log_level level, const char* fmt, ...)
{
    char msg[4096];

    va_list args;
    va_start(args, fmt);
    vsnprintf(msg, sizeof(msg), fmt, args);
    va_end(args);

    g_wrapped_log_cb(level, msg);
}

void handle_env_get_log_interface(
    struct retro_log_callback *retro_cb,
    wrapped_retro_log_print_t wrapped_cb)
{
    g_wrapped_log_cb = wrapped_cb;
    retro_cb->log = retro_log_snprintf;
}

static PyObject* cext_handle_get_log_interface(PyObject* self, PyObject* args)
{
    (void)self;

    struct retro_log_callback *retro_cb;
    wrapped_retro_log_print_t wrapped_cb;
    if (!PyArg_ParseTuple(args, "OO", &retro_cb, &wrapped_cb)) {
        return NULL;
    }

    handle_env_get_log_interface(retro_cb, wrapped_cb);

    wrapped_cb(RETRO_LOG_DEBUG, "Registered.");

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef cext_methods[] = {
    {"handle_env_get_log_interface", cext_handle_get_log_interface, METH_VARARGS,
     "Set a callback to be used in retro_log."},
    {NULL, NULL, 0, NULL},
};

static PyModuleDef cext_module = {
    PyModuleDef_HEAD_INIT,
    "cext",
    NULL,
    -1,
    cext_methods,
    0, 0, 0, 0
};

PyMODINIT_FUNC PyInit_cext(void)
{
    return PyModule_Create(&cext_module);
}

