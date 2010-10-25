#ifndef _TIMEZONE_H_
#define _TIMEZONE_H_

struct TimezonePeriod {
  long begin_time; //the first second on which the service_period is valid
  long end_time;   //the last second on which the service_period is valid
  int utc_offset;
  TimezonePeriod* next_period;
} ;

Timezone*
tzNew(void);

void
tzAddPeriod( Timezone* self, TimezonePeriod* period );

TimezonePeriod*
tzPeriodOf( Timezone* self, long time);

int
tzUtcOffset( Timezone* self, long time);

int
tzTimeSinceMidnight( Timezone* self, long time );

TimezonePeriod*
tzHead( Timezone* self );

void
tzDestroy( Timezone* self );

TimezonePeriod*
tzpNew( long begin_time, long end_time, int utc_offset );

void
tzpDestroy( TimezonePeriod* self );

int
tzpUtcOffset( TimezonePeriod* self );

int
tzpTimeSinceMidnight( TimezonePeriod* self, long time );

long
tzpBeginTime( TimezonePeriod* self );

long
tzpEndTime( TimezonePeriod* self );

TimezonePeriod*
tzpNextPeriod(TimezonePeriod* self);

#endif
