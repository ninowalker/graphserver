package org.graphserver.core.test;

import org.graphserver.core.*;

import junit.framework.TestCase;

public class TestGraph extends TestCase {

	public void testGraphCreate() {
		Graph g = new Graph();
		for (int i = 0; i < 1000; i++) {
			g.addVertex("" + i);
		}
		assertEquals(1000, g.getSize());
		for (int i = 0; i < 1000; i++) {
			assertNotNull(g.getVertex("" + i));
			assertEquals(g.getVertex("" + i).getLabel(), "" + i);
		}
		
		g.free();
	}
	
}
