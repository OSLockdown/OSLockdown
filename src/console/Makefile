##############################################################################
#
# Copyright (c) 2007-2016 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# OS Lockdown - Graphical Console 
#
##############################################################################

export ROOT ?= $(shell pwd)/root

#pick up top level locations for ant/java/grail/fop
include ../../Makefile_common.mk


SPECFILE := build/oslockdown-console.spec
DISTRO   := build/dist
WARFILE  := grails/OSLockdown/target/OSLockdown-${SB_VERSION}-${SB_RELEASE}.war

INITSCRIPT := init.osl-console init.osl-console.suse

# The following directories are excluded when a tar file is created during the
# package build process. They are not needed to build this package so, the more
# we can exclude the faster the RPM build will be.
export EXCLUDE_SRC_DIRS := --exclude=oslockdown/src/core  \
                           --exclude=oslockdown/src/dispatcher \
                           --exclude=oslockdown/src/selinux \
                           --exclude=oslockdown/src/security_modules \
                           --exclude=oslockdown/cfg/docs 
			   
OS_TYPE  := $(strip $(shell uname -s))

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
   INITSCRIPT := ./init.osl-console.solaris
   PKGINFO := build/solaris/pkginfo
   export ROOT := $(shell pwd)/build/solaris/root
   export EFFECTIVE_UID := $(shell /usr/xpg4/bin/id -u)

else
   export INSTALL ?= /usr/bin/install
   export EFFECTIVE_UID := $(shell /usr/bin/id -u)
   export ETH0_ADDR := $(shell /sbin/ifconfig eth0 |awk -F: '/inet addr/ {printf "%s\n", substr($$2, 1, index($$2, " ")-1)}')

   BUILDTARGET := build-linux
   INSTALLTARGET := install-linux

   LINUX_TYPE := $(shell lsb_release -i -s)
   LINUX_RELEASE := $(shell lsb_release -r -s | cut -d '.' -f 1)
   Utils_file :=  ../../os/redhat/utilities.mk


   ifeq ("${LINUX_TYPE}", "Fedora")
      Utils_file := ../../os/fedora/utilities.mk
   endif

   ifeq ("${LINUX_TYPE}", "SUSE LINUX")
      Utils_file := ../../os/suse/utilities.mk
   endif

   ifeq ("${LINUX_TYPE}", "Ubuntu")
      BUILDTARGET := build-ubuntu
      Utils_file := ../../os/ubuntu/utilities.mk
      JAVA_HOME  := /usr/lib/jvm/java-6-openjdk
      ROOT := $(shell pwd)/build/debian
   endif

   include $(Utils_file)

endif

export JAVAFLAVOR := $(strip $(shell python determineJavaFlavorVersion.py -f ${JAVA_HOME}))
export JAVAVERSION := $(strip $(shell python determineJavaFlavorVersion.py -v ${JAVA_HOME}))

# If we're running the IBM Java we need to override a transformer factory
ifeq ("${JAVAFLAVOR}" , "IBM")
  MY_JAVA_OPTS=' -Djavax.xml.transform.TransformerFactory=org.apache.xalan.processor.TransformerFactoryImpl '
else
 MY_JAVA_OPTS=''
endif

IS_S390 := 
ifeq ("$(shell $(UNAME) -m)", "s390x")
  IS_S390 := "yes"
endif


# TOMCAT_ARCHIVE should be an absolute path to where the *stock* Tomcat download (.tar.gz) is located
# We'll pull the filename and what not from that.  Fail if not set

ifndef TOMCAT_ARCHIVE
   $(error TOMCAT_ARCHIVE variable is not set )
endif
export TOMCAT_ARCHIVE ?= ""

# extract the basefilename w/o any sufix - we're assuming it is a .tar.gz file

export TOMCAT_VERS := $(shell basename ${TOMCAT_ARCHIVE} .tar.gz)
export TOMCAT_DIR    := $(shell pwd)/tomcat/${TOMCAT_VERS}

export GRAILS   := JAVA_OPTS=${MY_JAVA_OPTS} $(GRAILS_HOME)/bin/grails

export MAKE ?= /usr/bin/make
export CP ?= /bin/cp


##############################################################################
.DEFAULT_GOAL := war
	


