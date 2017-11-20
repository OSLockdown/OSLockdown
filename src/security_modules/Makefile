#=============================================================================
# Copyright (c) 2009-2015 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# OS Lockdown - Security Modules Makefile
#
#
#=============================================================================

# Pick up locations for commands...
include ../../Makefile_common.mk

# Where to install the product once built
# If ROOT was not defined on the command-line, 
# then define it now:
ROOT ?= $(shell pwd)/root

DISTRO   := build/dist

###############################################################################################

.DEFAULT_GOAL := modules

modules: TEST_PREREQUISITES
	$(ANT) modules

validate: TEST_PREREQUISITES
	$(ANT) validate

validateProfiles:
	(cd cfg ; python validateProfiles.py)

masterList: FORCE
	cd cfg && rm -f security-modules.xml_NEW && python cfgMasterXML.py -x security-modules.xml_NEW -d prod_sources -j
	cd cfg && mv security-modules.xml_NEW security-modules.xml

build:   TEST_PREREQUISITES masterList
	$(RPMDEVSETUP)
	$(ANT) clean-modules

	# Until we can get the svnant tasks working, we must pass the version property to ant
	#$(ANT) -Dsvn.revision=${SB_RELEASE} -Dsb.version=${SB_VERSION}-${SB_RELEASE} dist 
	$(ANT) dist 
	
	-mkdir ${DISTRO}
	-mv dist/*.pkg ${DISTRO}/
	-mv dist/*.log ${DISTRO}/
	-mv dist/*.rpm ${DISTRO}/
	@echo "Done moving files"

clean: TEST_PREREQUISITES
	$(ANT) clean-modules

TEST_PREREQUISITES:
	#Check for *valid* ANT facility 
	@if [ ! -f "${ANT}"  ]; then \
		echo "${ANT} does not exist";  \
		exit 1; \
	fi
	@if [ ! -x "${ANT}"  ]; then \
		echo "${ANT} does not appear to be an executable";  \
		exit 1; \
	fi


FORCE:

