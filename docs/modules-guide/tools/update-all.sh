#!/bin/sh

#python ./build-cis-crossx.py
#for i in cag dcid jafan fisma nispom other-stig cip cce pcidss unix-stig redhat5-stig nsa-rhel5 dhs
#   python ./build-${i}-crossx.py
#   echo

# build the appendix cross reference
echo 
python ./build-generic_crossx.py

# The following add sections that should appear in a specific order
# so they delete the simplesect if found, than append it to the end.
# Will add simplesect for Options
echo
python ./update-options.py

# Will add simplesect for Compliancy
echo
python ./update-compliancy.py

# clean up the individual modules themselves...
(cd ../modules/; sh ./cleanup )
echo

# Ok, new step - build the actual *modules-guide* by populating each chapter
# from the actual modules present - 
python ./build-module-index.py

#python ./build-index.py 
echo
# Marketing spreadsheet
python ./build-master-crossx.py

# Ok, final check - show all existing modules that don't have help pages...
python ./check_for_missing.py
