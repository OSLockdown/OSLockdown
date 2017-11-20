#=========================================================================
# Copyright (c) 2011-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# OS Lockdown - SELinux Policy Module
#
#
#=========================================================================

export ROOT ?= $(shell pwd)/root
export THISDIR ?= $(shell pwd)

#include ../../Makefile_common.mk

MAKE ?= /usr/bin/make



export RPMBUILD   := /usr/bin/rpmbuild
export GNUPGHOME := ${THISDIR}/../../gpg-keys
export DISTRO   := ${THISDIR}/build/dist

export SPECFILE ?= ${THISDIR}/build/oslockdown-selinux.spec

OS_TYPE := $(strip $(shell uname -s))
ifneq ("${OS_TYPE}", "SunOS")
   THISBOX := $(shell lsb_release -i -r -s )
else
   THISBOX := "SunOS"
endif

DEVEL_RPM := $(shell sh ./determine_policy_version.sh)



ifneq ("${DEVEL_RPM}", "")
    INSTALL_TARGET     := install-supported
    CLEAN_TARGET       := clean-supported
    MODULE_TARGET      := module-supported
    BUILD_TARGET       := build-supported
    SIGN-RPM_TARGET    := sign-rpm-supported
    LOAD-MODULE_TARGET := load-module-supported
else
    INSTALL_TARGET     := unsupported
    CLEAN_TARGET       := unsupported
    MODULE_TARGET      := unsupported
    BUILD_TARGET       := unsupported
    SIGN-RPM_TARGET    := unsupported
    LOAD-MODULE_TARGET := unsupportedendif
endif



all: module 
	@echo

install:     ${INSTALL_TARGET}

clean:       ${CLEAN_TARGET}

module:      ${MODULE_TARGET}

build:       ${BUILD_TARGET}

sign-rpm:    ${SIGN-RPM_TARGET}

load-module: ${LOAD-MODULE_TARGET}

unsupported:  
	@echo :: 
	@echo :: "Building SELinux policy not supported on ${THISBOX}"
	@echo :: "Touching build/dist/selinux.log to keep top level make happy"
	@echo ::
	@touch dist/selinux.log

install: ${INSTALL}        

install-supported:
	${MAKE} -C ${DEVEL_RPM} install

clean: ${CLEAN}

clean-supported: 
	${MAKE} -C ${DEVEL_RPM} clean

module: ${MODULE}

module-supported:  
	${MAKE} -C ${DEVEL_RPM} module

build: ${BUILD}

build-supported: clean 
	${MAKE} -C ${DEVEL_RPM} build

        
sign-rpm: ${SIGN-RPM}

sign-rpm-supported:
	${MAKE} -C ${DEVEL_RPM} sign-rpm

load-module: ${LOAD-MODULE}

load-module-supported: module
	${MAKE} -C ${DEVEL_RPM} load-module

FORCE:
