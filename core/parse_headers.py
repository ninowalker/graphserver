from pycparser import CParser
import re
from pycparser.c_ast import *

FILTERS = [
    re.compile(r'//.*'),
    re.compile(r'\binline\b')
]

START_MULTILINE = re.compile(r'/\*.*')
END_MULTILINE = re.compile(r'.*\*/')
is_multiline = False

def filter_c(s):
    global is_multiline
    for f in FILTERS:
        s = re.sub(f,"",s)
    if START_MULTILINE.search(s):
        if END_MULTILINE.search(s):
            return re.sub(r'/\*.*\*/'," ", s)
        is_multiline = True
        return re.sub(START_MULTILINE, "", s)
    if not is_multiline:
        return s
    if END_MULTILINE.search(s):
        is_multiline = False
        return re.sub(END_MULTILINE,"", s)
    return ""

def read_header(file):
    g = [filter_c(l) for l in open(file).readlines() if not l.startswith("#")]
    return g

decls = read_header("/Users/kolohe/dev/graphserver/core/graphserver.h")

def extract_type(t):
    ptr = 0
    if isinstance(t, (FuncDecl)): # return values or param names
        t = t.type
    while isinstance(t, PtrDecl):
        t = t.type
        ptr += 1
    if isinstance(t, TypeDecl):
        return (ptr, t.type.names[0])
    elif isinstance(t, PtrDecl):
        while isinstance(t.type.type, PtrDecl):
            t = t.type
            ptr += 1
        return (ptr, t.type.type.names[0])
    else:
        return (ptr, t.names[0])

def extract_functions(header):
    content = decls + header
    try:
        t = CParser().parse("".join(content), "")
    except Exception, e:
        print "".join(content)
        fail

    funcs = []
    for d in t.children():
        if not isinstance(d, Decl) or not d.name: 
            continue
        f = dict(name=d.name, argtypes=[], restype=extract_type(d.type))
        
        funcs.append(f)
        if not d.children()[0].args:
            continue
        params = [p for p in d.children()[0].args.params]
        for p in params:
            t = p.children()[0]
            f['argtypes'].append(extract_type(t))
    return funcs

def extract_types(header):
    tree = CParser().parse("".join(decls + header), "gs.h")
    types = []
    for d in tree.children():
        if not isinstance(d.type, TypeDecl):
            continue
        t = dict(name=d.name)
        types.append(t)
        if isinstance(d.type.type, IdentifierType):
            t['type'] = d.type.type.names[0]
        elif isinstance(d.type.type, Enum):
            t['type'] = 'enum'
            t['values'] = [v.name for v in d.type.type.values.children()]
        
        #d.show(attrnames=True)
    return types

def define_ctypes_types(types,classname="DLLTypes"):
    c = []
    c.append("class %s:" % classname)
    for t in types:
        if t.get('values'): # enum
            c.append("%(name)s = c_int" % t)
            c.append("class ENUM_%(name)s:" % t)
            for i, v in enumerate(t['values']):
                c.append("    %s = %d" % (v, i))
            c.append("")
        elif t.get('type'):
            c.append("%(name)s = c_%(type)s" % t)
        else:
            c.append("%(name)s = c_void_p" % t)
    return "\n    ".join(c)

def declare_ctypes_functions(funcs, types, declclass="DLLTypes", dllname="dll"):
    types = dict((t['name'], t) for t in types)
    c = []
    
    def typename(t, refoffset=0):
        ptr, s = t
        #ptr += refoffset
        if s == "void":
            if ptr == 1:
                return "c_void_p"
            if ptr == 2:
                return "POINTER(c_void_p)"
            return "None"
        elif s in types:
            if ptr > 1:
                return "POINTER(%s.%s)" % (declclass,s)
            return "%s.%s" % (declclass,s)
        elif ptr > 0:
            if s == "char":
                return "c_char_p"
            else:
                return "POINTER(c_%s)" % s
        else:
            return "c_" + s

    for f in funcs:
        #c.append(str(f))
        c.append("(%s.%s, %s, [%s])" % (dllname, 
                                                f['name'], 
                                                typename(f['restype'],-1),
                                                ", ".join((typename(p) for p in f['argtypes']))))
    return "declarations = [\\\n    %s\n]" % ",\n    ".join(c)
             

import glob, itertools
funcs = []
for f in itertools.chain(glob.glob("*.h"), glob.glob("*/*.h")):
    if f.endswith("graphserver.h"): 
        continue
    g = read_header(f)
    funcs.extend(extract_functions(g))

types = extract_types(g)
#print "\n".join(map(str,funcs))

print """
from ctypes import *
dll = CDLL("libgraphserver.so") 

def _declare(fun, restype, argtypes):
    fun.argtypes = argtypes
    fun.restype = restype

print c_size_t.in_dll(dll, "EDGEPAYLOAD_ENUM_SIZE")

"""

print define_ctypes_types(types, "LGSTypes")
print declare_ctypes_functions(funcs, types, "LGSTypes", "lgs")

print """
for d in declarations:
    _declare(*d)

"""
