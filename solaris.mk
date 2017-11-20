#==================================================================
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# OS Lockdown - Solaris Master Makefile
#
#
#===================================================================

# Product Name - Do not change! Many directories are based on this name
export NAME = oslockdown

# Where to install the product once built
# If ROOT was not defined on the command-line, 
# then define it now:
export ROOT ?= $(shell pwd)/root

include os/solaris/utilities.mk


# Platform Information
export ARCH    := $(shell $(UNAME) -m)
ifeq ("${PKGARCH}", "i86pc")
      REPOARCH := x86
else
      REPOARCH := sparc
endif

export OS_DIST := $(shell $(UNAME) -s)
export OS_REL  := $(shell $(UNAME) -r |$(CUT) -d. -f2- )

export JAVA_HOME ?= /usr/jdk/jdk1.6.0_16

# By default build the Console also.  If SB_CONSOLE=n is on the Make line, then skip
export SB_CONSOLE ?= y

# By default do build the PDF documentation.  
export SB_DOC_PDFS ?= y


BUILD_BASE := $(shell pwd)/os/solaris/build
DISTRO     := $(shell pwd)/build/dist
BUILD_LOG  := $(DISTRO)/build.log

#
# Python Version is important when using swig and compiling
# C-coded Python bindings. The version is to determine the include path
export PYTHON_VERS    := $(shell $(PYTHON) -V 2>&1 |$(CUT) -c8-10 )
export PYTHON_CMD     := $(PYTHON) -OO -c 
export PYTHON_COMPILE := import sys,compileall,re; ret = compileall.compile_dir
export BASE_DIR       := ${ROOT}/usr/share
export DATA_DIR       := ${ROOT}/var/lib
export TOPDIR         := $(shell pwd)
export SOURCE         := ./src
export SRCLIB         := ./srclib
export OS_DIR         := ./os/solaris
#
# Directory Locations within the this tree
#
export DIR_CORE       := ${SOURCE}/core
export DIR_CONSOLE    := ${SOURCE}/console
export DIR_ENTERPRISE := ${SOURCE}/enterprise-console
export DIR_DISPATCHER := ${SOURCE}/dispatcher
export DIR_SECMODULES := ${SOURCE}/security_modules
export DIR_DOCS       := docs


##############################################################################
# Targets
##############################################################################
all: 

	$(MAKE) -C $(DIR_SECMODULES)
	$(MAKE) -C $(DIR_CORE)
	$(MAKE) -C $(DIR_CONSOLE)
	$(MAKE) -C $(DIR_DISPATCHER) 

