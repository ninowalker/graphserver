struct Path {
  Vector *vertices;
  Vector *edges;
} ;

// PATH FUNCTIONS

Path *
pathNew( Vertex* origin, int init_size, int expand_delta );

void
pathDestroy(Path *self);

Vertex *
pathGetVertex( Path *self, int i );

Edge *
pathGetEdge( Path *self, int i );

void
pathAddSegment( Path *self, Vertex *vertex, Edge *edge );