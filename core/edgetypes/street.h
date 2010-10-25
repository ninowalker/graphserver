#ifndef _STREET_H_
#define _STREET_H_

#include <stdbool.h>

//---------------DECLARATIONS FOR STREET  CLASS---------------------

struct Street {
   edgepayload_t type;
   long external_id;
   State* (*walk)(struct EdgePayload*, struct State*, struct WalkOptions*);
   State* (*walkBack)(struct EdgePayload*, struct State*, struct WalkOptions*);
    
   char* name;
   double length;
   float rise;
   float fall;
   float slog;
   long way;
    
   bool reverse_of_source;
};

Street*
streetNew(const char *name, double length, bool reverse_of_source);

Street*
streetNewElev(const char *name, double length, float rise, float fall, bool reverse_of_source);

void
streetDestroy(Street* tokill);

inline State*
streetWalk(EdgePayload* superthis, State* state, WalkOptions* options);

inline State*
streetWalkBack(EdgePayload* superthis, State* state, WalkOptions* options);

char*
streetGetName(Street* self);

double
streetGetLength(Street* self);

float
streetGetRise(Street* self);

float
streetGetFall(Street* self);

void
streetSetRise(Street* self, float rise) ;

void
streetSetFall(Street* self, float fall) ;
long
streetGetWay(Street* self);

void
streetSetWay(Street* self, long way);

bool
streetGetReverseOfSource(Street* self) ;

#endif
