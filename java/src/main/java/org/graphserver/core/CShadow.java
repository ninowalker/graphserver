package org.graphserver.core;

import org.graphserver.jna.GraphserverLibrary;

import com.sun.jna.Pointer;
import com.sun.jna.Structure;

public abstract class CShadow<T> {

	protected static final GraphserverLibrary _dll = GraphserverLibrary.INSTANCE;
	
	protected T this_;

	public CShadow(T soul) {
		this_ = soul;
	}
	
	public CShadow() {
		this(null); 
	}
	
	public Structure soul() {
		return (Structure)this_;
	}
	
	public Pointer getPointer() {
		return this_ == null ? null : ((Structure)this_).getPointer();
	}
	
	public abstract void free();
}