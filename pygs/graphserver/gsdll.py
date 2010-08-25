
import atexit
from ctypes import cdll, CDLL, pydll, PyDLL, CFUNCTYPE
from ctypes import string_at, byref, c_int, c_long, c_float, c_size_t, c_char_p, c_double, c_void_p, py_object
from ctypes import c_int8, c_int16, c_int32, c_int64
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

def _declare(fun, restype, argtypes):
    fun.argtypes = argtypes
    fun.restype = restype
    fun.safe = True


class LGSTypes:
    ServiceId = c_int
    EdgePayload = c_void_p
    State = c_void_p
    WalkOptions = c_void_p
    Vertex = c_void_p
    Edge = c_void_p
    ListNode = c_void_p
    Graph = c_void_p
    Path = c_void_p
    Vector = c_void_p
    ServicePeriod = c_void_p
    ServiceCalendar = c_void_p
    Timezone = c_void_p
    TimezonePeriod = c_void_p
    Link = c_void_p
    Street = c_void_p
    Egress = c_void_p
    Wait = c_void_p
    ElapseTime = c_void_p
    Headway = c_void_p
    TripBoard = c_void_p
    HeadwayBoard = c_void_p
    HeadwayAlight = c_void_p
    Crossing = c_void_p
    Alight = c_void_p
    PayloadMethods = c_void_p
    CustomPayload = c_void_p
    edgepayload_t = c_int
    class ENUM_edgepayload_t:
        PL_STREET = 0
        PL_TRIPHOPSCHED_DEPRIC = 1
        PL_TRIPHOP_DEPRIC = 2
        PL_LINK = 3
        PL_EXTERNVALUE = 4
        PL_NONE = 5
        PL_WAIT = 6
        PL_HEADWAY = 7
        PL_TRIPBOARD = 8
        PL_CROSSING = 9
        PL_ALIGHT = 10
        PL_HEADWAYBOARD = 11
        PL_EGRESS = 12
        PL_HEADWAYALIGHT = 13
        PL_ELAPSE_TIME = 14
    
LGSTypes.edgepayload_t = {1:c_int8, 2:c_int16, 4:c_int32, 8:c_int64}[c_size_t.in_dll(lgs, "EDGEPAYLOAD_ENUM_SIZE").value]

