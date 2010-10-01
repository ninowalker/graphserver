#!/bin/sh

HEADERS="../core/*.h ../core/edgetypes/*.h"

java -jar lib/jnaerator-0.9.4.jar -library graphserver $HEADERS -o src -noJar -noComp -noMangling -package org.graphserver.jna
