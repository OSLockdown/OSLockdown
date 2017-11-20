#=========================================================================
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Build Platform: Solaris 10
#
# OS Lockdown - Variables for common utilities 
#
#=========================================================================

export AWK         := /usr/xpg4/bin/awk
export CC          := /usr/sfw/bin/gcc
export CXX         := /usr/sfw/bin/g++
export CUT         := /usr/bin/cut
export FIND        := /usr/bin/find
export GCC         := /usr/sfw/bin/gcc
export GXX         := /usr/sfw/bin/gxx
export GUNZIP      := /usr/bin/gunzip
export GZIP_EXE    := /usr/bin/gzip
export INSTALL     := /usr/ucb/install
export LD          := 
export LN          := /usr/bin/ln
export MAKE        ?= /usr/sfw/bin/gmake
export MKDIR       := /usr/bin/mkdir
export MV          := /usr/bin/mv
#export OPENSSL     := /usr/sfw/bin/openssl
export PKGINFO     := /usr/bin/pkginfo
export PRINTF      := /usr/bin/printf
export PYTHON      := /usr/bin/python
export RM          := /usr/bin/rm
export SWIG        := /usr/local/bin/swig
export STRIP       := /usr/ccs/bin/strip
export SVN         := /usr/local/bin/svn
export TAR         := /usr/sfw/bin/gtar
export TEE         := /usr/bin/tee
export TEST        := /usr/bin/test
export UNAME       := /usr/bin/uname
export MAKESHELL   := /usr/bin/sh

export NFS_PKG_SHARE := 192.168.1.34:/data/mirrors/solaris/10
export REQDPKGS := SUNWgcc SUNWbash SUNWgmake SUNWbison SUNWopenssl-include SUNWbinutils
