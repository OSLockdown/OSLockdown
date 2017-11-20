#!/bin/sh

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -----------------------------------------------------------------------------
# Start Script for the CATALINA Server
# -----------------------------------------------------------------------------

# Better OS/400 detection: see Bugzilla 31132
os400=false
case "`uname`" in
OS400*) os400=true;;
esac

# resolve links - $0 may be a softlink
PRG="$0"

while [ -h "$PRG" ] ; do
  ls=`ls -ld "$PRG"`
  link=`expr "$ls" : '.*-> \(.*\)$'`
  if expr "$link" : '/.*' > /dev/null; then
    PRG="$link"
  else
    PRG=`dirname "$PRG"`/"$link"
  fi
done

# added for LD_LIBRARY_PATH required for jni calls
LD_LIBRARY_PATH="/usr/share/oslockdown/lib"
export LD_LIBRARY_PATH 

PRGDIR=`dirname "$PRG"`
EXECUTABLE=catalina.sh

# Check that target executable exists
if $os400; then
  # -x will Only work on the os400 if the files are:
  # 1. owned by the user
  # 2. owned by the PRIMARY group of the user
  # this will not work if the user belongs in secondary groups
  eval
else
  if [ ! -x "$PRGDIR"/"$EXECUTABLE" ]; then
    echo "Cannot find $PRGDIR/$EXECUTABLE"
    echo "The file is absent or does not have execute permission"
    echo "This file is needed to run this program"
    exit 1
  fi
fi

# Look for a file that may set one or more environment variables that the
# console will look for.  The value doesn't matter, just that it is set.
# If this file is found, it is included then deleted.
#
# The variables are one or more of :
# SB_CONSOLE_LOAD_SECURITY_METADATA
# SB_CONSOLE_LOAD_SECURITY_PROFILES
# SB_CONSOLE_LOAD_BASELINE_METADATA
# SB_CONSOLE_LOAD_BASELINE_PROFILES

if [ -f ${HOME}/.database_refresh ]; then
    echo '	DETECTED ${HOME}/.database_refresh ! '
    for var in SECURITY_METADATA SECURITY_PROFILES BASELINE_METADATA BASELINE_PROFILES
    do
      egrep "^${var}\$" ${HOME}/.database_refresh 2>&1 1>/dev/null
      if [ $? -eq 0 ]; then
        eval "SB_CONSOLE_LOAD_${var}='yes'; export SB_CONSOLE_LOAD_${var}"
        echo "	Setting SB_CONSOLE_LOAD_${var}"
      fi
    done
    echo '	removing ${HOME}/.database_refresh file...'
    rm -f ${HOME}/.database_refresh    
fi
exec "$PRGDIR"/"$EXECUTABLE" start "$@"
