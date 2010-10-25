#ifndef _EDGEPAYLOAD_H_
#define _EDGEPAYLOAD_H_

//---------------DECLARATIONS FOR EDGEPAYLOAD CLASS---------------------

struct EdgePayload {
  edgepayload_t type;
  long external_id;
  State* (*walk)(struct EdgePayload*, struct State*, struct WalkOptions*);
  State* (*walkBack)(struct EdgePayload*, struct State*, struct WalkOptions*);
} ;

EdgePayload*
epNew( edgepayload_t type, void* payload );

void
epDestroy( EdgePayload* self );

edgepayload_t
epGetType( EdgePayload* self );

long
epGetExternalId( EdgePayload* self );

void
epSetExternalId( EdgePayload *self, long external_id );

State*
epWalk( EdgePayload* self, State* param, WalkOptions* options );

State*
epWalkBack( EdgePayload* self, State* param, WalkOptions* options );

#endif
