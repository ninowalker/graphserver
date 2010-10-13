from graphserver.core import Vertex, Edge, Link, Street, Graph
import unittest
from graphserver.gsdll import lgs
from tempfile import NamedTemporaryFile
import os

def tempfile():
    return NamedTemporaryFile(delete=False)

class TestGraphSerialize(unittest.TestCase):
    def setUp(self):
        self.out1 = tempfile()
        self.out2 = tempfile()
        self.g1 = Graph()
        self.g2 = Graph()

    def tearDown(self):
        self.g1.destroy()
        self.g2.destroy()

        try: os.unlink(self.out1.name)
        except: pass
        try: os.unlink(self.out2.name)
        except: pass

    def inout(self):
        self.g1.serialize(self.out1.name, self.out2.name)
        self.g2.deserialize(self.out1.name, self.out2.name)
    
    def test_vertices(self):
        nv = 10
        for i in xrange(10):
            self.g1.add_vertex(str(i))
        self.inout()
        self.assertEquals(self.g2.size, nv);

    def test_link_edge(self):
        self.g1.add_vertex("A")
        self.g1.add_vertex("B")
        self.g1.add_edge("A","B", Link())
        self.inout()
        self.assertEquals(self.g2.size, 2)
        print self.g2.vertices
        self.assertTrue(self.g2.get_vertex("A") != None)

if __name__ == '__main__':

    unittest.main()
