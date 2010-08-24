
import atexit
from ctypes import cdll, CDLL, pydll, PyDLL, CFUNCTYPE
from ctypes import string_at, byref, c_int, c_long, c_float, c_size_t, c_char_p, c_double, c_void_p, py_object
from ctypes import Structure, pointer, cast, POINTER, addressof
from ctypes.util import find_library

import os
import sys

# The libgraphserver.so object:
lgs = None

# Try loading from the source tree. If that doesn't work, fall back to the installed location.
_dlldirs = [os.path.dirname(os.path.abspath(__file__)),
            os.path.dirname(os.path.abspath(__file__)) + '/../../core',
            '/usr/lib',
            '/usr/local/lib']

for _dlldir in _dlldirs:
    _dllpath = os.path.join(_dlldir, 'libgraphserver.so')
    if os.path.exists(_dllpath):
        lgs = PyDLL( _dllpath )
        break

if not lgs:
    raise ImportError("unable to find libgraphserver shared library in the usual locations: %s" % "\n".join(_dlldirs))

class _EmptyClass(object):
    pass

def instantiate(cls):
    """instantiates a class without calling the constructor"""
    ret = _EmptyClass()
    ret.__class__ = cls
    return ret

def cleanup():
    """ Perform any necessary cleanup when the library is unloaded."""
    pass

atexit.register(cleanup)

class CShadow(object):
    """ Base class for all objects that shadow a C structure."""
    @classmethod
    def from_pointer(cls, ptr):
        if ptr is None:
            return None
        
        ret = instantiate(cls)
        ret.soul = ptr
        return ret
        
    def check_destroyed(self):
        if self.soul is None:
            raise Exception("You are trying to use an instance that has been destroyed")

def pycapi(func, rettype, cargs=None):
    """Convenience function for setting arguments and return types."""
    func.restype = rettype
    if cargs is not None:
        func.argtypes = cargs


def caccessor(cfunc, restype, ptrclass=None):
    """Wraps a C data accessor in a python function.
       If a ptrclass is provided, the result will be converted to by the class' from_pointer method."""
    cfunc.restype = restype
    cfunc.argtypes = [c_void_p]
    if ptrclass:
        def prop(self):
            self.check_destroyed()
            ret = cfunc( c_void_p( self.soul ) )
            return ptrclass.from_pointer(ret)
    else:
        def prop(self):
            self.check_destroyed()
            return cfunc( c_void_p( self.soul ) )
    return prop

def cmutator(cfunc, argtype, ptrclass=None):
    """Wraps a C data mutator in a python function.  
       If a ptrclass is provided, the soul of the argument will be used."""
    cfunc.argtypes = [c_void_p, argtype]
    cfunc.restype = None
    if ptrclass:
        def propset(self, arg):
            cfunc( self.soul, arg.soul )
    else:
        def propset(self, arg):
            cfunc( self.soul, arg )
    return propset

def cproperty(cfunc, restype, ptrclass=None, setter=None):
    """if restype is c_null_p, specify a class to convert the pointer into"""
    if not setter:
        return property(caccessor(cfunc, restype, ptrclass))
    return property(caccessor(cfunc, restype, ptrclass),
                    cmutator(setter, restype, ptrclass))

def ccast(func, cls):
    """Wraps a function to casts the result of a function (assumed c_void_p)
       into an object using the class's from_pointer method."""
    func.restype = c_void_p
    def _cast(self, *args):
        return cls.from_pointer(func(*args))
    return _cast
        

# GRAPH API        
pycapi(lgs.gNew, c_void_p)
pycapi(lgs.gDestroy, None, [c_void_p,c_int,c_int])
pycapi(lgs.gAddVertex, c_void_p, [c_void_p, c_char_p])
pycapi(lgs.gAddVertices, c_void_p, [c_void_p, c_void_p, c_int])
pycapi(lgs.gRemoveVertex, c_void_p, [c_void_p, c_char_p, c_int, c_int])
pycapi(lgs.gGetVertex, c_void_p, [c_void_p, c_char_p])
pycapi(lgs.gAddEdge, c_void_p, [c_void_p, c_char_p, c_char_p, c_void_p])
pycapi(lgs.gVertices, c_void_p, [c_void_p, c_void_p])
pycapi(lgs.gShortestPathTree,c_void_p, [c_void_p, c_char_p, c_char_p, c_void_p, c_int, c_long])
pycapi(lgs.gShortestPathTreeRetro,c_void_p, [c_void_p, c_char_p, c_char_p, c_void_p, c_int, c_long])
pycapi(lgs.gSize,c_void_p, [c_long])
pycapi(lgs.sptPathRetro,c_void_p, [c_void_p, c_char_p])
pycapi(lgs.gShortestPathTreeRetro,c_void_p, [c_void_p, c_char_p, c_char_p, c_void_p, c_int, c_long])
pycapi(lgs.gSetVertexEnabled,c_void_p, [c_void_p, c_char_p, c_int])
pycapi(lgs.gSetThicknesses, c_void_p, [c_void_p, c_char_p])

# SERVICE PERIOD API 
pycapi(lgs.spNew, c_void_p, [c_long, c_long, c_int, c_void_p])
pycapi(lgs.spRewind, c_void_p, [c_void_p])
pycapi(lgs.spFastForward, c_void_p, [c_void_p])
pycapi(lgs.spDatumMidnight, c_long, [c_void_p, c_int])
pycapi(lgs.spNormalizeTime, c_long, [c_void_p, c_int, c_long])
pycapi(lgs.spNextPeriod, c_void_p, [c_void_p])
pycapi(lgs.spPreviousPeriod, c_void_p, [c_void_p])
pycapi(lgs.spServiceIds, c_void_p, [c_void_p, c_void_p])

# SERVICE CALENDAR API
pycapi(lgs.scNew, c_void_p, [])
pycapi(lgs.scDestroy, None, [])
pycapi(lgs.scPeriodOfOrAfter, c_void_p, [c_void_p, c_int])
pycapi(lgs.scPeriodOfOrBefore, c_void_p, [c_void_p, c_int])
pycapi(lgs.scAddPeriod, None, [c_void_p, c_void_p])
pycapi(lgs.scGetServiceIdInt, c_int, [c_void_p, c_char_p])
pycapi(lgs.scGetServiceIdString, c_char_p, [c_void_p, c_int])

# TIMEZONE PERIOD API
pycapi(lgs.tzpNew, c_void_p, [c_long, c_long, c_int])
pycapi(lgs.tzpDestroy, None, [c_void_p])
pycapi(lgs.tzpUtcOffset, c_int, [c_void_p])
pycapi(lgs.tzpBeginTime, c_long, [c_void_p])
pycapi(lgs.tzpEndTime, c_long, [c_void_p])
pycapi(lgs.tzpNextPeriod, c_void_p, [c_void_p])
pycapi(lgs.tzpTimeSinceMidnight, c_int, [c_void_p])

# TIMEZONE API
pycapi(lgs.tzNew, c_void_p, [])
pycapi(lgs.tzDestroy, None, [])
pycapi(lgs.tzAddPeriod, None, [c_void_p])
pycapi(lgs.tzPeriodOf, c_void_p, [c_void_p, c_long])
pycapi(lgs.tzUtcOffset, c_int, [c_void_p, c_long])
pycapi(lgs.tzHead, c_void_p, [c_void_p])
pycapi(lgs.tzTimeSinceMidnight, c_int, [c_void_p, c_long])

# STATE API
pycapi(lgs.stateNew, c_void_p, [c_int, c_long])
pycapi(lgs.stateDup, c_void_p)
pycapi(lgs.stateDestroy, None)
pycapi(lgs.stateServicePeriod, c_void_p, [c_int])
pycapi(lgs.stateDangerousSetTripId, c_void_p, [c_void_p, c_char_p])
pycapi(lgs.stateSetServicePeriod, c_void_p, [c_void_p, c_int, c_void_p])

#VERTEX API
pycapi(lgs.vNew, c_void_p, [c_char_p])
pycapi(lgs.vPayload, c_void_p, [c_void_p])
pycapi(lgs.vDestroy, None, [c_void_p,c_int,c_int])
pycapi(lgs.vDegreeIn, c_int, [c_void_p])
pycapi(lgs.vDegreeOut, c_int, [c_void_p])
pycapi(lgs.vGetOutgoingEdgeList, c_void_p, [c_void_p])
pycapi(lgs.vGetIncomingEdgeList, c_void_p, [c_void_p])

