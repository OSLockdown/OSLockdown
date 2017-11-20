CATALINA_TMPDIR=/var/lib/oslockdown/console/temp
export CATALINA_TMPDIR

if [ ! -x /usr/share/oslockdown/tools/sb-keylocker ]; then
    echo "Cannot find /usr/share/oslockdown/tools/sb-keylocker"
    echo "This utility is needed to run this program"
    exit 1
fi

# added for LD_LIBRARY_PATH required for jni calls
LD_LIBRARY_PATH="/usr/share/oslockdown/lib"
export LD_LIBRARY_PATH 

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



# Set Memory Size startup size
JAVA_OPTS="$JAVA_OPTS -Xmx512M -XX:PermSize=64M -XX:MaxPermSize=128M -XX:+CMSClassUnloadingEnabled -XX:+CMSPermGenSweepingEnabled "
export JAVA_OPTS

# Set Version Requirement
#JAVA_OPTS="$JAVA_OPTS -version:1.6+"
#export JAVA_OPTS


CATALINA_PID=/var/lib/oslockdown/console/temp/osl-console.pid
export CATALINA_PID
