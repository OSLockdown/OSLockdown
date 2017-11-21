#!/bin/sh
##############################################################################
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# This script allows a developer to run a system baseline
# without actually installing OS Lockdown. However, 
# there are a couple of restrictions:
#
# 1. You must be root. Data being collected about the system
#    requires this level of access
#
# 2. You must be in the same directory as this script when it
#    is executed.
#
# 3. Enable/Disable Baseline modules in the ./baseline-profile.xml
#    file.
#
# 4. This script sets the PYTHONPATH variable so that Python
#    will search this current working directory for stuff under
#    sb_utils/* and then Baseline/*(
# 
# 5. If you modify the baseline-profile.xml during testing,
#    be sure to restore it to default setting prior to final 
#    product delivery! This will be delivered as the default
#    baseline profile for installations.
#
#
##############################################################################
PYTHONPATH=`pwd`:`pwd`/Baseline
export PYTHONPATH

BASELINE_CONFIG="cfg/baseline-modules.xml"
export BASELINE_CONFIG

BASELINE_OUTPUT_FILE="./baseline-test-report.xml"
export BASELINE_OUTPUT_FILE

echo " "
echo "==> Performing baseline using source code modules"
echo "==> Setting BASELINE_CONFIG = ${BASELINE_CONFIG}"
echo " "
python -OO -c "import Baseline; Baseline.create(baselineProfile='./baseline-profile.xml', modVerbose=True)"
echo " "

echo "==> Validating test report against schema..."
printf ":: "
xmllint --noout --schema ../../cfg/schema/BaselineReport.xsd baseline-test-report.xml

echo 
