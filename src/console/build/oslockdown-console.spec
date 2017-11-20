##############################################################################
# Copyright (c) 2007-2016 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# OS Lockdown Console
##############################################################################
%define debug_package %{nil}

%define sbRelease %(echo "$SB_RELEASE")

%define isProduction %(test -z "$SB_RELEASE" && echo 0 || echo 1)
%define sbVersion %(echo "$SB_VERSION")
%define buildFor %(echo "$SB_BUILTFOR")

%define isRhel4  0
%define isRhel4 %(test "`lsb_release -r -s |cut -f1 -d.`" = "4" && echo 1 || echo 0)

%define isS390x  0
%define isS390x %(test "`uname -m`" = "s390x" && echo 1 || echo 0)

%define isSuse   %(test -e /etc/SuSE-release   && echo 1 || echo 0)

%define isSuse10 0
%define isSuse11 0
%if %isSuse 
  %define isSuse10 %(test "`lsb_release -r -s |cut -f1 -d. `" = "10" && echo 1 || echo 0)
  %define isSuse11 %(test "`lsb_release -r -s |cut -f1 -d. `" = "11" && echo 1 || echo 0)
%endif


# Rename output RPM *ONLY* if compiling with IBM Java SDK
%define ibmjava %(test "$JAVAFLAVOR" = "IBM" && echo 1 || echo 0)
%if %ibmjava
%define packageName oslockdown-console-ibmjava
%define jreFlavor IBM 
%else
%define packageName oslockdown-console
%define jreFlavor openJDK/Oracle
%endif

##############################################################################
Summary: Security Lockdown Application Console
Name:    %{packageName}
Version: %{sbVersion}
Release: %{sbRelease}
License: GPLv3, and Apache V2(ASL2.0), and (GPLv3 and ApacheV2), and others
Group:   System/Configuration/Other
Source:  oslockdown.tar.gz
Vendor:  OSLockdown
URL:     http://www.TrustedCS.com

BuildArchitectures: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

Requires: oslockdown
%description
OS Lockdown Console - required %{jreFlavor} Java Runtime Environment - (Applicable for ${buildFor} systems)

##############################################################################
%prep
%setup -q -n oslockdown

%build
make -C ${RPM_BUILD_DIR}/oslockdown/src/console

%install
rm -rf ${RPM_BUILD_ROOT}
make ROOT="${RPM_BUILD_ROOT}" -C ${RPM_BUILD_DIR}/oslockdown/src/console install

%clean
rm -rf ${RPM_BUILD_ROOT}


##############################################################################
# Pre-install
%pre

if [ -x /etc/init.d/osl-console ]; then
    service osl-console stop 1>/dev/null 2>&1 || /bin/true
fi

if [ -d /usr/share/oslockdown/console/webapps/OSLockdown ]; then
   rm -rf /usr/share/oslockdown/console/webapps/OSLockdown/ 1>/dev/null 2>&1
fi



# Post-trans - need to do this *last* so we have our scripts used
%post


if [ -f /etc/SuSE-release ]; then
    cp /usr/share/oslockdown/init.osl-console.suse /etc/init.d/osl-console
else
    cp /usr/share/oslockdown/init.osl-console /etc/init.d/osl-console
fi

chown root:root /etc/init.d/osl-console
chmod 750 /etc/init.d/osl-console

# Pre-uninstall
%preun
if [ -x /etc/init.d/osl-console ]; then
    service osl-console stop 1>/dev/null 2>&1 || /bin/true
    rm -f /etc/init.d/osl-console 1>/dev/null 2>&1
fi
if [ -d /usr/share/oslockdown/console/webapps/OSLockdown ]; then
   rm -rf /usr/share/oslockdown/console/webapps/OSLockdown/ 1>/dev/null 2>&1
fi

# Post-uninstall
%postun
if [ -f /etc/init.d/osl-console ] ; then
  rm -f /etc/init.d/osl-console 
fi

##############################################################################
# Files 
##############################################################################
%files
%defattr(-,root,root)

%dir %attr(2750,root,sbwebapp)  /usr/share/oslockdown/cfg
%dir %attr(700,sbwebapp,sbwebapp) /var/lib/oslockdown/console
%dir %attr(700,sbwebapp,sbwebapp) /var/lib/oslockdown/console/temp
%dir %attr(700,sbwebapp,sbwebapp) /var/lib/oslockdown/console/db
%dir %attr(750,sbwebapp,sbwebapp) /var/lib/oslockdown/files/ClientUpdates

%attr(700,root,root)              /usr/share/oslockdown/init.osl-console
%attr(700,root,root)              /usr/share/oslockdown/init.osl-console.suse
%attr(750,root,sbwebapp)          /usr/share/oslockdown/cfg
%attr(700,sbwebapp,sbwebapp)      /usr/share/oslockdown/console
%attr(750,sbwebapp,sbwebapp)      /var/lib/oslockdown/files/ClientUpdates/*

