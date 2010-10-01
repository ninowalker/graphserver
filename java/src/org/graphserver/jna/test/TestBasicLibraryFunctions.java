package org.graphserver.jna.test;

import junit.framework.TestCase;
import org.graphserver.jna.*;

public class TestBasicLibraryFunctions extends TestCase {
	public void testVertex() {
		Vertex v = GraphserverLibrary.INSTANCE.vNew("Cows");
		assertEquals("Cows", GraphserverLibrary.INSTANCE.vGetLabel(v));
		GraphserverLibrary.INSTANCE.vDestroy(v, 1);
	}
	public void testGraph() {
		GraphserverLibrary i = GraphserverLibrary.INSTANCE;
		Graph g = i.gNew();
		i.gAddVertex(g, "Cows");
		i.gAddVertex(g, "Moo");
		assertEquals(2, i.gSize(g));
		i.gDestroy(g);
	}
}
