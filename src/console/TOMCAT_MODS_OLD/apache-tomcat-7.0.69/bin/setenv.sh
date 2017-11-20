CATALINA_TMPDIR=/var/lib/oslockdown/console/temp
export CATALINA_TMPDIR

if [ ! -x /usr/share/oslockdown/tools/sb-keylocker ]; then
    echo "Cannot find /usr/share/oslockdown/tools/sb-keylocker"
    echo "This utility is needed to run this program"
    exit 1
fi


# Set Memory Size startup size
JAVA_OPTS="$JAVA_OPTS -Xmx512M -XX:PermSize=64M -XX:MaxPermSize=128M -XX:+CMSClassUnloadingEnabled -XX:+CMSPermGenSweepingEnabled "
export JAVA_OPTS

# Set Version Requirement
#JAVA_OPTS="$JAVA_OPTS -version:1.6+"
#export JAVA_OPTS


CATALINA_PID=/var/lib/oslockdown/console/temp/osl-console.pid
export CATALINA_PID
