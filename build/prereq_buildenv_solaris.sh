#!/bin/sh
#=========================================================================
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Build Platform: Solaris 10
#        Product: OS Lockdown
# 
# Verify Packages and Utilities needed for the build environment 
# are installed 
#
#=========================================================================

PATH=/bin:/usr/bin
export PATH

AWK=/usr/xpg4/bin/awk

EXIT_STATUS=0

test -d ./os && UTILSFILE=os/solaris/utilities.mk
test -d ../os && UTILSFILE=../os/solaris/utilities.mk

#
# Packages where are required for the build
#
required_pkg () 
  {
    test -z "$1" && return 0
    printf "  %s" $1
    ${AWK} -v pkgname=$1 'BEGIN {for(i=0;i<40-length(pkgname);i++) printf "." }'
    pkginfo -q $1 1>/dev/null 2>&1 
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
devel_pkg () 
  {
    test -z "$1" && return 0
    printf "  %s" $1
    ${AWK} -v pkgname=$1 'BEGIN {for(i=0;i<40-length(pkgname);i++) printf "." }'
    pkginfo -q $1 1>/dev/null 2>&1 
    if [ $? -eq 0 ]; then
        echo ok
    else
        echo "not installed"
        EXIT_STATUS=1
    fi
    return
 }


##############################################################################
#   Main
##############################################################################

printf "\nPackages required by build environment:\n"
REQUIRED_PKGS="SUNWgcc SUNWPython SUNWPython-devel SUNWgmake SUNWopenssl-commands \
               SUNWopenssl-include SUNWopenssl-libraries SUNWhea SMCswig \
               SUNWscpu SUNWbtool SUNWgzip SUNWxcu4 SUNWpkgcmdsu"
for i in $REQUIRED_PKGS
do
    required_pkg $i
done

UTILS=`${AWK} '/^export/ {printf "%s ", $4} END {printf "\n"}' ${UTILSFILE}`
if [ ! -z "$UTILS" ]; then
    printf "\nVerifying paths specified in os/solaris/utilities.mk:\n"
    for i in $UTILS
    do
        printf "  %s" $i
        ${AWK} -v utilname=$i 'BEGIN {for(i=0;i<40-length(utilname);i++) printf "." }'
        if [ -x "$i" ]; then 
            echo "ok"
        else
            echo "not found"
        fi
    done
fi

printf "\nUseful Packages for Development and Testing:\n"
DEVEL_PKGS="SUNWtoo SUNWbash"
for i in $DEVEL_PKGS
do
    devel_pkg $i
done


printf "\n"
exit $EXIT_STATUS

