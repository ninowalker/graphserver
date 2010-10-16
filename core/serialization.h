#ifndef _SERIALIZATION_H_
#define _SERIALIZATION_H_
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <errno.h>
#include <stdbool.h>
#include <assert.h>

//#include "statetypes.h"
//#include "graph.h"
#include "graphserver.h"

typedef enum {
  OK,
  GRAPH_FILE_NOT_FOUND,
  MMAP_FILE_NOT_FOUND,
  UNSUPPORTED_EDGE_TYPE,
  SERIALIZATION_READ_ERROR,
  BAD_FILE_SIG,
  BINARY_INCOMPATIBILITY
} serialization_status_code_t;

serialization_status_code_t gDeserialize(Graph *g, char* gbin_name, char * mmf_name);
serialization_status_code_t gSerialize(Graph *g, char* gbin_name, char * mmf_name) ;
#endif