# PATH API
pycapi(lgs.pathNew, c_void_p, [c_void_p, c_int, c_int])
pycapi(lgs.pathDestroy, None, [c_void_p])
pycapi(lgs.pathGetEdge, c_void_p, [c_void_p, c_int])
pycapi(lgs.pathGetVertex, c_void_p, [c_void_p, c_int])
pycapi(lgs.pathAddSegment, None, [c_void_p, c_void_p, c_void_p])

# WALK OPTIONS API
pycapi(lgs.woNew, c_void_p, [])
pycapi(lgs.woDestroy, None, [])

#LIST NODE API
pycapi(lgs.liGetData, c_void_p, [c_void_p])
pycapi(lgs.liGetNext, c_void_p, [c_void_p])

#VECTOR API
pycapi(lgs.vecNew, c_void_p, [c_int, c_int])
pycapi(lgs.vecAdd, None, [c_void_p, c_void_p])
pycapi(lgs.vecExpand, c_void_p, [c_void_p, c_int])
pycapi(lgs.vecGet, c_void_p, [c_void_p, c_int])

#EDGE API
pycapi(lgs.eNew, c_void_p, [c_void_p, c_void_p, c_void_p])
pycapi(lgs.eGetFrom, c_void_p, [c_void_p])
pycapi(lgs.eGetTo, c_void_p, [c_void_p])
pycapi(lgs.eGetPayload, c_void_p, [c_void_p])
pycapi(lgs.eWalk, None, [c_void_p, c_void_p, c_int])
pycapi(lgs.eWalkBack, None, [c_void_p, c_void_p, c_int])

#EDGEPAYLOAD API
pycapi(lgs.epGetType, c_int, [c_void_p])
pycapi(lgs.epWalk, c_void_p, [c_void_p, c_void_p, c_void_p])
pycapi(lgs.epWalkBack, c_void_p, [c_void_p, c_void_p, c_void_p])

#LINKNODE API
pycapi(lgs.linkNew, c_void_p)
pycapi(lgs.linkDestroy, None)
pycapi(lgs.linkWalk, c_void_p, [c_void_p, c_void_p])
pycapi(lgs.linkWalkBack, c_void_p, [c_void_p, c_void_p])

#STREET API
pycapi(lgs.streetNew, c_void_p, [c_char_p, c_double])
pycapi(lgs.streetNewElev, c_void_p, [c_char_p, c_double, c_float, c_float])
pycapi(lgs.streetDestroy, None)
pycapi(lgs.streetWalk, c_void_p, [c_void_p, c_void_p])
pycapi(lgs.streetWalkBack, c_void_p, [c_void_p, c_void_p])

#EGRESS API
pycapi(lgs.egressNew, c_void_p, [c_char_p, c_double])
pycapi(lgs.egressDestroy, None)
pycapi(lgs.egressWalk, c_void_p, [c_void_p, c_void_p])
pycapi(lgs.egressWalkBack, c_void_p, [c_void_p, c_void_p])

#WAIT API
pycapi(lgs.waitDestroy, None, [c_void_p])
pycapi(lgs.waitNew, c_void_p, [c_long, c_void_p])
pycapi(lgs.waitWalk, c_void_p, [c_void_p, c_void_p, c_void_p])
pycapi(lgs.waitWalkBack, c_void_p, [c_void_p, c_void_p, c_void_p])
pycapi(lgs.waitWalkBack, c_void_p, [c_void_p, c_void_p, c_void_p])


#HEADWAY API
pycapi(lgs.headwayWalk, c_void_p, [c_void_p, c_void_p, c_int])
pycapi(lgs.headwayWalkBack, c_void_p, [c_void_p, c_void_p, c_int])

#TRIPBOARD API
pycapi(lgs.tbNew, c_void_p, [c_int, c_void_p, c_void_p, c_int])
pycapi(lgs.tbWalk, c_void_p, [c_void_p, c_void_p, c_int])
pycapi(lgs.headwayWalk, c_void_p, [c_void_p, c_void_p, c_int])
pycapi(lgs.tbAddBoarding, c_void_p, [c_void_p, c_char_p, c_int, c_int])
pycapi(lgs.tbGetBoardingTripId, c_char_p, [c_void_p, c_int])
pycapi(lgs.tbGetBoardingDepart, c_int, [c_void_p, c_int])
pycapi(lgs.tbGetBoardingStopSequence, c_int, [c_void_p, c_int])
pycapi(lgs.tbGetBoardingIndexByTripId, c_int, [c_void_p, c_char_p])
pycapi(lgs.tbDestroy, None, [c_void_p])
pycapi(lgs.tbGetNextBoardingIndex, c_int, [c_void_p, c_int])
pycapi(lgs.tbSearchBoardingsList, c_int, [c_void_p, c_int])

