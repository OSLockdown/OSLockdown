##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################
#
# OS Lockdown - Standalone (Core) Makefile
#
##############################################################################


include ../../Makefile_common.mk
\
# Where to install the product once built
# If ROOT was not defined on the command-line, 
# then define it now:
ROOT ?= $(shell pwd)/root

SPECFILE := build/oslockdown.spec
DISTRO   := build/dist
SRCLIB   := ../../srclib/


export PKGARCH ?= $(shell uname -m)

# The following directories are exlcuded when a tar file is created for the
# package build process. They are not needed to build this package so, the more
# we can exclude the faster the RPM build will be.
export EXCLUDE_SRC_DIRS := --exclude=oslockdown/src/console  \
                           --exclude=oslockdown/src/dispatcher \
                           --exclude=oslockdown/src/security_modules \
			   --exclude=oslockdown/src/selinux \
                           --exclude=oslockdown/cfg/docs \
                           --exclude=oslockdown/docs

OS_TYPE := $(strip $(shell uname -s))

# Different Linux distros define where RPMs are built in different
# places, and rather than parse this out (based on *actual* distro
# and version) we'll just force build things where we want
# to.  By default, this will be in each the 'rpmbuilddir' directory for
# this module.

BUILD_BASE := $(shell pwd)/rpmbuilddir

ifeq ("${OS_TYPE}", "SunOS")
   include ../../os/solaris/utilities.mk
   BUILDTARGET := build-solaris
   INSTALLTARGET := install-solaris
   PKGINFO := build/solaris/pkginfo
   PYLIBHOME := $(shell pwd)/build/solaris/root/usr/share/oslockdown
   ifeq ("${PKGARCH}", "sun4u")
      PKGARCH := sparc
      ARCHTEST := build/solaris/sparc-test
   endif 
   ifeq ("${PKGARCH}", "i86pc")
      ARCHTEST := build/solaris/x86-test
   endif
   WHITE_SUID := cfg/solaris/suid_whitelist
   WHITE_SGID := cfg/solaris/sgid_whitelist
else

   OS_RELEASE := $(shell lsb_release -r -s)
   LINUX_TYPE := $(shell lsb_release -i -s)
   export ARCH    ?= $(shell $(UNAME) -m)
   export OS_DIST ?= $(shell $(LSB_RELEASE) -i -s)
   export OS_REL  ?= $(shell $(LSB_RELEASE) -r -s |$(CUT) -d. -f1)

   BUILDTARGET := build-linux
   INSTALLTARGET := install-linux

   ifeq ("${LINUX_TYPE}", "SUSE LINUX")
      include ../../os/suse/utilities.mk
      WHITE_SUID := cfg/suse/suid_whitelist
      WHITE_SGID := cfg/suse/sgid_whitelist
   endif

   ifeq ("${LINUX_TYPE}", "Fedora")
      include ../../os/fedora/utilities.mk
      WHITE_SUID := cfg/fedora/suid_whitelist
      WHITE_SGID := cfg/fedora/sgid_whitelist
   endif

   ifeq ("${LINUX_TYPE}", "CentOS")
      include ../../os/redhat/utilities.mk
      WHITE_SUID := cfg/redhat/suid_whitelist
      WHITE_SGID := cfg/redhat/sgid_whitelist
   endif   

   ifeq ("${LINUX_TYPE}", "RedHatEnterpriseServer")
      include ../../os/redhat/utilities.mk
      # Red Hat 6.0 build system is like Fedora
      ifeq ("${OS_REL}", "6")
          RPMDEVSETUP := /usr/bin/rpmdev-setuptree
      endif 
      WHITE_SUID := cfg/redhat/suid_whitelist
      WHITE_SGID := cfg/redhat/sgid_whitelist
   endif   

   # Red Hat ES 4.8 is annoying, too
   ifeq ("${LINUX_TYPE}", "RedHatEnterpriseES")
      include ../../os/redhat/utilities.mk
      WHITE_SUID := cfg/redhat/suid_whitelist
      WHITE_SGID := cfg/redhat/sgid_whitelist
   endif   

   # Oracle Enterprise Linux is annoying...
   ifeq ("${LINUX_TYPE}", "EnterpriseEnterpriseServer")
      include ../../os/redhat/utilities.mk
      WHITE_SUID := cfg/redhat/suid_whitelist
      WHITE_SGID := cfg/redhat/sgid_whitelist
   endif   
 
   ifeq ("${LINUX_TYPE}", "Ubuntu")
      include ../../os/ubuntu/utilities.mk
      BUILDTARGET := build-ubuntu
      ROOT := build/debian
      WHITE_SUID := cfg/ubuntu/suid_whitelist
      WHITE_SGID := cfg/ubuntu/sgid_whitelist
   endif

endif

PROGPY := $(wildcard *.py)
PROG   := $(patsubst %.py,%.pyo,$(PROGPY))

STYLESHEETS := $(wildcard ../xsl/*.xsl)
SCHEMAS     := $(wildcard ../../cfg/schema/*.xsd)

PYLINT  := /usr/bin/pylint


# Python Version is important when using swig and compiling
# C-coded Python bindings. The version is to determine the include path
export PYTHON_VERS    := $(shell $(PYTHON) -V 2>&1 |$(CUT) -c8-10 )
export PYTHON_CMD     := $(PYTHON) -OO -c 
export PYTHON_COMPILE := import sys,compileall,re; ret = compileall.compile_dir

##############################################################################
.DEFAULT_GOAL := all


all: 

	##
	## Build Python Bytecode
	##
	$(PYTHON_CMD) "${PYTHON_COMPILE}('.', rx=re.compile('/[.]svn|templates|tools'), force=1); sys.exit(ret ^ 1)"



install: $(INSTALLTARGET)
	@echo


##############################################################################
install-dirs-linux: 

	$(TEST) -x $(INSTALL)
	##
	## Create directory structure for core engine
	##
	$(INSTALL) -m 0755 -d ${ROOT}/opt/h/LMGR/data
	$(INSTALL) -m 0755 -d ${ROOT}/usr/bin
	$(INSTALL) -m 0755 -d ${ROOT}/usr/sbin
	$(INSTALL) -m 0755 -d ${ROOT}/usr/share/applications
	$(INSTALL) -m 0755 -d $(ROOT)/usr/share/man/man8
	$(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME}
	$(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME}/sb_utils
	$(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME}/Baseline
	$(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME}/cfg
	$(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME}/cfg/schema
	$(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME}/cfg/stylesheets
	$(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME}/cfg/stylesheets/txt
	$(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME}/cfg/stylesheets/common

	@echo "Creating sb_utils/ subdirectories"
	@for sbdirs in `find sb_utils -type d ! -regex '.*/[.]svn.*' -print`; do \
	    $(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME}/$$sbdirs; \
	    printf "." ; \
        done

	@echo "Creating Baseline/ subdirectories"
	@for sbdirs in `find Baseline -type d ! -regex '.*/[.]svn.*' -print`; do \
	    $(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME}/$$sbdirs; \
	    printf "." ; \
        done
	@echo

	$(INSTALL) -m 0750 -d ${ROOT}/usr/share/${NAME}/security_modules
	$(INSTALL) -m 0750 -d ${ROOT}/usr/share/${NAME}/tools
	$(INSTALL) -m 0755 -d ${ROOT}/var/lib/${NAME}
	$(INSTALL) -m 0750 -d ${ROOT}/var/lib/${NAME}/reports/
	$(INSTALL) -m 0750 -d ${ROOT}/var/lib/${NAME}/reports/standalone

	$(INSTALL) -m 0755 -d ${ROOT}/var/lib/${NAME}/files
	$(INSTALL) -m 0750 -d ${ROOT}/var/lib/${NAME}/fs-scan/
	$(INSTALL) -m 0700 -d ${ROOT}/var/lib/${NAME}/profiles
	$(INSTALL) -m 0700 -d ${ROOT}/var/lib/${NAME}/baseline-profiles
	$(INSTALL) -m 0700 -d ${ROOT}/var/lib/${NAME}/backup
	$(INSTALL) -m 0700 -d ${ROOT}/var/lib/${NAME}/logs
	$(INSTALL) -m 0700 -d ${ROOT}/var/lib/${NAME}/files/certs

	$(INSTALL) -m 0755 -d ${ROOT}/etc/logrotate.d/

install-linux: install-dirs-linux

	@$(TEST) -x $(INSTALL)
	@$(TEST) -d ../../cfg/schema/
	@$(TEST) -d ../xsl/
	##
	## Install main programs
	##
	$(INSTALL) -m 750 ${NAME} ${ROOT}/usr/sbin/${NAME}
	$(INSTALL) -m 0440 cfg/exclude-dirs ${ROOT}/var/lib/${NAME}/files
	$(INSTALL) -m 0440 cfg/inclusion-fstypes ${ROOT}/var/lib/${NAME}/files
	$(INSTALL) -m 0440 ${WHITE_SUID} ${ROOT}/var/lib/${NAME}/files
	$(INSTALL) -m 0440 ${WHITE_SGID} ${ROOT}/var/lib/${NAME}/files
	$(INSTALL) -m 0444 cfg/baseline-modules.xml ${ROOT}/usr/share/${NAME}/cfg

	$(INSTALL) -m 0644 $(PROG) ${ROOT}/usr/share/${NAME}

	

	@echo "Installing sb_utils/ files"
	@for sbfile in `find sb_utils -name '*.pyo' -type f ! -regex '.*/[.]svn.*' -print`; do \
	    $(INSTALL) -m 0644 $$sbfile ${ROOT}/usr/share/${NAME}/$$sbfile; \
	    printf "."; \
        done
	@echo 
	@echo "Installing Baseline/ files"
	$(INSTALL) -m 0644 baseline-profile.xml ${ROOT}/var/lib/${NAME}/baseline-profiles/Default.xml
	@for sbfile in `find Baseline -name '*.pyo' -type f ! -regex '.*/[.]svn.*' -print`; do \
	    $(INSTALL) -m 0644 $$sbfile ${ROOT}/usr/share/${NAME}/$$sbfile; \
	    printf "."; \
	done
	@echo 
	$(INSTALL) -m 0644 sb_utils/misc/TCSLogger.pyo ${ROOT}/usr/share/${NAME}/
	$(INSTALL) -m 0644 sb_utils/misc/tcs_utils.pyo ${ROOT}/usr/share/${NAME}/
	$(INSTALL) -m 0640 cfg/logrotate-oslockdown ${ROOT}/etc/logrotate.d/oslockdown

	# Deliver some schema (xsd) files..
	$(INSTALL) -m 0444 ../../cfg/schema/Base*.xsd ${ROOT}/usr/share/${NAME}/cfg/schema
	$(INSTALL) -m 0444 ../../cfg/schema/Asses*.xsd ${ROOT}/usr/share/${NAME}/cfg/schema
	$(INSTALL) -m 0444 ../../cfg/schema/oslockdown-state.xsd ${ROOT}/usr/share/${NAME}/cfg/schema

	# Deliver generic XSL with core engine... the rest are delivered with the console
	$(INSTALL) -m 0444 ../xsl/txt/all-in-one-generic.xsl ${ROOT}/usr/share/${NAME}/cfg/stylesheets/txt/

	$(INSTALL) -m 0444 -o root -g root docs/oslockdown.8 ${ROOT}/usr/share/man/man8
	$(INSTALL) -m 0500 -o root -g root tools/SB_Setup $(ROOT)/usr/share/${NAME}/tools
	$(INSTALL) -m 0400 -o root -g root tools/SB_Remove $(ROOT)/usr/share/${NAME}/tools
	$(INSTALL) -m 0500 -o root -g root tools/PopulateAutoupdate.py $(ROOT)/usr/share/${NAME}/tools
	$(INSTALL) -m 0500 -o root -g root tools/cert_gen.sh $(ROOT)/usr/share/${NAME}/tools
#	$(INSTALL) -m 0500 -o root -g root tools/determine_javahome $(ROOT)/usr/share/${NAME}/tools
	$(INSTALL) -m 0500 -o root -g root tools/JavaHomeUtils.py $(ROOT)/usr/share/${NAME}/tools
	$(INSTALL) -m 0500 -o root -g root tools/shell_utils $(ROOT)/usr/share/${NAME}/tools

	@echo 
        
##############################################################################
install-dirs-solaris:

	###########################################################
	### Solaris MUST have its own install-dirs target because
	### it's system directories have such different ownerships
	###########################################################
	test ! -d build/solaris/root || rm -rf build/solaris/root
	##
	## Standard Solaris directory structures
	##
	$(INSTALL) -d -m 0755 -o root -g sys build/solaris/root/etc
	$(INSTALL) -d -m 0755 -o root -g sys build/solaris/root/etc/default
	$(INSTALL) -d -m 0755 -o root -g sys build/solaris/root/var 
	$(INSTALL) -d -m 0755 -o root -g sys build/solaris/root/usr 
	$(INSTALL) -d -m 0755 -o root -g bin build/solaris/root/lib
	$(INSTALL) -d -m 0755 -o root -g bin build/solaris/root/usr/bin
	$(INSTALL) -d -m 0755 -o root -g bin build/solaris/root/usr/sbin
	$(INSTALL) -d -m 0755 -o root -g sys build/solaris/root/usr/share 
	$(INSTALL) -d -m 0755 -o root -g other build/solaris/root/var/lib 

	$(INSTALL) -d -o root -g bin -m 0755 build/solaris/root/usr/share/man
	$(INSTALL) -d -o root -g bin -m 0755 build/solaris/root/usr/share/man/man1m

	##
	## Service Management Facility (SMF) directories
	##
	$(INSTALL) -o root -g bin -m 0755 -d build/solaris/root/lib/svc
	$(INSTALL) -o root -g bin -m 0755 -d build/solaris/root/lib/svc/method
	$(INSTALL) -o root -g sys -m 0755 -d build/solaris/root/var/svc
	$(INSTALL) -o root -g sys -m 0755 -d build/solaris/root/var/svc/manifest
	$(INSTALL) -o root -g sys -m 0755 -d build/solaris/root/var/svc/manifest/site


	##
	## Application specific
	##
	$(INSTALL) -d -m 0755 -o root -g root build/solaris/root/usr/share/${NAME}  
	$(INSTALL) -d -m 0755 -o root -g root build/solaris/root/usr/share/${NAME}/lib
	$(INSTALL) -d -m 0755 -o root -g root build/solaris/root/var/lib/${NAME}

	$(INSTALL) -d -m 0755 -o root -g root build/solaris/root/usr/share/${NAME}/sb_utils
	$(INSTALL) -d -m 0755 -o root -g root build/solaris/root/usr/share/${NAME}/Baseline
	$(INSTALL) -d -m 0755 -o root -g root build/solaris/root/usr/share/${NAME}/cfg
	$(INSTALL) -d -m 0755 -o root -g root build/solaris/root/usr/share/${NAME}/cfg/schema
	$(INSTALL) -d -m 0755 -o root -g root build/solaris/root/usr/share/${NAME}/cfg/stylesheets
	$(INSTALL) -d -m 0755 -o root -g root build/solaris/root/usr/share/${NAME}/cfg/stylesheets/txt

	@echo "Creating sb_utils/ subdirectories..."
	@for sbdirs in `find sb_utils -type d -print |egrep -v .svn `; do \
	    $(INSTALL) -d -m 0755 -o root -g root build/solaris/root/usr/share/${NAME}/$$sbdirs; \
	    printf "." ; \
        done

	@echo "Creating Baseline/ subdirectories..."
	@for sbdirs in `find Baseline -type d -print |egrep -v .svn `; do \
	    $(INSTALL) -d -m 0755 -o root -g root build/solaris/root/usr/share/${NAME}/$$sbdirs; \
	    printf "." ; \
        done
	@echo

	$(INSTALL) -d -o root -g root -m 0750 -d build/solaris/root/usr/share/${NAME}/security_modules
	$(INSTALL) -d -o root -g root -m 0750 -d build/solaris/root/usr/share/${NAME}/tools
	$(INSTALL) -d -o root -g root -m 0750 -d build/solaris/root/usr/share/${NAME}/tools/pciids
	$(INSTALL) -d -o root -g root -m 0750 -d build/solaris/root/var/lib/${NAME}/reports/
	$(INSTALL) -d -o root -g root -m 0750 -d build/solaris/root/var/lib/${NAME}/reports/standalone
	$(INSTALL) -d -o root -g root -m 0755 -d build/solaris/root/var/lib/${NAME}/files
	$(INSTALL) -d -o root -g root -m 0750 -d build/solaris/root/var/lib/${NAME}/fs-scan/
	$(INSTALL) -d -o root -g root -m 0700 -d build/solaris/root/var/lib/${NAME}/profiles
	$(INSTALL) -d -o root -g root -m 0700 -d build/solaris/root/var/lib/${NAME}/baseline-profiles
	$(INSTALL) -d -o root -g root -m 0700 -d build/solaris/root/var/lib/${NAME}/backup
	$(INSTALL) -d -o root -g root -m 0700 -d build/solaris/root/var/lib/${NAME}/logs
	$(INSTALL) -d -o root -g root -m 3750 -d build/solaris/root/var/lib/${NAME}/files/certs

install-solaris: install-dirs-solaris

	##
	## Installing Solaris files
	##
	$(TEST) -x $(INSTALL)
	$(TEST) -d ../../cfg/schema/
	$(TEST) -d ../xsl/

	$(INSTALL) -m 0750 -o root -g root ${NAME} build/solaris/root/usr/sbin/${NAME}
	$(INSTALL) -m 0440 -o root -g root cfg/exclude-dirs build/solaris/root/var/lib/${NAME}/files
	$(INSTALL) -m 0440 -o root -g root cfg/inclusion-fstypes build/solaris/root/var/lib/${NAME}/files
	$(INSTALL) -m 0440 -o root -g root ${WHITE_SUID} build/solaris/root/var/lib/${NAME}/files
	$(INSTALL) -m 0440 -o root -g root ${WHITE_SGID} build/solaris/root/var/lib/${NAME}/files
	$(INSTALL) -m 0444 -o root -g root cfg/baseline-modules.xml build/solaris/root/usr/share/${NAME}/cfg
	$(INSTALL) -m 0644 -o root -g root $(PROG) build/solaris/root/usr/share/${NAME}

	@echo "Installing sb_utils/ files"
	@for sbfile in `find sb_utils -name '*.pyo' -type f -print |egrep -v .svn`; do \
	    $(INSTALL) -o root -g root -m 0644 $$sbfile build/solaris/root/usr/share/${NAME}/$$sbfile; \
	    printf "."; \
        done
	@echo 
	@echo "Installing Baseline/ files"
	$(INSTALL) -m 0644 -o root -g root baseline-profile.xml build/solaris/root/var/lib/${NAME}/baseline-profiles/Default.xml
	@for sbfile in `find Baseline -name '*.pyo' -type f -print |egrep -v .svn`; do \
	    $(INSTALL) -o root -g root -m 0644 $$sbfile build/solaris/root/usr/share/${NAME}/$$sbfile; \
	    printf "."; \
        done
	@echo 

	$(INSTALL) -m 0644 -o root -g root sb_utils/misc/TCSLogger.pyo build/solaris/root/usr/share/${NAME}/
	$(INSTALL) -m 0644 -o root -g root sb_utils/misc/tcs_utils.pyo build/solaris/root/usr/share/${NAME}/

	$(INSTALL) -m 0444 -o root -g root ../../cfg/schema/*.xsd build/solaris/root/usr/share/${NAME}/cfg/schema
	$(INSTALL) -m 0444 -o root -g root ../xsl/txt/baseline-generic.xsl build/solaris/root/usr/share/${NAME}/cfg/stylesheets/txt/cmdline-baseline-generic.xsl
	$(INSTALL) -m 0444 -o root -g root ../xsl/txt/assessment-generic.xsl build/solaris/root/usr/share/${NAME}/cfg/stylesheets/txt/cmdline-assessment-generic.xsl

	$(INSTALL) -m 0500 -o root -g root tools/SB_Setup build/solaris/root/usr/share/${NAME}/tools
	
	# Note that SB_Remove does *not* have execute perms, it must be sourced
	$(INSTALL) -m 0400 -o root -g root tools/SB_Remove build/solaris/root/usr/share/${NAME}/tools
	$(INSTALL) -m 0500 -o root -g root tools/PopulateAutoupdate.py build/solaris/root/usr/share/${NAME}/tools
	$(INSTALL) -m 0500 -o root -g root tools/cert_gen.sh build/solaris/root/usr/share/${NAME}/tools
#	$(INSTALL) -m 0500 -o root -g root tools/determine_javahome build/solaris/root/usr/share/${NAME}/tools
	$(INSTALL) -m 0500 -o root -g root tools/JavaHomeUtils.py build/solaris/root/usr/share/${NAME}/tools
	$(INSTALL) -m 0500 -o root -g root tools/shell_utils build/solaris/root/usr/share/${NAME}/tools

	##
	## Solaris PCI tools
	##
	$(INSTALL) -o root -g root -m 0500 tools/Solaris/prtpci build/solaris/root/usr/share/${NAME}/tools/prtpci
	@echo "Installing tools/pciids files.."
	@for sbfile in `find tools/Solaris/pciids -name '*.ids' -type f -print |egrep -v .svn`; do \
	    $(INSTALL) -o root -g root -m 0500 $$sbfile build/solaris/root/usr/share/${NAME}/tools/pciids/`basename $$sbfile`; \
        done

	##
	## Install SMF Components
	##
	$(INSTALL) -o root -g bin -m 0555 Solaris-ndd/ndd-config build/solaris/root/lib/svc/method
	$(INSTALL) -o root -g bin -m 0644 Solaris-ndd/ndd-config.xml build/solaris/root/var/svc/manifest/site
	$(INSTALL) -o root -g bin -m 0640 Solaris-ndd/etc_default_ndd build/solaris/root/etc/default/ndd

	@echo 


##############################################################################
clean: FORCE 

	-$(RM) -f *.pyo  
	-$(RM) -f *.pyc  
	-$(RM) -f baseline-test-report.xml

	-$(RM) -f build/dist/*rpm
	-$(RM) -f build/dist/*pkg
	-$(RM) -f build/dist/*deb
	-$(RM) -f build/dist/build_core.log
	-$(RM) -f build/*log
	-$(RM) -rf rpmbuilddir

	# Clean up Debian build
	$(TEST) ! -d build/debian || $(RM) -rf build/debian

	# Clean up Solaris build
	$(TEST) ! -d build/solaris/root || $(RM) -rf build/solaris/root
	$(TEST) ! -d build/solaris/package || $(RM) -rf build/solaris/package
	$(TEST) ! -f build/solaris/Prototype || $(RM) -f build/solaris/Prototype
	$(TEST) ! -f build/solaris/pkginfo || $(RM) -f build/solaris/pkginfo

	@echo "Cleaning *.pyo from sb_utils/ directory..."
	-@for sbfile in `find sb_utils -name '*.pyo' -type f -print |egrep -v .svn `; do \
	    $(RM) -f $$sbfile; \
	    printf "."; \
        done
	@echo

	@echo "Cleaning *.pyo from Baseline/ directory..."
	-@for sbfile in `find Baseline -name '*.pyo' -type f -print |egrep -v .svn `; do \
	    $(RM) -f $$sbfile; \
	    printf "."; \
        done
	@echo

	@echo


##############################################################################
# Build Packages
##############################################################################
build: $(BUILDTARGET)
	@echo

build-ubuntu: FORCE clean all install-dirs-linux install-linux
	@echo "##"
	@echo "## Building Ubuntu package "
	@echo "##"
	mkdir -p build/debian/DEBIAN
	sed 's/^Version: .*/Version: ${SB_VERSION}-${SB_RELEASE}/' build/ubuntu/control > build/debian/DEBIAN/control
	cp build/ubuntu/changelog build/debian/DEBIAN
	dpkg-deb --build build/debian build/dist/oslockdown_${SB_VERSION}-${SB_RELEASE}_all.deb


build-linux: FORCE 
	@echo ## 
	@echo ## Creating RPM build directories if required....
	@echo ##
	mkdir -p ${BUILD_BASE}/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

	$(TEST) -f ${SPECFILE}
        
	echo "Creating tarball to build RPM using ${SPECFILE}"; \
        $(TAR) -C ../../.. ${EXCLUDE_SRC_DIRS} ${COMMON_EXCLUDES} -czf ${BUILD_BASE}/SOURCES/oslockdown.tar.gz oslockdown ; 

	# Build Packages
	$(RPMBUILD) --define "_topdir ${BUILD_BASE}" -bb ${SPECFILE} 2>&1 |$(TEE) ${DISTRO}/build_core.log
	@echo

	# Copy Packages into distro folder
        -mkdir -p ${DISTRO}/
	-mv ${BUILD_BASE}/RPMS/noarch/oslockdown*.rpm ${DISTRO}/


build-solaris: FORCE clean all install
	@echo "Building Solaris package..."
	#
	# Pkginfo 
	#
	printf "PKG=\"TCSoslockdown\"\n" > $(PKGINFO)
	printf "NAME=\"OS Lockdown\"\n" >> $(PKGINFO)
	printf "VERSION=\"%s\"\n" ${SB_VERSION}-${SB_RELEASE} >> $(PKGINFO)
	printf "ARCH=\"%s\"\n" $(PKGARCH) >> $(PKGINFO)
	printf "SUNW_PRODNAME=\"SunOS\"\n" >> $(PKGINFO)
	printf "SUNW_PRODVERS=\"5.10\"\n" >> $(PKGINFO)
	printf "CLASSES=\"none\"\n" >> $(PKGINFO)
	printf "MAXINST=1\n" >> $(PKGINFO)
	printf "SUNW_PKG_THISZONE=true\n" >> $(PKGINFO)
	printf "CATEGORY=\"utility\"\n" >> $(PKGINFO)
	printf "VENDOR=\"OSLockdown"\n" >> $(PKGINFO)
	printf "BASEDIR=\"/\"\n" >> $(PKGINFO)
	cat build/solaris/create_sbwebapp > build/solaris/preinstall
	cat ${ARCHTEST} >> build/solaris/preinstall
	#
	# Prototype
	#
	echo "i pkginfo" > build/solaris/Prototype
	echo "i depend" >> build/solaris/Prototype
	echo "i preinstall" >> build/solaris/Prototype
	echo "i postinstall" >> build/solaris/Prototype
	echo "i checkinstall" >> build/solaris/Prototype
	echo "i preremove" >> build/solaris/Prototype
	
	test ! -d build/solaris/package || rm -rf build/solaris/package
	-mkdir -p build/solaris/package
	(cd build/solaris/root/; pkgproto . >> ../Prototype )
	(cd build/solaris/; pkgmk -o -r root -d package -f Prototype)
	(cd build/solaris/; pkginfo -l -d package TCSoslockdown)
	(cd build/solaris/; pkgtrans -s package oslockdown-${SB_VERSION}-${SB_RELEASE}.sol10.${PKGARCH}.pkg TCSoslockdown)
	mkdir -p ${DISTRO}
	mv build/solaris/package/oslockdown-${SB_VERSION}-${SB_RELEASE}.sol10.${PKGARCH}.pkg ${DISTRO}/
	cat /dev/null > build/solaris/preinstall


##############################################################################
test-all: validate pylint
	@echo

pylint:
	@test -x $(PYLINT)
	@echo
	@echo ":: Using PYLINT to test source code..."
	@for sbfile in `find . -name "*.py" -type f ! -regex '.*/[.]svn.*' -print`; do \
	    $(PRINTF) "%s\n" $$sbfile; \
	    $(PYLINT) -e $$sbfile; \
	done
	@echo

validate:
	@test -x $(XMLLINT)
	@echo
	@echo ":: Validating XML configuration files against their schema (XSD)..."
	$(XMLLINT) --noout cfg/baseline-modules.xml
	@echo



##############################################################################
# Leave blank (empty target)!!
##
FORCE:

