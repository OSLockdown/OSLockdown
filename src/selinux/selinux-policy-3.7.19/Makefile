#=========================================================================
# Copyright (c) 2011-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# OS Lockdown - SELinux Policy Module
#
#=========================================================================

export ROOT ?= $(shell pwd)/root

MAKE ?= /usr/bin/make

include ../../../Makefile_common.mk
export SHAREDIR := /usr/share/selinux/devel

ifneq ($(wildcard ${SHAREDIR}),)
  ${$(error SELinux policy development source not found at ${SHAREDIR})
endif
export SELINUX_MAKEFILE := ${SHAREDIR}/Makefile
$(warning SELINUX_MAKEFILE = ${SELINUX_MAKEFILE})

LINUX_TYPE        := $(shell lsb_release -i -s)

# Different Linux distros define where RPMs are built in different
# places, and rather than parse this out (based on *actual* distro
# and version) we'll just force build things where we want
# to.  By default, this will be in each the 'rpmbuilddir' directory for
# this module.

BUILD_BASE := $(shell pwd)/rpmbuilddir

# The following directories are excluded when a tar file is created during the
# package build process. They are not needed to build this package so, the more
# we can exclude the faster the RPM build will be.
export EXCLUDE_SRC_DIRS := --exclude=oslockdown/src/console  \
                           --exclude=oslockdown/src/dispatcher \
                           --exclude=oslockdown/src/security_modules \
                           --exclude=oslockdown/src/core \
                           --exclude=oslockdown/cfg/docs \
                           --exclude=oslockdown/docs

OS_TYPE := $(strip $(shell uname -s))
ifneq ("${OS_TYPE}", "SunOS")
   LINUX_TYPE := $(shell lsb_release -i -s)
   OS_RELEASE := $(shell lsb_release -r -s | cut -d '.' -f 1)

   ifeq ("${LINUX_TYPE}", "SUSE LINUX")
      include ../../../os/suse/utilities.mk
   endif

   ifeq ("${LINUX_TYPE}", "Fedora")
      include ../../../os/fedora/utilities.mk
   endif

   ifeq ("${LINUX_TYPE}", "Ubuntu")
      include ../../../os/ubuntu/utilities.mk
      JAVA_HOME  := /usr/lib/jvm/java-6-openjdk
      JAVA_INCS  := -I${JAVA_HOME}/include -I${JAVA_HOME}/include/linux
      ROOT := $(shell pwd)/build/debian
      BUILDTARGET := build-ubuntu
   endif

   ifeq ("${LINUX_TYPE}", "CentOS")
      include ../../../os/redhat/utilities.mk
   endif   

   # Red Hat ES 4.8 is annoying, too
   ifeq ("${LINUX_TYPE}", "RedHatEnterpriseES")
      include ../../../os/redhat/utilities.mk
   endif

   ifeq ("${LINUX_TYPE}", "RedHatEnterpriseServer")
      include ../../../os/redhat/utilities.mk
      # Red Hat 6.x build system is like Fedora
      ifeq ("${OS_RELEASE}", "6")
          RPMDEVSETUP := /usr/bin/rpmdev-setuptree
      endif 
   endif   
endif
	
.DEFAULT_GOAL := all
	
all: module 
	@echo


install:
	install -m 0750 -o root -g root -d ${ROOT}/usr/share/oslockdown/selinux
	install -m 0440 -o root -g root oslockdown.pp ${ROOT}/usr/share/oslockdown/selinux
	install -m 0440 -o root -g root TransitionSBtoOSL.pp ${ROOT}/usr/share/oslockdown/selinux


clean: 
	test -f ${SELINUX_MAKEFILE} && $(MAKE) -f ${SELINUX_MAKEFILE} clean
	test ! -d root || rm -rf root
	-rm -rf dist/build_selinux.log rpmbuilddir

module:  
	@echo :: 
	@echo :: Building SELinux Policy Module
	@echo :: 
	$(MAKE) -f ${SHAREDIR}/Makefile

build: clean 
	@echo ## 
	@echo ## Creating RPM build directories if required....
	@echo ##
	mkdir -p ${BUILD_BASE}/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

	echo "Creating tarball to build RPM using ${SPECFILE}"; \
	$(TAR) -C ../../../.. ${EXCLUDE_SRC_DIRS} ${COMMON_EXCLUDES} -czf ${BUILD_BASE}/SOURCES/oslockdown.tar.gz oslockdown ; 
	-mkdir -p ${DISTRO}
	$(RPMBUILD) --define "_topdir ${BUILD_BASE}" -bb  ${SPECFILE} 2>&1 |tee ${DISTRO}/build_selinux.log 
	-mv ${BUILD_BASE}/RPMS/noarch/oslockdown-selinux*.rpm ${DISTRO}/

sign-rpm:
	@echo ::
	@echo ":: Signing Package(s)"
	@echo ::
	rpm --define "_gpg_name OS Lockdown" --addsign dist/oslockdown-selinux*rpm
	@echo ::
	rpm --checksig dist/oslockdown-selinux-*.rpm

load-module: module
	/usr/sbin/semodule -v -i oslockdown.pp 
	/sbin/restorecon -F  /var/log/oslockdown-dispatcher.log
	/sbin/restorecon -F /sbin/SB_Dispatcher
	/sbin/restorecon -F -R /usr/share/oslockdown
	/sbin/restorecon -F -R /var/lib/oslockdown
	/sbin/restorecon -F /etc/init.d/sb*
	/sbin/restorecon -F /sbin/SB_Dispatcher
	/sbin/restorecon -F /usr/sbin/oslockdown
	

FORCE:
