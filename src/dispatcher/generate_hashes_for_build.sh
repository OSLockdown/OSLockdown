#!/bin/sh
#
# Copyright (c) 2009-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Compute Fingerprints of externally called files
# and store them as constants in the fingerprints.h
# header file.
# 

echo "  Creating fingerprints.h"
cat<<EOF > fingerprints.h
/*
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 * 
 * SHA1 fingerprints of programs which get ran externally
 * via popen()
 */

#define SB_SHA1_FILENAME "/usr/share/oslockdown/oslockdown.pyo"
#define SB_SCRIPT_SHA1_FILENAME "/usr/sbin/oslockdown"

EOF

echo "  Computing hashes..."
fingerprint=`openssl sha1 ../core/oslockdown.pyo |awk '{print $2}'`
printf '#define SB_SHA1 "%s"\n' $fingerprint >> fingerprints.h

fingerprint=`openssl sha1 ../core/oslockdown |awk '{print $2}'`
printf '#define SB_SCRIPT_SHA1 "%s"\n' $fingerprint >> fingerprints.h

echo >> fingerprints.h

echo "Done"
echo 
exit 0
