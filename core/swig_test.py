import cgraph
import os

g = cgraph.CGraph()
g.addVertex("A")
g.addVertex("B")
assert g.getVertex("A")
assert g.getVertex("B")
assert g.getVertex("C") == None

serial = "test.gbin"
try:
    os.unlink(serial)
except: pass

g.serialize(serial)
del g

g = cgraph.CGraph()
g.deserialize(serial)
assert g.getVertex("A")
assert g.getVertex("B")
assert g.getVertex("C") == None
