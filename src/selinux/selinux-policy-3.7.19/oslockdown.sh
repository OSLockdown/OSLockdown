#!/bin/sh
##############################################################################
# Copyright (c) 2011-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################

DIRNAME=`dirname $0`
cd $DIRNAME
USAGE="$0 [ --update ]"
if [ `id -u` != 0 ]; then
echo 'You must be root to run this script'
exit 1
fi

if [ ! -f /usr/share/selinux/devel/Makefile ]; then
echo 'selinux-policy-devel not installed, package required for building policy'
echo '# yum install selinux-policy-devel'
exit 1
fi

if [ $# -eq 1 ]; then
	if [ "$1" = "--update" ] ; then
		time=`ls -l --time-style="+%x %X" oslockdown.te | awk '{ printf "%s %s", $6, $7 }'`
		rules=`ausearch --start $time -m avc --raw -se oslockdown`
		if [ x"$rules" != "x" ] ; then
			echo "Found avc's to update policy with"
			echo -e "$rules" | audit2allow -R
			echo "Do you want these changes added to policy [y/n]?"
			read ANS
			if [ "$ANS" = "y" -o "$ANS" = "Y" ] ; then
				echo "Updating policy"
				echo -e "$rules" | audit2allow -R >> oslockdown.te
				# Fall though and rebuild policy
			else
				exit 0
			fi
		else
			echo "No new avcs found"
			exit 0
		fi
	else
		echo -e $USAGE
		exit 1
	fi
elif [ $# -ge 2 ] ; then
	echo -e $USAGE
	exit 1
fi

echo "Building and Loading Policy"
set -x
make -f /usr/share/selinux/devel/Makefile
/usr/sbin/semodule -i oslockdown.pp

# Fixing the file context on /usr/sbin/oslockdown
/sbin/restorecon -F -R -v /usr/sbin/oslockdown
# Fixing the file context on /var/lib/oslockdown
/sbin/restorecon -F -R -v /var/lib/oslockdown
# Fixing the file context on /usr/share/oslockdown
/sbin/restorecon -F -R -v /usr/share/oslockdown
