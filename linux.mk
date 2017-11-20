#=========================================================================
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# OS Lockdown - Master Linux Makefile
# $LastChangedDate: 2017-11-14 14:06:36 -0500 (Tue, 14 Nov 2017) $
# $LastChangedRevision: 24144 $
# $LastChangedBy: rsanders $
# 
# $Id: linux.mk 24144 2017-11-14 19:06:36Z rsanders $
#
#=========================================================================

# Product Name - Do not change! Many directories are based on this name
export NAME = oslockdown

# Where to install the product once built
# If ROOT was not defined on the command-line, 
# then define it now:
export ROOT ?= $(shell pwd)/root

export SECURITY_BLANKET_IS_FULL_BUILD := "YES"

# By default build the Console also.  If SB_CONSOLE=n is on the Make line, then skip
export SB_CONSOLE ?= y

# By default do build the PDF documentation.  
export SB_DOC_PDFS ?= y

ifeq  "$(strip $(shell uname -s))" "Linux"

  export JAVA_HOME ?= /etc/alternatives/java_sdk_1.6.0

  redhat := $(findstring RedHat,$(shell lsb_release -i -s))
  centos := $(findstring CentOS,$(shell lsb_release -i -s))
  fedora := $(findstring Fedora,$(shell lsb_release -i -s))
  suse   := $(findstring SUSE,$(shell lsb_release -i -s))
  ubuntu := $(findstring Ubuntu,$(shell lsb_release -i -s))
  myarch := $(strip $(shell uname -m))

  ifeq "$(redhat)" "RedHat"
      BUILD_BASE := /usr/src/redhat
      ifeq "$(strip $(shell uname -m))" "s390x"
          osName := redhat-s390
      else
          osName := redhat
      endif
  endif

  ifeq "$(centos)" "CentOS"
      osName := redhat
      BUILD_BASE := /usr/src/redhat
  endif

  ifeq "$(fedora)" "Fedora"
      osName := fedora
      BUILD_BASE := ${HOME}/rpmbuild
  endif

  ifeq "$(ubuntu)" "Ubuntu"
      osName := ubuntu
  endif

  ifeq "$(suse)" "SUSE"
      osName := suse
      BUILD_BASE := /usr/src/packages
  endif
endif
include os/$(osName)/utilities.mk

# Platform Information
export OS_DIST := $(shell $(LSB_RELEASE) -i -s)
export OS_REL  := $(shell $(LSB_RELEASE) -r -s |$(CUT) -d. -f1)


ifeq ("$(shell $(UNAME) -m)", "s390x")
    export ARCH := s390x
else 
ifeq ("$(shell $(UNAME) -m)", "x86_64")
    export ARCH := x86_64
else
    export ARCH := i386
endif
endif

#
# Directory/Components Locations within the this tree
#
export TOPDIR           := $(shell pwd)
export BASENAME         := $(notdir $(TOPDIR))
export DISTRO           := $(TOPDIR)/build/dist
export SRCDIR           := $(TOPDIR)/src
export DOCS             := $(TOPDIR)/docs
export CORE             := $(SRCDIR)/core
export CONSOLE          := $(SRCDIR)/console
export SECMODULES       := $(SRCDIR)/security_modules
export DISPATCHER       := $(SRCDIR)/dispatcher
export GPG_KEYRING      := $(TOPDIR)/gpg-keys
export SELINUXDIR       := $(SRCDIR)/selinux


all:

	#$(MAKE) -C $(DOCS) modules-guide
	#$(MAKE) -C $(DOCS) manpages
	$(MAKE) -C $(CORE) 
	@if [ ${SB_CONSOLE} = "n" ] ; then \
	    echo "Skipping CONSOLE build" ;\
	else \
	    $(MAKE) -C $(CONSOLE) ;\
	fi
	$(MAKE) -C $(SECMODULES)
	$(MAKE) -C $(DISPATCHER)
	$(MAKE) -C $(SELINUXDIR)

help:
	@echo "Available build targets:"
	@echo "  all:                     Build all units in place"
	@echo "  docs:                    Build only docs in place"
	@echo "  build_distro_arch     :  Build specific distro/ver/arch packages "
	@echo "    -> dispatcher"
	@echo "  build_distro_ver_noarch: Build distro/ver noarch packages"
	@echo "    -> standalone, modules, selinux(RH5/6 only)"
	@echo "  build_noarch:            Build noarch packages"
	@echo "    -> console, betacerts"
	@echo "  build:                   Build *all* packages"
	@echo "  clean:                   Clean all units"
	@echo "  distclean:               Do full cleanup"
	@echo "  env-setup:               Attempt to pull all required packages to build codebase"

