#=========================================================================
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# OS Lockdown - Variables for common utilities (Ubuntu)
#
# Other Makefiles should include this to ensure common paths to these
# utilities.
#
#=========================================================================

export AWK         := /usr/bin/awk
export CC          := /usr/bin/gcc
export CXX         := /usr/bin/g++
export CUT         := /usr/bin/cut
export FIND        := /usr/bin/find
export GCC         := /usr/bin/gcc
export GUNZIP      := /bin/gunzip
export GXX         := /usr/bin/g++
export GZIP_EXE    := /bin/gzip
export INSTALL     := /usr/bin/install
export LD          := /usr/bin/ld
export LN          := /bin/ln
export LSB_RELEASE := /usr/bin/lsb_release
export MAKE        ?= /usr/bin/make
export MAKESHELL   := /bin/bash
export MKDIR       := /bin/mkdir
#export OPENSSL     := /usr/bin/openssl
export PKGINSTALL  := /usr/bin/apt-get install 
export PYTHON      := /usr/bin/python
export PRINTF      := /usr/bin/printf
export RM          := /bin/rm
#export RPMBUILD    := /usr/bin/rpmbuild
export SPLINT      := /usr/bin/splint
export SWIG        := /usr/bin/swig
export STRIP       := /usr/bin/strip
export TAR         := /bin/tar
export TEE         := /usr/bin/tee
export TEST        := /usr/bin/test
export UNAME       := /bin/uname
export UNLINK      := /usr/bin/unlink
export XMLLINT     := /usr/bin/xmllint

## List all packages required to build
## the product:
export REQDPKGS := python-dev python ant1.8 libssl-dev 
