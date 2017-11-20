#=========================================================================
# Copyright (c) 2007-2016 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# OS Lockdown - Master Makefile common elements 
#
#
#=========================================================================
#=========================================================================
#
# Other Makefiles should include this to ensure common paths to these
# utilities.
#
#=========================================================================

# If SB_HOME is *not* set then figure it out as a relative path from the 
# list of includes processed so far - we (this file) should be the last
# file.  So take the abspath of the last file

# Doing this specifically for *force* absolute recursive assignment if it isn't defined...

ifeq ($(origin SB_HOME), undefined)
  # Ok, ugly, but RHEL4 and Solaris 10 by default have gmake 3.80, which doesn't have lastword, abspath, etc
  export SB_HOME := $(shell python -c 'import sys,os; print os.path.dirname(os.path.abspath("${MAKEFILE_LIST}".split()[-1]))')
endif

# Product Name - Do not change! Many directories are based on this name
export NAME       ?= oslockdown
export SB_VERSION ?= 5.0.0
export SB_RELEASE ?= opensource

# Ok, we need to positively identify the distro we're being built on
# This is because we normally build once for each distro major#/arch combination
# *BUT* we need to distinguish between suse/opensuse, and more importantly 
# we need to know absolutely if we're building on opensuse11 sp3 and sp4, as
# each of these must be treated effectively as separate 'major distributions'
# Note that we are not drilling down for an *exact* name all the time - all
# of the RHEL/CentOS/Oracle/SciLi platforms are 'the same'.  
# The aim is to build a 'BUILD_ARCH' string that will be put in the RELEASE
# field of the RPMs, so we can detect *WHAT* that RPM is for when handling
# autoupdates.  The BUILD_ARCH is a trifecta of DISTRO, VERSION, ARCH

export SB_BUILTFOR          := $(shell python ${SB_HOME}/src/console/autoupdate/DetermineOS.py -s)
export SB_BUILTFOR_PLATFORM := $(shell python ${SB_HOME}/src/console/autoupdate/DetermineOS.py -s | cut -d "-" -f1)
export SB_BUILTFOR_RELEASE  := $(shell python ${SB_HOME}/src/console/autoupdate/DetermineOS.py -s | cut -d "-" -f2)
#$(warning SB_BUILTFOR = ${SB_BUILTFOR})

# For Linux - this is the top level of directories we're excluding when
# we create a tarball to build an RPM from.  Each subdirectory can
# add more entries.  For example, when building the SELinux rpms we
# don't need any docs, or anything from the other units.
# This is ignored under Solaris
export COMMON_EXCLUDES := --exclude=*.rpm \
			      --exclude=*.log \
			      --exclude=*.pkg \
			      --exclude='.svn' \
			      --exclude=rpmbuilddir \
			      --exclude=externals
