#=========================================================================
# Copyright (c) 2007-2016 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# OS Lockdown - Master Makefile
#
#=========================================================================

# Product Name - Do not change! Many directories are based on this name


# Where to install the product once built
# If ROOT was not defined on the command-line, 
# then define it now:
export ROOT ?= $(shell pwd)/root
include Makefile_common.mk


export GPG_KEYRING := $(shell pwd)/gpg-keys

# Determine which operating system using uname; then just
# include (execute) the respective Makefile for that operating system

ifeq  "$(strip $(shell uname -s))" "Linux"
   include linux.mk
endif

ifeq  "$(strip $(shell uname -s))" "SunOS" 
   include solaris.mk
endif

fileExists = $(if $(wildcard "$1"),Exists ,MISSING)
checkFile = $(warning isFile $(call fileExists,$2) : $1  = $2)

ifDir = $(if $(shell test -d "$2" && echo 'yes'),YES : $1 = $2 ,NO  : $1)
checkDir = $(warning IsDir  $(call ifDir,$1,$2) )

ifExec = $(if $(shell test -x "$2" && echo 'yes'),YES : $1 = $2 ,NO  : $1)
checkExec = $(warning IsExec $(call ifExec,$1,$2) )

ifExist = $(if $(shell test -f "$2" && echo 'yes'),YES : $1 = $2 ,NO  : $1)
checkExist = $(warning IsExec $(call ifExist,$1,$2) )

envExists = $(if $(shell test -n "$2" && echo 'yes'),YES : $1 = $2 ,NO  : $1)
checkEnv = $(warning Envvar $(call envExists,$1,$2) )
	
testLocations: 	
	$(warning Sanity checking for required environment variables)
	$(call checkEnv,NAME,${NAME})
	$(call checkEnv,SB_VERSION,${SB_VERSION})
	$(call checkEnv,SB_RELEASE,${SB_RELEASE})
	$(call checkDir,SB_HOME,${SB_HOME})
	$(call checkDir,JAVA_HOME,${JAVA_HOME})
	$(call checkExec,$$JAVA_HOME/bin/java,${JAVA_HOME}/bin/java)
	$(call checkExec,$$JAVA_HOME/bin/javac,${JAVA_HOME}/bin/javac)
	$(call checkDir,(optional)JAVA_HOME2,${JAVA_HOME2})
	$(call checkExec,(optional)$$JAVA_HOME2/bin/java,${JAVA_HOME2}/bin/java)
	$(call checkExec,(optional)$$JAVA_HOME2/bin/javac,${JAVA_HOME2}/bin/javac)
	$(call checkDir,GSOAP_HOME,${GSOAP_HOME})
	$(call checkExec,$$GSOAP_HOME/bin/wsdl2h,${GSOAP_HOME}/bin/wsdl2h)
	$(call checkDir,GRAILS_HOME,${GRAILS_HOME})
	$(call checkExist,$$GRAILS_HOME/bin/grails,${GRAILS_HOME}/bin/grails)
	$(call checkDir,SAXON_HOME,${SAXON_HOME})
	$(call checkExist,$$SAXON_HOME/saxon.jar,${SAXON_HOME}/saxon.jar)
	$(call checkDir,FOP_HOME,${FOP_HOME})
	$(call checkExist,$$FOP_HOME/fop,${FOP_HOME}/fop)
	$(call checkDir,JAXWSRI_HOME,${JAXWSRI_HOME})
	$(call checkExis,$$JAXWSRI_HOME/bin/wsget.sh,${JAXWSRI_HOME}/bin/wsgen.sh)
	$(call checkDir,DOCBOOK_STYLESHEETS,${DOCBOOK_STYLESHEETS})
	$(call checkDir,$$DOCBOOK_STYLESHEETS/fo,${DOCBOOK_STYLESHEETS}/fo)
	$(call checkDir,ANT_HOME,${ANT_HOME})
	$(call checkExec,ANT,${ANT})
	$(call checkExist,TOMCAT_ARCHIVE,${TOMCAT_ARCHIVE})
	$(call checkDir,(optional)GRAILS_DEP_HOME,${GRAILS_DEP_HOME})

testArch: FORCE
	@echo "Build Architecture is = ${SB_BUILTFOR}"
	@echo "Dest directory is ${DISTRO}"
FORCE:
