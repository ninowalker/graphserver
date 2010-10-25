#ifndef GRAPH_HPP
#define GRAPH_HPP

#include <vector>

extern "C" {
#include "graphserver.h"
#include "graph.h"
#include "serialization.h"
};

class CGraph;

class CVertex {
public:
  CVertex(Graph* g, Vertex* v);
  ~CVertex();
protected:
  Graph* _g;
  Vertex* _v;
};

class CGraph {
public:
  CGraph();
  ~CGraph();
  serialization_status_code_t deserialize(char* filename);
  serialization_status_code_t serialize(char* filename);
  CVertex* getVertex(char* name);
  CVertex* addVertex(char* name);
protected:
  Graph* _g;
};

#endif
