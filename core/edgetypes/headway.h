#ifndef _HEADWAY_H_
#define _HEADWAY_H_

//---------------DECLARATIONS FOR HEADWAY  CLASS---------------------

struct Headway {
  edgepayload_t type;
  long external_id;
  State* (*walk)(struct EdgePayload*, struct State*, struct WalkOptions*);
  State* (*walkBack)(struct EdgePayload*, struct State*, struct WalkOptions*);
    
  int begin_time;
  int end_time;
  int wait_period;
  int transit;
  char* trip_id;
  ServiceCalendar* calendar;
  Timezone* timezone;
  int agency;
  ServiceId service_id;
} ;

Headway*
headwayNew(int begin_time, int end_time, int wait_period, int transit, char* trip_id, ServiceCalendar* calendar, Timezone* timezone, int agency, ServiceId service_id);

void
headwayDestroy(Headway* tokill);

inline State*
headwayWalk(EdgePayload* self, State* param, WalkOptions* options);

inline State*
headwayWalkBack(EdgePayload* self, State* param, WalkOptions* options);

int
headwayBeginTime(Headway* self);

int
headwayEndTime(Headway* self);

int
headwayWaitPeriod(Headway* self);

int
headwayTransit(Headway* self);

char*
headwayTripId(Headway* self);

ServiceCalendar*
headwayCalendar(Headway* self);

Timezone*
headwayTimezone(Headway* self);

int
headwayAgency(Headway* self);

ServiceId
headwayServiceId(Headway* self);

#endif
