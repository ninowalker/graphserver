struct Vector {
  int num_elements;
  int num_alloc;
  int expand_delta;
    
  void **elements;
} ;

// VECTOR FUNCTIONS

Vector *
vecNew( int init_size, int expand_delta );

void
vecDestroy(Vector *self);

void
vecAdd(Vector *self, void *element);

void *
vecGet(Vector *self, int index);

void
vecExpand(Vector *self, int amount);