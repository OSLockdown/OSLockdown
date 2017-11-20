#!/bin/sh
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################
JAXWS_VERSION=jaxws-ri-2.2.5
THIRDPARTY_DIR=../../thirdparty
JAXJARS=`find ${THIRDPARTY_DIR}/${JAXWS_VERSION}/lib -name '*.jar' | sed -e :a -e '/$/N;s/\n/:/;ta'`
COMMONJARS=../build/dist/testswsc.jar:${THIRDPARTY_DIR}/commons/cli/1.2/commons-cli-1.2.jar:${THIRDPARTY_DIR}/log4j/apache-log4j-1.2.15/log4j-1.2.15.jar
