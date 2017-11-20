##############################################################################
# Copyright (c) 2007-2016 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# rpm spec - Package Specification file for OS Lockdown Modules 
#
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
%define isRhel4      0
%define isRhel5      0
%define isSuse10     0
%define isSuse11     0
%define isFc10       0
%define isFc11       0
%define isFc12       0
%define isOpenSuse   0
%define isNovellSuse 0

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
%define isOpenSuse   %(test "`grep -i suse /etc/SuSE-release |cut -f1 -d' '`"  = "openSUSE" && echo 1 || echo 0)
%define isNovellSuse %(test "`grep -i suse /etc/SuSE-release | cut -f1 -d' '`" = "SUSE"     && echo 1 || echo 0)
%endif

%if %isFedora
%define dist .fc%{osRelease}
%define isFc10 %(test "`lsb_release -r -s |cut -f1 -d.`" = "10" && echo 1 || echo 0)
%define isFc11 %(test "`lsb_release -r -s |cut -f1 -d.`" = "11" && echo 1 || echo 0)
%define isFc12 %(test "`lsb_release -r -s |cut -f1 -d.`" = "12" && echo 1 || echo 0)
%endif

##############################################################################
Summary: Security Lockdown Application Modules
Name:    oslockdown-modules
Version: %{sbVersion}
Release: %{sbRelease}%{?dist}
Group:   System/Configuration/Other
Source:  oslockdown-modules.tar
Vendor:   OSLockdown
URL:      http://www.TrustedCS.com
License:  GPLv3

BuildArchitectures: noarch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: binutils 
BuildRequires: make
BuildRequires: python 
BuildRequires: python-devel

Requires: oslockdown >= %{version}

Requires: net-tools 
Requires: patch
Requires: pciutils 
Requires: procps 
Requires: python 
Requires: rpm-python
Requires: sed 
%if %isS390x
%else
Requires: usbutils 
%endif

%if %isRhel4
Requires: chkconfig 
Requires: shadow-utils 
%endif

%if %isRhel5
Requires: chkconfig 
Requires: shadow-utils 
%endif

%if %isFc10
Requires: chkconfig 
%endif

%if %isFc11
Requires: chkconfig 
%endif

%if %isFc12
Requires: chkconfig 
%endif

%if %isSuse11
Requires: aaa_base 
%endif

%if %isSuse10
%if %isNovellSuse 
Requires: python-devel
%endif
%endif

%define debug_package %{nil}

%description 
OS Lockdown modules perform the scan, apply, and undo actions.  (Applicable for %{buildFor} systems)

##############################################################################
# Build Packages
##############################################################################
%prep
# note - modules are build 'in-place', so yep - we need to prep with our
# own stuff
%setup -q -n sb

%build
#make -C ${RPM_BUILD_DIR}/oslockdown/src/security_modules

%install
mkdir -p ${RPM_BUILD_ROOT}
cp -rp ${RPM_BUILD_DIR}/sb/root/* ${RPM_BUILD_ROOT}

%clean
rm -rf ${RPM_BUILD_ROOT}

###############################################################################
%pre 


##############################################################################
%post

##############################################################################
%files 
%defattr(-,root,root)

%dir %attr(3770,sbwebapp,sbwebapp) /var/lib/oslockdown/profiles
%dir %attr(2750,root,sbwebapp)    /usr/share/oslockdown/cfg

%attr(700,sbwebapp,sbwebapp) /var/lib/oslockdown/profiles/*
%attr(750,root,sbwebapp) /usr/share/oslockdown/cfg
%attr(750,root,sbwebapp) /usr/share/oslockdown/security_modules

##############################################################################
