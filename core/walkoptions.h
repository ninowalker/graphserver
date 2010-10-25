#ifndef _WALKOPTIONS_H_
#define _WALKOPTIONS_H_

//---------------DECLARATIONS FOR WALKOPTIONS CLASS---------------

struct WalkOptions {
    int transfer_penalty;
    float walking_speed;
    float walking_reluctance;
    float uphill_slowness;
    float downhill_fastness;
    float phase_change_grade;
    float hill_reluctance;    
    int max_walk;
    float walking_overage;
    int turn_penalty;
    
    float phase_change_velocity_factor;
} ;

WalkOptions*
woNew(void);

void
woDestroy( WalkOptions* self );

int
woGetTransferPenalty( WalkOptions* self );

void
woSetTransferPenalty( WalkOptions* self, int transfer_penalty );

float
woGetWalkingSpeed( WalkOptions* self );

void
woSetWalkingSpeed( WalkOptions* self, float walking_speed );

float
woGetWalkingReluctance( WalkOptions* self );

void
woSetWalkingReluctance( WalkOptions* self, float walking_reluctance );

int
woGetMaxWalk( WalkOptions* self );

void
woSetMaxWalk( WalkOptions* self, int max_walk );

float
woGetWalkingOverage( WalkOptions* self );

void
woSetWalkingOverage( WalkOptions* self, float walking_overage );

int
woGetTurnPenalty( WalkOptions* self );

void
woSetTurnPenalty( WalkOptions* self, int turn_penalty );

#endif
