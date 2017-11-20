##############################################################################
# Copyright (c) 2009-2016 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# OS Lockdown Dispatcher
#
##############################################################################


%define isProduction %(test -z "$SB_RELEASE" && echo 0 || echo 1)

%define sbRelease %(echo "$SB_RELEASE")
%define sbVersion %(echo "$SB_VERSION")
%define builtFor %(echo "$SB_BUILTFOR")

%define isSuse   %(test -e /etc/SuSE-release   && echo 1 || echo 0)
%define isFedora %(test -e /etc/fedora-release && echo 1 || echo 0)
%define isRedhat %(test -e /etc/redhat-release && echo 1 || echo 0)

%define osFullRellease %(lsb_release -r -s)
%define osRelease %(lsb_release -r -s |cut -f1 -d.)

# Define and turn off distribution flags
%define isRhel4  0
%define isRhel5  0
%define isRhel6  0
%define isSuse10 0
%define isSuse11 0
%define isFc10   0
%define isFc11   0
%define isFc12   0
%define isFc13   0

# Turn on appropriate distribution flags
%if %isRedhat
%define dist .el%{osRelease}
%define isRhel4 %(test "`lsb_release -r -s |cut -f1 -d.`" = "4" && echo 1 || echo 0)
%define isRhel5 %(test "`lsb_release -r -s |cut -f1 -d.`" = "5" && echo 1 || echo 0)
%define isRhel6 %(test "`lsb_release -r -s |cut -f1 -d.`" = "6" && echo 1 || echo 0)
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

%define debug_package %{nil}

##############################################################################
Summary: Security Lockdown Application Dispatcher
Name:    oslockdown-dispatcher
Version: %{sbVersion}
Release: %{sbRelease}%{?dist}
License: GPLv3
Group:   System/Configuration/Other
Source:  oslockdown.tar.gz
Vendor:  OSLockdown
URL:     http://www.TrustedCS.com

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot


BuildRequires: make bison flex
%if %isSuse
%if %isSuse10
BuildRequires: openssl-devel 
%else
BuildRequires: libopenssl-devel 
%endif
BuildRequires: gcc-c++ 
%else
BuildRequires: gcc openssl-devel 
%endif


Requires: oslockdown = %{version}-%{sbRelease}%{?dist}

%description
OS Lockdown Dispatcher (Applicable for %{builtFor} systems)

##############################################################################
%prep
%setup -q -n oslockdown

%build
make -C ${RPM_BUILD_DIR}/oslockdown/src/core
make -C ${RPM_BUILD_DIR}/oslockdown/src/dispatcher

%install
rm -rf ${RPM_BUILD_ROOT}
make ROOT="${RPM_BUILD_ROOT}" -C ${RPM_BUILD_DIR}/oslockdown/src/dispatcher install

%clean
rm -rf ${RPM_BUILD_ROOT}

##############################################################################
%pre
if [ -x /etc/init.d/sb-agentd ]; then
    service sb-agentd stop 1>/dev/null 2>&1
    chkconfig sb-agentd off 1> /dev/null 2>&1
fi
if [ -x /etc/init.d/osl-dispatcher ]; then
    service osl-dispatcher stop 1>/dev/null 2>&1
fi

%post
cp /usr/share/oslockdown/init.osl-dispatcher /etc/init.d/osl-dispatcher
chown root:root /etc/init.d/osl-dispatcher
chmod 750 /etc/init.d/osl-dispatcher

# Don't prelink on RHEL6 anymore

#
%if ! %isRhel6
if [ -x /usr/sbin/prelink ]; then
    /usr/sbin/prelink -q /sbin/OSL_Dispatcher
    /usr/sbin/prelink -q /usr/share/oslockdown/tools/RegisterClient
    /usr/sbin/prelink -q /usr/share/oslockdown/tools/sb-keylocker
    if [ -f /usr/bin/python ]; then
	/usr/sbin/prelink -q /usr/bin/python
    fi
    /usr/sbin/prelink -q /usr/lib/libpython* 2>/dev/null || /bin/true
fi
%endif

%preun
if [ -x /etc/init.d/osl-dispatcher ]; then
    service osl-dispatcher stop 1>/dev/null 2>&1
    rm -f /etc/init.d/osl-dispatcher 1>/dev/null 2>&1
fi

##############################################################################
%files
%defattr(-,root,root)

/usr/share/oslockdown/init.osl-dispatcher
/sbin/OSL_Dispatcher
/usr/share/oslockdown/tools/RegisterClient
/usr/share/oslockdown/tools/sb-keylocker

# Sigh, case issues....
%doc /usr/share/man/man8/*ispatcher*

##############################################################################
