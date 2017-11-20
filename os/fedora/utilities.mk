#=========================================================================
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# OS Lockdown - Variables for common utilities (Fedora)
#
# Other Makefiles should include this to ensure common paths to these
# utilities.
#
#=========================================================================

export AWK         := /bin/awk
export CC          := /usr/bin/gcc
export CXX         := /usr/bin/g++
export CUT         := /bin/cut
export FIND        := /usr/bin/find
export GCC         := /usr/bin/gcc
export GUNZIP 	   := /usr/bin/gunzip
export GXX         := /usr/bin/g++
export GZIP_EXE    := /usr/bin/gzip  
export INSTALL     := /usr/bin/install
export KIDC        := /usr/bin/kidc
export LD          := /usr/bin/ld
export LN          := /bin/ln
export LSB_RELEASE := /usr/bin/lsb_release
export MAKE        ?= /usr/bin/make
export MAKESHELL   := /bin/bash
export MKDIR       := /bin/mkdir
#export OPENSSL     := /usr/bin/openssl
export PKGINSTALL  := /usr/bin/yum -y install 
export PRINTF      := /usr/bin/printf
export PYTHON      := /usr/bin/python
export RM          := /bin/rm
export RPM         := /bin/rpm
export RPMBUILD    := /usr/bin/rpmbuild
export RPMDEVSETUP := /usr/bin/rpmdev-setuptree
export SPLINT      := /usr/bin/splint
export SWIG        := /usr/bin/swig
export STRIP       := /usr/bin/strip
export TAR         := /bin/tar
export TEE         := /usr/bin/tee
export TEST        := /usr/bin/test
export UNAME       := /bin/uname
export UNLINK      := /bin/unlink
export XMLTO       := /usr/bin/xmlto
export XMLLINT     := /usr/bin/xmllint

## List all packages (RPMs) required to build
## the product:
export REQDPKGS := byacc gcc gcc-c++ swig openssl-devel binutils bison xmlto \
                   python python-devel rpm-build rpmdevtools
