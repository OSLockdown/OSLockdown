#! /bin/sh


export JAVA_HOME=/etc/alternatives/jre_1.6.0
export JAVAHELP_HOME=./jh2.0
export CLASSPATH=$CLASSPATH:$JAVAHELP_HOME/javahelp/lib/jhall.jar
export PATH=$JAVAHELP_HOME/javahelp/bin

export SBHELP=./javahelp/jhelpset.hs

exec ${JAVA_HOME}/bin/java -jar $JAVAHELP_HOME/demos/bin/hsviewer.jar -helpset $SBHELP &
