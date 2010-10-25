#ifndef _CUSTOMPAYLOAD_H_
#define _CUSTOMPAYLOAD_H_

struct PayloadMethods {
	void (*destroy)(void*);
	State* (*walk)(void*,State*,WalkOptions*);
	State* (*walkBack)(void*,State*,WalkOptions*);
	//char* (*to_str)(void*);
};

struct CustomPayload {
  edgepayload_t type;
  void* soul;
  PayloadMethods* methods;
};

PayloadMethods*
defineCustomPayloadType(void (*destroy)(void*),
						State* (*walk)(void*,State*,WalkOptions*),
						State* (*walkback)(void*,State*,WalkOptions*));


void
undefineCustomPayloadType( PayloadMethods* self );

CustomPayload*
cpNew( void* soul, PayloadMethods* methods );

void
cpDestroy( CustomPayload* self );

void*
cpSoul( CustomPayload* self );

PayloadMethods*
cpMethods( CustomPayload* self );

State*
cpWalk(CustomPayload* self, State* state, WalkOptions* walkoptions);

State*
cpWalkBack(CustomPayload* self, State* state, WalkOptions* walkoptions);

#endif