war: TEST_PREREQUISITES docs wsdl

	# Build Web Archive (WAR)
	$(TEST) -d grails/OSLockdown/
	- $(TEST) -f grails/OSLockdown/web-app/WEB-INF/applicationContext.xml || \
	    (cd grails/OSLockdown/;  $(GRAILS) upgrade --non-interactive ) 
	# Slowly migrating pieces to the build.xml file. This will make it easier
	# to check dependencies ultimately speeding up the console build.
	$(ANT) console

	@if [ "${IS_S390}" ] ; then \
	  echo "IBM Java doesn't work with tomcat pluging - remove it" ;\
	  (cd grails/OSLockdown/ ; $(GRAILS) uninstall-plugin tomcat;  ) ; \
	fi
	(cd grails/OSLockdown/; $(GRAILS) set-version $(SB_VERSION)-${SB_RELEASE} )

	(cd grails/OSLockdown/; $(GRAILS) clean-all )

	## Build WAR file for deployment
	(cd grails/OSLockdown/; $(GRAILS) prod war --verbose --non-interactive)

docs: FORCE
	$(MAKE) -C ../../docs prep

TEST_PREREQUISITES: FORCE	
	# Check for a *valid* JAVA_HOME setup with javac 
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

	# Check for a *valid* ANT development environment
	@if [ "${ANT_HOME}" = "" ]; then \
		echo "ANT_HOME is not set";  \
		exit 1; \
	fi
	@if [ ! -d "${ANT_HOME}"  ]; then \
		echo "ANT_HOME (${ANT_HOME}) is not a directory";  \
		exit 1; \
	fi
	@if [ ! -f "${ANT_HOME}/bin/ant"  ]; then \
		echo "${ANT_HOME}/bin/ant does not exist";  \
		exit 1; \
	fi
	@if [ ! -x "${ANT_HOME}/bin/ant"  ]; then \
		echo "${ANT_HOME}/bin/ant is not an executable";  \
		exit 1; \
	fi

	# Check for a *valid* Grails development environment
	@if [ "${GRAILS_HOME}" = "" ]; then \
		echo "GRAILS_HOME is not set";  \
		exit 1; \
	fi
	@if [ ! -d "${GRAILS_HOME}"  ]; then \
		echo "GRAILS_HOME is not a directory";  \
		exit 1; \
	fi
	@if [ ! -f "${GRAILS_HOME}/bin/grails"  ]; then \
		echo "${GRAILS_HOME}/bin/grails does not exist";  \
		exit 1; \
	fi
	@if [ ! -x "${GRAILS_HOME}/bin/grails"  ]; then \
		echo "${GRAILS_HOME}/bin/grails is not an executable";  \
		exit 1; \
	fi



foobar: FORCE
	@echo "Using ${JAVAFLAVOR} ${JAVAVERSION} Java SDK..."
	@echo "JAVA_HOME is ${JAVA_HOME}"
	@echo "MY_JAVA_OPTS are : ${MY_JAVA_OPTS}"
	(cd grails/OSLockdown/; $(GRAILS) set-version $(SB_VERSION)-${SB_RELEASE} )

wsdl: TEST_PREREQUISITES
	@echo "Building Linux package..."
	@echo "Using ${JAVAFLAVOR} ${JAVAVERSION} Java SDK..."

	$(ANT) console-wsdl
#######################################################################
api-docs:
	$(ANT) api-docs


#######################################################################
install-dirs-linux: 

	$(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME} 
	$(INSTALL) -m 0700 -d ${ROOT}/usr/share/${NAME}/console 
	@echo "Creating console (Tomcat) directories"
	@for sbdirs in `(cd $(TOMCAT_DIR); find . -type d -print |egrep -v  '.*/[.]svn.*')`; do \
	    $(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME}/console/$$sbdirs ; \
	    printf "." ; \
	done
	@echo
	$(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME}/lib 
	$(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME}/tools/

	@echo "Creating stylesheets/ subdirectories"
	@for sbdirs in `find ../xsl -type d ! -regex '.*/[.]svn.*' -print | cut -d / -f 3-`; do \
	    $(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME}/cfg/stylesheets/$$sbdirs; \
	    printf "." ; \
        done
	@echo

	$(INSTALL) -m 0700 -d ${ROOT}/var/lib/${NAME}/console/db
	$(INSTALL) -m 0700 -d ${ROOT}/var/lib/${NAME}/console/temp
	$(INSTALL) -m 0755 -d ${ROOT}/var/lib/${NAME}/files

	$(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME}/cfg
	$(INSTALL) -m 0755 -d ${ROOT}/usr/share/${NAME}/cfg/schema
	$(INSTALL) -m 0700 -d ${ROOT}/usr/share/${NAME}/cfg/wsdl

	$(INSTALL) -m 0700 -d ${ROOT}/var/lib/${NAME}/logs
	$(INSTALL) -m 0700 -d ${ROOT}/var/lib/${NAME}/profiles
	$(INSTALL) -m 0700 -d ${ROOT}/var/lib/${NAME}/baseline-profiles
	$(INSTALL) -m 0700 -d ${ROOT}/var/lib/${NAME}/reports
	$(INSTALL) -m 0750 -d ${ROOT}/var/lib/${NAME}/files/ClientUpdates
	$(INSTALL) -m 0750 -d ${ROOT}/var/lib/${NAME}/files/ClientUpdates/autoupdate

