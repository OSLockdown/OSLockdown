#=========================================================================
#
# Copyright (c) 2009-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# OSLockdown Dispatcher - Makefile
#
#=========================================================================

export ROOT ?= $(shell pwd)/root


include ../../Makefile_common.mk
MAKE ?= /usr/bin/make


export PKGARCH ?= $(shell uname -m)

# The following directories are exlcuded when a tar file is created during the
# package build process. They are not needed to build this package so, the more
# we can exclude the faster the RPM build will be.
export EXCLUDE_SRC_DIRS := --exclude=oslockdown/src/console/build \
                           --exclude=oslockdown/src/selinux \
                           --exclude=oslockdown/src/security_modules \
                           --exclude=oslockdown/cfg \
                           --exclude=oslockdown/docs


SPECFILE := build/oslockdown-dispatcher.spec
DISTRO   := build/dist

BASEDIR := $(shell pwd)
WORK_DIR := $(BASEDIR)/work

GSOAP_DEBUG := no
GSOAP_CONF_WITH_IPV6 := yes


ifeq ("${GSOAP_CONF_WITH_IPV6}","yes")
  GSOAP_CONFIG_IPV6 := --enable-ipv6
  GSOAP_IPV6_FLAGS := -DWITH_IPV6 -DWITH_NO_IPV6_V6ONLY
else
  GSOAP_CONFIG_IPV6 := 
  GSOAP_IPV6_FLAGS := 
endif

GSOAP_FLAGS := -DWITH_OPENSSL -DWITH_NONAMESPACES -DSOCKET_CLOSE_ON_EXIT ${GSOAP_IPV6_FLAGS} 
BLD_REV := -DSB_RELEASE="\"${SB_RELEASE}\""

BLD_FLAGS :=  ${BLD_REV}

SELINUX := 



# if GSOAP_HOME is *not* defined, or doesn't exist, 
# we need to build it ourselves

ifndef GSOAP_HOME
  $(warning GSOAP_HOME does not exist, setting GSOAP_HOME to /tmp/SB_GSOAP_HOME just in case we built it already locally)
  export GSOAP_HOME := /tmp/SB_GSOAP_HOME
endif
ifeq ($(wildcard ${GSOAP_HOME}/bin/wsdl2h),)
  GSOAP_BUILD = gsoap-local
  $(warning ${GSOAP_HOME}/bin/wsdl2h doesn't exist, setting GSOAP_HOME to /tmp/SB_GSOAP_HOME to build locally )
else
  GSOAP_BUILD := 
endif



ifeq ("${GSOAP_DEBUG}","yes")
  GSOAP_CONFIGURE := --prefix=$(GSOAP_HOME) --enable-debug ${GSOAP_CONFIG_IPV6}
  BLD_FLAGS := -g -DDEBUG=1 -DSOAP_MEM_DEBUG 
  BLD_FLAGS := -ggdb3 ${BLD_REV}
else
  GSOAP_CONFIGURE := --prefix=$(GSOAP_HOME)  ${GSOAP_CONFIG_IPV6}
  BLD_FLAGS :=  ${BLD_REV}
endif


# Grab OS dependant bits...

ARCH     := $(strip $(shell uname -m))
OS_TYPE  := $(strip $(shell uname -s))
export PYTHON_VERS ?= $(shell python -V 2>&1 |cut -c8-10 )
CXXFLAGS  :=  $(DEBUG_FLAG) ${BLD_REV} -fPIC $(SYS_INCS)  -Wcast-qual


# Different Linux distros define where RPMs are built in different
# places, and rather than parse this out (based on *actual* distro
# and version) we'll just force build things where we want
# to.  By default, this will be in each the 'rpmbuilddir' directory for
# this module.

BUILD_BASE := $(shell pwd)/rpmbuilddir


ifeq ("${OS_TYPE}", "SunOS")
   include ../../os/solaris/utilities.mk

   PKGINFO := build/solaris/pkginfo
   BUILDTARGET := build-solaris
   INSTALLTARGET := install-solaris
   INITSCRIPT := ./init.osl-dispatcher.solaris
   SHARED_FLAGS := -G
   PYTHON_INCS  := -I/usr/include/python${PYTHON_VERS}
   PYTHON_LIBS  :=

   ifeq ("${PKGARCH}", "sun4u")
      PKGARCH := sparc
      ARCHTEST := build/solaris/sparc-test
   endif
   ifeq ("${PKGARCH}", "i86pc")
      ARCHTEST := build/solaris/x86-test
   endif

else

   export INSTALL ?= /usr/bin/install

   BUILDTARGET := build-linux
   INSTALLTARGET := install-linux

   INITSCRIPT := ./init.osl-dispatcher
   LINUX_TYPE := $(shell lsb_release -i -s)
   LINUX_RELEASE := $(shell lsb_release -r -s | cut -d '.' -f 1)
   OS_RELEASE := $(shell lsb_release -r -s)
   SHARED_FLAGS := -shared
   PYTHON_INCS  := -I/usr/include/python${PYTHON_VERS}
   PYTHON_LIBS  :=

   Utils_file :=  ../../os/redhat/utilities.mk

   # Red Hat 6.x build system is like Fedora
   ifeq ("${LINUX_TYPE}", "RedHatEnterpriseServer")
      # Red Hat 6.x build system is like Fedora
      ifeq ("${LINUX_RELEASE}", "6")
          RPMDEVSETUP := /usr/bin/rpmdev-setuptree
      endif
   endif


   ifeq ("${LINUX_TYPE}", "Fedora")
      Utils_file := ../../os/fedora/utilities.mk
   endif

   ifeq ("${LINUX_TYPE}", "SUSE LINUX")
      INITSCRIPT := ./init.osl-dispatcher.suse
      Utils_file := ../../os/suse/utilities.mk
      SELINUX := 
   endif

   ifeq ("${LINUX_TYPE}", "Ubuntu")
      ROOT := build/debian
      BUILDTARGET := build-ubuntu
      Utils_file := ../../os/ubuntu/utilities.mk
      SELINUX := 
   endif

  include $(Utils_file)
endif

ifeq ("$(shell $(UNAME) -m)", "s390x")
    export ARCH := s390x
else 
ifeq ("$(shell $(UNAME) -m)", "x86_64")
    export ARCH := x86_64
else
    export ARCH := i386
endif
endif




GSOAP_INCS := -I../include -I${GSOAP_HOME}/include -I${WORK_DIR} 
GSOAP_LIBS := -L${GSOAP_HOME}/lib -lgsoapssl++ 
WSDL2H := ${GSOAP_HOME}/bin/wsdl2h
SOAPCPP := ${GSOAP_HOME}/bin/soapcpp2 -x -d${WORK_DIR}

WSDL_SOURCE_DIR := ../console/AgentCommunication/wsgen/resources
WSDL_SOURCE := AgentServiceImplService.wsdl ConsoleServiceImplService.wsdl  \
		ReportsServiceImplService.wsdl  SchedulerServiceImplService.wsdl \
		TaskVerificationServiceImplService.wsdl \
		ClientRegistrationServiceImplService.wsdl \
		UpdateSBServiceImplService.wsdl

WSDL_H := ${WORK_DIR}/wsdl_out.h

ifeq ("${OS_TYPE}", "SunOS")
  OS_UTILS := SB_Info_solaris.cc
  OS_LIBS := -lkstat -lsocket -lnsl -lssl -lz -lpthread -lcrypto -lrt
  OS_FLAGS := -DSOLARIS
  export PATH := ${PATH}:/usr/ccs/bin
else
  OS_UTILS := SB_Info_linux.cc
  OS_LIBS := -lssl -lz -lpthread -lcrypto
  OS_FLAGS := 
endif

CXX ?= g++
CLIENT_STUBS := ${WORK_DIR}/soapAgentServiceImplPortBindingProxy.cpp 
SERVER_STUBS := ${WORK_DIR}/soapAgentServiceImplPortBindingService.cpp
AGENT_UTILS  := SB_Dispatcher_Utils.cc SB_Info.cc SB_Update.cc sub_proc.cc $(OS_UTILS) SB_Status.cc compute_sha1.cc SB_Tasks.cc SB_time_code.cc
REGISTER_UTILS := SB_Dispatcher_Utils.cc 
AUTOUPDATE_COMMS_UTILS := AutoupdateComms_Utils.cc 
SOAP_COMMON   := ${WORK_DIR}/soapC.cpp


DISPATCHER_MAIN := SB_Dispatcher.cc
DISPATCHER := OSL_Dispatcher
DISPATCHER_SOURCE  := ${SERVER_STUBS} ${CLIENT_STUBS} $(SOAP_COMMON) ${DISPATCHER_MAIN}

REGISTER_CLIENT_MAIN := RegisterClient.cc
REGISTER_CLIENT := ${REGISTER_CLIENT_MAIN:.cc=}
REGISTER_CLIENT_SOURCE := ${CLIENT_STUBS} $(SOAP_COMMON) ${REGISTER_CLIENT_MAIN}


AUTOUPDATE_COMMS_TEST_MAIN := AutoupdateComms_test.cc
AUTOUPDATE_COMMS_TEST := ${AUTOUPDATE_COMMS_TEST_MAIN:.cc=}
AUTOUPDATE_COMMS_TEST_SOURCE := ${AUTOUPDATE_COMMS_TEST_MAIN}

AUTOUPDATE_COMMS_LIB_MAIN   := AutoupdateComms.cc
AUTOUPDATE_COMMS_LIB        := ${AUTOUPDATE_COMMS_LIB_MAIN:.cc=.o}
AUTOUPDATE_COMMS_LIB_SOURCE := ${AUTOUPDATE_COMMS_LIB_MAIN} ${CLIENT_STUBS} $(SOAP_COMMON) 

###############################################################################
.DEFAULT_GOAL := all
	
all: TEST_PREREQUISITES core-engine OSL_Dispatcher RegisterClient sb-keylocker swig 

gsoap-local: ${GSOAP_HOME}/bin/wsdl2h
	cd ${GSOAP_SRC} ; ./configure ${GSOAP_CONFIGURE} > config.output
	cd ${GSOAP_SRC} ; ${MAKE}
	cd ${GSOAP_SRC} ; ${MAKE} install
	
core-engine:
	$(MAKE) -C ../core	

sb-keylocker: ${GSOAP_BUILD} sb-keylocker.cc
	${CXX} -o sb-keylocker sb-keylocker.cc
	
shimster: shimster.cc
	${CXX} -g -o shimster shimster.cc ${OS_LIBS}

${WORK_DIR} :
	mkdir -p ${WORK_DIR}

${WSDL_SOURCE_DIR}:
	$(warn WSDL_SOURCE_DIR)
	
${WSDL_H} : ${WORK_DIR}
	${TEST} -d ${WSDL_SOURCE_DIR} || $(MAKE) -C ../console wsdl
	${WSDL2H} -z6 -s -I ${WSDL_SOURCE_DIR}  -o ${WSDL_H} ${WSDL_SOURCE} 

${CLIENT_STUBS} : ${WSDL_H}
	${SOAPCPP}  -i -C ${WSDL_H} 

${SERVER_STUBS} : ${WSDL_H}
	${SOAPCPP}  -i -S ${WSDL_H} 

SWIG_INTERFACE := AutoupdateComms.i

# NOTE - valid *TARGET* for TEST_PREREQUISITES, but body of target
#   is a set of make conditionals - notice no tab indent

TEST_PREREQUISITES: FORCE
	# Check for a *valid* GSOAP facility existing 
	@if [ "${GSOAP_HOME}" = "" ]; then \
		echo "GSOAP_HOME is not set";  \
		exit 1; \
	fi
	@if [ ! -d "${GSOAP_HOME}"  ]; then \
		echo "GSOAP_HOME is not a directory";  \
		exit 1; \
	fi
	@if [ ! -f "${WSDL2H}"  ]; then \
		echo "${WSDL2H} does not exist";  \
		exit 1; \
	fi
	@if [ ! -f "${WSDL2H}"  ]; then \
		echo "${WSDL2H} does not exist";  \
		exit 1; \
	fi
	@if [ ! -x "${WSDL2H}"  ]; then \
		echo "${WSDL2H} is not an executable";  \
		exit 1; \
	fi

	# Check for a *valid* JAVA development environment
	@if [ "${JAVA_HOME}" = "" ]; then \
		echo "JAVA_HOME is not set";  \
		exit 1; \
	fi
	@if [ ! -d "${JAVA_HOME}"  ]; then \
		echo "JAVA_HOME is not a directory";  \
		exit 1; \
	fi
	@if [ ! -f "${JAVA_HOME}/bin/javac"  ]; then \
		echo "${JAVA_HOME}/bin/javac does not exist";  \
		exit 1; \
	fi
	@if [ ! -x "${JAVA_HOME}/bin/javac"  ]; then \
		echo "${JAVA_HOME}/bin/javac is not an executable";  \
		exit 1; \
	fi

	# Check for a *valid* SWIG facility
	@if [ ! -f "${SWIG}"  ]; then \
		echo "${SWIG} does not exist";  \
		exit 1; \
	fi
	@if [ ! -x "${SWIG}"  ]; then \
		echo "${SWIG} does not appear to be an executable";  \
		exit 1; \
	fi


${DISPATCHER} : TEST_PREREQUISITES ${GSOAP_BUILD} fingerprints.h $(UTIL_SOURCES) ${DISPATCHER_SOURCE} ${AGENT_UTILS} ${SERVER_STUBS} 
	${CXX} ${OS_FLAGS} ${BLD_FLAGS} $(GSOAP_FLAGS) -o ${DISPATCHER}  ${GSOAP_INCS} ${DISPATCHER_SOURCE} ${AGENT_UTILS} $(UTIL_SOURCES) ${GSOAP_LIBS} ${OS_LIBS} 

${REGISTER_CLIENT} :  TEST_PREREQUISITES ${GSOAP_BUILD} $(UTIL_SOURCES) ${REGISTER_CLIENT_SOURCE} ${REGISTER_UTILS}  ${SERVER_STUBS} 
	${CXX} ${OS_FLAGS} ${BLD_FLAGS} $(GSOAP_FLAGS) -o ${REGISTER_CLIENT}  ${GSOAP_INCS} ${REGISTER_CLIENT_SOURCE} ${REGISTER_UTILS} $(UTIL_SOURCES) ${GSOAP_LIBS} ${OS_LIBS} 


fingerprints.h: ../core/oslockdown.pyo ../core/oslockdown
	@ echo "Generating fingerprint hashes for integrity check..."
	./generate_hashes_for_build.sh 

../core/oslockdown.pyo ../core/oslockdown   : FORCE
	$(TEST) -f $@ 

time-harness: time-harness.cc SB_time_code.cc
	${CXX} ${OS_FLAGS} ${BLD_FLAGS} -o time-harness time-harness.cc SB_time_code.cc
	
####################################################################################
install: $(INSTALLTARGET)

install-dirs-linux:

	${TEST} -x $(INSTALL)
	$(INSTALL) -m 0755 -o root -g root -d ${ROOT}/sbin
	$(INSTALL) -m 0755 -o root -g root -d $(ROOT)/usr/share/oslockdown/tools
	$(INSTALL) -m 0755 -o root -g root -d $(ROOT)/usr/share/man/man8

install-dirs-solaris:

	###########################################################
	### Solaris MUST have its own install-dirs target because
	### it's system directories have such different ownerships
	###########################################################
	test ! -d build/solaris/root || rm -rf build/solaris/root
        
	##
	## Standard Solaris directory structures
        ##
	$(INSTALL) -d -m 0755 -o root -g sys build/solaris/root/usr 
	$(INSTALL) -d -m 0755 -o root -g sys build/solaris/root/sbin 
	$(INSTALL) -d -m 0755 -o root -g sys build/solaris/root/usr/share 
	$(INSTALL) -d -m 0755 -o root -g sys build/solaris/root/var
	$(INSTALL) -d -m 0755 -o root -g bin build/solaris/root/lib
	$(INSTALL) -d -m 0755 -o root -g bin -d build/solaris/root/usr/share/man/man1m

	# SMF Directories
	$(INSTALL) -o root -g bin -m 0755 -d build/solaris/root/lib/svc
	$(INSTALL) -o root -g bin -m 0755 -d build/solaris/root/lib/svc/method
	$(INSTALL) -o root -g sys -m 0755 -d build/solaris/root/var/svc
	$(INSTALL) -o root -g sys -m 0755 -d build/solaris/root/var/svc/manifest
	$(INSTALL) -o root -g sys -m 0755 -d build/solaris/root/var/svc/manifest/site
	$(INSTALL) -o root -g sys -m 0755 -d build/solaris/root/var/svc/profile
        
	# Application specific
	$(INSTALL) -d -m 0755 -o root -g root build/solaris/root/usr/share/${NAME}  
	$(INSTALL) -d -m 0755 -o root -g root build/solaris/root/usr/share/${NAME}/tools 


install-linux: install-dirs-linux

	${TEST} -x $(INSTALL)
	$(STRIP) --strip-all OSL_Dispatcher
	$(STRIP) --strip-all RegisterClient
	$(STRIP) --strip-all sb-keylocker
	$(INSTALL) -m 0500 -o root -g root OSL_Dispatcher ${ROOT}/sbin/OSL_Dispatcher
	$(INSTALL) -m 0750 -o root -g root ${INITSCRIPT} ${ROOT}/usr/share/${NAME}/init.osl-dispatcher
	$(INSTALL) -m 0755 -o root -g root RegisterClient ${ROOT}/usr/share/${NAME}/tools/RegisterClient
	$(INSTALL) -m 0755 -o root -g root sb-keylocker ${ROOT}/usr/share/${NAME}/tools/sb-keylocker
	$(INSTALL) -m 0444 -o root -g root docs/OSL_Dispatcher.8 ${ROOT}/usr/share/man/man8
	$(INSTALL) -m 0444 -o root -g root docs/OSL_Dispatcher.8 ${ROOT}/usr/share/man/man8/osl-dispatcher.8

install-solaris: install-dirs-solaris

	${TEST} -x $(INSTALL)
	$(STRIP) OSL_Dispatcher
	$(STRIP) sb-keylocker
	$(INSTALL) -m 0500 -o root -g root OSL_Dispatcher build/solaris/root/sbin/
	$(INSTALL) -m 0755 -o root -g root RegisterClient build/solaris/root/usr/share/${NAME}/tools/RegisterClient
	$(INSTALL) -m 0755 -o root -g root sb-keylocker build/solaris/root/usr/share/${NAME}/tools/sb-keylocker
	$(INSTALL) -m 0444 -o root -g root docs/OSL_Dispatcher.1m build/solaris/root/usr/share/man/man1m
	$(INSTALL) -m 0444 -o root -g root docs/OSL_Dispatcher.1m build/solaris/root/usr/share/man/man1m/osl-dispatcher.1m

	# Service Management Facility (SMF)
	$(INSTALL) -m 0755 -o root -g bin ${INITSCRIPT} build/solaris/root/lib/svc/method/osl-dispatcher
	$(INSTALL) -m 0444 -o root -g sys osl-dispatcher.xml build/solaris/root/var/svc/manifest/site/osl-dispatcher.xml


${AUTOUPDATE_COMMS_LIB} : TEST_PREREQUISITES ${AUTOUPDATE_COMMS_LIB_SOURCE} ${AUTOUPDATE_COMMS_UTILS} 
	${CXX} -c ${OS_FLAGS} -w ${CXXFLAGS} ${BLD_FLAGS} $(GSOAP_FLAGS) ${GSOAP_INCS} ${AUTOUPDATE_COMMS_LIB_SOURCE} ${AUTOUPDATE_COMMS_UTILS}  

${AUTOUPDATE_COMMS_TEST} : TEST_PREREQUISITES  ${AUTOUPDATE_COMMS_TEST_SOURCE} ${AUTOUPDATE_COMMS_UTILS} ${AUTOUPDATE_COMMS_LIB_SOURCE}
	${CXX}  -w ${CXXFLAGS} -o ${AUTOUPDATE_COMMS_TEST} ${OS_FLAGS} ${BLD_FLAGS} $(GSOAP_FLAGS) ${GSOAP_INCS} ${AUTOUPDATE_COMMS_TEST_SOURCE} ${AUTOUPDATE_COMMS_LIB_SOURCE} ${AUTOUPDATE_COMMS_UTILS} ${GSOAP_LIBS} ${OS_LIBS} 

swig: ${SWIG_INTERFACE} ${AUTOUPDATE_COMMS_LIB}
	$(TEST) -x $(SWIG)
	#
	$(MKDIR) -p swig_dir
	cp ${SWIG_INTERFACE} AutoupdateComms.o AutoupdateComms_Utils.o soapAgentServiceImplPortBindingProxy.o soapC.o swig_dir
	cd swig_dir ; $(SWIG) -c++ -python ${SWIG_INTERFACE}
	cd swig_dir ; $(CXX) ${SHARED_FLAGS} ${CXXFLAGS} -I../ -o _AutoupdateComms.so AutoupdateComms_wrap.cxx *.o -w ${PYTHON_INCS}  ${GSOAP_LIBS} ${OS_LIBS} 
	cd swig_dir ; $(PYTHON) -OO -c "import sys,py_compile; ret = py_compile.compile('AutoupdateComms.py'); sys.exit(ret)"
	@echo
        
####################################################################################
clean_dispatcher: FORCE

	-$(RM) -rf ${WORK_DIR} ${DISPATCHER} $(REGISTER_CLIENT) $(AUTOUPDATE_COMMS) $(AUTOUPDATE_COMMS_TEST) swig_dir sb-keylocker shimster *.o *.LOG *.log fingerprints.h build/debian


clean: clean_dispatcher distclean

	-$(RM) -f  build/solaris/Prototype
	-$(RM) -f  build/solaris/pkginfo
	-$(RM) -rf  rpmbuilddir
	
	$(TEST) ! -d root || $(RM) -rf root
	$(TEST) ! -d build/solaris/root || rm -rf build/solaris/root
	$(TEST) ! -d build/solaris/package || rm -rf build/solaris/package

distclean: 

	@ $(RM) -f build/dist/*
	@ $(RM) -f build/*log

####################################################################################
build:  TEST_PREREQUISITES $(BUILDTARGET)
	@echo

	
build-ubuntu: FORCE core-engine all install

	@echo ## 
	@echo ## Build Ubuntu (Debian) Package 
	@echo ##
	mkdir -p ${ROOT}/DEBIAN
	sed 's/^Version: .*/Version: ${SB_VERSION}-${SB_RELEASE}/' build/ubuntu/control > ${ROOT}/DEBIAN/control
	sed -i 's/^Architecture: .*/Architecture: ${ARCH}/' ${ROOT}/DEBIAN/control
	dpkg-deb --build build/debian build/dist/oslockdown-dispatcher_${SB_VERSION}-${SB_RELEASE}_${ARCH}.deb


build-linux: 

	@echo ## 
	@echo ## Creating RPM build directories if required....
	@echo ##
	mkdir -p ${BUILD_BASE}/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

	$(TEST) -f ${SPECFILE}

	# Create TAR of source code

	echo "Creating tarball to build RPM using ${SPECFILE}"; \
	$(TAR) -C ../../.. ${EXCLUDE_SRC_DIRS} ${COMMON_EXCLUDES} -czf ${BUILD_BASE}/SOURCES/oslockdown.tar.gz oslockdown ; 

	# Build Packages
	$(RPMBUILD) --target ${ARCH} --define "_topdir ${BUILD_BASE}" -bb ${SPECFILE} 2>&1 |$(TEE) ${DISTRO}/build-dispatcher.log
	@echo

	# Copy Packages into distro folder
	-mkdir -p ${DISTRO}
	-mv ${BUILD_BASE}/RPMS/$(ARCH)/oslockdown-dispatcher*.rpm ${DISTRO}/
	-mv ${BUILD_BASE}/BUILD/oslockdown/src/dispatcher/swig_dir/AutoupdateComms.pyo ${DISTRO}/
	-mv ${BUILD_BASE}/BUILD/oslockdown/src/dispatcher/swig_dir/_AutoupdateComms.so ${DISTRO}/

build-solaris: all install
	@echo "Building Solaris package..."
	#
	# Pkginfo 
	#
	printf "PKG=\"TCSoslockdown-dispatcher\"\n" > $(PKGINFO)
	printf "NAME=\"OSLockdown Dispatcher\"\n" >> $(PKGINFO)
	printf "VERSION=\"%s\"\n" ${SB_VERSION}-${SB_RELEASE} >> $(PKGINFO)
	printf "ARCH=\"%s\"\n" $(PKGARCH) >> $(PKGINFO)
	printf "SUNW_PRODNAME=\"SunOS\"\n" >> $(PKGINFO)
	printf "SUNW_PRODVERS=\"5.10\"\n" >> $(PKGINFO)
	printf "CLASSES=\"none\"\n" >> $(PKGINFO)
	printf "MAXINST=1\n" >> $(PKGINFO)
	printf "SUNW_PKG_THISZONE=true\n" >> $(PKGINFO)
	printf "CATEGORY=\"utility\"\n" >> $(PKGINFO)
	printf "VENDOR=\"OSLockown\"\n" >> $(PKGINFO)
	printf "BASEDIR=\"/\"\n" >> $(PKGINFO)
	cat ${ARCHTEST} > build/solaris/preinstall
	#
	# Package Manifest 
	#
	echo "i pkginfo" > build/solaris/Prototype
	echo "i depend" >> build/solaris/Prototype
	echo "i preinstall" >> build/solaris/Prototype
	echo "i postinstall" >> build/solaris/Prototype
	echo "i checkinstall" >> build/solaris/Prototype
	echo "i preremove" >> build/solaris/Prototype
       	 
	test ! -d build/solaris/package || rm -rf build/solaris/package
	mkdir -p build/solaris/package
	(cd build/solaris/root/; pkgproto . >> ../Prototype )
	(cd build/solaris/; pkgmk -o -r root -d package -f Prototype)
	(cd build/solaris/; pkginfo -l -d package TCSoslockdown-dispatcher)
	(cd build/solaris/; pkgtrans -s package oslockdown-dispatcher-${SB_VERSION}-${SB_RELEASE}.sol10.${PKGARCH}.pkg TCSoslockdown-dispatcher)
	
	-mkdir -p ${DISTRO}
	mv build/solaris/package/oslockdown-dispatcher-${SB_VERSION}-${SB_RELEASE}.sol10.${PKGARCH}.pkg ${DISTRO}/
	mv swig_dir/AutoupdateComms.pyo ${DISTRO}/
	mv swig_dir/_AutoupdateComms.so ${DISTRO}/
	
	cat /sodev/null > build/solaris/preinstall



####################################################################################
FORCE:

