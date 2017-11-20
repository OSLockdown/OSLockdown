##############################################################################
# Copyright (c) 2007-2016 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# rpm spec - Package Specification file for OS Lockdown 
#
##############################################################################

%define isProduction %(test -z "$SB_RELEASE" && echo 0 || echo 1)

%define sbRelease %(echo "$SB_RELEASE")
%define sbVersion %(echo "$SB_VERSION")
%define buildFor %(echo "$SB_BUILTFOR")

%define isSuse   %(test -e /etc/SuSE-release   && echo 1 || echo 0)
%define isFedora %(test -e /etc/fedora-release && echo 1 || echo 0)
%define isRedhat %(test -e /etc/redhat-release && echo 1 || echo 0)

%define osFullRellease %(lsb_release -r -s)
%define osRelease %(lsb_release -r -s |cut -f1 -d.)

# Define and turn off distribution flags
%define isRhel4  0
%define isRhel5  0
%define isSuse10 0
%define isSuse11 0
%define isFc10   0
%define isFc11   0
%define isFc12   0
%define isFc13   0

%define isS390x 0
%define isS390x %(test "`uname -m `" = "s390x" && echo 1 || echo 0)

# Turn on appropriate distribution flags
%if %isRedhat
%define dist .el%{osRelease}
%define isRhel4 %(test "`lsb_release -r -s |cut -f1 -d.`" = "4" && echo 1 || echo 0)
%define isRhel5 %(test "`lsb_release -r -s |cut -f1 -d.`" = "5" && echo 1 || echo 0)
%endif

%if %isSuse
%define dist .suse%{osRelease}
%define isSuse10 %(test "`lsb_release -r -s |cut -f1 -d.`" = "10" && echo 1 || echo 0)
%define isSuse11 %(test "`lsb_release -r -s |cut -f1 -d.`" = "11" && echo 1 || echo 0)
%endif

%if %isFedora
%define dist .fc%{osRelease}
%define isFc10 %(test "`lsb_release -r -s |cut -f1 -d.`" = "10" && echo 1 || echo 0)
%define isFc11 %(test "`lsb_release -r -s |cut -f1 -d.`" = "11" && echo 1 || echo 0)
%define isFc12 %(test "`lsb_release -r -s |cut -f1 -d.`" = "12" && echo 1 || echo 0)
%define isFc13 %(test "`lsb_release -r -s |cut -f1 -d.`" = "13" && echo 1 || echo 0)
%endif

##############################################################################
Summary: Security Blanet Lockdown Application Core
Name:    oslockdown
Version: %{sbVersion}
Release: %{sbRelease}%{?dist}
License: GPLv3
Group:   System/Configuration/Other
Source:  %{name}.tar.gz
Vendor:  OSLockdown
URL:     http://www.TrustedCS.com

BuildArchitectures: noarch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: make 
BuildRequires: python 
BuildRequires: python-devel


%if %isRhel4
BuildRequires: redhat-lsb
%endif

%if %isRhel5
BuildRequires: redhat-lsb
%endif

%if %isFc10
BuildRequires: redhat-lsb
%endif

%if %isFc11
BuildRequires: redhat-lsb
%endif

%if %isFc12
BuildRequires: redhat-lsb
%endif

%if %isFc13
BuildRequires: redhat-lsb
%endif

Requires: coreutils 
Requires: diffutils
Requires: e2fsprogs
Requires: gawk 
Requires: grep 
Requires: libxml2
Requires: libxml2-python
Requires: libxslt 
Requires: net-tools 
Requires: patch
Requires: pciutils 
Requires: procps 
Requires: python 
Requires: rpm-python
Requires: sed 

%if %isSuse
Requires: python-xml
%endif

%if %isS390x
%else
Requires: usbutils 
%endif

%if %isRhel4
Requires: chkconfig 
Requires: openssl >= 0.9.7a
Requires: shadow-utils 
%endif

%if %isRhel5
Requires: chkconfig 
%if %isS390x
%else
Requires: dmidecode 
%endif
Requires: openssl >= 0.9.8b
Requires: shadow-utils 
%endif

%if %isFc10
Requires: chkconfig 
Requires: openssl >= 0.9.8g
%endif

%if %isFc11
Requires: chkconfig 
Requires: openssl >= 0.9.8k
%endif

%if %isFc12
Requires: chkconfig 
Requires: openssl >= 0.9.8k
%endif

%if %isFc13
Requires: chkconfig 
#Requires: openssl >= 1.0.0a-fips
Requires: openssl >= 1.0.0
%endif

%if %isSuse11
Requires: aaa_base 
Requires: openssl >= 0.9.8h
# pmtools was renamed to 'dmidecode' in 11.2
#Requires: pmtools
%endif

%if %isSuse11
Requires: libexpat1 
%else
Requires: expat
%endif

%define debug_package %{nil}

%description
OS Lockdown is an application to aid in the process of securing a system against malicious attacks.  (Applicable for %{buildFor} systems)


##############################################################################
# Build Packages
##############################################################################
%prep
%setup -q -n %{name}

%build
make BUILDARCH=%{_arch} -C ${RPM_BUILD_DIR}/oslockdown/src/core

%install
make ROOT="${RPM_BUILD_ROOT}" -C ${RPM_BUILD_DIR}/oslockdown/src/core install

%clean
rm -rf ${RPM_BUILD_ROOT}


###############################################################################
# Pre- and Post-install 
###############################################################################
%pre 
/usr/bin/getent group sbwebapp > /dev/null || groupadd -r sbwebapp
/usr/bin/getent passwd sbwebapp > /dev/null || \
    useradd -r -g sbwebapp -d /usr/share/oslockdown/console -M -s /bin/bash -c "OS Lockdown GUI" sbwebapp
    
if [ ! -f /etc/SuSE-release ]; then
    passwd -l sbwebapp 1>/dev/null 2>&1 || /bin/true
fi

%post


##############################################################################
# Files 
##############################################################################
%files
%defattr(-,root,root)
%{_sbindir}/%{name}

%dir %attr(750,root,sbwebapp) /usr/share/%{name}
%dir /var/lib/%{name}
%dir /var/lib/%{name}/backup 
%dir /var/lib/%{name}/fs-scan 
%dir %attr(2750,root,sbwebapp)  /usr/share/%{name}/cfg
%dir %attr(3770,root,sbwebapp) /var/lib/%{name}/logs 
%dir %attr(3770,root,sbwebapp)/var/lib/%{name}/reports
%dir %attr(750,root,sbwebapp) /usr/share/%{name}/sb_utils
%dir %attr(750,root,sbwebapp) /usr/share/%{name}/tools
%dir %attr(3750,root,sbwebapp) /var/lib/%{name}/reports/standalone
%dir %attr(750,root,sbwebapp) /var/lib/%{name}/files
%dir %attr(3770,sbwebapp,sbwebapp) /var/lib/%{name}/baseline-profiles
%dir %attr(3770,sbwebapp,sbwebapp) /var/lib/%{name}/profiles

%attr(750,root,sbwebapp)     /usr/share/%{name}/cfg
%attr(770,sbwebapp,sbwebapp) /var/lib/%{name}/baseline-profiles/*
%attr(440,root,sbwebapp) /var/lib/%{name}/files/exclude-dirs
%attr(440,root,sbwebapp) /var/lib/%{name}/files/inclusion-fstypes
%attr(440,root,sbwebapp) /var/lib/%{name}/files/sgid_whitelist
%attr(440,root,sbwebapp) /var/lib/%{name}/files/suid_whitelist

# Note explicit removal of execute perms for SB_Remove
%attr(440,root,root) /usr/share/%{name}/tools/SB_Remove

%attr(750,root,sbwebapp) /usr/share/%{name}/sb_utils/auth

/etc/logrotate.d/oslockdown
/usr/share/%{name}/Diagnostics.pyo
/usr/share/%{name}/ModuleInfo.pyo
/usr/share/%{name}/CoreEngine.pyo
/usr/share/%{name}/sbProps.pyo
/usr/share/%{name}/oslockdown.pyo
/usr/share/%{name}/StateHandler.pyo
/usr/share/%{name}/TCSLogger.pyo
/usr/share/%{name}/tcs_utils.pyo
/usr/share/%{name}/AutoUpdate.pyo
/usr/share/%{name}/PreserveCustomChanges.pyo
/usr/share/%{name}/tools
/usr/share/%{name}/sb_utils
/usr/share/%{name}/Baseline

%doc /usr/share/man/man8/oslockdown.*

##############################################################################
# Change History
##############################################################################
