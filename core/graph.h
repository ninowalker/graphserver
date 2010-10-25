#ifndef GRAPH_H
#define GRAPH_H

struct Graph {
   struct hashtable* vertices;
};

struct ShortestPathTree {
   struct hashtable* vertices;
};

//for shortest path trees
struct prev_entry {
  char* from;
  char* to;
  char* desc;
  edgepayload_t type;
  long delta_weight; //DEBUG; not really necessary for anything else
  long weight;
  long end_time;
};

struct Vertex {
   int degree_out;
   int degree_in;
   ListNode* outgoing;
   ListNode* incoming;
   char* label;
    
   int deleted_neighbors;
} ;

struct SPTVertex {
   int degree_out;
   int degree_in;
   ListNode* outgoing;
   ListNode* incoming;
   char* label;
   State* state;
   int hop;
   Vertex *mirror;
} ;

struct Edge {
  Vertex* from;
  Vertex* to;
  EdgePayload* payload;
  int enabled;
} ;

//GRAPH FUNCTIONS

Graph*
gNew(void);

void
gDestroyBasic( Graph* self, int free_edge_payloads );

void
gDestroy( Graph* self );

Vertex*
gAddVertex( Graph* self, char *label );

void
gRemoveVertex( Graph* self, char *label, int free_edge_payloads );

Vertex*
gGetVertex( Graph* self, char *label );

void
gAddVertices( Graph* self, char **labels, int n );

Edge*
gAddEdge( Graph* self, char *from, char *to, EdgePayload *payload );

Vertex**
gVertices( Graph* self, long* num_vertices );

ShortestPathTree*
gShortestPathTree( Graph* self, char *from, char *to, State* init_state, WalkOptions* options, long maxtime, int hoplimit, long weightlimit );

ShortestPathTree*
gShortestPathTreeRetro( Graph* self, char *from, char *to, State* init_state, WalkOptions* options, long mintime, int hoplimit, long weightlimit );

//direction specifies forward or retro routing
State*
gShortestPath( Graph* self, char *from, char *to, State* init_state, int direction, long *size, WalkOptions* options, long timelimit, int hoplimit, long weightlimit );

long
gSize( Graph* self );

void
gSetVertexEnabled( Graph *self, char *label, int enabled );

//SPT METHODS

ShortestPathTree*
sptNew(void);

void
sptDestroy( ShortestPathTree *self );

SPTVertex*
sptAddVertex( ShortestPathTree *self, Vertex *mirror, int hop );

void
sptRemoveVertex( ShortestPathTree *self, char *label );

SPTVertex*
sptGetVertex( ShortestPathTree *self, char *label );

Edge*
sptAddEdge( ShortestPathTree *self, char *from, char *to, EdgePayload *payload );

SPTVertex**
sptVertices( ShortestPathTree *self, long* num_vertices );

long
sptSize( ShortestPathTree* self );

Path *
sptPathRetro(Graph* g, char* origin_label);

//VERTEX FUNCTIONS

Vertex *
vNew( char* label ) ;

void
vDestroy(Vertex* self, int free_edge_payloads) ;

// TODO
//void
//vMark(Vertex* self) ;

Edge*
vLink(Vertex* self, Vertex* to, EdgePayload* payload) ;

Edge*
vSetParent( Vertex* self, Vertex* parent, EdgePayload* payload );

inline ListNode*
vGetOutgoingEdgeList( Vertex* self );

inline ListNode*
vGetIncomingEdgeList( Vertex* self );

void
vRemoveOutEdgeRef( Vertex* self, Edge* todie );

void
vRemoveInEdgeRef( Vertex* self, Edge* todie );

char*
vGetLabel( Vertex* self );

int
vDegreeOut( Vertex* self );

int
vDegreeIn( Vertex* self );

//SPTVERTEX FUNCTIONS

SPTVertex *
sptvNew( Vertex* mirror, int hop ) ;

void
sptvDestroy(SPTVertex* self) ;

Edge*
sptvLink(SPTVertex* self, SPTVertex* to, EdgePayload* payload) ;

Edge*
sptvSetParent( SPTVertex* self, SPTVertex* parent, EdgePayload* payload );

inline ListNode*
sptvGetOutgoingEdgeList( SPTVertex* self );

inline ListNode*
sptvGetIncomingEdgeList( SPTVertex* self );

void
sptvRemoveOutEdgeRef( SPTVertex* self, Edge* todie );

void
sptvRemoveInEdgeRef( SPTVertex* self, Edge* todie );

char*
sptvGetLabel( SPTVertex* self );

int
sptvDegreeOut( SPTVertex* self );

int
sptvDegreeIn( SPTVertex* self );

State*
sptvState( SPTVertex* self );

int
sptvHop( SPTVertex* self );

Edge*
sptvGetParent( SPTVertex* self );

Vertex*
sptvMirror( SPTVertex* self );

//EDGE FUNCTIONS

Edge*
eNew(Vertex* from, Vertex* to, EdgePayload* payload);

void
eDestroy(Edge *self, int destroy_payload) ;

// TODO
//void
//eMark(Edge *self) ;

State*
eWalk(Edge *self, State* state, WalkOptions* options) ;

State*
eWalkBack(Edge *self, State *state, WalkOptions* options) ;

Vertex*
eGetFrom(Edge *self);

Vertex*
eGetTo(Edge *self);

EdgePayload*
eGetPayload(Edge *self);

int
eGetEnabled(Edge *self);

void
eSetEnabled(Edge *self, int enabled);

#endif
