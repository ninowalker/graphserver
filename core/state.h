#ifndef _STATE_H_
#define _STATE_H_

//---------------DECLARATIONS FOR STATE CLASS---------------------

struct State {
   long          time;           //seconds since the epoch
   long          weight;
   double        dist_walked;    //meters
   int           num_transfers;
   EdgePayload*  prev_edge;
   char*         trip_id;
   int           stop_sequence;
   int           n_agencies;
   ServicePeriod** service_periods;
} ;

State*
stateNew(int numcalendars, long time);

void
stateDestroy( State* self);

State*
stateDup( State* self );

long
stateGetTime( State* self );

long
stateGetWeight( State* self);

double
stateGetDistWalked( State* self );

int
stateGetNumTransfers( State* self );

EdgePayload*
stateGetPrevEdge( State* self );

char*
stateGetTripId( State* self );

int
stateGetStopSequence( State* self );

int
stateGetNumAgencies( State* self );

ServicePeriod*
stateServicePeriod( State* self, int agency );

void
stateSetServicePeriod( State* self,  int agency, ServicePeriod* cal );

void
stateSetTime( State* self, long time );

void
stateSetWeight( State* self, long weight );

void
stateSetDistWalked( State* self, double dist );

void
stateSetNumTransfers( State* self, int n);

// the state does not keep ownership of the trip_id, so the state
// may not live longer than whatever object set its trip_id
void
stateDangerousSetTripId( State* self, char* trip_id );

void
stateSetPrevEdge( State* self, EdgePayload* edge );

#endif
