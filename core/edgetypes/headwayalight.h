#ifndef _HEADWAYALIGHT_H_
#define _HEADWAYALIGHT_H_

//---------------DECLARATIONS FOR HEADWAYALIGHT CLASS---------------------------------------

struct HeadwayAlight {
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
};

HeadwayAlight*
haNew(  ServiceId service_id, ServiceCalendar* calendar, Timezone* timezone, int agency, char* trip_id, int start_time, int end_time, int headway_secs );

void
haDestroy(HeadwayAlight* self);

ServiceCalendar*
haGetCalendar( HeadwayAlight* self );

Timezone*
haGetTimezone( HeadwayAlight* self );

int
haGetAgency( HeadwayAlight* self );

ServiceId
haGetServiceId( HeadwayAlight* self );

char*
haGetTripId( HeadwayAlight* self );

int
haGetStartTime( HeadwayAlight* self );

int
haGetEndTime( HeadwayAlight* self );

int
haGetHeadwaySecs( HeadwayAlight* self );

inline State*
haWalk( EdgePayload* superthis, State* state, WalkOptions* options );

inline State*
haWalkBack( EdgePayload* superthis, State* state, WalkOptions* options );

#endif
