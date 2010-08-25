#!/usr/bin/env python2.6
import libgraphserver_swig as lgs
import pickle


class TestSWIG:
    def test_laundry(self):
        g = lgs.Graph(1)
        assert g.size == 0
        g.add_vertex("Foo")
        g.add_vertex("Bar")
        assert g.size == 2
        assert g.get_vertex("Foo") != None
        assert g.get_vertex("Cow") == None
        g.add_edge("Foo", "Bar", lgs.Link())
        s = lgs.Street("foo", 10)
        assert s.name == 'foo'
        assert s.length == 10
        assert s.walk
        
        s1 = pickle.loads(pickle.dumps( s ))
        assert s1.name == s.name
        assert s1.length == s.length
        
        g.add_edge("Foo", "Bar", lgs.Street("Foo2Bar", 40))
            
        try:
            g.add_edge("Foo", "Bar2", lgs.Link())
            assert False
        except lgs.VertexNotFoundError: pass
        assert map(lambda x: x.label, g.vertices()) == ['Foo', 'Bar']
        
        map(lambda x: x.to_xml(), g.edges())
        
        v = g.get_vertex("Foo")
        assert v
        #assert len(v.incoming) == 0
        #assert len(v.outgoing) == 2
        #print v.outgoing 
        assert len(v.outgoing_edges()) == 2, v.outgoing_edges()
        assert len(v.incoming_edges()) == 0
        assert v.get_outgoing_edge(0).payload.name == "Foo2Bar", v.get_outgoing_edge(0)
        
        wo = lgs.WalkOptions()
        wo.del_patch_graph = True
        del wo
        
        sp = lgs.ServicePeriod(0, 10000, [1,2,3,4])
        assert sp.n_service_ids == 4
        assert sp.get_service_id_at(0) == 1
        assert sp.get_service_id_at(3) == 4
        assert sp.service_ids == [1,2,3,4]
        
        del g
        
        g = lgs.Graph()
        for i in xrange(100):
            g.add_vertex(str(i).zfill(3))
        for i in xrange(1,100):
            g.add_edge(str(i-1).zfill(3), str(i).zfill(3), lgs.Street("FOO", (i-1)+i))
        
        spt = g.shortest_path_tree("010", "020", lgs.State(0,0))
        assert spt
        assert spt.get_vertex("010").label == "010"
        assert spt.get_vertex("020")
        assert not spt.get_vertex("021")
        assert len(list(spt.vertices())) == 11, len(list(spt.vertices()))
        assert len(list(spt.edges())) == 10, len(list(spt.edges()))
        del spt
        pi = g.shortest_path("010", "020", lgs.State(0,0))
        assert pi
        assert pi.num_vertices == 11, pi.num_vertices
        assert pi.get_vertex(0)
        assert pi.get_vertex(0).label == "010"
        assert pi.get_edge(0).name == 'FOO'
        assert pi.get_vertex(10).label == "020"
        for i in xrange(1, pi.num_vertices):
            assert pi.get_vertex(i).label == str(i+10).zfill(3)
            assert pi.get_edge(i-1).name == 'FOO'
            assert pi.get_edge(i-1).length == i*2+19
        del pi
        print "Passed"
