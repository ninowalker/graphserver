#include "graph.hpp"

CVertex::CVertex(Graph* g, Vertex* v) : _g(g), _v(v) {}
CVertex::~CVertex() {}

CGraph::CGraph() {
  _g = gNew();
}

CGraph::~CGraph() {
  gDestroy(_g);
}

serialization_status_code_t CGraph::deserialize(char* filename) {
  return gDeserialize(_g, filename, (char*)NULL);
}
serialization_status_code_t CGraph::serialize(char* filename) {
  return gSerialize(_g, filename, (char*)NULL);
}

CVertex* CGraph::getVertex(char* name) {
  Vertex* v = gGetVertex(_g, name);
  if (!v) {
    return NULL;
  }
  return new CVertex(_g, v);
}

CVertex* CGraph::addVertex(char* name) {
  CVertex* v = this->getVertex(name);
  if (v) {
    return v;
  }
  return new CVertex(_g, gAddVertex(_g, name));
}