install-dirs-solaris: 
	###########################################################
	### Solaris MUST have its own install-dirs target because
	### it's system directories have such different ownerships
	###########################################################
	test ! -d build/solaris/root || rm -rf build/solaris/root

	##
	## Standard Solaris directory structures
	##
	$(INSTALL) -d -m 0755 -o root -g sys build/solaris/root/var 
	$(INSTALL) -d -m 0755 -o root -g sys build/solaris/root/usr 
	$(INSTALL) -d -m 0755 -o root -g sys build/solaris/root/etc 
	$(INSTALL) -d -m 0755 -o root -g sys build/solaris/root/etc/init.d
	$(INSTALL) -d -m 0755 -o root -g other build/solaris/root/var/lib 
	$(INSTALL) -d -m 0755 -o root -g sys build/solaris/root/usr/share 
	$(INSTALL) -d -m 0755 -o root -g bin build/solaris/root/lib
	#
	# SMF Directories
	#
	$(INSTALL) -o root -g bin -m 0755 -d build/solaris/root/lib/svc
	$(INSTALL) -o root -g bin -m 0755 -d build/solaris/root/lib/svc/method
	$(INSTALL) -o root -g sys -m 0755 -d build/solaris/root/var/svc
	$(INSTALL) -o root -g sys -m 0755 -d build/solaris/root/var/svc/manifest
	$(INSTALL) -o root -g sys -m 0755 -d build/solaris/root/var/svc/manifest/site
	$(INSTALL) -o root -g sys -m 0755 -d build/solaris/root/var/svc/profile

	# Application specific
	$(INSTALL) -d -m 0755 -o root -g root build/solaris/root/usr/share/${NAME}  
	$(INSTALL) -d -m 0700 -o root -g root build/solaris/root/usr/share/${NAME}/console  
	$(INSTALL) -d -m 0755 -o root -g root build/solaris/root/usr/share/${NAME}/tools  

	@echo "Creating stylesheets/ subdirectories..."
	@for sbdirs in `find ../xsl -type d -print |egrep -v .svn | cut -d / -f 3-`; do \
	    $(INSTALL) -d -m 0755 -o root -g root build/solaris/root/usr/share/${NAME}/cfg/stylesheets/$$sbdirs; \
	    printf "." ; \
        done
	@echo

	@echo "Creating console (Tomcat) directories..."
	for sbdirs in `(cd $(TOMCAT_DIR); find . -type d -print |egrep -v  '.*/[.]svn.*')`; do \
	    $(INSTALL) -d -o root -g root -m 0750 build/solaris/root/usr/share/${NAME}/console/$$sbdirs ; \
	    printf "." ; \
	done
	@echo 

	$(INSTALL) -d -m 0755 -o root -g root build/solaris/root/usr/share/${NAME}/lib  

	$(INSTALL) -d -o root -g root -m 0700 build/solaris/root/var/lib/${NAME}/console/db
	$(INSTALL) -d -o root -g root -m 0700 build/solaris/root/var/lib/${NAME}/console/temp
	$(INSTALL) -d -o root -g root -m 0755 build/solaris/root/var/lib/${NAME}/console/files

	$(INSTALL) -d -o root -g root -m 0755 build/solaris/root/usr/share/${NAME}/cfg
	$(INSTALL) -d -o root -g root -m 0755 build/solaris/root/usr/share/${NAME}/cfg/schema
	$(INSTALL) -d -o root -g root -m 0700 build/solaris/root/usr/share/${NAME}/cfg/wsdl

	$(INSTALL) -d -o root -g root -m 0700 build/solaris/root/var/lib/${NAME}/logs
	$(INSTALL) -d -o root -g root -m 0700 build/solaris/root/var/lib/${NAME}/profiles
	$(INSTALL) -d -o root -g root -m 0700 build/solaris/root/var/lib/${NAME}/baseline-profiles
	$(INSTALL) -d -o root -g root -m 0700 build/solaris/root/var/lib/${NAME}/reports
	$(INSTALL) -d -o root -g root -m 0750 build/solaris/root/var/lib/${NAME}/files/ClientUpdates
	$(INSTALL) -d -o root -g root -m 0750 build/solaris/root/var/lib/${NAME}/files/ClientUpdates/autoupdate



