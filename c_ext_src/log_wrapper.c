#include <stdio.h>
#include <stdarg.h>
#include <Python.h>
#include "libretro.h"

static PyObject* g_log_cb_pyfunc = NULL;

void retro_log_snprintf(enum retro_log_level level, const char* fmt, ...)
{
    char msg[4096];

    va_list args;
    va_start(args, fmt);
    vsnprintf(msg, sizeof(msg), fmt, args);
    va_end(args);

    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    PyObject* py_args = PyTuple_Pack(2, PyLong_FromLong(level), PyBytes_FromString(msg));
    PyObject_CallObject(g_log_cb_pyfunc, py_args);
    PyGILState_Release(gstate);
}

void handle_env_get_log_interface(
    struct retro_log_callback *retro_cb,
    PyObject* wrapped_cb)
{
    if (g_log_cb_pyfunc) {
        Py_DECREF(g_log_cb_pyfunc);
    }
    Py_INCREF(wrapped_cb);

    g_log_cb_pyfunc = wrapped_cb;
    retro_cb->log = retro_log_snprintf;
}

static PyObject* cext_handle_get_log_interface(PyObject* self, PyObject* args)
{
    (void)self;

    struct retro_log_callback* retro_cb;
    PyObject* wrapped_cb;

    if (!PyArg_ParseTuple(args, "lO", &retro_cb, &wrapped_cb)) {
        return NULL;
    }

    handle_env_get_log_interface(retro_cb, wrapped_cb);

    retro_log_snprintf(RETRO_LOG_DEBUG, "Registered log callback.");

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
    if (! PyEval_ThreadsInitialized()) {
        PyEval_InitThreads();
    }
    return PyModule_Create(&cext_module);
}

