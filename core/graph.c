#include "graphserver.h"

#include "graph.h"
#include "fibheap/fibheap.h"
#include "fibheap/dirfibheap.h"

#include <stddef.h>
#include <string.h>
#include "hashtable/hashtable_gs.h"
#include "hashtable/hashtable_itr.h"

#ifndef INFINITY
  #define INFINITY 1000000000
#endif

const size_t EDGEPAYLOAD_ENUM_SIZE = sizeof(edgepayload_t);

//GRAPH FUNCTIONS

Graph*
gNew() {
  Graph *this = (Graph*)malloc(sizeof(Graph));
  this->vertices = create_hashtable_string(16); //TODO: find a better number.

  return this;
}

void
gDestroy( Graph* this, int kill_vertex_payloads, int kill_edge_payloads ) {

  //destroy each vertex contained within
  struct hashtable_itr *itr = hashtable_iterator(this->vertices);
  int next_exists = hashtable_count(this->vertices);

  while(itr && next_exists) {
    Vertex* vtx = hashtable_iterator_value( itr );
    vDestroy( vtx, kill_vertex_payloads, kill_edge_payloads );
    next_exists = hashtable_iterator_advance( itr );
  }

  free(itr);
  //destroy the table
  hashtable_destroy( this->vertices, 0 );
  //destroy the graph object itself
  free( this );

}

Vertex*
gAddVertex( Graph* this, char *label ) {
  Vertex* exists = gGetVertex( this, label );
  if( !exists ) {
    exists = vNew( label );
    hashtable_insert_string( this->vertices, label, exists );
  }

  return exists;
}

void
gRemoveVertex( Graph* this, char *label, int free_vertex_payload, int free_edge_payloads ) {
    Vertex *exists = gGetVertex( this, label );
    if(!exists) {
        return;
    }
    
    hashtable_remove( this->vertices, label );
    vDestroy( exists, free_vertex_payload, free_edge_payloads );
}

void 
gAddVertices( Graph* this, char **labels, int n ) {
  int i;
  for (i = 0; i < n; i++) {
  	gAddVertex(this, labels[i]);
  }
}

Vertex*
gGetVertex( Graph* this, char *label ) {
  return hashtable_search( this->vertices, label );
}

Edge*
gAddEdge( Graph* this, char *from, char *to, EdgePayload *payload ) {
  Vertex* vtx_from = gGetVertex( this, from );
  Vertex* vtx_to   = gGetVertex( this, to );

  if(!(vtx_from && vtx_to))
    return NULL;

  return vLink( vtx_from, vtx_to, payload );
}

Vertex**
gVertices( Graph* this, long* num_vertices ) {
  unsigned int nn = hashtable_count(this->vertices);
  Vertex** ret = (Vertex**)malloc(nn*sizeof(Vertex*));

  long i=0;
  struct hashtable_itr *itr = hashtable_iterator(this->vertices);
  int next_exists=nn; //next_exists is false when number of vertices is 0

  while(itr && next_exists) {
    Vertex* vtx = hashtable_iterator_value( itr );
    ret[i] = vtx;
    next_exists = hashtable_iterator_advance( itr );
    i++;
  }

  *num_vertices = nn;
  return ret;
}

long
set_spt_edge_thickness( Edge* edge ) {
    long thickness = edge->to->payload->weight - edge->from->payload->weight;
    
    ListNode* outgoing_edge_node = vGetOutgoingEdgeList( edge->to );
    while(outgoing_edge_node) {
        thickness += set_spt_edge_thickness( outgoing_edge_node->data );
        outgoing_edge_node = outgoing_edge_node->next;
    }
    
    edge->thickness = thickness;
    
    return thickness;
}

void
gSetThicknesses( Graph* this, char *root_label ) {
    Vertex* root = gGetVertex( this, root_label );

    ListNode* outgoing_edge_node = vGetOutgoingEdgeList( root );

    while(outgoing_edge_node) {
        set_spt_edge_thickness( outgoing_edge_node->data );
        outgoing_edge_node = outgoing_edge_node->next;
    }
}

#undef RETRO
#include "router.c"
#define RETRO
#include "router.c"
#undef RETRO

#define LARGEST_ROUTE_SIZE 10000

State*
gShortestPath( Graph* this, char *from, char *to, State* init_state, int direction, long *size, WalkOptions* options, long timelimit ) {
  //make sure from/to vertices exist
  if( !gGetVertex( this, from ) ) {
    fprintf( stderr, "Origin vertex \"%s\" does not exist\n", from );
    return NULL;
  }
  if( !gGetVertex( this, to ) ) {
    fprintf( stderr, "Destination vertex \"%s\" does not exist\n", to );
    return NULL;
  }

  //find minimum spanning tree
  Graph *raw_tree;
  Vertex *curr;
  if(direction) {
    raw_tree = gShortestPathTree( this, from, to, init_state, options, timelimit );
    curr = gGetVertex( raw_tree, to );
  } else {
    raw_tree = gShortestPathTreeRetro( this, from, to, init_state, options, timelimit );
    curr = gGetVertex( raw_tree, from );
  }

  if( !curr ) {
    gDestroy(raw_tree, 1, 0); //destroy raw_table and contents, as they won't be used
    fprintf( stderr, "Destination vertex never reached\n" );
    return NULL;
  }

  //TODO: replace ret with a resizeable array
  State *temppath = (State*)malloc(LARGEST_ROUTE_SIZE*sizeof(State));


  int i=0;
  while( curr ) {
    if( i > LARGEST_ROUTE_SIZE ) {         //Bail if our crude memory management techniques fail
      gDestroy( raw_tree, 1, 0 );
      free(temppath);
      fprintf( stderr, "Route %d hops long, larger than preallocated %d hops\n", i, LARGEST_ROUTE_SIZE );
      return NULL;
    }

    temppath[i] = *((State*)(curr->payload));
    i++;

    if( curr->degree_in == 0 )
      break;
    else
      curr = vGetIncomingEdgeList( curr )->data->from;
  }

  int n = i;
  //reverse path while copying to a newly allocated set of prev_entries
  State *ret = (State*)malloc(n*sizeof(State));
  //path need not be reversed in the case of a retro route; the tree trace started at the beginning
  if(direction) {
    i=0;
    int j=n-1;
    for( ; i<n; ) {
      ret[i] = temppath[j];
      i++;
      j--;
    }
  } else {
    //memcpy would be faster
    for(i=0; i<n; i++) {
      ret[i] = temppath[i];
    }
  }
  free( temppath );

  //destroy vertex payloads - we've transferred the relevant state information out
  //do not destroy the edge payloads - they belong to the creating graph
  //TODO: fix this so memory stops leaking:
  //gDestroy( raw_tree, 1, 0 );

  //return
  *size = n;
  return ret;
}

Path *
sptPathRetro(Graph* g, char* origin_label) {
	Vertex* curr = gGetVertex(g, origin_label);
	ListNode* incoming = NULL;
	Edge* edge = NULL;
    
    Path *path = pathNew(curr, 50, 50);
	
    // trace backwards up the tree until the current vertex has no parents
	while ((incoming = vGetIncomingEdgeList(curr))) {
        
		edge = liGetData(incoming);
		curr = eGetFrom(edge);
        
        pathAddSegment( path, curr, edge );
	}

	return path;	
}

long
gSize( Graph* this ) {
  return hashtable_count( this->vertices );
}

void
gSetVertexEnabled( Graph *this, char *label, int enabled ) {
    
    Vertex *vv = gGetVertex( this, label );
    
    ListNode* outgoing_edge_node = vGetOutgoingEdgeList( vv );

    while(outgoing_edge_node) {
        eSetEnabled( outgoing_edge_node->data, enabled );
        outgoing_edge_node = outgoing_edge_node->next;
    }

    ListNode* incoming_edge_node = vGetIncomingEdgeList( vv );

    while(incoming_edge_node) {
        eSetEnabled( incoming_edge_node->data, enabled );
        incoming_edge_node = incoming_edge_node->next;
    }
    
}


// VERTEX FUNCTIONS

