#ifndef _ALIGHT_H_
#define _ALIGHT_H_

//---------------DECLARATIONS FOR ALIGHT CLASS---------------------------------------------

struct TripAlight {
    edgepayload_t type;
    long external_id;
    State* (*walk)(struct EdgePayload*, struct State*, struct WalkOptions*);
    State* (*walkBack)(struct EdgePayload*, struct State*, struct WalkOptions*);
    
    int n;
    int* arrivals;
    char** trip_ids;
    int* stop_sequences;
    
    ServiceCalendar* calendar;
    Timezone* timezone;
    int agency;
    ServiceId service_id;
    
    int overage; //number of seconds schedules past midnight of the last departure. If it's at 12:00:00, the overage is 0.
} ;

TripAlight*
alNew( ServiceId service_id, ServiceCalendar* calendar, Timezone* timezone, int agency );

void
alDestroy(TripAlight* self);

ServiceCalendar*
alGetCalendar( TripAlight* self );

Timezone*
alGetTimezone( TripAlight* self );

int
alGetAgency( TripAlight* self );

ServiceId
alGetServiceId( TripAlight* self );

int
alGetNumAlightings(TripAlight* self);

void
alAddAlighting(TripAlight* self, char* trip_id, int arrival, int stop_sequence);

char*
alGetAlightingTripId(TripAlight* self, int i);

int
alGetAlightingArrival(TripAlight* self, int i);

int
alGetAlightingStopSequence(TripAlight* self, int i);

int
alSearchAlightingsList(TripAlight* self, int time);

int
alGetLastAlightingIndex(TripAlight* self, int time);

int
alGetOverage(TripAlight* self);

int
alGetAlightingIndexByTripId(TripAlight* self, char* trip_id);

inline State*
alWalk(EdgePayload* self, State* state, WalkOptions* options);

inline State*
alWalkBack(EdgePayload* self, State* state, WalkOptions* options);

#endif
