#ifdef SWIGPYTHON
%module libgraphserver_swig
#endif
#ifdef SWIGJAVA
%module libgraphserver_java
#endif

%{
#define SWIG_FILE_WITH_INIT
#include "graph.h"
#include "statetypes.h"
#include "edgetypes.h"
#include <stdbool.h>
%}

#ifdef SWIGPYTHON
%include "typemaps.i"

%typemap(out) EdgePayload* {
    switch ($1->type) {
    case PL_LINK: $result = SWIG_NewPointerObj(SWIG_as_voidptr($1), SWIGTYPE_p_Link, 0 |  0 ); break;
    case PL_STREET: $result = SWIG_NewPointerObj(SWIG_as_voidptr($1), SWIGTYPE_p_Street, 0 |  0 ); break;
    default: $result = SWIG_NewPointerObj(SWIG_as_voidptr($1), SWIGTYPE_p_EdgePayload, 0 |  0 ); break;
    }
}

%typemap(in) (int nsids, ServiceId* service_ids) {
  /* Check if is a list */
  if (PyList_Check($input)) {
    int i;
    $1 = PyList_Size($input);
    $2 = (ServiceId*) malloc(($1)*sizeof(ServiceId *));
    for (i = 0; i < $1; i++) {
      PyObject *o = PyList_GetItem($input,i);
      if (PyInt_Check(o))
	$2[i] = (int)PyInt_AsLong(PyList_GetItem($input,i));
      else {
	PyErr_SetString(PyExc_TypeError,"list must contain ints");
	free($2);
	return NULL;
      }
    }
  } else {
    PyErr_SetString(PyExc_TypeError,"not a list");
    return NULL;
  }
}

%typemap(freearg) (int nsids, ServiceId* service_ids) {
  free((ServiceId*) $2);
}


%pythoncode %{
import pytz, calendar

class VertexNotFoundError(Exception): pass

def generic_setstate(self, dict):
    self.__init__()
    for key, value in dict.iteritems():
        setattr(self, key, value)

def generic_getstate(self):
    return dict((var, getattr(self, var)) for var in 
        __pickle_vars__[self.__class__.__name__])

def __xml_str__(self):
    return self.to_xml()

%}
#endif

%include "graph.h"
%include "statetypes.h"
%include "edgetypes.h"


%clear EdgePayload *;

%inline %{
EdgePayload* epCast(void* p) {
    return (EdgePayload*)p;
}

%}

%extend Graph {
    Graph(int numagencies=0) {
        // todo numagencies
        return gNew();
    }
    ~Graph() { gDestroy(self, 1, 1); }
    
    long size() { return gSize(self); }
    
    Vertex* add_vertex(char* label) {
        return gAddVertex(self, label);
    }

    Graph* shortest_path_tree(char* fromv, char* tov, State* initstate, WalkOptions* walk_options=NULL, long long maxtime=2000000000, bool retro=false) {
        if (tov == NULL) {
            tov = "*bogus^*^vertex*";
        }
        
        if (walk_options == NULL) {
            walk_options = woNew();
            Graph* ret;
            if (retro) ret = gShortestPathTreeRetro(self, fromv, tov, initstate, walk_options, maxtime);
            else ret = gShortestPathTree(self, fromv, tov, initstate, walk_options, maxtime);
            woDestroy(walk_options);
            return ret;
        }
        if (retro) return gShortestPathTreeRetro(self, fromv, tov, initstate, walk_options, maxtime);
        
        return gShortestPathTree(self, fromv, tov, initstate, walk_options, maxtime);
    }
    
    Vertex* get_vertex(char* label) {
        return gGetVertex(self, label);
    }
    
    Edge* m_add_edge(char* fromv, char* tov, EdgePayload* ep) {
        return gAddEdge(self, fromv, tov, ep);
    }

#ifdef SWIGPYTHON
    %pythoncode %{
    @property
    def soul(self): return self.this
    
    @property
    def size(self):
        return gSize(self)

    def add_edge(self, fromv, tov, payload):
        e = gAddEdge(self, fromv, tov, epCast(payload))
        
        if e != None:
            payload.thisown = 0
            return e

        if not self.get_vertex(fromv):
            raise VertexNotFoundError(fromv)
        raise VertexNotFoundError(tov)

    def vertices(self):
        vl = gVertexList(self)
        try:
            for i in xrange(vl.count):
                yield vlGetVertex(vl, i)
        finally:
            vlDestroy(vl)

    def edges(self):
        for vertex in self.vertices():
            for e in vertex.outgoing_edges():
                yield e
    %}
#endif
}

%extend Edge {
#ifdef PYTHONSWIG
    %pythoncode %{
    @property
    def soul(self): return self.this
    __str__ = __xml_str__
    def to_xml(self):
        return "<Edge>%s</Edge>" % (self.payload)
    %}
#endif
}

%extend State {
    State(int n_agencies, long long time) { return stateNew(n_agencies, time); }
    ~State() { stateDestroy(self); }
    
    ServicePeriod* service_period(int agency) { return stateServicePeriod(self, agency); }
    
    void set_service_period(int agency, ServicePeriod* sp) {
        if (agency > self->n_agencies) { return; }
        stateSetServicePeriod( self, agency, sp);
    }
    
    State* clone() { return stateDup(self); }
#ifdef SWIGPYTHON
    %pythoncode %{
    @property
    def soul(self): return self.this
    __str__ = __xml_str__

    def to_xml(self):        
        ret = "<state time='%d' weight='%s' dist_walked='%s' " \
              "num_transfers='%s' prev_edge_type='%s' prev_edge_name='%s' trip_id='%s'>" % \
               (self.time,
               self.weight,
               self.dist_walked,
               self.num_transfers,
               self.prev_edge_type,
               self.prev_edge_name,
               self.trip_id)
        for i in range(self.num_agencies):
            if self.service_period(i) is not None:
                ret += self.service_period(i).to_xml()
        return ret + "</state>"
    
    __str__ = __xml_str__

    def __copy__(self):
        return self.clone()
    %}
#endif
}

%extend WalkOptions {
    WalkOptions() { return woNew(); }
    ~WalkOptions() {
        woDestroy(self);
    }
#ifdef PYTHONSWIG
%pythoncode %{
    @property
    def soul(self): return self.this
    %}   
#endif
}

%extend Vertex {
    Vertex(char* label) { return vNew(label); }
    ~Vertex() { vDestroy(self, 1, 1); }
    State* state() { return vPayload(self); }
#ifdef PYTHONSWIG
    %pythoncode %{
    def destroy(self): self.thisown = 1
    
    del incoming
    del outgoing
    
    def to_xml(self):
        return "<Vertex degree_out='%s' degree_in='%s' label='%s'/>" % (self.degree_out, self.degree_in, self.label)
    
    __str__ = __xml_str__
    
    def outgoing_edges(self):
        return self._edges(self.outgoing)
    
    def incoming_edges(self):
        return self._edges(self.incoming)
        
    def get_outgoing_edge(self,i):
        return self._edges(self.outgoing, i)
        
    def get_incoming_edge(self,i):
        return self._edges(self.incoming, i)

    def _edges(self, node, index = -1):
        e = []
        i = 0
        node = node.next
        while node:
            if index != -1:
                if i == index: return node.data
            else:
                e.append(node.data)
            node = node.next
            i = i+1
        if index == -1:
            return e
        return None

    %}       
#endif
}

%extend EdgePayload {
#ifdef PYTHONSWIG
    %pythoncode %{
    @property
    def soul(self): return self.this

    __str__ = __xml_str__
    def to_xml(self):
        return "<genericedgepayload type='%s'/>" % self.type
    %}
#endif
}

/*
#=============================================================================#
# Edge Type Support Classes                                                   #
#=============================================================================#
*/

%extend ServicePeriod {
    ServicePeriod(long begin, long end, int nsids, ServiceId* service_ids) {
        return spNew(begin, end, nsids, service_ids);
    }
    ~ServicePeriod() { spDestroyPeriod(self); }
    
    int get_service_id_at(int index) {
        if (index > self->n_service_ids) { return -1; }
        return (int)self->service_ids[index];
    }
    
    ServicePeriod* rewind() {
        return spRewind(self);
    }
    ServicePeriod* fast_forward() {
        return spFastForward(self);
    }
        
    long normalize_time(int timezone_offset, long long time) {
        return spNormalizeTime(self, timezone_offset, time);
    }
    
#ifdef PYTHONSWIG
    %pythoncode %{
    @property
    def service_ids(self):
        ids = []
        for i in xrange(self.n_service_ids):
            ids.append(self.get_service_id_at(i))
        return ids

    @property
    def previous(self):
        return self.previous_period

    @property
    def next(self):
        return self.next_period

    __str__ = __xml_str__
    
    def to_xml(self, cal=None):
        if cal is not None:
            sids = [cal.get_service_id_string(x) for x in self.service_ids]
        else:
            sids = [str(x) for x in self.service_ids]

        return "<ServicePeriod begin_time='%d' end_time='%d' service_ids='%s'/>" %( self.begin_time, self.end_time, ",".join(sids))

    def __getstate__(self):
        return (self.begin_time, self.end_time, self.service_ids)
        
    def __setstate__(self, state):
        self.__init__(*state)

    %}   
#endif
}

%extend ServiceCalendar {
    ServiceCalendar() { return scNew(); }
    ~ServiceCalendar() { scDestroy(self); }
    
    int get_service_id_int(char* service_id) {
        return scGetServiceIdInt( self, service_id );
    }
    
    char* get_service_id_string(int service_id) {
        return scGetServiceIdString( self, service_id );
    }

    ServicePeriod* period_of_or_after(long long time) {
        return scPeriodOfOrAfter(self, time);
    }
    ServicePeriod* period_of_or_before(long long time) {
        return scPeriodOfOrBefore(self, time);
    }
#ifdef PYTHONSWIG
    %pythoncode %{
    @property
    def periods(self):
        curr = self.head
        while curr:
            yield curr
            curr = curr.next
            
    __str__ = __xml_str__

    def to_xml(self):
        ret = ["<ServiceCalendar>"]
        for period in self.periods:
            ret.append( period.to_xml(self) )
        ret.append( "</ServiceCalendar>" )
        return "".join(ret)
        
    def __getstate__(self):
        ret = []
        sids_map = {}
        curs = self.head
        while curs:
            start, end, sids = curs.__getstate__()
            for sid in sids:
                sids_map[sid] = self.get_service_id_string(sid)
            sids = [self.get_service_id_string(sid) for sid in sids]

            ret.append( (start,end,sids) )
            curs = curs.next
        return (sids_map, ret)
        
    def __setstate__(self, state):
        self.__init__()
        sids_map, periods = state
        for k in sorted(sids_map.keys()):
            new_k = self.get_service_id_int(sids_map[k])
            assert k == new_k
            
        for p in periods:
            self.add_period( *p )

    def expound(self, timezone_name):
        periodstrs = []
        
        for period in self.periods:
            begin_time = TimeHelpers.unix_to_localtime( period.begin_time, timezone_name )
            end_time = TimeHelpers.unix_to_localtime( period.end_time, timezone_name )
            service_ids = dict([(id,self.get_service_id_string(id)) for id in period.service_ids])
            periodstrs.append( "sids:%s active from %d (%s) to %d (%s)"%(service_ids, period.begin_time, begin_time, period.end_time, end_time) )
        
        return "\n".join( periodstrs )
    %}
#endif
}

%extend TimezonePeriod {
    TimezonePeriod(long long begin_time, long long end_time, long utc_offset) { return tzpNew(begin_time, end_time, utc_offset); }
    
    long time_since_midnight(long time) {
        return tzpTimeSinceMidnight( self, time );
    }
    
#ifdef PYTHONSWIG
    %pythoncode %{
    @property
    def soul(self): return self.this

    def __getstate__(self):
        return (self.begin_time, self.end_time, self.utc_offset)
    
    def __setstate__(self, state):
        self.__init__(*state)
    %}
#endif
}