#################################################
install-linux: prepTomcat install-dirs-linux

	$(TEST) -f $(WARFILE)
	@echo "Copying java_test.sh helper script...."
	$(INSTALL) -m 0750 java_test.sh ${ROOT}/usr/share/${NAME}/console/bin

	@echo "Copying Tomcat files...."
	@for sbfiles in `(cd $(TOMCAT_DIR); find . -type f |egrep -v '.*/[.]svn.*')`; do \
	    $(INSTALL) -m 0640 $(TOMCAT_DIR)/$$sbfiles ${ROOT}/usr/share/${NAME}/console/$$sbfiles; \
	    printf "." ; \
	done
        
	@echo
	@for sbfile in ${INITSCRIPT}; do \
	    $(INSTALL) -m 0750 $$sbfile ${ROOT}/usr/share/${NAME}/$$sbfile; \
	    printf "Copying %s ..." $$sbfile; \
	done

	@echo
	@echo "Installing stylesheets/ files"
	@for sbfile in `find ../xsl -name '*.xsl' -type f ! -regex '.*/[.]svn.*' -print | grep -v all-in-one-generic.xsl | cut -d / -f 3-`; do \
	    $(INSTALL) -m 0444 ../xsl/$$sbfile ${ROOT}/usr/share/${NAME}/cfg/stylesheets/$$sbfile; \
	    printf "."; \
        done

	@ echo
	$(INSTALL) -m 0644 ../xsl/common/* ${ROOT}/usr/share/${NAME}/cfg/stylesheets/common/
	$(INSTALL) -m 0644 ../xsl/fo/*png ${ROOT}/usr/share/${NAME}/cfg/stylesheets/fo/
	$(INSTALL) -m 0644 grails/OSLockdown/web-app/images/OSLockdown_report.png ${ROOT}/usr/share/${NAME}/cfg/stylesheets/fo/
	$(INSTALL) -m 0600 ${WARFILE} ${ROOT}/usr/share/${NAME}/console/webapps/OSLockdown.war

	$(INSTALL) -m 0644 ../../cfg/ConsoleWarningBanner.txt ${ROOT}/usr/share/${NAME}/cfg
	$(INSTALL) -m 0644 ../../cfg/USG-ConsoleWarningBanner.txt ${ROOT}/usr/share/${NAME}/cfg

	$(INSTALL) -m 0400 AgentCommunication/wsgen/resources/*.wsdl ${ROOT}/usr/share/${NAME}/cfg/wsdl
	$(INSTALL) -m 0400 AgentCommunication/wsgen/resources/*.xsd  ${ROOT}/usr/share/${NAME}/cfg/wsdl

	@ echo "Installing autoupdate core files"
	$(INSTALL) -m 0750 autoupdate/AutoupdateCommsShim.py ${ROOT}/var/lib/oslockdown/files/ClientUpdates/autoupdate
	$(INSTALL) -m 0750 autoupdate/DetermineOS.py         ${ROOT}/var/lib/oslockdown/files/ClientUpdates/autoupdate
	$(INSTALL) -m 0750 autoupdate/InstallUpdate.py	     ${ROOT}/var/lib/oslockdown/files/ClientUpdates/autoupdate
	$(INSTALL) -m 0750 autoupdate/SB_errors.py    	     ${ROOT}/var/lib/oslockdown/files/ClientUpdates/autoupdate
	$(INSTALL) -m 0750 autoupdate/SB_Updaters.py  	     ${ROOT}/var/lib/oslockdown/files/ClientUpdates/autoupdate


#################################################
install-solaris: clean prepTomcat install-dirs-solaris war

	$(TEST) -f $(WARFILE)
	@echo "Copying java_test.sh helper script...."
	$(INSTALL) -m 0750 -o root -g root java_test.sh  build/solaris/root/usr/share/${NAME}/console/bin

	@echo "Copying Tomcat files...."
	@for sbfiles in `(cd $(TOMCAT_DIR); find . -type f |egrep -v '.*/[.]svn.*')`; do \
	    $(INSTALL) -m 0640 -o root -g root $(TOMCAT_DIR)/$$sbfiles build/solaris/root/usr/share/${NAME}/console/$$sbfiles; \
	    printf "." ; \
	done
	@echo

	@echo "Installing stylesheets/ files"
	@for sbfile in `find ../xsl -name '*.xsl' -type f -print |egrep -v .svn | grep -v all-in-one-generic.xsl | cut -d / -f 3-`; do \
	    $(INSTALL) -o root -g root -m 0644 ../xsl/$$sbfile build/solaris/root/usr/share/${NAME}/cfg/stylesheets/$$sbfile; \
	    printf "."; \
        done
	@echo

	chmod +x build/solaris/root/usr/share/${NAME}/console/bin/*.sh

	$(INSTALL) -m 0644 -o root -g root ../xsl/common/* build/solaris/root/usr/share/${NAME}/cfg/stylesheets/common/
	$(INSTALL) -m 0644 -o root -g root ../xsl/fo/*png build/solaris/root/usr/share/${NAME}/cfg/stylesheets/fo/
	$(INSTALL) -m 0644 -o root -g root grails/OSLockdown/web-app/images/OSLockdown_report.png build/solaris/root/usr/share/${NAME}/cfg/stylesheets/fo/

	$(INSTALL) -m 0600 -o root -g root ${WARFILE} build/solaris/root/usr/share/${NAME}/console/webapps/OSLockdown.war
	#
	# Service Management Facility (SMF)
	$(INSTALL) -m 0755 -o root -g bin ${INITSCRIPT} build/solaris/root/lib/svc/method/osl-console
	$(INSTALL) -m 0444 -o root -g sys osl-console.xml build/solaris/root/var/svc/manifest/site/osl-console.xml 
	#
	$(INSTALL) -m 0644 -o root -g root ../../cfg/ConsoleWarningBanner.txt build/solaris/root/usr/share/${NAME}/cfg
	$(INSTALL) -m 0644 -o root -g root ../../cfg/USG-ConsoleWarningBanner.txt build/solaris/root/usr/share/${NAME}/cfg

	# Solaris /usr/ucb/install command won't take wildcards :-(
	for sbfiles in `(cd AgentCommunication/wsgen/resources; ls -1 *.wsdl)`; do \
	    $(INSTALL) -m 0640 -o root -g root AgentCommunication/wsgen/resources/$$sbfiles build/solaris/root/usr/share/${NAME}/cfg/wsdl; \
	done
	for sbfiles in `(cd AgentCommunication/wsgen/resources; ls -1 *.xsd)`; do \
	    $(INSTALL) -m 0640 -o root -g root AgentCommunication/wsgen/resources/$$sbfiles build/solaris/root/usr/share/${NAME}/cfg/wsdl; \
	done

	@ echo "Installing autoupdate core files"
	$(INSTALL) -m 0750 -o root -g root autoupdate/AutoupdateCommsShim.py build/solaris/root/var/lib/${NAME}/files/ClientUpdates/autoupdate
	$(INSTALL) -m 0750 -o root -g root autoupdate/DetermineOS.py	     build/solaris/root/var/lib/${NAME}/files/ClientUpdates/autoupdate
	$(INSTALL) -m 0750 -o root -g root autoupdate/InstallUpdate.py       build/solaris/root/var/lib/${NAME}/files/ClientUpdates/autoupdate
	$(INSTALL) -m 0750 -o root -g root autoupdate/SB_errors.py	     build/solaris/root/var/lib/${NAME}/files/ClientUpdates/autoupdate
	$(INSTALL) -m 0750 -o root -g root autoupdate/SB_Updaters.py	     build/solaris/root/var/lib/${NAME}/files/ClientUpdates/autoupdate

install: $(INSTALLTARGET)
	@echo


#######################################################################
build: TEST_PREREQUISITES $(BUILDTARGET) 
	@echo 


prepTomcat_old: FORCE
	@echo ##
	@echo ## Prepare Tomcat distribution from compressed tarball
	@echo ## Start with *stock* tomcat tarball
	@echo ##
	$(TEST) -d tomcat || ${MKDIR} tomcat
	$(TEST) -f tomcat/${TOMCAT_VERS}.tar.gz || cp ${TOMCAT_ARCHIVE} tomcat/
	$(TEST) ! -f tomcat/${TOMCAT_VERS}.tar || $(RM) -f tomcat/${TOMCAT_VERS}.tar
	cd tomcat; ${GUNZIP} -q -f ${TOMCAT_VERS}.tar.gz
	cd tomcat; ${TAR} xf ${TOMCAT_VERS}.tar
	@echo ##
	@echo ## Delete all webapps and clear some default configs that we overwrite during our config time
	@echo ##
	cd tomcat/${TOMCAT_VERS} ; ${RM} -rf webapps conf/server.xml conf/catalina.properties
	@echo ##
	@echo ## Overwrite with our modified/new files
	@echo ##
	${CP} -r TOMCAT_MODS_OLD/${TOMCAT_VERS}/* tomcat//${TOMCAT_VERS}

prepTomcat: FORCE
	#
	#  NOTE - IF YOU UPDATE TOMCAT, VERIFY THAT THE CHANGES BELOW STILL WORK
	#  ESPECIALLY IF THE CONTENTS OF conf/server.xml CHANGE
	#
	@echo ##
	@echo ## Prepare Tomcat distribution from compressed tarball
	@echo ## Start with *stock* tomcat tarball
	@echo ##
	$(TEST) ! -d tomcat || rm -rf tomcat
	${MKDIR} tomcat
	cd tomcat; ${TAR} xzf ${TOMCAT_ARCHIVE}
	@echo ##
	@echo ## Delete all webapps. amd replace with our minimal root set to redirect to our app (important - we're using servlet 2.5
	@echo ##
	${RM} -rf tomcat/${TOMCAT_VERS}/webapps 
	${CP} -r TOMCAT_MODS/webapps tomcat/${TOMCAT_VERS}
	@echo ##
	
	## Add our environment set/checks
	${CP} -r TOMCAT_MODS/bin/setenv.sh tomcat/${TOMCAT_VERS}/bin/setenv.sh
	
	## Add library file to suppress version on error
	${CP} -r TOMCAT_MODS/lib/org tomcat/${TOMCAT_VERS}/lib/
	
	## Preserve the default catalina properties, but with some defaults for timeouts
	mv tomcat/${TOMCAT_VERS}/conf/catalina.properties tomcat/${TOMCAT_VERS}/conf/catalina.properties_gold
	echo "#" >>  tomcat/${TOMCAT_VERS}/conf/catalina.properties_gold
	echo "#" >>  tomcat/${TOMCAT_VERS}/conf/catalina.properties_gold
	echo "# Specify Console startup info, such as ip, key/truststore & passkeys, notification address" >> tomcat/${TOMCAT_VERS}/conf/catalina.properties_gold
	echo "tcs.sb.console.notification.poll.interval=30" >> tomcat/${TOMCAT_VERS}/conf/catalina.properties_gold
	echo "tcs.sb.console.registration.poll.interval=30" >> tomcat/${TOMCAT_VERS}/conf/catalina.properties_gold
	
	## Edit logging properties to remove references to host/manager logs, and hardcode logging dir
	## Note we can't use the '-i' option for sed, as Solaris 10 does not support that option
	

	cat tomcat/${TOMCAT_VERS}/conf/logging.properties | \
		sed -e 's:\$${catalina.base}:/var/lib/oslockdown:g' \
		    -e '/^.manager/d' -e '/^.host-manager/ d' > tomcat/${TOMCAT_VERS}/conf/working \
		    -e 's/, .manager.org.apache.juli.FileHandler/ /g' \
		    -e 's/, .host-manager.org.apache.juli.FileHandler/ /g' \
	            -e '/\/manager/ d' -e '/\/host-manager/ d' > tomcat/${TOMCAT_VERS}/conf/working 
	mv tomcat/${TOMCAT_VERS}/conf/working tomcat/${TOMCAT_VERS}/conf/logging.properties 

	## Copy in our server.xml files, and remove stock server.xml
	${CP} TOMCAT_MODS/conf/server.xml_all_ciphers tomcat/${TOMCAT_VERS}/conf
	${CP} TOMCAT_MODS/conf/server.xml_restrict_ciphers tomcat/${TOMCAT_VERS}/conf
	${RM} tomcat/${TOMCAT_VERS}/conf/server.xml

build-ubuntu: FORCE war install

	@echo ##
	@echo ## Building Ubuntu (Debian) Package 
	@echo ##
	mkdir -p ${ROOT}/DEBIAN
	sed 's/^Version: .*/Version: ${SB_VERSION}-${SB_RELEASE}/' build/ubuntu/control > ${ROOT}/DEBIAN/control
	dpkg-deb --build build/debian build/dist/oslockdown-console_${SB_VERSION}-${SB_RELEASE}_all.deb


