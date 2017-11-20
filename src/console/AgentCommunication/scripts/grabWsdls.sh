#!/bin/sh
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################
for service in agent console reports scheduler
do
  curl http://192.168.1.171:8080/agentws/services/$service?wsdl -o "../web/wsdl/$service.wsdl"
done