docs:   FORCE
	$(MAKE) -C $(DOCS) clean
	$(MAKE) -C $(DOCS) 

build-docs: FORCE
	-@if [ $(SB_DOC_PDFS) = "y" ] ; then \
	  $(MAKE) -e -C $(DOCS) pdfs && mv ${DOCS}/dist/pdf/*.pdf ${DISTRO}; \
	fi


build:  clean build-docs
	$(RPMDEVSETUP)
	mkdir -p ${DISTRO}
	@echo ${SB_BUILTFOR} > ${DISTRO}/BUILT_FOR

	$(MAKE) -e -C ${CORE} build 

	$(MAKE) -e -C ${DISPATCHER} build

	$(MAKE) -e -C ${SELINUXDIR} build

	@if [ ${SB_CONSOLE} = "n" ] ; then \
	    echo "Skipping CONSOLE build" ;\
	else \
	    $(MAKE) -C ${CONSOLE} build ; \
	    mv ${CONSOLE}/build/dist/*.{rpm,log} ${DISTRO}/ ;\
	    if [ ! -z "${JAVA_HOME2}" ] ; then \
	       echo "Building alternate Java Console" ;\
	       JAVA_HOME="${JAVA_HOME2}" $(MAKE) -C ${CONSOLE} build ;\
	       mv ${CONSOLE}/build/dist/*.{rpm,log} ${DISTRO}/ ;\
	    fi \
	fi

# Do MODULES LAST - the build therein (possibly) clobbers the build environment
	$(MAKE) -e -C ${SECMODULES} build

	$(RM) -f ${BUILD_BASE}/SOURCES/oslockdown.tar
	@echo "================================================================="
	@echo "All packages built: ${DISTRO}"
	@echo "Packages built for target : " `cat ${DISTRO}/BUILT_FOR`
	@echo
	@ls -1 ${DISTRO}/BUILT_FOR ${DISTRO}/*.rpm


clean: FORCE distclean

	$(MAKE) -C $(CORE) clean
	@if [ ${SB_CONSOLE} = "n" ] ; then \
	    echo "Skipping CONSOLE cleanup" ;\
	else \
	    $(MAKE) -C $(CONSOLE) clean ;\
	fi
	$(MAKE) -C $(DISPATCHER) clean
	$(MAKE) -C $(SELINUXDIR) clean
	#
	# Commented out to keep SECMODULES RPM when running build-production.sh
	#$(MAKE) -C $(SECMODULES) clean
	#$(MAKE) -C $(DOCS) clean
	$(TEST) ! -f /tmp/.pkglist || $(RM) /tmp/.pkglist
	@echo

furby:  

distclean:

	-$(RM) -f ${DISTRO}/*.rpm
	-$(RM) -f ${DISTRO}/*.log
	-$(RM) -f ${DISTRO}/*.log
	-$(RM) -f ant-build.log


env-setup:

	@$(TEST) ! -z "$(REQDPKGS)"
	##
	## Checking for required packages for build
	##
	@echo > /tmp/.pkglist
	@for pkg in $(REQDPKGS); do \
	    $(RPM) -q $$pkg 1>/dev/null 2>&1 || printf "%s " $$pkg >> /tmp/.pkglist; \
	done
	@if $(TEST) ! -z "`cat /tmp/.pkglist`" ; then \
	    echo $(PKGINSTALL) `cat /tmp/.pkglist` ;\
	    $(PKGINSTALL) `cat /tmp/.pkglist` ;\
	fi
	$(TEST) ! -f /tmp/.pkglist || $(RM) /tmp/.pkglist
	@echo :: Done

###########################################################################
# Key Management - Targets for Signing Packages 
###########################################################################
setup-keys:
	gpg --homedir ${GPG_KEYRING} --export -a 'OS Lockdown' > RPM-GPG-KEY.SecurityBlanket
	rpm -q gpg-pubkey-a111d000-4cf8f3ae 1>/dev/null 2>&1 || rpm --import RPM-GPG-KEY.SecurityBlanket
	rm -f RPM-GPG-KEY.SecurityBlanket
	@echo ::
	@echo :: All keys in public keyring
	@echo ::
	@rpm -q gpg-pubkey --qf '%{name}-%{version}-%{release} --> %{summary}\n'
	@echo ::
	@echo :: OS Lockdown Package Key
	@echo ::
	@rpm -qi gpg-pubkey-a111d000-4cf8f3ae

list-keys:
	gpg --homedir ${GPG_KEYRING} --list-keys

propset:
	svn propset svn:keywords $(SVN_PROPS_KEYWORDS) Makefile	
	svn propset svn:keywords $(SVN_PROPS_KEYWORDS) *.mk	

FORCE:
