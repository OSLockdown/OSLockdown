# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
echo ""
if [ -z "$JAVA_HOME" ] ; then
  echo '$JAVA_HOME environment variable not set'
elif [ ! -d "$JAVA_HOME" ] ; then
  echo '$JAVA_HOME directory does not existst'
elif [ ! -x "$JAVA_HOME/bin/java" ] ; then
  echo '$JAVA_HOME/bin/java is not executable'
else
  echo '$JAVA_HOME/bin/java is executable'
fi