##############################################################################
# Install Targets
##############################################################################
install-dirs:

	@echo ------------------------------------------------------------------------
	#
	# Setup Product directory structure
	#
	$(INSTALL) -o root -g sys -m 0755 -d ${ROOT}/sbin
	$(INSTALL) -o root -g sys -m 0755 -d ${ROOT}/usr
	$(INSTALL) -o root -g bin -m 0755 -d ${ROOT}/usr/bin
	$(INSTALL) -o root -g bin -m 0755 -d ${ROOT}/usr/sbin
	$(INSTALL) -o root -g sys -m 0755 -d ${BASE_DIR}
	$(INSTALL) -o root -g bin -m 0755 -d ${BASE_DIR}/man
	$(INSTALL) -o root -g bin -m 0755 -d ${BASE_DIR}/man/man8
	$(INSTALL) -o root -g bin -m 0755 -d ${BASE_DIR}/man/man1
	$(INSTALL) -o root -g bin -m 0755 -d ${BASE_DIR}/man/man1m
	$(INSTALL) -o root -g sys -m 0755 -d ${ROOT}/etc
	$(INSTALL) -o root -g sys -m 0755 -d ${ROOT}/etc/profile.d
	$(INSTALL) -o root -g sys -m 0755 -d ${ROOT}/etc/default
	$(INSTALL) -o root -g bin -m 0755 -d ${ROOT}/lib
	$(INSTALL) -o root -g bin -m 0755 -d ${ROOT}/lib/svc
	$(INSTALL) -o root -g bin -m 0755 -d ${ROOT}/lib/svc/method
	$(INSTALL) -o root -g sys -m 0755 -d ${ROOT}/var
	$(INSTALL) -o root -g sys -m 0755 -d ${ROOT}/var/svc
	$(INSTALL) -o root -g sys -m 0755 -d ${ROOT}/var/svc/manifest
	$(INSTALL) -o root -g sys -m 0755 -d ${ROOT}/var/svc/manifest/site
	$(INSTALL) -o root -g sys -m 0755 -d ${ROOT}/var/svc/profile

	$(INSTALL) -o root -g other -m 0755 -d ${DATA_DIR}

	$(INSTALL) -o root -g root -m 0755 -d ${BASE_DIR}/${NAME}
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/security_modules
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/images
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/Custom_login_banner
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/profiles
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/tools
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/tools/pciids
	$(INSTALL) -o root -g root -m 0755 -d ${BASE_DIR}/${NAME}/templates
	$(INSTALL) -o root -g root -m 0500 -d ${BASE_DIR}/${NAME}/ssl
	$(INSTALL) -o root -g root -m 0500 -d ${BASE_DIR}/${NAME}/cfg
	$(INSTALL) -o root -g root -m 0500 -d ${BASE_DIR}/${NAME}/cfg/schema
	$(INSTALL) -o root -g root -m 0500 -d ${BASE_DIR}/${NAME}/cfg/stylesheets

	$(INSTALL) -o root -g root -m 0755 -d ${DATA_DIR}/${NAME}
	$(INSTALL) -o root -g root -m 0750 -d ${DATA_DIR}/${NAME}/analysis
	$(INSTALL) -o root -g root -m 0750 -d ${DATA_DIR}/${NAME}/baseline
	$(INSTALL) -o root -g root -m 0750 -d ${DATA_DIR}/${NAME}/backup
	$(INSTALL) -o root -g root -m 0750 -d ${DATA_DIR}/${NAME}/fs-scan
	$(INSTALL) -o root -g root -m 0750 -d ${DATA_DIR}/${NAME}/baseline/images
	$(INSTALL) -o root -g root -m 0750 -d ${DATA_DIR}/${NAME}/analysis/images/
	$(INSTALL) -o root -g root -m 0750 -d ${DATA_DIR}/${NAME}/profiles
	$(INSTALL) -o root -g root -m 0750 -d ${DATA_DIR}/${NAME}/profiles/enterprise
	$(INSTALL) -o root -g root -m 0750 -d ${DATA_DIR}/${NAME}/files
	$(INSTALL) -o root -g root -m 0750 -d ${DATA_DIR}/${NAME}/fs-scan/

	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/sb_utils
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/sb_utils/file
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/sb_utils/filesystem
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/sb_utils/auth
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/sb_utils/proc
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/sb_utils/generic_modules
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/sb_utils/baseline
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/sb_utils/template
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/sb_utils/reporting
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/sb_utils/misc
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/sb_utils/errors
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/sb_utils/os
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/sb_utils/acctmgt
	$(INSTALL) -o root -g root -m 0750 -d ${BASE_DIR}/${NAME}/sb_utils/hardware


install: printenv install-dirs

	test -d ${DIR_CORE}
	test -d ${SOURCE}/xsl
	test -d ./cfg/schema
	test -d profiles
	test -d os/solaris/services

	$(INSTALL) -o root -g root -m 0755 ${DIR_CORE}/${NAME} ${ROOT}/usr/sbin
	$(INSTALL) -o root -g root -m 0444 ${PROG} ${BASE_DIR}/${NAME} 

	$(INSTALL) -o root -g root -m 0600 ${DIR_CORE}/exclude-dirs  ${DATA_DIR}/${NAME}/files
	$(INSTALL) -o root -g root -m 0600 ${DIR_CORE}/inclusion-fstypes ${DATA_DIR}/${NAME}/files

	$(INSTALL) -o root -g root -m 0500 ${OS_DIR}/tools/prtpci ${BASE_DIR}/${NAME}/tools/prtpci
	$(INSTALL) -o root -g root -m 0500 ${OS_DIR}/tools/pciids/*.ids ${BASE_DIR}/${NAME}/tools/pciids

	$(INSTALL) -o root -g root -m 0444 ${SOURCE}/xsl/*.xsl ${BASE_DIR}/${NAME}/cfg/stylesheets/
	$(INSTALL) -o root -g root -m 0444 ./cfg/schema/*.xsd ${BASE_DIR}/${NAME}/cfg/schema/
	$(INSTALL) -o root -g root -m 0400 profiles/*.xml ${ROOT}/usr/share/${NAME}/profiles/

	#
	# Install SMF Components
	#
	$(INSTALL) -o root -g bin -m 0555 os/solaris/services/ndd-config ${ROOT}/lib/svc/method
	$(INSTALL) -o root -g bin -m 0644 os/solaris/services/ndd-config.xml ${ROOT}/var/svc/manifest/site
	$(INSTALL) -o root -g bin -m 0640 os/solaris/services/etc_default_ndd ${ROOT}/etc/default/ndd

	# Whitelist files
	$(INSTALL) -o root -g root -m 0440 os/solaris/suid_whitelist ${ROOT}/var/lib/${NAME}/files
	$(INSTALL) -o root -g root -m 0440 os/solaris/sgid_whitelist ${ROOT}/var/lib/${NAME}/files


	$(MAKE) -C $(DIR_SECMODULES) install

	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/misc/tcs_utils.pyo ${BASE_DIR}/${NAME}/
	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/misc/TCSLogger.pyo ${BASE_DIR}/${NAME}/
	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/*.pyo ${BASE_DIR}/${NAME}/sb_utils
	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/file/*.pyo ${BASE_DIR}/${NAME}/sb_utils/file
	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/file/store.dat ${BASE_DIR}/${NAME}/sb_utils/file
	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/filesystem/*.pyo ${BASE_DIR}/${NAME}/sb_utils/filesystem
	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/auth/*.pyo ${BASE_DIR}/${NAME}/sb_utils/auth
	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/proc/*.pyo ${BASE_DIR}/${NAME}/sb_utils/proc
	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/generic_modules/*.pyo ${BASE_DIR}/${NAME}/sb_utils/generic_modules
	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/baseline/*.pyo ${BASE_DIR}/${NAME}/sb_utils/baseline
	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/template/*.pyo ${BASE_DIR}/${NAME}/sb_utils/template
	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/reporting/*.pyo ${BASE_DIR}/${NAME}/sb_utils/reporting
	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/misc/*.pyo ${BASE_DIR}/${NAME}/sb_utils/misc
	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/errors/*.pyo ${BASE_DIR}/${NAME}/sb_utils/errors
	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/os/*.pyo ${BASE_DIR}/${NAME}/sb_utils/os
	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/acctmgt/*.pyo ${BASE_DIR}/${NAME}/sb_utils/acctmgt
	$(INSTALL) -o root -g root -m 0440 ${DIR_CORE}/sb_utils/hardware/*.pyo ${BASE_DIR}/${NAME}/sb_utils/hardware

	$(INSTALL) -o root -g root -m 0444 ${DIR_DOCS}/unix-man-pages/oslockdown.8 ${BASE_DIR}/man/man8





##############################################################################
# Targets to clean up or uninstall
##############################################################################
clean:

	$(MAKE) -C $(DIR_SECMODULES) clean
	$(MAKE) -C ${DIR_CORE} clean
	$(MAKE) -C ${DIR_DISPATCHER} clean
	$(MAKE) -C ${DIR_CONSOLE} clean

	-rm -f $(DISTRO)/*.pkg
	-rm -f $(DISTRO)/build.log
	-rm -rf ${BUILD_BASE}/Prototype
	-rm -rf ${BUILD_BASE}/package/TCSoslockdown
	-rm -rf ${BUILD_BASE}/root
	-rm -rf ${BUILD_BASE}/package/*

	-rm -rf ${SRCLIB}/PyXML-0.8.4
	-rm -f .pkglist


clean-python-libs:

	(cd ${SRCLIB}/PyXML-0.8.4; $(PYTHON) setup.py clean)


##############################################################################
# Packaging product for distro
##############################################################################
build: build-docs build-prep build-noarch build-arch
	@echo
	@echo "Solaris packages built and are in .${DISTRO}/*.pkg"
	@echo "======================================================================="
	@echo "You can do a hands-free install or upgrade without removing previous 
	@echo "packages with the following command: "
	@echo " "
	@echo "# /usr/sbin/pkgadd -a ./os/solaris/packageAdmin -G -d ${DISTRO}/<packagename.pkg> all"
	@echo "======================================================================="
	@echo " "
	@echo "All packages built: ${DISTRO}"
	@echo "Packages built for target : " `cat ${DISTRO}/BUILT_FOR`
	@echo
	@ls -1 ${DISTRO}/BUILT_FOR ${DISTRO}/*.pkg

build-prep: FORCE
	mkdir -p ${DISTRO}
	@echo ${SB_BUILTFOR} > ${DISTRO}/BUILT_FOR

build-docs: FORCE
	-@if [ $(SB_DOC_PDFS) = "y" ] ; then \
	  $(MAKE) -C $(DIR_DOCS) pdfs && $(MV) ${DIR_DOCS}/dist/pdf/*.pdf ${DISTRO}; \
	fi
	
build-noarch: FORCE
	$(MAKE) -C src/core build
	$(MAKE) -C src/security_modules build
	
	@if [ ${SB_CONSOLE} = "y" ] ; then \
	  $(MAKE) -C src/console build && $(MV) src/console/build/dist/*.pkg $(DISTRO); \
	fi
	$(MV) src/core/build/dist/*.pkg $(DISTRO)
	$(MV) src/security_modules/build/dist/*.pkg $(DISTRO)

build-arch: FORCE printenv
	$(MAKE) -C src/dispatcher build

	$(MV) src/dispatcher/build/dist/*.pkg $(DISTRO)
	$(MV) src/dispatcher/build/dist/AutoupdateComms.pyo $(DISTRO)
	$(MV) src/dispatcher/build/dist/_AutoupdateComms.so $(DISTRO)


build-prereq: FORCE printenv

	-@build/prereq_buildenv_solaris.sh



	

setup-os:

	/usr/bin/crle -c /var/ld/ld.config -l /lib:/usr/lib:/usr/sfw/lib:/usr/local/lib
	if [ ! -h /usr/sfw/lib/libstdc++.so.5 -a -f /usr/sfw/lib/libstdc++.so.6.0.3 ]; then \
	    (cd /usr/sfw/lib; /usr/bin/ln -s libstdc++.so.6.0.3 libstdc++.so.5); \
	fi

printenv: FORCE

	@echo
	@echo "================== BUILD ENVIRONMENT ========================"
	@echo "Platform:     Solaris $(OS_REL) $(ARCH)"
	@echo "Python:       v$(PYTHON_VERS) $(PYTHON) "
	@echo "GCC Compiler: `$(CC) -v 2>&1 |tail -1` "
	@echo "OpenSSL:      `$(OPENSSL) version`"
	@echo "              $(OPENSSL)"
	@echo "============================================================="
	@echo `date`
	@echo


env-setup:


	@$(TEST) ! -z "$(NFS_PKG_SHARE)"
	@$(TEST) ! -z "$(REQDPKGS)"
	##
	## Checking for required packages for build
	##
	@cat /dev/null > .pkglist
	@for pkg in $(REQDPKGS); do \
	     $(PKGINFO) -q $$pkg 1>/dev/null 2>&1 || printf "%s\n" $$pkg >> .pkglist; \
	done
	umask 022
	$(TEST) -d /root || mkdir /root
	chmod 700 /root
	chown root:root /root

	@-umount /tcs-mirrors
	#
	# For Solaris client to be able to mount Linux NFS share, be sure
	# that the /etc/exports file uses 'insecure' option for /data/mirrors
	#
	mount -o ro,vers=3 ${NFS_PKG_SHARE}/${REPOARCH}/Product /tcs-mirrors
	@for pkg in "`cat .pkglist`" ; do \
	    if [ ! -d /tcs-mirrors/$$pkg ]; then \
	      printf "\n\nCan't package %s in /tcs-mirrors\n\n" $$pkg;\
	      exit 1; \
	    fi ; \
	    if [ ! -z "$$pkg" ]; then \
	        /usr/sbin/pkgadd -d /tcs-mirrors $$pkg ;\
	    fi ; \
	done
	umount /tcs-mirrors
	@echo
	passmgmt -m -s /usr/bin/bash root
	passmgmt -m -h /root root
	$(TEST) ! -d /.mozilla || mv -f /.mozilla /root
	$(TEST) ! -d /.gnome || mv -f /.gnome /root
	$(TEST) ! -d /.gnome2 || mv -f /.gnome2 /root
	$(TEST) ! -d /.gconf || mv -f /.gconf /root
	$(TEST) ! -d /.ssh || mv -f /.ssh /root
	$(TEST) ! -d /.grails || mv -f /.grails /root
	$(TEST) ! -d /.kshrc || mv -f /.kshrc /root
	$(TEST) ! -d /.subversion || mv -f /.subversion /root
	$(TEST) ! -d /.gnome2_private || mv -f /.gnome2_private /root
	$(TEST) ! -d /.nautilus || mv -f /.nautilus /root
	$(TEST) ! -d /.dt || mv -f /.dt /root
	$(TEST) ! -d /.metacity || mv -f /.metacity /root
	$(TEST) ! -d /.sunw || mv -f /.sunw /root
	$(TEST) ! -d /.iiim || mv -f /.iiim /root
	$(TEST) ! -d /.softwareupdate || mv -f /.softwareupdate /root

	$(TEST) ! -f /.gtkrc-1.2-gnome2 || mv -f /.gtkrc-1.2-gnome2 /root
	$(TEST) ! -f /.bash_history || mv -f /.bash_history /root
	$(TEST) ! -f /.dtprofile || mv -f /.dtprofile /root
	$(TEST) ! -f /.esd_auth || mv -f /.esd_auth /root
	$(TEST) ! -f /.ICEauthority || mv -f /.ICEauthority /root
	$(TEST) ! -f /.Xauthority || mv -f /.Xauthority /root
	$(TEST) ! -f /.recently-used || mv -f /.recently-used /root
	@-$(RM) -f .pkglist
	@echo PATH=/usr/sbin:/usr/bin:/usr/local/bin:/usr/sfw/bin:/usr/openwin/bin:/usr/ucb > /root/.profile
	@echo export PATH >> /root/.profile
	chmod 700 /root/.profile
	#

propset:
	svn propset svn:keywords $(SVN_PROPS_KEYWORDS) Makefile	
	svn propset svn:keywords $(SVN_PROPS_KEYWORDS) *.mk	

##############################################################################
# Phony target (must be blank/empty!!)

FORCE:
