#ifndef _HEAP_H_
#define _HEAP_H_

struct HeapNode {
    long priority;
    void *payload;
} ;

struct Heap {
    struct HeapNode* nodes;
    int capacity;
    int size;
} ;

Heap* heapNew( int init_capacity ) ;

void heapDestroy( Heap* self ) ;

void heapInsert( Heap* self, void* payload, long priority ) ;

int heapEmpty( Heap* self ) ;

void* heapMin( Heap* self, long* priority ) ;

void* heapPop( Heap* self, long* priority ) ;

#endif