%extend Timezone {
    Timezone() { return tzNew(); }
    ~Timezone() { tzDestroy(self); }
    
    TimezonePeriod* period_of(long long time) { return tzPeriodOf(self, time); }
    long time_since_midnight(long long time) { return tzTimeSinceMidnight(self, time); }

#ifdef PYTHONSWIG
    %pythoncode %{
    @property
    def soul(self): return self.this

    def utc_offset(self, time):
        ret = tzUtcOffset( self, time )
        
        if ret==-360000:
            raise IndexError( "%d lands within no timezone period"%time )
            
        return ret

    def add_period(self, p):
        tzAddPeriod(self, p);
        p.thisown = 0

    @classmethod
    def generate(cls, timezone_string):
        ret = Timezone()
        
        timezone = pytz.timezone(timezone_string)
        tz_periods = zip(timezone._utc_transition_times[:-1],timezone._utc_transition_times[1:])
            
        #exclude last transition_info entry, as it corresponds with the last utc_transition_time, and not the last period as defined by the last two entries
        for tz_period, (utcoffset,dstoffset,periodname) in zip( tz_periods, timezone._transition_info[:-1] ):
            period_begin, period_end = [calendar.timegm( (x.year, x.month, x.day, x.hour, x.minute, x.second) ) for x in tz_period]
            period_end -= 1 #period_end is the last second the period is active, not the first second it isn't
            utcoffset = utcoffset.days*24*3600 + utcoffset.seconds
            
            ret.add_period( TimezonePeriod( long(period_begin), long(period_end), long(utcoffset) ) )
        
        return ret
        
    def __getstate__(self):
        ret = []
        curs = self.head
        while curs:
            ret.append( curs.__getstate__() )
            curs = curs.next_period
        return ret
        
    def __setstate__(self, state):
        self.__init__()
        for tzpargs in state:
            self.add_period( TimezonePeriod(*tzpargs) )

    %}
#endif
}



/*
#=============================================================================#
# Edge Types                                                                  #
#=============================================================================#
*/
%extend Link {
    Link() { return linkNew(); }
    ~Link() { linkDestroy(self); }
#ifdef PYTHONSWIG
    %pythoncode %{
    @property
    def soul(self): return self.this

    def to_xml(self):
        return "<Link name='%s'/>" % (self.name)

    __str__ = __xml_str__
    
    def __getstate__(self):
        return tuple([])
        
    def __setstate__(self, state):
        self.__init__()
    
    @classmethod
    def reconstitute(self, state, resolver):
        return Link()

    %}
#endif
}

%extend Street {
    Street(char* n, float len) {
        return streetNew(n, len);
    }
    ~Street() { streetDestroy(self); }

#ifdef PYTHONSWIG
    %pythoncode %{
    @property
    def soul(self): return self.this

    def to_xml(self):
        return "<Street name='%s' length='%f' />" % (self.name, self.length)
    
    __str__ = __xml_str__

    def __getstate__(self):
        return (self.name,self.length)
        
    def __setstate__(self, state):
        self.__init__(*state)
        
    @classmethod
    def reconstitute(self, state, resolver):
        return Street( *state )

    %}
#endif
};

%extend ElapseTime {
    ElapseTime(long seconds) { return elapseTimeNew(seconds); }
    ~ElapseTime() { elapseTimeDestroy(self); }

#ifdef PYTHONSWIG
    %pythoncode %{
    @property
    def soul(self): return self.this

    def to_xml(self):
        return "<ElapseTime seconds='%ld' />"%(self.seconds)
    
    __str__ = __xml_str__

    def __getstate__(self):
        return self.seconds
    
    @classmethod
    def reconstitute(cls, state, resolver):
        return cls(state)
    %}
#endif
}