#HEADWAY API
pycapi(lgs.headwayNew, c_void_p, [c_int, c_int, c_int, c_int, c_void_p, c_void_p, c_void_p, c_int, c_int])

#HEADWAY BOARD
pycapi(lgs.hbNew, c_void_p, [c_int, c_void_p, c_void_p, c_int, c_void_p, c_int, c_int, c_int])
pycapi(lgs.hbDestroy, None, [c_void_p])

#HEADWAY ALIGHT
pycapi(lgs.haNew, c_void_p, [c_int, c_void_p, c_void_p, c_int, c_void_p, c_int, c_int, c_int])
pycapi(lgs.haDestroy, None, [c_void_p])

#ALIGHT API
pycapi(lgs.alNew, c_void_p, [c_int, c_void_p, c_void_p, c_int])
pycapi(lgs.alDestroy, None, [c_void_p])
pycapi(lgs.alAddAlighting, None, [c_void_p, c_char_p, c_int, c_int])
pycapi(lgs.alGetAlightingTripId, c_char_p, [c_void_p, c_int])
pycapi(lgs.alGetAlightingArrival, c_int, [c_void_p, c_int])
pycapi(lgs.alGetAlightingStopSequence, c_int, [c_void_p, c_int])
pycapi(lgs.alGetAlightingIndexByTripId, c_int, [c_void_p, c_char_p])
pycapi(lgs.alGetLastAlightingIndex, c_int, [c_void_p, c_int])
pycapi(lgs.alSearchAlightingsList, c_int, [c_void_p, c_int])

#ELAPSE TIME API
pycapi(lgs.elapseTimeNew, c_void_p, [c_long])
pycapi(lgs.elapseTimeDestroy, None)
pycapi(lgs.elapseTimeWalk, c_void_p, [c_void_p, c_void_p])
pycapi(lgs.elapseTimeWalkBack, c_void_p, [c_void_p, c_void_p])
pycapi(lgs.elapseTimeGetSeconds, c_long, [c_void_p])

#CROSSING API
pycapi(lgs.crNew, c_void_p, [])
pycapi(lgs.crDestroy, None, [c_void_p])
pycapi(lgs.crAddCrossingTime, c_void_p, [c_void_p, c_char_p, c_int])
pycapi(lgs.crGetCrossingTime, c_int, [c_void_p, c_char_p])
pycapi(lgs.crGetCrossingTimeByIndex, c_int, [c_void_p, c_int])
pycapi(lgs.crGetCrossingTimeTripIdByIndex, c_char_p, [c_void_p, c_int])
pycapi(lgs.crGetSize, c_int, [c_void_p])

#CUSTOM TYPE API
class PayloadMethodTypes:
    """ Enumerates the ctypes of the function pointers."""
    destroy = CFUNCTYPE(c_void_p, py_object)
    walk = CFUNCTYPE(c_void_p, py_object, c_void_p, c_void_p)
    walk_back = CFUNCTYPE(c_void_p, py_object, c_void_p, c_void_p)
    
pycapi(lgs.cpSoul, py_object, [c_void_p])
pycapi(lgs.cpDestroy, None, [c_void_p])
pycapi(lgs.cpNew, c_void_p, [c_void_p, c_void_p])
# args are not specified to allow for None
lgs.defineCustomPayloadType.restype = c_void_p
lgs.undefineCustomPayloadType.restype = None

import traceback, sys
class SafeWrapper(object):
    def __init__(self, lib, name):
        self.lib = lib
        self.called = set([])
        self.name = name

    def __getattr__(self, attr):
        v = getattr(self.lib, attr)
        #if v.argtypes is None:
        #    raise Exception("Calling unsafe method %s" % attr)
        if attr not in self.called:
            #print "%s" % attr
            #sys.stdout.flush()
            #traceback.print_stack(limit=3)
            self.called.add(attr)
        return SafeWrapper(v, name=self.name + "." + attr)

    def __call__(self, *args):
        sys.stderr.write( "-%s %s\n" % (self.lib.restype, self.name))
        sys.stderr.flush()

        return self.lib(*args)

lgs = SafeWrapper(lgs,'lgs')
