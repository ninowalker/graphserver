package org.graphserver.core;

public class Vertex extends CShadow<org.graphserver.jna.Vertex> {

	public Vertex(org.graphserver.jna.Vertex v) {
		super(v);
	}
	public Vertex(String s) {
		super(_dll.vNew(s));
	}
	
	public String getLabel() {
		return _dll.vGetLabel(this_);
	}
	
	@Override
	public void free() {
		_dll.vDestroy(this_, 0);
	}

}
