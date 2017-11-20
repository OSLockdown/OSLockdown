#!/bin/sh
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################
. commonEnv.sh
java -classpath ${JAXJARS}:../build/dist/clientregistrationwsc.jar:${COMMONJARS} com.trustedcs.sb.ws.client.ClientRegistrationCommunicator $*
