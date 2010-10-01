package org.graphserver.jna.test;

import java.lang.reflect.Method;

import junit.framework.TestCase;

import com.ochafik.lang.jnaerator.runtime.LibraryExtractor;
import com.sun.jna.NativeLibrary;

public class TestJNALibraryAccess extends TestCase {
	public void testLibraryExists() {
		String libname = LibraryExtractor
		.getLibraryPath("graphserver", false,
				Object.class);
		assertNotNull("libname", libname);
	}
	
	public void testLibraryInstanceCreated() throws ClassNotFoundException, SecurityException, NoSuchFieldException {
		ClassLoader cl = TestJNALibraryAccess.class.getClassLoader();
		Class c = cl.loadClass("org.graphserver.jna.GraphserverLibrary");
		assertNotNull(c);
		assertNotNull(c.getField("INSTANCE"));
	}
	
	public void testLibraryMethod() throws ClassNotFoundException, SecurityException, NoSuchFieldException, Exception {
		Class c = TestJNALibraryAccess.class.getClassLoader().loadClass("org.graphserver.jna.GraphserverLibrary");
		Object jnawrapper = c.getField("INSTANCE");
		Method m = c.getMethod("chNew", new Class[]{});
		assertNotNull(m);
		//m.invoke(jnawrapper, new Object[]{});
	}
}
