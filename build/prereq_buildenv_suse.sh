#!/bin/sh
#=========================================================================
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Build Platform: SUSE LINUX (or clone)
#        Product: OS Lockdown
# 
# Verify Packages and Utilities needed for the build environment 
# are installed 
#
#=========================================================================

PATH=/bin:/usr/bin
export PATH

EXIT_STATUS=0

test -d ./os && UTILSFILE=os/suse/utilities.mk
test -d ../os && UTILSFILE=../os/suse/utilities.mk

#
# Packages where are required for the build
#
required_rpm () 
  {
    test -z "$1" && return 0
    printf "  %s" $1
    awk -v pkgname=$1 'BEGIN {for(i=0;i<40-length(pkgname);i++) printf "." }'
    rpm -q $1 1>/dev/null 2>&1 
    if [ $? -eq 0 ]; then
        echo ok
    else
        echo "not installed (required)"
        EXIT_STATUS=1
    fi
    return
  }

#
# Packages where are not required for the build but are useful during development
#
devel_rpm () 
  {
    test -z "$1" && return 0
    printf "  %s" $1
    awk -v pkgname=$1 'BEGIN {for(i=0;i<40-length(pkgname);i++) printf "." }'
    rpm -q $1 1>/dev/null 2>&1 
    if [ $? -eq 0 ]; then
        echo ok
    else
        echo "not found"
        EXIT_STATUS=1
    fi
    return
 }


##############################################################################
#   Main
##############################################################################

printf "\nRPMs required by build environment:\n"
REQUIRED_RPMS="gcc gcc-c++ swig make libxml2-devel libopenssl-devel python \
              python-devel rpm lsb linux-kernel-headers"
for i in $REQUIRED_RPMS
do
    required_rpm $i
done

UTILS=`awk '/^export/ {printf "%s ", $4} END {printf "\n"}' ${UTILSFILE}`
if [ ! -z "$UTILS" ]; then
    printf "\nVerifying paths specified in os/suse/utilities.mk:\n"
    for i in $UTILS
    do
        printf "  %s" $i
        awk -v utilname=$i 'BEGIN {for(i=0;i<40-length(utilname);i++) printf "." }'
        if [ -x "$i" ]; then 
            echo "ok"
        else
            echo "missing or not executable"
        fi
    done
fi

printf "\nUseful Packages for Development and Testing:\n"
DEVEL_RPMS="subversion pylint splint valgrind strace"
for i in $DEVEL_RPMS
do
    devel_rpm $i
done


printf "\n"
exit $EXIT_STATUS

