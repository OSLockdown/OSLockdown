##############################################################################
# Copyright (c) 2011-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
##############################################################################
#
# OS Lockdown SELinux Policy Module
#
##############################################################################
%define isProduction %(test -z "$SB_RELEASE" && echo 0 || echo 1)

%global _signature gpg
%global _gpg_name OS Lockdown
#%define _gpg_path ../../gpg-keys 

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
Summary:  OS Lockdown SELinux Policy Module
Name:     oslockdown-selinux
Version:  %{sbVersion}
Release:  %{sbRelease}%{?dist}
License:  GPLv3
Group:    System/Configuration/Other
Source:   oslockdown.tar.gz
Vendor:   OSLockdown
URL:      http://www.TrustedCS.com

BuildArchitectures: noarch
BuildRoot:          %{_tmppath}/%{name}-%{version}-%{release}-buildroot
#
# Note - no explicit requirement on policy-devel because we are going to use
#        the oldest policy package (installed manually in the SB source tree)
#        for each major version. 
#BuildRequires:      make selinux-policy-devel

#Requires: oslockdown >= %{version}

Requires: policycoreutils

%if %isRhel6
Requires: policycoreutils-python
%endif
%if %isFc11
Requires: policycoreutils-python
%endif
%if %isFc12
Requires: policycoreutils-python
%endif
%if %isFc13
Requires: policycoreutils-python
%endif

%description
OS Lockdown SELinux Policy Module (Applicable for %{buildFor} systems)

##############################################################################
%prep
%setup -q -n oslockdown

%build
make -C ${RPM_BUILD_DIR}/oslockdown/src/selinux 

%install
make ROOT="${RPM_BUILD_ROOT}" -C ${RPM_BUILD_DIR}/oslockdown/src/selinux install

%clean
rm -rf ${RPM_BUILD_ROOT}

%post 
# call semodule to install the files and restorecon to relabel everything
# Important - upgrading from Security Blanket (SB) to OS Lockdown (OSL)
# requires a 'Transition' policy to let SB (which is running the upgrade) to
# transition to OSL.  

if [ -x /usr/sbin/semodule ] ; then
    cd /usr/share/oslockdown/selinux
    
    
    if [ -f oslockdown.pp ] ; then
        policyFiles="oslockdown.pp"

        semodule -l | grep securityblanket 1>/dev/null 2>&1
        if [ $? -eq 0 ] ; then
          policyFiles="${policyFiles} TransitionSBtoOSL.pp"
        fi
                
        /usr/sbin/semodule -i ${policyFiles}

    fi
    

fi

if [ -x /sbin/restorecon ] ; then

    if [ -d /usr/share/oslockdown ] ; then
        /sbin/restorecon -F -R /usr/share/oslockdown 
    fi
 
    if [ -d /var/lib/oslockdown ] ; then
        /sbin/restorecon -F -R /var/lib/oslockdown 
    fi
 
    if [ -f /usr/sbin/oslockdown ] ; then
        /sbin/restorecon -F /usr/sbin/oslockdown 
    fi
    if [ -f /sbin/OSL_Dispatcher ] ; then
        /sbin/restorecon -F /sbin/OSL_Dispatcher
    fi
    if [ -f /etc/init.d/osl-console ] ; then
        /sbin/restorecon -F /etc/init.d/osl-console
    fi
    if [ -f /etc/init.d/osl-dispatcher ] ; then
        /sbin/restorecon -F /etc/init.d/osl-dispatcher
    fi
    if [ -f /var/log/oslockdown-dispatcher.log ] ; then
        /sbin/restorecon -F /var/log/oslockdown-dispatcher.log
    fi
fi

%postun
if [ $1 -eq 0 ] ; then 
   # this is the final removal, so explicitly unload the *.pp and 
   # relabel everything...    
   if [ -x /usr/sbin/semodule ] ; then
       
       policyFiles=""
       semodule -l | grep TransitionSBtoOSL 1>/dev/null 2>&1
       if [ $? -eq 0 ] ; then
         policyFiles="${policyFiles} TransitionSBtoOSL"
       fi
       
       semodule -l | grep oslockdown 1>/dev/null 2>&1
       if [ $? -eq 0 ] ; then
         policyFiles="${policyFiles} oslockdown"
       fi
       
       if [ ! -z "${policyFiles}" ] ; then
         semodule -r ${policyFiles}
       fi
   fi

   if [ -x /sbin/restorecon ] ; then
       if [ -f /usr/sbin/oslockdown ] ; then
           /sbin/restorecon -F -R /usr/sbin/oslockdown 
       fi
       if [ -f /sbin/SB_Dispatcher ] ; then
           /sbin/restorecon -F /sbin/SB_Dispatcher
       fi
       if [ -f /etc/init.d/osl-console ] ; then
           /sbin/restorecon -F /etc/init.d/osl-console
       fi
       if [ -f /etc/init.d/osl-dispatcher ] ; then
           /sbin/restorecon -F /etc/init.d/osl-dispatcher
       fi
       if [ -f /var/log/oslockdown-dispatcher.log ] ; then
           /sbin/restorecon -F /var/log/oslockdown-dispatcher.log
       fi

       if [ -d /var/lib/oslockdown ] ; then
           /sbin/restorecon -F -R /var/lib/oslockdown
       fi

       if [ -d /usr/share/oslockdown ] ; then
           /sbin/restorecon -F -R /usr/share/oslockdown
       fi
   fi
fi

    
##############################################################################
%files
%defattr(-,root,root)
/usr/share/oslockdown/selinux


##############################################################################
