package org.graphserver.core;

import org.graphserver.jna.GraphserverLibrary;

import com.sun.jna.Structure;

public class Graph extends CShadow<org.graphserver.jna.Graph> {
	
	public Graph() {
		super(_dll.gNew());
	}
	public Graph(org.graphserver.jna.Graph g) {
		super(g);
	}
	
	public void addVertex(String v) {
		_dll.gAddVertex(this_, v);
	}
	
	public int getSize() {
		return _dll.gSize(this_);
	}
	
	public void addEdge(String from, String to, Payload p) {
		_dll.gAddEdge(this_, from, to, (org.graphserver.jna.EdgePayload)p.soul());
	}
	
	public void free() {
		_dll.gDestroy(this_, 1);
	}
	public Vertex getVertex(String v) {
		return new Vertex(_dll.gGetVertex(this_, v));
	}
}
