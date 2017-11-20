##############################################################################
# Copyright (c) 2007-2008 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Gernate Security Blanket Documentation
#  - This Makefile is really just a skeleton build script which
#    calls Ant builds.
#
##############################################################################

NAME ?= security-blanket
include ../Makefile_common.mk

ANT ?= "${ANT_HOME}/bin/ant"

export DRAFT_MODE    ?= yes
export SHOW_COMMENTS := 1

docs: prep
	$(ANT) docs

all: docs pdfs 
	@echo "Built all doc, pdf, and texts"

prep: xsl/docbook-xsl-stylesheets
	@echo "Preparing customized docbook directory..."
	
xsl/docbook-xsl-stylesheets: 
	cd xsl ; cp -r ${DOCBOOK_STYLESHEETS} docbook-xsl-stylesheets
	 
modules-guide: prep
	(cd modules-guide/tools ; sh update-all.sh)
	$(ANT) -Ddraft.mode=${DRAFT_MODE} -Dshow.comments=${SHOW_COMMENTS} modules-guide

admin-guide: prep
	$(ANT) admin-guide

admin-guide-pdf: prep
	$(ANT) admin-guide-pdf

pdfs: admin-guide-pdf modules-guide-pdf 
	echo "Making PDFs"

modules-guide-pdf: prep 
	$(ANT) modules-guide-pdf

projecthelp:
	@$(ANT) -version
	@$(ANT) -projecthelp 

init:
	$(ANT) init
clean:
	$(ANT) clean-docs
	rm -rf xsl/docbook-xsl-stylesheets

FORCE:
