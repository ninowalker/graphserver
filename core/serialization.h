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
bool gDeserialize(Graph *g, char* gbin_name, char * mmf_name);
bool gSerialize(Graph *g, char* gbin_name, char * mmf_name) ;
#endif