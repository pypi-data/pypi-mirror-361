#include <Python.h>
#include "../matrix/matrix.hpp"
#include "matrixbinding.hpp"

// --- 1-D type definition ----------------------------------------
static PyMethodDef PyArrayD1_methods[] = {
    {"get", (PyCFunction)PyArrayD1_get, METH_VARARGS,
     "get(index) -> float\n\n"
     "Return the element at position `index` (0-based)."},
     {"set", (PyCFunction)PyArrayD1_set, METH_VARARGS, "set(index)->float\n\n"
     "Change the element at position index"},
    {NULL, NULL, 0, NULL}
};

static PyGetSetDef PyArrayD1_getset[] = {
    {NULL, NULL, NULL, NULL, NULL}
};

static PyTypeObject PyArrayD1Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name      = "pypearl.ArrayD1",
    .tp_basicsize = sizeof(PyArrayD1Object),
    .tp_dealloc   = (destructor)PyArrayD1_dealloc,
    .tp_flags     = Py_TPFLAGS_DEFAULT,
    .tp_doc       = "1-D double array",
    .tp_methods   = PyArrayD1_methods,
    .tp_getset    = PyArrayD1_getset,
    .tp_new       = PyArrayD1_new,
    .tp_init      = (initproc)PyArrayD1_init,
};


static PySequenceMethods PyArrayD1_as_sequence = {
    /* sq_length    */ (lenfunc)         PyArrayD1_length,
    /* sq_concat    */ 0,
    /* sq_repeat    */ 0,
    /* sq_item      */ (ssizeargfunc)    PyArrayD1_item,      // <— adapter
    /* sq_slice     */ 0,
    /* sq_ass_item  */ (ssizeobjargproc) PyArrayD1_ass_item,  // <— adapter
    /* …rest zero… */
};


// --- 2-D type definition ----------------------------------------
static PyMethodDef PyArrayD2_methods[] = {
    
    {NULL, NULL, 0, NULL}
};

static PyGetSetDef PyArrayD2_getset[] = {
    {NULL, NULL, NULL, NULL, NULL}
};

static PyTypeObject PyArrayD2Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name      = "pypearl.ArrayD2",
    .tp_basicsize = sizeof(PyArrayD2Object),
    .tp_dealloc   = (destructor)PyArrayD2_dealloc,
    .tp_flags     = Py_TPFLAGS_DEFAULT,
    .tp_doc       = "2-D double array",
    .tp_methods   = PyArrayD2_methods,
    .tp_getset    = PyArrayD2_getset,
    .tp_new       = PyArrayD2_new,
    .tp_init      = (initproc)PyArrayD2_init,
};

PyObject *add(PyObject *self, PyObject *args){
    int x;
    int y;

    PyArg_ParseTuple(args, "ii", &x, &y);

    return PyLong_FromLong(((long)(x+y)));
};

static PyMethodDef methods[] {
    {"add", add, METH_VARARGS, "Adds two numbers together"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef pypearl = {
    PyModuleDef_HEAD_INIT,
    "pypearl",
    "Documentation: To be implemented, as a safeguard if this is somehow still in place August 2025 or later, please contact me.",
    -1,
    methods
};

PyMODINIT_FUNC
PyInit__pypearl(void)
{
    PyObject *m = PyModule_Create(&pypearl);
    if (!m) return NULL;
    PyArrayD1Type.tp_as_sequence = &PyArrayD1_as_sequence;

    // --- register ArrayD1 ---
    if (PyType_Ready(&PyArrayD1Type) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    Py_INCREF(&PyArrayD1Type);
    PyModule_AddObject(m, "ArrayD1", (PyObject*)&PyArrayD1Type);

    // --- register ArrayD2 ---
    if (PyType_Ready(&PyArrayD2Type) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    Py_INCREF(&PyArrayD2Type);
    PyModule_AddObject(m, "ArrayD2", (PyObject*)&PyArrayD2Type);

    return m;
}

