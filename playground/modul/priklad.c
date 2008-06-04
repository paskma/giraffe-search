/*
  gcc prikladmodule.c -I/usr/include/python2.2 -shared -o prikladmodule.so
  cesta k hlavičkovým souborům je pouze orientační
   */
#include <Python.h>
PyObject* naseFunkce(PyObject* self, PyObject* args)
/* nikoliv void funkce(void), jak možná čekáte */
{
    if(!PyArg_ParseTuple(args,"")) return NULL;
    puts("Ahoj světe!");
    /* Tady bude náš kýžený C kód */
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject* uni(PyObject* self, PyObject* args)
{
	PyObject *a = NULL;
	PyObject *b = NULL;
	PyObject *voa = NULL;
	PyObject *vob = NULL;
	PyObject *r = NULL;
	int sa = -1;
	int sb = -1;
	int ia = 0;
	int ib = 0;
	int va = -1;
	int vb = -1;
	if(!PyArg_ParseTuple(args,"OO", &a, &b)) return NULL;
	//puts("this is uni");
	sa = PyList_GET_SIZE(a);
	sb = PyList_GET_SIZE(b);
	r = PyList_New(0);
	while(ia < sa && ib < sb)
	{
		voa = PyList_GET_ITEM(a, ia);
		vob = PyList_GET_ITEM(b, ib);
		va = (int)PyInt_AsLong(voa);
		vb = (int)PyInt_AsLong(vob);
		if (va < vb)
		{
			PyList_Append(r, voa);
			ia++;
		}
		else if (va > vb)
		{
			PyList_Append(r, vob);
			ib++;
		}
		else if (va == vb)
		{
			PyList_Append(r, voa);
			ia++;
			ib++;
		}
	}
	
	while (ia < sa)
	{
		voa = PyList_GET_ITEM(a, ia);
		PyList_Append(r, voa);
		ia++;
	}
	
	while (ib < sb)
	{
		vob = PyList_GET_ITEM(b, ib);
		PyList_Append(r, vob);
		ib++;
	}
	
	return r;
}

PyObject* otocit(PyObject* self, PyObject* args)
{
    char *s;
    int i;
    PyObject *o=NULL;
 
    if(!PyArg_ParseTuple(args,"s|O",&s,&o)) return NULL;
    puts(s); /* Vypsání povinného parametru */
    
    if(!o || o==Py_None){
        Py_INCREF(Py_None);
        return Py_None;
    }
    if(PyInt_Check(o)){
        i=(int)PyInt_AsLong(o);
        return Py_BuildValue("i", -i);
    }
  /* Pokud to je řetězec */
    if(PyString_Check(o)){
        const char *s;
        char *r, *p;
        int l;
     /* Převedeme ho na C řetězec */
        s=PyString_AsString(o);
     /* Otočíme ho do r   */
        l=strlen(s);
        r=(char *)malloc(l+1);
        p=r+l;
        *p--=0;
        while(p>=r) *p-- = *s++;
     /* Vytvoříme pythonovský řetězec */
        o=Py_BuildValue("s", r);
        free(r);
     /* ... který vrátíme */
        return o;
    }
    PyErr_SetString(PyExc_TypeError, "Mohu otáčet jen nic, int nebo string");
    return NULL;
} /* konec funkce */

PyMethodDef priklad_methods[] = {
    {"funkce", (PyCFunction)naseFunkce, METH_VARARGS, "komentar"},
    {"uni", (PyCFunction)uni, METH_VARARGS, "komentar"},
    {"otocit", (PyCFunction)otocit, METH_VARARGS, "komentar"},
    {NULL, NULL} /* NULLy pro ukončení bloku*/
};

/* v C++ nezapomenout na extern "C" */
void initpriklad(void)
{
    Py_InitModule("priklad", priklad_methods);
}