Vertex *
vNew( char* label ) {
    Vertex *this = (Vertex *)malloc(sizeof(Vertex)) ;
    this->degree_in = 0;
    this->degree_out = 0;
    this->outgoing = liNew( NULL ) ;
    this->incoming = liNew( NULL ) ;
    this->payload = NULL;

    size_t labelsize = strlen(label)+1;
    this->label = (char*)malloc(labelsize*sizeof(char));
    strcpy(this->label, label);

    return this ;
}

void
vDestroy(Vertex *this, int free_vertex_payload, int free_edge_payloads) {
    if( free_vertex_payload && this->payload )
      stateDestroy( this->payload );

    //delete incoming edges
    while(this->incoming->next != NULL) {
      eDestroy( this->incoming->next->data, free_edge_payloads );
    }
    //delete outgoing edges
    while(this->outgoing->next != NULL) {
      eDestroy( this->outgoing->next->data, free_edge_payloads );
    }
    //free the list dummy-heads that remain
    free(this->outgoing);
    free(this->incoming);

    //and finally, sweet release*/
    free( this->label );
    free( this );
}


Edge*
vLink(Vertex* this, Vertex* to, EdgePayload* payload) {
    //create edge object
    Edge* link = eNew(this, to, payload);

    ListNode* outlistnode = liNew( link );
    liInsertAfter( this->outgoing, outlistnode );
    this->degree_out++;

    ListNode* inlistnode = liNew( link );
    liInsertAfter( to->incoming, inlistnode );
    to->degree_in++;

    return link;
}

//the comments say it all
Edge*
vSetParent( Vertex* this, Vertex* parent, EdgePayload* payload ) {
    //delete all incoming edges
    ListNode* edges = vGetIncomingEdgeList( this );
    while(edges) {
      ListNode* nextnode = edges->next;
      eDestroy( edges->data, 0 );
      edges = nextnode;
    }

    //add incoming edge
    return vLink( parent, this, payload );
}

ListNode*
vGetOutgoingEdgeList( Vertex* this ) {
    return this->outgoing->next; //the first node is a dummy
}

ListNode*
vGetIncomingEdgeList( Vertex* this ) {
    return this->incoming->next; //the first node is a dummy
}

void
vRemoveOutEdgeRef( Vertex* this, Edge* todie ) {
    liRemoveRef( this->outgoing, todie );
}

void
vRemoveInEdgeRef( Vertex* this, Edge* todie ) {
    liRemoveRef( this->incoming, todie );
}

char*
vGetLabel( Vertex* this ) {
    return this->label;
}

int
vDegreeOut( Vertex* this ) {
    return this->degree_out;
}

int
vDegreeIn( Vertex* this ) {
    return this->degree_in;
}

State*
vPayload( Vertex* this ) {
	return this->payload;
}

long
eGetThickness(Edge *this) {
    return this->thickness;
}

void
eSetThickness(Edge *this, long thickness) {
    this->thickness = thickness;
}

// EDGE FUNCTIONS

Edge*
eNew(Vertex* from, Vertex* to, EdgePayload* payload) {
    Edge *this = (Edge *)malloc(sizeof(Edge));
    this->from = from;
    this->to = to;
    this->payload = payload;
    this->thickness = -1;
    this->enabled = 1;
    return this;
}

void
eDestroy(Edge *this, int destroy_payload) {
    //free payload
    if(destroy_payload)
      epDestroy( this->payload ); //destroy payload object and contents

    vRemoveOutEdgeRef( this->from, this );
    vRemoveInEdgeRef( this->to, this );
    free(this);
}

State*
eWalk(Edge *this, State* state, WalkOptions* options) {
  if( this->enabled ) {
    return epWalk( this->payload, state, options );
  } else {
    return NULL;
  }
}

State*
eWalkBack(Edge *this, State* state, WalkOptions* options) {
  if( this->enabled ) {
    return epWalkBack( this->payload, state, options );
  } else {
    return NULL;
  }
}

Vertex*
eGetFrom(Edge *this) {
  return this->from;
}

Vertex*
eGetTo(Edge *this) {
  return this->to;
}

EdgePayload*
eGetPayload(Edge *this) {
  return this->payload;
}

int
eGetEnabled(Edge *this) {
    return this->enabled;
}

void
eSetEnabled(Edge *this, int enabled) {
    this->enabled = enabled;
}
