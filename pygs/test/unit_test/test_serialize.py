from graphserver.core import Vertex, Edge, Link, Street, Graph, NoOpPyPayload
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
        lgs.gSerialize(self.g1.soul, self.out1.name, self.out2.name)
        lgs.gDeserialize(self.g2.soul, self.out1.name, self.out2.name)
    

    def test_errors(self):
       self.assertRaises(IOError, self.g1.serialize, "/dev/asdfafsdaf")
       self.assertRaises(IOError, self.g1.serialize, "/dev/asdfafsdaf", True)
       self.g1.add_vertices(('a','b'))
       self.g1.add_edge('a','b', NoOpPyPayload(5))
       self.assertRaises(Exception, self.g1.serialize, self.out1.name)

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
        self.assertEquals(len(self.g2.get_vertex("A").outgoing), 1)
        self.assertEquals(len(self.g2.get_vertex("B").outgoing), 0)
        self.assertEquals(len(self.g2.get_vertex("B").incoming), 1)
        self.assertEquals(self.g2.get_vertex("A").outgoing[0].payload.__class__, Link)

    def test_street_edge(self):
        self.g1.add_vertex("A")
        self.g1.add_vertex("B")
        s1_args = ("s1", 2, 2, 2, False)
        s2_args = ("s2", 3, 3, 3, True)
        self.g1.add_edge("A","B", Street(*s1_args))
        self.assertEquals(self.g1.get_vertex("A").outgoing[0].payload.reverse_of_source, False)
        
        self.g1.add_edge("B","A", Street(*s2_args))
        self.inout()
        self.assertEquals(self.g2.size, 2)
        print self.g2.vertices
        self.assertTrue(self.g2.get_vertex("A") != None)
        self.assertEquals(len(self.g2.get_vertex("A").outgoing), 1)
        self.assertEquals(len(self.g2.get_vertex("B").outgoing), 1)
        self.assertEquals(len(self.g2.get_vertex("B").incoming), 1)
        self.assertEquals(self.g2.get_vertex("A").outgoing[0].payload.__class__, Street)
        s1 = self.g2.get_vertex("A").outgoing[0].payload
        s2 = self.g2.get_vertex("B").outgoing[0].payload
        self.assertEquals(s1.name, "s1")
        for e,args in ((s1, s1_args), (s2, s2_args)):
            for f,v in zip(("name","length","rise","fall","reverse_of_source"),args):
                print f,v, getattr(e,f)
                self.assertEquals(getattr(e,f), v)

if __name__ == '__main__':

    unittest.main()
