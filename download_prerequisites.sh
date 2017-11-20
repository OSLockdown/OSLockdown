#!/bin/sh 


#
# Download all primary external prequisites for Security Blanket
#
downloadArchive()
{
  #1 = URL of download
  #2 = directory to extract into (required)
  #    if directory = "." use current working directory
  #    if not empty then attempt to create dir and extract there
  #      
  url=${1}
  destFile=`basename "${1}"`
  prefix=`echo "${1}" | awk -F':' '{print $1}'`
  suffix=`echo "${1}" | awk -F'.' '{print $NF}'`
  destDir=$2
  
  
  if [ "${prefix}" = "http" ]; then
    WGET_FLAGS=" "
  else
    WGET_FLAGS=" --no-check-certificate"
  fi
  
  TEST_CMD=""
  MKDIR_CMD=""
  EXPAND_CMD=""
  EXPAND_INTO=""
  
  if [ "${suffix}" = "zip" ] ; then
    TEST_CMD="zipinfo $destFile "
    if [ ! -z "${destDir}" ] ; then
      EXPAND_CMD="unzip ${destFile}"
      if [ "${destDir}" != "." ] ; then
        MKDIR_CMD="mkdir -p $destDir"
        EXPAND_INTO="-d $destDir"
      fi
    fi
  elif [ "${suffix}" = "gz" ] ; then
    TEST_CMD="${TAR_CMD} -tzf $destFile "
    if [ ! -z "$destDir" ] ; then
      EXPAND_CMD="${TAR_CMD} -xzf ${destFile}"
      if [ "$destDir" != "." ] ; then
        MKDIR_CMD="mkdir -p $destDir"
        EXPAND_INTO="-C $destDir"
      fi 
    fi
  elif [ "${suffix}" = "tar" ] ; then
    TEST_CMD="${TAR_CMD} -tf $destFile "
    if [ ! -z "$destDir" ] ; then
      EXPAND_CMD="${TAR_CMD} -xf ${destFile}"
      if [ "$destDir" != "." ] ; then
        MKDIR_CMD="mkdir -p $destDir"
        EXPAND_INTO="-C $destDir"
      fi 
    fi
  else
      TEST_CMD=""
      EXPAND_CMD=""
  fi

#  echo "prefix/suffix/destdir -> ${prefix}/${suffix}/${destdir}"
#  echo "Download -> wget -nv ${WGET_FLAGS} -O ${destFile} ${url}"
#  echo "Test ->     ${TEST_CMD}"
#  echo "Make dir -> ${MKDIR_CMD}"
#  echo "Extract ->  ${EXPAND_CMD}"
#  echo " " ; return

  echo "----> Downloading ${url}..."
    
  /usr/sfw/bin/wget  ${WGET_FLAGS} -O ${destFile} ${url} 1>/dev/null 2>&1
  if [ $? -ne 0 ] ; then
      echo "----> Unable to download $url"
      echo " "
      
      
  fi
  
  echo "----> Downloaded $url"
  
  # Ok, got the download, test it first to see if it appears complete.

  if [ -z "${TEST_CMD}" ] ; then
      echo "----> $url has an unknown suffix, unable to expand or test"
      echo " "
      return
  fi  
  ${TEST_CMD}  1>/dev/null
  
  if [ $? -ne 0 ] ; then
    echo "----> Archive ${destFile} appears corrupted, not trying to expand"
    echo " "
    return
  fi
  
  # Ok, download appears complete.  Try and extract it
  if [ ! -z "${MKDIR_CMD}" ] ; then
    echo "----> Creating directory to expand to..."
    ${MKDIR_CMD} 
  fi
  if [ ! -z "${EXPAND_CMD}" ] ; then 
    echo "----> Extracting ${destFile} with << ${EXPAND_CMD} ${EXPAND_INTO} >>"
  
    ${EXPAND_CMD} ${EXPAND_INTO} 1>/dev/null   
  
    if [ $? -ne 0 ] ; then
      echo "----> Unable to extract archive ${destFile}"
      echo " "
      return
    fi    
    rm -f ${destFile}
  else
    echo "----> Not extracting ${destFile}"
  fi
  echo " "
}


### Main program starts here.
# We *EXPECT* an argument to indicate where the user would like us to download things.  
# It must :
#    - not be a regular file
#    - not canonicalize to '/'

if [ $# -gt 1 ] ; then
  echo "Usage: $0 [DIRNAME]"
  echo "   DIRNAME must be a directory or not exist"
  exit 1
elif [ $# -eq 1 ] ; then
  if [ -f ${1} ] ; then
    echo "${1} exists and is not a directory, aborting."
    exit 1
  elif [ ! -d ${1} ] ; then
    echo "Attempting to create ${1}"
    mkdir -p ${1}
    if [ $? -ne 0 ] ; then
      echo "Unable to create ${1}"
      exit 1
    fi
  fi
  cd "${1}"
fi

echo "Downloading components to `pwd`"


if [ "`uname -s`" = "SunOS" ] ; then
  TAR_CMD='/usr/sfw/bin/gtar'
else
  TAR_CMD='tar'
fi


echo "Downloading Apache Ant (1.9.2)..."
downloadArchive http://archive.apache.org/dist/ant/binaries/apache-ant-1.9.2-bin.tar.gz "."

echo "Downloading Apache FOP (1.0)..."
downloadArchive http://archive.apache.org/dist/xmlgraphics/fop/binaries/fop-1.0-bin.tar.gz "."

echo "Downloading Apache Tomcat (7.0.82)..."
downloadArchive http://archive.apache.org/dist/tomcat/tomcat-7/v7.0.82/bin/apache-tomcat-7.0.82.tar.gz ""

echo "Downloading docbook-xsl-stylesheets (1.74.0)..."
downloadArchive https://sourceforge.net/projects/docbook/files/docbook-xsl/1.74.0/docbook-xsl-1.74.0.tar.gz "." 

echo "Downloading Grails (2.3.7)..."
downloadArchive https://github.com/grails/grails-core/releases/download/v2.3.7/grails-2.3.7.zip "."
    
echo "Downloading gSOAP (2.8.18)..."
downloadArchive https://sourceforge.net/projects/gsoap2/files/oldreleases/gsoap_2.8.18.zip "."

echo "Downloading JAXWS-RI (2.2.10)..."
# downloadArchive https://jax-ws.java.net/2.2.5/JAXWS2.2.5-20110729.zip "."
# java.net now points at github, and doesn't have older verions, so use maven repo instead
downloadArchive http://repo1.maven.org/maven2/com/sun/xml/ws/jaxws-ri/2.2.5-promoted-b04/jaxws-ri-2.2.5-promoted-b04.zip "."

echo "Downloading SAXON (6.5.5)..."
downloadArchive https://sourceforge.net/projects/saxon/files/saxon6/6.5.5/saxon6-5-5.zip saxon-6.5.5 

echo "Downloading swig (1.39)..."
downloadArchive https://sourceforge.net/projects/swig/files/swig/swig-1.3.39/swig-1.3.39.tar.gz "." 