declarations = [\
    (lgs.epNew, LGSTypes.EdgePayload, [LGSTypes.edgepayload_t, c_void_p]),
    (lgs.epDestroy, None, [LGSTypes.EdgePayload]),
    (lgs.epGetType, LGSTypes.edgepayload_t, [LGSTypes.EdgePayload]),
    (lgs.epWalk, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.epWalkBack, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.gNew, LGSTypes.Graph, []),
    (lgs.gDestroy, None, [LGSTypes.Graph, c_int, c_int]),
    (lgs.gAddVertex, LGSTypes.Vertex, [LGSTypes.Graph, c_char_p]),
    (lgs.gRemoveVertex, None, [LGSTypes.Graph, c_char_p, c_int, c_int]),
    (lgs.gGetVertex, LGSTypes.Vertex, [LGSTypes.Graph, c_char_p]),
    (lgs.gAddVertices, None, [LGSTypes.Graph, POINTER(c_char_p), c_int]),
    (lgs.gAddEdge, LGSTypes.Edge, [LGSTypes.Graph, c_char_p, c_char_p, LGSTypes.EdgePayload]),
    (lgs.gVertices, POINTER(LGSTypes.Vertex), [LGSTypes.Graph, POINTER(c_long)]),
    (lgs.gShortestPathTree, LGSTypes.Graph, [LGSTypes.Graph, c_char_p, c_char_p, LGSTypes.State, LGSTypes.WalkOptions, c_long]),
    (lgs.gShortestPathTreeRetro, LGSTypes.Graph, [LGSTypes.Graph, c_char_p, c_char_p, LGSTypes.State, LGSTypes.WalkOptions, c_long]),
    (lgs.gShortestPath, LGSTypes.State, [LGSTypes.Graph, c_char_p, c_char_p, LGSTypes.State, c_int, POINTER(c_long), LGSTypes.WalkOptions, c_long]),
    (lgs.gSize, c_long, [LGSTypes.Graph]),
    (lgs.gSetThicknesses, None, [LGSTypes.Graph, c_char_p]),
    (lgs.gSetVertexEnabled, None, [LGSTypes.Graph, c_char_p, c_int]),
    (lgs.sptPathRetro, LGSTypes.Path, [LGSTypes.Graph, c_char_p]),
    (lgs.vNew, LGSTypes.Vertex, [c_char_p]),
    (lgs.vDestroy, None, [LGSTypes.Vertex, c_int, c_int]),
    (lgs.vLink, LGSTypes.Edge, [LGSTypes.Vertex, LGSTypes.Vertex, LGSTypes.EdgePayload]),
    (lgs.vSetParent, LGSTypes.Edge, [LGSTypes.Vertex, LGSTypes.Vertex, LGSTypes.EdgePayload]),
    (lgs.vGetOutgoingEdgeList, LGSTypes.ListNode, [LGSTypes.Vertex]),
    (lgs.vGetIncomingEdgeList, LGSTypes.ListNode, [LGSTypes.Vertex]),
    (lgs.vRemoveOutEdgeRef, None, [LGSTypes.Vertex, LGSTypes.Edge]),
    (lgs.vRemoveInEdgeRef, None, [LGSTypes.Vertex, LGSTypes.Edge]),
    (lgs.vGetLabel, c_char_p, [LGSTypes.Vertex]),
    (lgs.vDegreeOut, c_int, [LGSTypes.Vertex]),
    (lgs.vDegreeIn, c_int, [LGSTypes.Vertex]),
    (lgs.vPayload, LGSTypes.State, [LGSTypes.Vertex]),
    (lgs.eNew, LGSTypes.Edge, [LGSTypes.Vertex, LGSTypes.Vertex, LGSTypes.EdgePayload]),
    (lgs.eDestroy, None, [LGSTypes.Edge, c_int]),
    (lgs.eWalk, LGSTypes.State, [LGSTypes.Edge, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.eWalkBack, LGSTypes.State, [LGSTypes.Edge, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.eGetFrom, LGSTypes.Vertex, [LGSTypes.Edge]),
    (lgs.eGetTo, LGSTypes.Vertex, [LGSTypes.Edge]),
    (lgs.eGetPayload, LGSTypes.EdgePayload, [LGSTypes.Edge]),
    (lgs.eGetEnabled, c_int, [LGSTypes.Edge]),
    (lgs.eSetEnabled, None, [LGSTypes.Edge, c_int]),
    (lgs.eGetThickness, c_long, [LGSTypes.Edge]),
    (lgs.eSetThickness, None, [LGSTypes.Edge, c_long]),
    (lgs.liNew, LGSTypes.ListNode, [LGSTypes.Edge]),
    (lgs.liInsertAfter, None, [LGSTypes.ListNode, LGSTypes.ListNode]),
    (lgs.liRemoveAfter, None, [LGSTypes.ListNode]),
    (lgs.liRemoveRef, None, [LGSTypes.ListNode, LGSTypes.Edge]),
    (lgs.liGetData, LGSTypes.Edge, [LGSTypes.ListNode]),
    (lgs.liGetNext, LGSTypes.ListNode, [LGSTypes.ListNode]),
    (lgs.pathNew, LGSTypes.Path, [LGSTypes.Vertex, c_int, c_int]),
    (lgs.pathDestroy, None, [LGSTypes.Path]),
    (lgs.pathGetVertex, LGSTypes.Vertex, [LGSTypes.Path, c_int]),
    (lgs.pathGetEdge, LGSTypes.Edge, [LGSTypes.Path, c_int]),
    (lgs.pathAddSegment, None, [LGSTypes.Path, LGSTypes.Vertex, LGSTypes.Edge]),
    (lgs.scNew, LGSTypes.ServiceCalendar, []),
    (lgs.scAddServiceId, c_int, [LGSTypes.ServiceCalendar, c_char_p]),
    (lgs.scGetServiceIdString, c_char_p, [LGSTypes.ServiceCalendar, c_int]),
    (lgs.scGetServiceIdInt, c_int, [LGSTypes.ServiceCalendar, c_char_p]),
    (lgs.scAddPeriod, None, [LGSTypes.ServiceCalendar, LGSTypes.ServicePeriod]),
    (lgs.scPeriodOfOrAfter, LGSTypes.ServicePeriod, [LGSTypes.ServiceCalendar, c_long]),
    (lgs.scPeriodOfOrBefore, LGSTypes.ServicePeriod, [LGSTypes.ServiceCalendar, c_long]),
    (lgs.scHead, LGSTypes.ServicePeriod, [LGSTypes.ServiceCalendar]),
    (lgs.scDestroy, None, [LGSTypes.ServiceCalendar]),
    (lgs.spNew, LGSTypes.ServicePeriod, [c_long, c_long, c_int, POINTER(LGSTypes.ServiceId)]),
    (lgs.spDestroyPeriod, None, [LGSTypes.ServicePeriod]),
    (lgs.spPeriodHasServiceId, c_int, [LGSTypes.ServicePeriod, LGSTypes.ServiceId]),
    (lgs.spRewind, LGSTypes.ServicePeriod, [LGSTypes.ServicePeriod]),
    (lgs.spFastForward, LGSTypes.ServicePeriod, [LGSTypes.ServicePeriod]),
    (lgs.spPrint, None, [LGSTypes.ServicePeriod]),
    (lgs.spPrintPeriod, None, [LGSTypes.ServicePeriod]),
    (lgs.spNormalizeTime, c_long, [LGSTypes.ServicePeriod, c_int, c_long]),
    (lgs.spBeginTime, c_long, [LGSTypes.ServicePeriod]),
    (lgs.spEndTime, c_long, [LGSTypes.ServicePeriod]),
    (lgs.spServiceIds, POINTER(LGSTypes.ServiceId), [LGSTypes.ServicePeriod, POINTER(c_int)]),
    (lgs.spNextPeriod, LGSTypes.ServicePeriod, [LGSTypes.ServicePeriod]),
    (lgs.spPreviousPeriod, LGSTypes.ServicePeriod, [LGSTypes.ServicePeriod]),
    (lgs.spDatumMidnight, c_long, [LGSTypes.ServicePeriod, c_int]),
    (lgs.stateNew, LGSTypes.State, [c_int, c_long]),
    (lgs.stateDestroy, None, [LGSTypes.State]),
    (lgs.stateDup, LGSTypes.State, [LGSTypes.State]),
    (lgs.stateGetTime, c_long, [LGSTypes.State]),
    (lgs.stateGetWeight, c_long, [LGSTypes.State]),
    (lgs.stateGetDistWalked, c_double, [LGSTypes.State]),
    (lgs.stateGetNumTransfers, c_int, [LGSTypes.State]),
    (lgs.stateGetPrevEdge, LGSTypes.EdgePayload, [LGSTypes.State]),
    (lgs.stateGetTripId, c_char_p, [LGSTypes.State]),
    (lgs.stateGetStopSequence, c_int, [LGSTypes.State]),
    (lgs.stateGetNumAgencies, c_int, [LGSTypes.State]),
    (lgs.stateServicePeriod, LGSTypes.ServicePeriod, [LGSTypes.State, c_int]),
    (lgs.stateSetServicePeriod, None, [LGSTypes.State, c_int, LGSTypes.ServicePeriod]),
    (lgs.stateSetTime, None, [LGSTypes.State, c_long]),
    (lgs.stateSetWeight, None, [LGSTypes.State, c_long]),
    (lgs.stateSetDistWalked, None, [LGSTypes.State, c_double]),
    (lgs.stateSetNumTransfers, None, [LGSTypes.State, c_int]),
    (lgs.stateDangerousSetTripId, None, [LGSTypes.State, c_char_p]),
    (lgs.stateSetPrevEdge, None, [LGSTypes.State, LGSTypes.EdgePayload]),
    (lgs.tzNew, LGSTypes.Timezone, []),
    (lgs.tzAddPeriod, None, [LGSTypes.Timezone, LGSTypes.TimezonePeriod]),
    (lgs.tzPeriodOf, LGSTypes.TimezonePeriod, [LGSTypes.Timezone, c_long]),
    (lgs.tzUtcOffset, c_int, [LGSTypes.Timezone, c_long]),
    (lgs.tzTimeSinceMidnight, c_int, [LGSTypes.Timezone, c_long]),
    (lgs.tzHead, LGSTypes.TimezonePeriod, [LGSTypes.Timezone]),
    (lgs.tzDestroy, None, [LGSTypes.Timezone]),
    (lgs.tzpNew, LGSTypes.TimezonePeriod, [c_long, c_long, c_int]),
    (lgs.tzpDestroy, None, [LGSTypes.TimezonePeriod]),
    (lgs.tzpUtcOffset, c_int, [LGSTypes.TimezonePeriod]),
    (lgs.tzpTimeSinceMidnight, c_int, [LGSTypes.TimezonePeriod, c_long]),
    (lgs.tzpBeginTime, c_long, [LGSTypes.TimezonePeriod]),
    (lgs.tzpEndTime, c_long, [LGSTypes.TimezonePeriod]),
    (lgs.tzpNextPeriod, LGSTypes.TimezonePeriod, [LGSTypes.TimezonePeriod]),
    (lgs.vecNew, LGSTypes.Vector, [c_int, c_int]),
    (lgs.vecDestroy, None, [LGSTypes.Vector]),
    (lgs.vecAdd, None, [LGSTypes.Vector, c_void_p]),
    (lgs.vecGet, c_void_p, [LGSTypes.Vector, c_int]),
    (lgs.vecExpand, None, [LGSTypes.Vector, c_int]),
    (lgs.woNew, LGSTypes.WalkOptions, []),
    (lgs.woDestroy, None, [LGSTypes.WalkOptions]),
    (lgs.woGetTransferPenalty, c_int, [LGSTypes.WalkOptions]),
    (lgs.woSetTransferPenalty, None, [LGSTypes.WalkOptions, c_int]),
    (lgs.woGetWalkingSpeed, c_float, [LGSTypes.WalkOptions]),
    (lgs.woSetWalkingSpeed, None, [LGSTypes.WalkOptions, c_float]),
    (lgs.woGetWalkingReluctance, c_float, [LGSTypes.WalkOptions]),
    (lgs.woSetWalkingReluctance, None, [LGSTypes.WalkOptions, c_float]),
    (lgs.woGetMaxWalk, c_int, [LGSTypes.WalkOptions]),
    (lgs.woSetMaxWalk, None, [LGSTypes.WalkOptions, c_int]),
    (lgs.woGetWalkingOverage, c_float, [LGSTypes.WalkOptions]),
    (lgs.woSetWalkingOverage, None, [LGSTypes.WalkOptions, c_float]),
    (lgs.woGetTurnPenalty, c_int, [LGSTypes.WalkOptions]),
    (lgs.woSetTurnPenalty, None, [LGSTypes.WalkOptions, c_int]),
    (lgs.woGetUphillSlowness, c_float, [LGSTypes.WalkOptions]),
    (lgs.woSetUphillSlowness, None, [LGSTypes.WalkOptions, c_float]),
    (lgs.woGetDownhillFastness, c_float, [LGSTypes.WalkOptions]),
    (lgs.woSetDownhillFastness, None, [LGSTypes.WalkOptions, c_float]),
    (lgs.woGetHillReluctance, c_float, [LGSTypes.WalkOptions]),
    (lgs.woSetHillReluctance, None, [LGSTypes.WalkOptions, c_float]),
    (lgs.woGetMaxWalk, c_int, [LGSTypes.WalkOptions]),
    (lgs.woSetMaxWalk, None, [LGSTypes.WalkOptions, c_int]),
    (lgs.woGetWalkingOverage, c_float, [LGSTypes.WalkOptions]),
    (lgs.woSetWalkingOverage, None, [LGSTypes.WalkOptions, c_float]),
    (lgs.woGetTurnPenalty, c_int, [LGSTypes.WalkOptions]),
    (lgs.woSetTurnPenalty, None, [LGSTypes.WalkOptions, c_int]),
    (lgs.alNew, LGSTypes.Alight, [LGSTypes.ServiceId, LGSTypes.ServiceCalendar, LGSTypes.Timezone, c_int]),
    (lgs.alDestroy, None, [LGSTypes.Alight]),
    (lgs.alGetCalendar, LGSTypes.ServiceCalendar, [LGSTypes.Alight]),
    (lgs.alGetTimezone, LGSTypes.Timezone, [LGSTypes.Alight]),
    (lgs.alGetAgency, c_int, [LGSTypes.Alight]),
    (lgs.alGetServiceId, LGSTypes.ServiceId, [LGSTypes.Alight]),
    (lgs.alGetNumAlightings, c_int, [LGSTypes.Alight]),
    (lgs.alAddAlighting, None, [LGSTypes.Alight, c_char_p, c_int, c_int]),
    (lgs.alGetAlightingTripId, c_char_p, [LGSTypes.Alight, c_int]),
    (lgs.alGetAlightingArrival, c_int, [LGSTypes.Alight, c_int]),
    (lgs.alGetAlightingStopSequence, c_int, [LGSTypes.Alight, c_int]),
    (lgs.alSearchAlightingsList, c_int, [LGSTypes.Alight, c_int]),
    (lgs.alGetLastAlightingIndex, c_int, [LGSTypes.Alight, c_int]),
    (lgs.alGetOverage, c_int, [LGSTypes.Alight]),
    (lgs.alGetAlightingIndexByTripId, c_int, [LGSTypes.Alight, c_char_p]),
    (lgs.alWalk, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.alWalkBack, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.crNew, LGSTypes.Crossing, []),
    (lgs.crDestroy, None, [LGSTypes.Crossing]),
    (lgs.crAddCrossingTime, None, [LGSTypes.Crossing, c_char_p, c_int]),
    (lgs.crGetCrossingTime, c_int, [LGSTypes.Crossing, c_char_p]),
    (lgs.crGetCrossingTimeTripIdByIndex, c_char_p, [LGSTypes.Crossing, c_int]),
    (lgs.crGetCrossingTimeByIndex, c_int, [LGSTypes.Crossing, c_int]),
    (lgs.crGetSize, c_int, [LGSTypes.Crossing]),
    (lgs.crWalk, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.crWalkBack, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
#    (lgs.defineCustomPayloadType, LGSTypes.PayloadMethods, [CFUNCTYPE(c_void_p, c_void_p), CFUNCTYPE(LGSTypes.State, c_void_p, LGSTypes.State, LGSTypes.WalkOptions), CFUNCTYPE(LGSTypes.State, c_void_p, LGSTypes.State, LGSTypes.WalkOptions)]),
    (lgs.defineCustomPayloadType, LGSTypes.PayloadMethods, None),
    (lgs.undefineCustomPayloadType, None, [LGSTypes.PayloadMethods]),
    (lgs.cpNew, LGSTypes.CustomPayload, [py_object, LGSTypes.PayloadMethods]),
    (lgs.cpDestroy, None, [LGSTypes.CustomPayload]),
    (lgs.cpSoul, c_void_p, [LGSTypes.CustomPayload]),
    (lgs.cpMethods, LGSTypes.PayloadMethods, [LGSTypes.CustomPayload]),
    (lgs.cpWalk, LGSTypes.State, [LGSTypes.CustomPayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.cpWalkBack, LGSTypes.State, [LGSTypes.CustomPayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.egressNew, LGSTypes.Egress, [c_char_p, c_double]),
    (lgs.egressDestroy, None, [LGSTypes.Egress]),
    (lgs.egressWalk, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.egressWalkBack, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.egressGetName, c_char_p, [LGSTypes.Egress]),
    (lgs.egressGetLength, c_double, [LGSTypes.Egress]),
    (lgs.elapse_time_and_service_period_forward, None, [LGSTypes.State, LGSTypes.State, c_long]),
    (lgs.elapse_time_and_service_period_backward, None, [LGSTypes.State, LGSTypes.State, c_long]),
    (lgs.elapseTimeNew, LGSTypes.ElapseTime, [c_long]),
    (lgs.elapseTimeDestroy, None, [LGSTypes.ElapseTime]),
    (lgs.elapseTimeWalk, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.elapseTimeWalkBack, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.elapseTimeGetSeconds, c_long, [LGSTypes.ElapseTime]),
    (lgs.headwayNew, LGSTypes.Headway, [c_int, c_int, c_int, c_int, c_char_p, LGSTypes.ServiceCalendar, LGSTypes.Timezone, c_int, LGSTypes.ServiceId]),
    (lgs.headwayDestroy, None, [LGSTypes.Headway]),
    (lgs.headwayWalk, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.headwayWalkBack, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.headwayBeginTime, c_int, [LGSTypes.Headway]),
    (lgs.headwayEndTime, c_int, [LGSTypes.Headway]),
    (lgs.headwayWaitPeriod, c_int, [LGSTypes.Headway]),
    (lgs.headwayTransit, c_int, [LGSTypes.Headway]),
    (lgs.headwayTripId, c_char_p, [LGSTypes.Headway]),
    (lgs.headwayCalendar, LGSTypes.ServiceCalendar, [LGSTypes.Headway]),
    (lgs.headwayTimezone, LGSTypes.Timezone, [LGSTypes.Headway]),
    (lgs.headwayAgency, c_int, [LGSTypes.Headway]),
    (lgs.headwayServiceId, LGSTypes.ServiceId, [LGSTypes.Headway]),
    (lgs.haNew, LGSTypes.HeadwayAlight, [LGSTypes.ServiceId, LGSTypes.ServiceCalendar, LGSTypes.Timezone, c_int, c_char_p, c_int, c_int, c_int]),
    (lgs.haDestroy, None, [LGSTypes.HeadwayAlight]),
    (lgs.haGetCalendar, LGSTypes.ServiceCalendar, [LGSTypes.HeadwayAlight]),
    (lgs.haGetTimezone, LGSTypes.Timezone, [LGSTypes.HeadwayAlight]),
    (lgs.haGetAgency, c_int, [LGSTypes.HeadwayAlight]),
    (lgs.haGetServiceId, LGSTypes.ServiceId, [LGSTypes.HeadwayAlight]),
    (lgs.haGetTripId, c_char_p, [LGSTypes.HeadwayAlight]),
    (lgs.haGetStartTime, c_int, [LGSTypes.HeadwayAlight]),
    (lgs.haGetEndTime, c_int, [LGSTypes.HeadwayAlight]),
    (lgs.haGetHeadwaySecs, c_int, [LGSTypes.HeadwayAlight]),
    (lgs.haWalk, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.haWalkBack, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.hbNew, LGSTypes.HeadwayBoard, [LGSTypes.ServiceId, LGSTypes.ServiceCalendar, LGSTypes.Timezone, c_int, c_char_p, c_int, c_int, c_int]),
    (lgs.hbDestroy, None, [LGSTypes.HeadwayBoard]),
    (lgs.hbGetCalendar, LGSTypes.ServiceCalendar, [LGSTypes.HeadwayBoard]),
    (lgs.hbGetTimezone, LGSTypes.Timezone, [LGSTypes.HeadwayBoard]),
    (lgs.hbGetAgency, c_int, [LGSTypes.HeadwayBoard]),
    (lgs.hbGetServiceId, LGSTypes.ServiceId, [LGSTypes.HeadwayBoard]),
    (lgs.hbGetTripId, c_char_p, [LGSTypes.HeadwayBoard]),
    (lgs.hbGetStartTime, c_int, [LGSTypes.HeadwayBoard]),
    (lgs.hbGetEndTime, c_int, [LGSTypes.HeadwayBoard]),
    (lgs.hbGetHeadwaySecs, c_int, [LGSTypes.HeadwayBoard]),
    (lgs.hbWalk, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.hbWalkBack, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.linkNew, LGSTypes.Link, []),
    (lgs.linkDestroy, None, [LGSTypes.Link]),
    (lgs.linkWalk, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.linkWalkBack, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.linkGetName, c_char_p, [LGSTypes.Link]),
    (lgs.streetNew, LGSTypes.Street, [c_char_p, c_double]),
    (lgs.streetNewElev, LGSTypes.Street, [c_char_p, c_double, c_float, c_float]),
    (lgs.streetDestroy, None, [LGSTypes.Street]),
    (lgs.streetWalk, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.streetWalkBack, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.streetGetName, c_char_p, [LGSTypes.Street]),
    (lgs.streetGetLength, c_double, [LGSTypes.Street]),
    (lgs.streetGetRise, c_float, [LGSTypes.Street]),
    (lgs.streetGetFall, c_float, [LGSTypes.Street]),
    (lgs.streetSetRise, None, [LGSTypes.Street, c_float]),
    (lgs.streetSetFall, None, [LGSTypes.Street, c_float]),
    (lgs.streetGetWay, c_long, [LGSTypes.Street]),
    (lgs.streetSetWay, None, [LGSTypes.Street, c_long]),
    (lgs.streetSetSlog, None, [LGSTypes.Street, c_float]),
    (lgs.streetGetSlog, c_float, [LGSTypes.Street]),
    (lgs.tbNew, LGSTypes.TripBoard, [LGSTypes.ServiceId, LGSTypes.ServiceCalendar, LGSTypes.Timezone, c_int]),
    (lgs.tbDestroy, None, [LGSTypes.TripBoard]),
    (lgs.tbGetCalendar, LGSTypes.ServiceCalendar, [LGSTypes.TripBoard]),
    (lgs.tbGetTimezone, LGSTypes.Timezone, [LGSTypes.TripBoard]),
    (lgs.tbGetAgency, c_int, [LGSTypes.TripBoard]),
    (lgs.tbGetServiceId, LGSTypes.ServiceId, [LGSTypes.TripBoard]),
    (lgs.tbGetNumBoardings, c_int, [LGSTypes.TripBoard]),
    (lgs.tbAddBoarding, None, [LGSTypes.TripBoard, c_char_p, c_int, c_int]),
    (lgs.tbGetBoardingTripId, c_char_p, [LGSTypes.TripBoard, c_int]),
    (lgs.tbGetBoardingDepart, c_int, [LGSTypes.TripBoard, c_int]),
    (lgs.tbGetBoardingStopSequence, c_int, [LGSTypes.TripBoard, c_int]),
    (lgs.tbSearchBoardingsList, c_int, [LGSTypes.TripBoard, c_int]),
    (lgs.tbGetNextBoardingIndex, c_int, [LGSTypes.TripBoard, c_int]),
    (lgs.tbGetOverage, c_int, [LGSTypes.TripBoard]),
    (lgs.tbWalk, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.tbWalkBack, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.tbGetBoardingIndexByTripId, c_int, [LGSTypes.TripBoard, c_char_p]),
    (lgs.waitNew, LGSTypes.Wait, [c_long, LGSTypes.Timezone]),
    (lgs.waitDestroy, None, [LGSTypes.Wait]),
    (lgs.waitWalk, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.waitWalkBack, LGSTypes.State, [LGSTypes.EdgePayload, LGSTypes.State, LGSTypes.WalkOptions]),
    (lgs.waitGetEnd, c_long, [LGSTypes.Wait]),
    (lgs.waitGetTimezone, LGSTypes.Timezone, [LGSTypes.Wait])
]

for d in declarations:
    _declare(*d)

def caccessor(cfunc, restype, ptrclass=None):
    """Wraps a C data accessor in a python function.
       If a ptrclass is provided, the result will be converted to by the class' from_pointer method."""
    #cfunc.restype = restype
    #cfunc.argtypes = [c_void_p]
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
    #cfunc.argtypes = [c_void_p, argtype]
    #cfunc.restype = None
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
# pycapi(lgs.gNew, c_void_p)
# pycapi(lgs.gDestroy, None, [c_void_p,c_int,c_int])
# pycapi(lgs.gAddVertex, c_void_p, [c_void_p, c_char_p])
# pycapi(lgs.gAddVertices, c_void_p, [c_void_p, c_void_p, c_int])
# pycapi(lgs.gRemoveVertex, c_void_p, [c_void_p, c_char_p, c_int, c_int])
# pycapi(lgs.gGetVertex, c_void_p, [c_void_p, c_char_p])
# pycapi(lgs.gAddEdge, c_void_p, [c_void_p, c_char_p, c_char_p, c_void_p])
# pycapi(lgs.gVertices, c_void_p, [c_void_p, c_void_p])
# pycapi(lgs.gShortestPathTree,c_void_p, [c_void_p, c_char_p, c_char_p, c_void_p, c_int, c_long])
# pycapi(lgs.gShortestPathTreeRetro,c_void_p, [c_void_p, c_char_p, c_char_p, c_void_p, c_int, c_long])
# pycapi(lgs.gSize,c_void_p, [c_long])
# pycapi(lgs.sptPathRetro,c_void_p, [c_void_p, c_char_p])
# pycapi(lgs.gShortestPathTreeRetro,c_void_p, [c_void_p, c_char_p, c_char_p, c_void_p, c_int, c_long])
# pycapi(lgs.gSetVertexEnabled,c_void_p, [c_void_p, c_char_p, c_int])
# pycapi(lgs.gSetThicknesses, c_void_p, [c_void_p, c_char_p])

# SERVICE PERIOD API 
# pycapi(lgs.spNew, c_void_p, [c_long, c_long, c_int, c_void_p])
# pycapi(lgs.spRewind, c_void_p, [c_void_p])
# pycapi(lgs.spFastForward, c_void_p, [c_void_p])
# pycapi(lgs.spDatumMidnight, c_long, [c_void_p, c_int])
# pycapi(lgs.spNormalizeTime, c_long, [c_void_p, c_int, c_long])
# pycapi(lgs.spNextPeriod, c_void_p, [c_void_p])
# pycapi(lgs.spPreviousPeriod, c_void_p, [c_void_p])
# pycapi(lgs.spServiceIds, c_void_p, [c_void_p, c_void_p])

# SERVICE CALENDAR API
# pycapi(lgs.scNew, c_void_p, [])
# pycapi(lgs.scDestroy, None, [])
# pycapi(lgs.scPeriodOfOrAfter, c_void_p, [c_void_p, c_int])
# pycapi(lgs.scPeriodOfOrBefore, c_void_p, [c_void_p, c_int])
# pycapi(lgs.scAddPeriod, None, [c_void_p, c_void_p])
# pycapi(lgs.scGetServiceIdInt, c_int, [c_void_p, c_char_p])
# pycapi(lgs.scGetServiceIdString, c_char_p, [c_void_p, c_int])

# TIMEZONE PERIOD API
# pycapi(lgs.tzpNew, c_void_p, [c_long, c_long, c_int])
# pycapi(lgs.tzpDestroy, None, [c_void_p])
# pycapi(lgs.tzpUtcOffset, c_int, [c_void_p])
# pycapi(lgs.tzpBeginTime, c_long, [c_void_p])
# pycapi(lgs.tzpEndTime, c_long, [c_void_p])
# pycapi(lgs.tzpNextPeriod, c_void_p, [c_void_p])
# pycapi(lgs.tzpTimeSinceMidnight, c_int, [c_void_p])

# # TIMEZONE API
# pycapi(lgs.tzNew, c_void_p, [])
# pycapi(lgs.tzDestroy, None, [])
# pycapi(lgs.tzAddPeriod, None, [c_void_p])
# pycapi(lgs.tzPeriodOf, c_void_p, [c_void_p, c_long])
# pycapi(lgs.tzUtcOffset, c_int, [c_void_p, c_long])
# pycapi(lgs.tzHead, c_void_p, [c_void_p])
# pycapi(lgs.tzTimeSinceMidnight, c_int, [c_void_p, c_long])

# # STATE API
# pycapi(lgs.stateNew, c_void_p, [c_int, c_long])
# pycapi(lgs.stateDup, c_void_p)
# pycapi(lgs.stateDestroy, None)
# pycapi(lgs.stateServicePeriod, c_void_p, [c_int])
# pycapi(lgs.stateDangerousSetTripId, c_void_p, [c_void_p, c_char_p])
# pycapi(lgs.stateSetServicePeriod, c_void_p, [c_void_p, c_int, c_void_p])

# #VERTEX API
# pycapi(lgs.vNew, c_void_p, [c_char_p])
# pycapi(lgs.vPayload, c_void_p, [c_void_p])
# pycapi(lgs.vDestroy, None, [c_void_p,c_int,c_int])
# pycapi(lgs.vDegreeIn, c_int, [c_void_p])
# pycapi(lgs.vDegreeOut, c_int, [c_void_p])
# pycapi(lgs.vGetOutgoingEdgeList, c_void_p, [c_void_p])
# pycapi(lgs.vGetIncomingEdgeList, c_void_p, [c_void_p])

# # PATH API
# pycapi(lgs.pathNew, c_void_p, [c_void_p, c_int, c_int])
# pycapi(lgs.pathDestroy, None, [c_void_p])
# pycapi(lgs.pathGetEdge, c_void_p, [c_void_p, c_int])
# pycapi(lgs.pathGetVertex, c_void_p, [c_void_p, c_int])
# pycapi(lgs.pathAddSegment, None, [c_void_p, c_void_p, c_void_p])

# # WALK OPTIONS API
# pycapi(lgs.woNew, c_void_p, [])
# pycapi(lgs.woDestroy, None, [])

# #LIST NODE API
# pycapi(lgs.liGetData, c_void_p, [c_void_p])
# pycapi(lgs.liGetNext, c_void_p, [c_void_p])

# #VECTOR API
# pycapi(lgs.vecNew, c_void_p, [c_int, c_int])
# pycapi(lgs.vecAdd, None, [c_void_p, c_void_p])
# pycapi(lgs.vecExpand, c_void_p, [c_void_p, c_int])
# pycapi(lgs.vecGet, c_void_p, [c_void_p, c_int])

# #EDGE API
# pycapi(lgs.eNew, c_void_p, [c_void_p, c_void_p, c_void_p])
# pycapi(lgs.eGetFrom, c_void_p, [c_void_p])
# pycapi(lgs.eGetTo, c_void_p, [c_void_p])
# pycapi(lgs.eGetPayload, c_void_p, [c_void_p])
# pycapi(lgs.eWalk, None, [c_void_p, c_void_p, c_int])
# pycapi(lgs.eWalkBack, None, [c_void_p, c_void_p, c_int])

# #EDGEPAYLOAD API
# pycapi(lgs.epGetType, c_int, [c_void_p])
# pycapi(lgs.epWalk, c_void_p, [c_void_p, c_void_p, c_void_p])
# pycapi(lgs.epWalkBack, c_void_p, [c_void_p, c_void_p, c_void_p])

# #LINKNODE API
# pycapi(lgs.linkNew, c_void_p)
# pycapi(lgs.linkDestroy, None)
# pycapi(lgs.linkWalk, c_void_p, [c_void_p, c_void_p])
# pycapi(lgs.linkWalkBack, c_void_p, [c_void_p, c_void_p])

# #STREET API
# pycapi(lgs.streetNew, c_void_p, [c_char_p, c_double])
# pycapi(lgs.streetNewElev, c_void_p, [c_char_p, c_double, c_float, c_float])
# pycapi(lgs.streetDestroy, None)
# pycapi(lgs.streetWalk, c_void_p, [c_void_p, c_void_p])
# pycapi(lgs.streetWalkBack, c_void_p, [c_void_p, c_void_p])

# #EGRESS API
# pycapi(lgs.egressNew, c_void_p, [c_char_p, c_double])
# pycapi(lgs.egressDestroy, None)
# pycapi(lgs.egressWalk, c_void_p, [c_void_p, c_void_p])
# pycapi(lgs.egressWalkBack, c_void_p, [c_void_p, c_void_p])

# #WAIT API
# pycapi(lgs.waitDestroy, None, [c_void_p])
# pycapi(lgs.waitNew, c_void_p, [c_long, c_void_p])
# pycapi(lgs.waitWalk, c_void_p, [c_void_p, c_void_p, c_void_p])
# pycapi(lgs.waitWalkBack, c_void_p, [c_void_p, c_void_p, c_void_p])
# pycapi(lgs.waitWalkBack, c_void_p, [c_void_p, c_void_p, c_void_p])


# #HEADWAY API
# pycapi(lgs.headwayWalk, c_void_p, [c_void_p, c_void_p, c_int])
# pycapi(lgs.headwayWalkBack, c_void_p, [c_void_p, c_void_p, c_int])

# #TRIPBOARD API
# pycapi(lgs.tbNew, c_void_p, [c_int, c_void_p, c_void_p, c_int])
# pycapi(lgs.tbWalk, c_void_p, [c_void_p, c_void_p, c_int])
# pycapi(lgs.headwayWalk, c_void_p, [c_void_p, c_void_p, c_int])
# pycapi(lgs.tbAddBoarding, c_void_p, [c_void_p, c_char_p, c_int, c_int])
# pycapi(lgs.tbGetBoardingTripId, c_char_p, [c_void_p, c_int])
# pycapi(lgs.tbGetBoardingDepart, c_int, [c_void_p, c_int])
# pycapi(lgs.tbGetBoardingStopSequence, c_int, [c_void_p, c_int])
# pycapi(lgs.tbGetBoardingIndexByTripId, c_int, [c_void_p, c_char_p])
# pycapi(lgs.tbDestroy, None, [c_void_p])
# pycapi(lgs.tbGetNextBoardingIndex, c_int, [c_void_p, c_int])
# pycapi(lgs.tbSearchBoardingsList, c_int, [c_void_p, c_int])

# #HEADWAY API
# pycapi(lgs.headwayNew, c_void_p, [c_int, c_int, c_int, c_int, c_void_p, c_void_p, c_void_p, c_int, c_int])

# #HEADWAY BOARD
# pycapi(lgs.hbNew, c_void_p, [c_int, c_void_p, c_void_p, c_int, c_void_p, c_int, c_int, c_int])
# pycapi(lgs.hbDestroy, None, [c_void_p])

# #HEADWAY ALIGHT
# pycapi(lgs.haNew, c_void_p, [c_int, c_void_p, c_void_p, c_int, c_void_p, c_int, c_int, c_int])
# pycapi(lgs.haDestroy, None, [c_void_p])

# #ALIGHT API
# pycapi(lgs.alNew, c_void_p, [c_int, c_void_p, c_void_p, c_int])
# pycapi(lgs.alDestroy, None, [c_void_p])
# pycapi(lgs.alAddAlighting, None, [c_void_p, c_char_p, c_int, c_int])
# pycapi(lgs.alGetAlightingTripId, c_char_p, [c_void_p, c_int])
# pycapi(lgs.alGetAlightingArrival, c_int, [c_void_p, c_int])
# pycapi(lgs.alGetAlightingStopSequence, c_int, [c_void_p, c_int])
# pycapi(lgs.alGetAlightingIndexByTripId, c_int, [c_void_p, c_char_p])
# pycapi(lgs.alGetLastAlightingIndex, c_int, [c_void_p, c_int])
# pycapi(lgs.alSearchAlightingsList, c_int, [c_void_p, c_int])

# #ELAPSE TIME API
# pycapi(lgs.elapseTimeNew, c_void_p, [c_long])
# pycapi(lgs.elapseTimeDestroy, None)
# pycapi(lgs.elapseTimeWalk, c_void_p, [c_void_p, c_void_p])
# pycapi(lgs.elapseTimeWalkBack, c_void_p, [c_void_p, c_void_p])
# pycapi(lgs.elapseTimeGetSeconds, c_long, [c_void_p])

# #CROSSING API
# pycapi(lgs.crNew, c_void_p, [])
# pycapi(lgs.crDestroy, None, [c_void_p])
# pycapi(lgs.crAddCrossingTime, c_void_p, [c_void_p, c_char_p, c_int])
# pycapi(lgs.crGetCrossingTime, c_int, [c_void_p, c_char_p])
# pycapi(lgs.crGetCrossingTimeByIndex, c_int, [c_void_p, c_int])
# pycapi(lgs.crGetCrossingTimeTripIdByIndex, c_char_p, [c_void_p, c_int])
# pycapi(lgs.crGetSize, c_int, [c_void_p])

#CUSTOM TYPE API
class PayloadMethodTypes:
    """ Enumerates the ctypes of the function pointers."""
    destroy = CFUNCTYPE(c_void_p, py_object)
    walk = CFUNCTYPE(c_void_p, py_object, c_void_p, c_void_p)
    walk_back = CFUNCTYPE(c_void_p, py_object, c_void_p, c_void_p)
    
# pycapi(lgs.cpSoul, py_object, [c_void_p])
# pycapi(lgs.cpDestroy, None, [c_void_p])
# pycapi(lgs.cpNew, c_void_p, [c_void_p, c_void_p])
# args are not specified to allow for None
#lgs.defineCustomPayloadType.restype = c_void_p
#lgs.undefineCustomPayloadType.restype = None

import traceback, sys
class SafeWrapper(object):
    def __init__(self, lib, name):
        self.lib = lib
        self.called = set([])
        self.name = name

    def __getattr__(self, attr):
        v = getattr(self.lib, attr)
        if not getattr(v, 'safe', False):
            raise Exception("Calling unsafe method %s" % attr)
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

if 'GS_RUN_SAFE' in os.environ:
    lgs = SafeWrapper(lgs,'lgs')
