#!/bin/sh
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################
#
# Wrapper Script to build all Packages
#
# This is necessary right because the security-modules package
# is getting built with Ant Rpm tasks and the rpmbuild commands
# are not inheriting the working directories correctly.
#


usage()
{
  printf "Usage: %s: -b [-n] [-d] \n"  $0
  printf "     : -b = invoke build - usage shown if missing\n"
  printf "     : -n = do *NOT* build the console (default is to build console)\n"
  printf "     : -d = build PDF documenation\n"
  printf " \n"
  exit 1
}

#Process optional command line arguments intelligently....

#initial values
SB_CONSOLE='y'
SB_DOC_PDFS='n'
BUILD_IT='n'

while getopts dbnr: name
do
     case $name in
     b)      BUILD_IT='y';;
     n)      SB_CONSOLE='n';;
     d)      SB_DOC_PDFS='y';;
     ?)      usage $0;;
     esac
done

if [ ${BUILD_IT} = 'n' ] ; then
  usage $0
fi


export SB_CONSOLE
export SB_DOC_PDFS

echo "SB_CONSOLE = ${SB_CONSOLE}"
echo "SB_DOC_PDFS = ${SB_DOC_PDFS}"


if [ `uname -s` = "SunOS" ] ; then
  makecmd=gmake
else
  makecmd=make
fi

# ensure a clean build tree
${makecmd} -C src/security_modules clean

# we build the modules first, and outside the main build procedure
${makecmd} -C src/security_modules build

# and go build the rest
exec ${makecmd} build


