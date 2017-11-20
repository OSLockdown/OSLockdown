#!/bin/sh
#=========================================================================
# Copyright (c) 2011-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# OS Lockdown - SELinux Policy helper bui
#
#=========================================================================

poldir=""
if [ -x /bin/rpm ] ; then 
    # First look for a devel package
    polversion=`rpm -q --queryformat="%{VERSION}" selinux-policy`
#    echo "Policy version is ${polversion}" > /dev/stderr
    
    if [ ! -z "${polversion}" ] ; then
    
        for prefix in selinux-policy selinux-policy-devel ;
        do
            candidate="${prefix}-${polversion}"
#            echo "Checking for ${candidate}" > /dev/stderr
# We're allowing for an optional  '_SBTEST' version for easier development/testing
# It take priority over the 'official' build version.
            if [ -d "${candidate}_SBTEST" ] ; then
#                echo "Candidate ${candidate} exists!" > /dev/stderr
                poldir="${candidate}_SBTEST"
                break;
            elif [ -d "${candidate}" ] ; then
#                echo "Candidate ${candidate} exists!" > /dev/stderr
                poldir="${candidate}"
                break;
            fi
        done
    fi
fi

#echo "Poldir is ${poldir}" > /dev/stderr
echo "${poldir}"
