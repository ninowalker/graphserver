#ifndef _HEADWAYBOARD_H_
#define _HEADWAYBOARD_H_

//---------------DECLARATIONS FOR HEADWAYBOARD CLASS---------------------------------------

struct HeadwayBoard {
    edgepayload_t type;
    long external_id;
    State* (*walk)(struct EdgePayload*, struct State*, struct WalkOptions*);
    State* (*walkBack)(struct EdgePayload*, struct State*, struct WalkOptions*);
    
    ServiceId service_id;
    char* trip_id;
    int start_time;
    int end_time;
    int headway_secs;
    
    ServiceCalendar* calendar;
    Timezone* timezone;
    int agency;
} ;

HeadwayBoard*
hbNew(  ServiceId service_id, ServiceCalendar* calendar, Timezone* timezone, int agency, char* trip_id, int start_time, int end_time, int headway_secs );

void
hbDestroy(HeadwayBoard* self);

ServiceCalendar*
hbGetCalendar( HeadwayBoard* self );

Timezone*
hbGetTimezone( HeadwayBoard* self );

int
hbGetAgency( HeadwayBoard* self );

ServiceId
hbGetServiceId( HeadwayBoard* self );

char*
hbGetTripId( HeadwayBoard* self );

int
hbGetStartTime( HeadwayBoard* self );

int
hbGetEndTime( HeadwayBoard* self );

int
hbGetHeadwaySecs( HeadwayBoard* self );

inline State*
hbWalk( EdgePayload* superthis, State* state, WalkOptions* options );

inline State*
hbWalkBack( EdgePayload* superthis, State* state, WalkOptions* options );

#endif
