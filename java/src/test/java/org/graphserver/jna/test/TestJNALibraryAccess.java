package org.graphserver.jna.test;

import java.lang.reflect.Field;
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
	
	public void testLibraryInstanceCreated() throws ClassNotFoundException, SecurityException, NoSuchFieldException, Exception, Exception {
		ClassLoader cl = TestJNALibraryAccess.class.getClassLoader();
		Class c = cl.loadClass("org.graphserver.jna.GraphserverLibrary");
		assertNotNull(c);
		assertNotNull(c.getField("INSTANCE").get(c));
		Field libname = c.getField("JNA_LIBRARY_NAME");
		assertEquals("/usr/local/lib/libgraphserver.dylib", (String)libname.get(c));
	}
	
	public void testLibraryMethod() throws ClassNotFoundException, SecurityException, NoSuchFieldException, Exception {
		Class c = TestJNALibraryAccess.class.getClassLoader().loadClass("org.graphserver.jna.GraphserverLibrary");
		Object jnawrapper = c.getField("INSTANCE");
		Method m = c.getMethod("chNew", new Class[]{});
		assertNotNull(m);
		//m.invoke(jnawrapper, new Object[]{});
	}
}