build-linux: 

	@echo "Building Linux package..."
	@echo "Using ${JAVAFLAVOR} ${JAVAVERSION} Java SDK..."
        
	@echo ## 
	@echo ## Creating RPM build directories if required....
	@echo ##
	mkdir -p ${BUILD_BASE}/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

	$(TEST) -f ${SPECFILE}

	# Create TAR of source code
	echo "Creating tarball to build RPM using ${SPECFILE}"; \
	$(TAR) -C ../../.. ${EXCLUDE_SRC_DIRS} ${COMMON_EXCLUDES} -czf ${BUILD_BASE}/SOURCES/oslockdown.tar.gz oslockdown ;

	# Build Packages
	-mkdir -p ${DISTRO}
	$(RPMBUILD) --define "_topdir ${BUILD_BASE}" -bb ${SPECFILE} 2>&1 |$(TEE) ${DISTRO}/build-console_${JAVAFLAVOR}_${JAVAVERSION}.log
	@echo
        	
	# Copy Packages into distro folder
	-mv ${BUILD_BASE}/RPMS/noarch/oslockdown-console*.rpm ${DISTRO}/
	
build-solaris: FORCE install

        # We use parameters out of the spec file to build Solaris package properties
	$(TEST) -f ${SPECFILE}

	@echo "Building Solaris package..."
	#
	# Pkginfo 
	#
	printf "PKG=\"TCSoslockdown-console\"\n" > $(PKGINFO)
	printf "NAME=\"OS Lockdown Console\"\n" >> $(PKGINFO)
	printf "VERSION=\"%s\"\n" ${SB_VERSION}-${SB_RELEASE} >> $(PKGINFO)
	printf "ARCH=\"all\"\n" >> $(PKGINFO)
	printf "SUNW_PRODNAME=\"SunOS\"\n" >> $(PKGINFO)
	printf "SUNW_PRODVERS=\"5.10\"\n" >> $(PKGINFO)
	printf "CLASSES=\"none\"\n" >> $(PKGINFO)
	printf "MAXINST=1\n" >> $(PKGINFO)
	printf "SUNW_PKG_THISZONE=true\n" >> $(PKGINFO)
	printf "CATEGORY=\"utility\"\n" >> $(PKGINFO)
	printf "VENDOR=\"OSLockdown\"\n" >> $(PKGINFO)
	printf "BASEDIR=\"/\"\n" >> $(PKGINFO)
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
	(cd build/solaris/; pkginfo -l -d package TCSoslockdown-console)
	(cd build/solaris/; pkgtrans -s package oslockdown-console-${SB_VERSION}-${SB_RELEASE}.sol10.noarch.pkg TCSoslockdown-console)

	mkdir -p ${DISTRO}
	mv build/solaris/package/oslockdown-console-${SB_VERSION}-${SB_RELEASE}.sol10.noarch.pkg build/dist

account:

	id -u sbwebapp 1>/dev/null 2>&1 || useradd -r -K  SYS_UID_MIN=100 -U -d /usr/share/oslockdown/console -M -s /bin/bash sbwebapp
	passwd -l sbwebapp


refresh:
	(cd grails/OSLockdown/; $(GRAILS) refresh-dependencies --non-interactive)

dependency:
	(cd grails/OSLockdown/; $(GRAILS) --refresh-dependencies dependency-report )

################################################################################
	

dev-setup: war 

	$(TEST) -f grails/OSLockdown/web-app/WEB-INF/applicationContext.xml || \
	    (cd grails/OSLockdown/;  $(GRAILS) upgrade --non-interactive )

	$(ANT) console
	# Put anything that needs to be done as root here....
	
	mkdir -p /usr/share/oslockdown/console/conf
	echo "tcs.sb.console.port=8080" > /usr/share/oslockdown/console/conf/catalina.properties
	echo "tcs.sb.console.ip=${ETH0_ADDR}" >> /usr/share/oslockdown/console/conf/catalina.properties
	echo "tcs.sb.console.notification.poll.interval=30" >> /usr/share/oslockdown/console/conf/catalina.properties
	echo "tcs.sb.console.registration.poll.interval=30" >> /usr/share/oslockdown/console/conf/catalina.properties

	mkdir -p /var/lib/oslockdown/profiles
	cp ../security_modules/profiles/*.xml /var/lib/oslockdown/profiles

	mkdir -p /var/lib/oslockdown/baseline-profiles
	cp ../core/baseline-profile.xml /var/lib/oslockdown/baseline-profiles/Default.xml

	mkdir -p grails/OSLockdown/web-app/WEB-INF/
	cp grails/OSLockdown/grails-app/conf/sun-jaxws.xml grails/OSLockdown/web-app/WEB-INF/

	mkdir -p /usr/share/oslockdown/console/webapps/OSLockdown/sbhelp/admin
	cp grails/OSLockdown/web-app/sbhelp/admin/jhelpmap.jhm /usr/share/oslockdown/console/webapps/OSLockdown/sbhelp/admin

	mkdir -p /usr/share/oslockdown/console/webapps/OSLockdown/sbhelp/modules
	cp grails/OSLockdown/web-app/sbhelp/modules/jhelpmap.jhm /usr/share/oslockdown/console/webapps/OSLockdown/sbhelp/modules
	
	mkdir -p /usr/share/oslockdown/cfg
	cp ../core/cfg/baseline-modules.xml /usr/share/oslockdown/cfg
	cp ../security_modules/cfg/*.xml /usr/share/oslockdown/cfg

	mkdir -p /usr/share/oslockdown/cfg/schema
	cp ../../cfg/schema/*.xsd /usr/share/oslockdown/cfg/schema
	cp ../security_modules/cfg/schema/*.xsd /usr/share/oslockdown/cfg/schema
	
	@for sbdirs in `find ../xsl -type d ! -regex '.*/[.]svn.*' -print | cut -d / -f 3-`; do \
	    mkdir -p /usr/share/oslockdown/cfg/stylesheets/$$sbdirs; \
	done

	@for sbfile in `find ../xsl -name '*.xsl' -type f ! -regex '.*/[.]svn.*' -print | cut -d / -f 3-`; do \
	    cp  ../xsl/$$sbfile /usr/share/oslockdown/cfg/stylesheets/$$sbfile; \
	done        

	mkdir -p /usr/share/oslockdown/cfg/wsdl
	cp AgentCommunication/wsgen/resources/*.xsd /usr/share/oslockdown/cfg/wsdl/
	cp AgentCommunication/wsgen/resources/*.wsdl /usr/share/oslockdown/cfg/wsdl/

	@echo

dev-new-db:
	-$(RM) -f grails/OSLockdown/instance.script grails/OSLockdown/instance.properties grails/OSLockdown/instance.logs	


dev-run-asis: 
	cd grails/OSLockdown ; ${GRAILS} --reloading dev run-app


dev-run-enterprise: dev-setup
	mkdir -p /var/lib/oslockdown/files
	echo "Enterprise" > /var/lib/oslockdown/files/ConsoleType.txt
	cd grails/OSLockdown ; ${GRAILS} --reloading dev run-app


dev-run-standalone: dev-setup
	mkdir -p /var/lib/oslockdown/files
	echo "Standalone" > /var/lib/oslockdown/files/ConsoleType.txt
	cd grails/OSLockdown ; ${GRAILS} --reloading dev run-app

	
compile: dev-setup
	(cd grails/OSLockdown/; $(GRAILS) compile)

depreport: 
	(cd grails/OSLockdown/; $(GRAILS) dependency-report)

################################################################################
clean: TEST_PREREQUISITES  

	## Cleaning
	- (cd grails/OSLockdown/; $(GRAILS) clean)
	(cd AgentCommunication/; $(ANT) clean)
	#
	-$(RM) -rf tomcat
	-$(RM) -f grails/OSLockdown/OSLockdown*.war
	-$(RM) -f autoupdate.tgz
	-$(RM) -f ${DISTRO}/*
	$(ANT) clean-console

	-$(RM) -rf $(GRAILS_HOME)/downloads/*
	$(TEST)  ! -d root || $(RM) -rf root
	$(TEST)  ! -d build/solaris/root || $(RM) -rf build/solaris/root
	$(TEST)  ! -d build/solaris/package || $(RM) -rf build/solaris/package

	-$(RM) -f build/solaris/Prototype
	-$(RM) -f build/solaris/pkginfo
	-$(RM) -f grails/OSLockdown/web-app/css/main.css
	-$(RM) -fr rpmbuilddir

FORCE:

