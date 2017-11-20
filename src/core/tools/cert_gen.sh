#!/bin/sh 
# 
# Copyright (c) 2009-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
#
#  This script is designed to help create the required SSL certificates for 
#  networked communications within the OS Lockdown framework.
#  
#  The design is to have a single CA authorizing all certificates. By default 
#  we are going to use a self-signed internal CA that we create ourselves, although 
#  we will prompt the user for an 'official' root CA if they have one.
#  In that case we'll need the location of the cert and the passphrase, so we can 
#  sign our certs with that CA.
#
#  We are not doing mutual authentication. When a client contacts a server 
#  (gui -> dispatcher or dispatcher -> gui) the server will present a cert 
#  signed by the CA, which will be sufficient for our comms.  In the Enterprise 
#  world an extra step will need to be done to push the CA cert down to the 
#  clients. 
#

. /usr/share/oslockdown/tools/shell_utils
#. /usr/share/oslockdown/tools/determine_javahome

SSL_FQDN_SUFFIX=""

##
# General exit routine - try and change back to original directory (if required)
# and exit with the indicated value

scriptExit()
{
  if [ -n ${olddir} -a -d ${olddir} -a -x ${olddir} ] ; then
    cd ${olddir}
  fi
  exit $1
}

##############################################################################
# Helper Function - Update sbwebapp's .profile with JAVA_HOME and LD_LIBRARY_PATH
update_sbwebapp_profile ()
{
    if [ ! -z "${JavaHome}" ]; then
        echo "# .profile : Updated by SB_Setup on `date`" > ${profile}
        echo " " >> ${profile}
        echo "JAVA_HOME=$JavaHome" >> ${profile}
        echo "export JAVA_HOME" >> ${profile}
        echo " " >> ${profile}
        echo "LD_LIBRARY_PATH=/usr/share/oslockdown/lib" >> ${profile}
        echo "export LD_LIBRARY_PATH" >> ${profile}
        echo " - Updated ${profile}"
        echo " - JAVA_HOME=$JavaHome"
        echo
        chown sbwebapp ${profile}
        chmod 700 ${profile}
    fi
}

##############################################################################
confirm_openssl()
{
  OPENSSL="openssl"
  whichout=`which ${OPENSSL} 2>/dev/null | wc -w`
  if [ ${whichout} -ne 1 ] ; then
    echo "The 'openssl' command does not appear to be in your path."
    echo "Please add the location to the openssl command to your "
    echo "path and try running cert_gen.sh again."
    scriptExit 1
  fi
  export OPENSSL
}

##############################################################################
confirm_keytool()
{
  # Try to locate a Java 1.6 install... If we find one push it to the front
  # of our path...
  JavaHome=""
  
  JavaHome=`/usr/share/oslockdown/tools/JavaHomeUtils.py -u sbwebapp`
  
  # if a problem or no JAVA_HOME set, then we must call
  if [ $? -ne 0 -o -z "${JavaHome}" ]; then
     keepJava="NO"
  else
    ask_yes_or_no "    Use ${JavaHome} as JAVA_HOME" keepJava
  fi
  
  if [ "${keepJava}" = "NO" ] ; then   
    /usr/share/oslockdown/tools/JavaHomeUtils.py -i -u sbwebapp
    JavaHome=`/usr/share/oslockdown/tools/JavaHomeUtils.py -u sbwebapp`
  fi
  
#  set_java_home

  if [ ! -z "${JavaHome}" ] ; then
    PATH="${JavaHome}/bin:${PATH}"
    export PATH
  else
    echo "Unable to locate acceptable JAVA_HOME, exiting"
    scriptExit 1
  fi

  KEYTOOL="${JavaHome}/bin/keytool"
  whichout=`which ${KEYTOOL} 2>/dev/null | wc -w`
  if [ ${whichout} -ne 1 ] ; then
    echo "The 'keytool' command does not appear to be in your path."
    echo "Please add the location to the keytool command to your "
    echo "path and try running cert_gen.sh again."
    scriptExit 1
  fi
  ${KEYTOOL} 2>&1 | grep gnu 2>&1 1>/dev/null
  if [ $? -eq 0 ] ; then
    echo "The 'GNU' version of the 'keytool' command has been detected."
    echo "This version of keytool does not support the commands needed"
    echo "to generate the SSL certificates required by Java."
    if [ "`uname -s`" = "SunOS" ]; then
      echo "Please install the latest version of SUN's JAVA 1.6 JDK and"
      echo "then rerun this script."
    else
      echo "Please install the latest version of SUN's JAVA 1.6 JDK or"
      echo "the 1.6 version of the OpenJDK packages (if supported on your"
      echo "Linux distro), and then return this script."
    fi
    scriptExit 1
  fi
  if [ "`uname -s`" = "SunOS" ]; then
    ${KEYTOOL} 2>&1 | grep "\-importcert" 2>&1 1>/dev/null
    if [ $? -eq 1 ] ; then
      echo "The default version of the keytool command doesn't support the"
      echo "-importcert option.  Please reconfigure your path to have the"
      echo "Java 1.6 version of keytool run, then rerun this script."
      scriptExit 1
    fi
  fi
  export KEYTOOL
}

##############################################################################
# Restore default SELinux security context if SELinux enabled - *RECURSIVELY*
restore_context()
{
  
  [ -x /usr/sbin/selinuxenabled -a -x /sbin/restorecon ] && /usr/sbin/selinuxenabled || return
  echo ":: Setting SELinux context(s) for ${1}..."
  /sbin/restorecon -F -R ${1}
}

##############################################################################
setup_vars()
{
  log_file=""
  SSL_CERTS_DIR=""
  SSL_CERTS_WORKING=""
  SB_KEYLOCKER=""
  CACERT_PASSPHRASE=""
  KEYSTORE_PASSPHRASE=""
  TRUSTSTORE_PASSPHRASE=""
  ALIAS_NAME="tomcat"
  GUI_PASSPHRASE=""
  DISPATCHER_PASSPHRASE=""
  CERT_SUBJ_BASE=""
  DIGEST=""
  
  export KEYTOOL
  export log_file
  export SSL_CERTS_DIR
  export SSL_CERTS_WORKING
  export SB_KEYLOCKER
  export CACERT_PASSPHRASE
  export KEYSTORE_PASSPHRASE
  export TRUSTSTORE_PASSPHRASE
  export ALIAS_NAME
  export GUI_PASSPHRASE
  export DISPATCHER_PASSPHRASE
  export CERT_SUBJ_BASE
  export DIGEST
}

##############################################################################
generate_cert_base()
{
  echo " "
  echo ":: Certificate Base Information"
  echo " "
  if [ -z "${CERT_SUBJ_BASE}" -a -f ssl_subj_base.txt ] ; then
    echo "    Found previous base information:"
    cat ssl_subj_base.txt |awk '{printf "    %s\n", $0}'
    ask_yes_or_no "    Use this base information (DN)" yes_or_no
    if [ "${yes_or_no}" = "YES" ]  ; then
      CERT_SUBJ_BASE="`cat ssl_subj_base.txt`"
    fi
  fi 
 
  if [ -z "${CERT_SUBJ_BASE}" ] ; then
    ask_for_string "    Enter Country (2 letters)              " cert_country
    ask_for_string "    Enter State or Province                " cert_state
    ask_for_string "    Enter Locality (city)                  " cert_city
    ask_for_string "    Enter Organization/company             " cert_org
    ask_for_string "    Enter Unit name/section                " cert_section
    ask_for_string "    Enter contact email (optional)         " cert_email
    CERT_SUBJ_BASE="/C=${cert_country}/ST=${cert_state}/L=${cert_city}/O=${cert_org}/OU=${cert_section}/emailAddress=${cert_email}"
    echo " "
    echo ":: Saving answers for later use..."
    echo "${CERT_SUBJ_BASE}" > ssl_subj_base.txt
  fi
}

##############################################################################
#
#  Strip the 'default' passphrase off of a specific cert
#
strip_passphrase()
{
  certToStrip="$1"
  this_step=":: Strip passphrase from ${certToStrip}"
  PASSPHRASE="-passin pass:nopassword "

  
  ARGS="${PASSPHRASE} -in${certToStrip} -out ${certToStrip}"
  echo "${this_step} " | tee -a ${log_file}
  echo "" >> ${log_file}
  echo "${OPENSSL} rsa  ${ARGS} " >> ${log_file} 
  echo "" >> ${log_file}
  ${OPENSSL} rsa ${ARGS} 1>>${log_file} 2>&1
  if [ $? != 0 ] ; then
    echo "${this_step} >>>> FAILED" | tee -a ${log_file} 
    scriptExit 1
  fi  
  
}

##############################################################################
#
#  Generate Root CA certificates
#
generate_root_ca()
{
  echo " "
  echo ":: Generate self-signed certificate authority"
  echo " "

  ask_for_passphrase "    ROOT CA passphrase (for signing)       " CACERT_PASSPHRASE
  generate_cert_base
  CERT_SUBJ="${CERT_SUBJ_BASE}/CN='OS Lockdown CA'"
  this_step=":: Generate Root CA REQ"
  if [ -z "${CACERT_PASSPHRASE}" ] ; then
    PASSPHRASE="-passout pass:nopassword "
  else
    PASSPHRASE="-passout env:CACERT_PASSPHRASE"
  fi
  ARGS="${PASSPHRASE} -newkey rsa:2048 ${DIGEST} -keyout rootkey.pem -out rootreq.pem"
  echo "${this_step} " | tee -a ${log_file}
  echo "" >> ${log_file}
  echo "${OPENSSL} req -subj \"${CERT_SUBJ}\" ${ARGS}  ">> ${log_file} 
  echo "" >> ${log_file}
  ${OPENSSL} req -subj "${CERT_SUBJ}" ${ARGS} 1>>${log_file} 2>&1
  if [ $? != 0 ] ; then
    echo "${this_step} >>>> FAILED" | tee -a ${log_file} 
    scriptExit 1
  fi

  this_step=":: Generate signed ROOT CA"
  if [ -z "${CACERT_PASSPHRASE}" ] ; then
    PASSPHRASES=""
  else
    PASSPHRASES="-passin env:CACERT_PASSPHRASE"
  fi
  ARGS=" -req -in rootreq.pem -extfile v3_ca.ext ${DIGEST} -extensions v3_ca -signkey rootkey.pem -out cacert.pem -days ${cert_days}"
  echo "${this_step} " | tee -a ${log_file}
  echo "" >> ${log_file}
  echo "${OPENSSL} x509 ${ARGS} ${PASSPHRASES}" >> ${log_file} 
  echo "" >> ${log_file}
  ${OPENSSL} x509 ${ARGS} ${PASSPHRASES} 1>>${log_file} 2>&1
  if [ $? != 0 ] ; then
    echo "${this_step} >>>> FAILED" | tee -a ${log_file}
    scriptExit 1
  fi

  this_step=":: Creating root.pem file for signing other certs"
  echo "${this_step} "| tee -a ${log_file}
  echo "" >> ${log_file}
  echo "cat cacert.pem rootkey.pem > root.pem " >> ${log_file}
  echo "" >> ${log_file}
  cat cacert.pem rootkey.pem > root.pem 
  if [ $? != 0 ] ; then
    echo "${this_step} >>>> FAILED" | tee -a ${log_file}
    scriptExit 1
  fi
}

##############################################################################
#
#  Generate Certificate for WebServer (either Standalone -OR- Enterprise)
#
#
generate_webserver_certificate()
{
  echo " "
  echo ":: Generate webserver certificate (for Tomcat)"
  echo " "

  ask_for_passphrase "    WebServer passphrase                   " GUI_PASSPHRASE
  CERT_SUBJ="${CERT_SUBJ_BASE}/CN=`hostname`${SSL_FQDN_SUFFIX}"

  this_step="Generate Webserver certificate for `hostname`${SSL_FQDN_SUFFIX}"
  if [ -z "${GUI_PASSPHRASE}" ] ; then
    PASSPHRASES="-passout pass:nopassword"
  else
    PASSPHRASES="-passout env:GUI_PASSPHRASE"
  fi
  ARGS=" -newkey rsa:2048 ${DIGEST} -keyout GUIkey.pem -out GUIreq.pem "
  echo ":: ${this_step}" | tee -a ${log_file}
  echo "" >> ${log_file}
  echo "${OPENSSL} req ${ARGS} -subj \"${CERT_SUBJ}\" ${PASSPHRASES} ">> ${log_file} 
  echo "" >> ${log_file}
  ${OPENSSL} req ${ARGS} -subj "${CERT_SUBJ}" ${PASSPHRASES} 1>>${log_file} 2>&1
  if [ $? != 0 ] ; then
    echo ":: ${this_step} >>>> FAILED" | tee -a ${log_file} 
    scriptExit 1
  fi

  if [ -z "${GUI_PASSPHRASE}" ] ; then
    strip_passphrase GUIreq.pem
  fi
}

sign_webserver_certificate()
{
  echo " "
  echo ":: Sign webserver certificate (for Tomcat)"
  echo " "
  this_step="Sign GUI CERT"

  if [ -z "${CACERT_PASSPHRASE}" ] ; then
    PASSPHRASES=""
  else
    PASSPHRASES="-passin env:CACERT_PASSPHRASE"
  fi
  CA_ARGS="-CA root.pem -CAkey root.pem -CAcreateserial "
  ARGS="-req -in GUIreq.pem ${DIGEST} -extfile console.ext -extensions usr_cert -out GUIcert.pem -days ${cert_days}"
  echo ":: ${this_step}" | tee -a ${log_file}
  echo "" >> ${log_file}
  echo "${OPENSSL} x509  ${ARGS} ${PASSPHRASES} ${CA_ARGS}" >> ${log_file} 
  echo "" >> ${log_file}
  ${OPENSSL} x509 ${ARGS}  ${PASSPHRASES} ${CA_ARGS} 1>>${log_file} 2>&1
  if [ $? != 0 ] ; then
    echo ":: ${this_step} >>>> FAILED" | tee -a ${log_file} 
    scriptExit 1
  fi
}

import_webserver_certificate()
{
  path_to_tomcat_cert="."
  validPath=0
  while [ ${validPath} != 1 ] ; do
     ask_for_string "Filename of signed webserver certificate " path_to_tomcat_cert
     if [ ! -f "${path_to_tomcat_cert}" ] ; then
       echo "Unable to locate signed webserver certificate."
     else
       cp ${path_to_tomcat_cert} "."/GUIcert.pem
       validPath=1
     fi
  done
}

import_ca_certificate()
{
  validPath=0
  while [ ${validPath} != 1 ] ; do
     ask_for_string "Filename of CA certificate " path_to_ca_cert
     if [ ! -f "${path_to_ca_cert}" ] ; then
       echo "Unable to locate CA certificate."
     else
       cp ${path_to_ca_cert} "."/cacert.pem
       path_to_ca_cert="."/cacert.pem
       validPath=1
     fi
  done
}

##############################################################################
#
# Generate Certificate for Dispatcher
#
generate_dispatcher_certificate()
{
  echo " "
  echo ":: Generate Dispatcher certificate (for Client Agent daemon)"
  echo " "

  ask_for_passphrase "    Dispatcher passphrase                  " DISPATCHER_PASSPHRASE
  this_step="Generate Dispatcher certificate"
  

  box_name=`hostname`
  CERT_SUBJ="${CERT_SUBJ_BASE}/CN=${box_name}${SSL_FQDN_SUFFIX}"
  
  if [ -z "${DISPATCHER_PASSPHRASE}" ] ; then
    PASSPHRASES="-passout pass:nopassword "
  else
    PASSPHRASES=" -passout env:DISPATCHER_PASSPHRASE"
  fi
  ARGS=" -newkey rsa:2048 ${DIGEST} -keyout Dispkey.pem -out Dispreq.pem"
  echo ":: ${this_step}" | tee -a ${log_file}
  echo "" >> ${log_file}
  echo "${OPENSSL} req ${ARGS} -subj \"${CERT_SUBJ}\" ${PASSPHRASES}" >> ${log_file} 
  echo "" >> ${log_file}
  ${OPENSSL} req ${ARGS} -subj "${CERT_SUBJ}" ${PASSPHRASES} 1>>${log_file} 2>&1
  if [ $? != 0 ] ; then
    echo ":: ${this_step} >>>> FAILED" | tee -a ${log_file} 
    scriptExit 1
  fi
  if [ -z "${GUI_PASSPHRASE}" ] ; then
    strip_passphrase Dispreq.pem
  fi
}

sign_dispatcher_certificate()
{
  echo " "
  echo ":: Sign dispatcher certificate (for Client Agent daemons)"
  echo " "

  this_step="Sign DISPATCHER CERT"
  if [ -z "${CACERT_PASSPHRASE}" ] ; then
    PASSPHRASES=""
  else
    PASSPHRASES="-passin env:CACERT_PASSPHRASE"
  fi
  CA_ARGS="-CA root.pem -CAkey root.pem -CAcreateserial"
  ARGS=" -req -in Dispreq.pem ${DIGEST} -extfile dispatcher.ext -extensions usr_cert -out Dispcert.pem -days ${cert_days}"
  echo ":: ${this_step}" | tee -a ${log_file}
  echo "" >> ${log_file}
  echo "${OPENSSL} x509 ${ARGS} ${PASSPHRASES} ${CA_ARGS}" >> ${log_file} 
  echo "" >> ${log_file}
  ${OPENSSL} x509 ${ARGS} ${PASSPHRASES} ${CA_ARGS} 1>>${log_file} 2>&1
  if [ $? != 0 ] ; then
    echo ":: ${this_step} >>>> FAILED" | tee -a ${log_file} 
    scriptExit 1
  fi
}

package_dispatcher_certificate()
{
  this_step="Package Dispatcher certs for SB_Dispatcher"
  echo ":: ${this_step}" | tee -a ${log_file}
  echo "" >> ${log_file}
  echo "cat Dispcert.pem Dispkey.pem cacert.pem > Disp.pem" >> ${log_file} 
  echo "" >> ${log_file}
  cat Dispcert.pem Dispkey.pem cacert.pem > Disp.pem
  if [ $? != 0 ] ; then
    echo ":: ${this_step} >>>> FAILED" | tee -a ${log_file} 
    scriptExit 1
  fi
}

import_dispatcher_certificate()
{
  path_to_dispatcher_cert="."
  validPath=0
  while [ ${validPath} != 1 ] ; do
     ask_for_string "Filename of signed dispatcher certificate " path_to_dispatcher_cert
     if [ ! -f "${path_to_dispatcher_cert}" ] ; then
       echo "Unable to locate signed dispatcher certificate."
     else
       cp ${path_to_dispatcher_cert} "."/Dispcert.pem
       validPath=1
     fi
  done
}


##############################################################################
#
# Package the webserver Certificates into a Java keystore/truststore combo 
#
package_webserver_certificates_for_java()
{
  # The KEYSTORE_PASSPHRASE *MUST* match the GUI_PASSPHRASE.
  
  TRUSTSTORE_PASSPHRASE=${GUI_PASSPHRASE}
  KEYSTORE_PASSPHRASE=${GUI_PASSPHRASE}
  
  this_step="Create PKCS12 file (removing if already exists)"

  
 
  # Export GUIcert.pem as pkcs12 file - the only way to get the private keys out....
  if [ -z "${GUI_PASSPHRASE}" ] ; then
    PASSPHRASES=""
  else
    PASSPHRASES=" -passin env:GUI_PASSPHRASE -passout env:GUI_PASSPHRASE"
  fi

  ARGS=" -export -in GUIcert.pem -inkey GUIkey.pem -out GUI.p12 "
  echo ":: ${this_step}" | tee -a ${log_file}
  echo "" >> ${log_file}
  echo "rm -f GUI.p12" 1>>${log_file} 
  echo "${OPENSSL} pkcs12 ${ARGS} ${PASSPHRASES}" >> ${log_file} 
  echo "" >> ${log_file}
  rm -f GUI.p12 1>>${log_file} 2>&1
  ${OPENSSL} pkcs12 ${ARGS} ${PASSPHRASES} 1>>${log_file} 2>&1
  if [ $? != 0 ] ; then
    echo ":: ${this_step} >>>> FAILED" | tee -a ${log_file} 
    scriptExit 1
  fi

  this_step="Create new JAVA truststore file for GUI from self-signed certificate (removing if already exists)"
  PASSPHRASES="-storepass ${TRUSTSTORE_PASSPHRASE} -keypass ${GUI_PASSPHRASE}"
  ARGS="-noprompt -keystore GUI_truststore -alias `hostname`${SSL_FQDN_SUFFIX} -file cacert.pem"
  echo ":: ${this_step}" | tee -a ${log_file}
  echo "" >> ${log_file}
  echo "rm -f GUI_truststore " >> ${log_file} 
  echo "${KEYTOOL} -importcert ${ARGS} ${PASSPHRASES} " >> ${log_file}
  echo "" >> ${log_file}
  rm -f GUI_truststore 1>>${log_file} 2>&1 
  ${KEYTOOL} -importcert ${ARGS} ${PASSPHRASES} 1>>${log_file} 2>&1  
  if [ $? != 0 ] ; then
    echo ":: ${this_step} >>>> FAILED" | tee -a ${log_file} 
    scriptExit 1
  fi

  
  # Ok, there is a bug in some versions of openssl such that the creation of the PKCS12 file
  # won't let us 'set' the alias(friendlyName) directly.  So to work around this we'll determine the *actual*
  # alias that was set, and then reset it to something a bit more useful
  # determine what alias(friendlyName) was set
  if [ -z "${GUI_PASSPHRASE}" ] ; then
    PASSPHRASES=""
  else
    PASSPHRASES="-storepass ${GUI_PASSPHRASE}"
  fi

  this_step="Determine current alias (friendlyName) used when pkcs12 file was created"
  ARGS="-keystore GUI.p12 -storetype pkcs12 -v ${PASSPHRASES} "
  echo ":: ${this_step}" | tee -a ${log_file}
  echo "" >> ${log_file}
  echo "export friendlyName=\`${KEYTOOL} -list ${ARGS} ${PASSPHRASES} | grep Alias | awk -F':' '{print \$2}'| sed 's/^ //'\`" 1>>${log_file} >> ${log_file}
  echo "" >> ${log_file}
  friendlyName=`${KEYTOOL} -list ${ARGS} ${PASSPHRASES} | grep Alias | awk -F':' '{print $2}'| sed 's/^ //'`
  export friendlyName
  if [ $? != 0 ] ; then
    echo ":: ${this_step} >>>> FAILED" | tee -a ${log_file} 
    scriptExit 1
  fi



  this_step="Import PKCS12 keystore into JAVA keystore (remove keystore if exists), setting the alias to 'tomcat'"
  SRC_PASSPHRASES="-srckeypass ${GUI_PASSPHRASE} -srcstorepass ${GUI_PASSPHRASE}"
  SRC_PASSPHRASES=" -srcstorepass ${GUI_PASSPHRASE}"
  DST_PASSPHRASES=" -deststorepass ${KEYSTORE_PASSPHRASE} "
  ARGS="-v -destkeystore GUI_keystore -srckeystore GUI.p12 -srcstoretype PKCS12"
  echo ":: ${this_step}" | tee -a ${log_file}
  echo "" >> ${log_file}
  echo "rm -f GUI_keystore" >> ${log_file}
  echo "${KEYTOOL} -importkeystore  ${ARGS} ${SRC_PASSPHRASES} ${DST_PASSPHRASES} -srcalias \"${friendlyName}\" -destalias 'tomcat'" >> ${log_file} 
  echo "" >> ${log_file}
  rm -f GUI_keystore 1>>${log_file} 2>&1
  ${KEYTOOL} -importkeystore ${ARGS}  ${SRC_PASSPHRASES} ${DST_PASSPHRASES} -srcalias "${friendlyName}" -destalias 'tomcat' 1>>${log_file} 2>&1
  if [ $? != 0 ] ; then
    echo ":: ${this_step} >>>> FAILED" | tee -a ${log_file} 
    scriptExit 1
  fi

#  this_step="Change alias for Tomcat"
#  PASSPHRASES="-storepass ${KEYSTORE_PASSPHRASE} -keypass ${GUI_PASSPHRASE}"
#  ARGS="-keystore GUI_keystore -alias 1 -destalias tomcat"
#  echo ":: ${this_step}" | tee -a ${log_file}
#  echo "" >> ${log_file}
#  echo ${KEYTOOL} -changealias ${ARGS} ${PASSPHRASES} >> ${log_file} 
#  echo "" >> ${log_file}
#  ${KEYTOOL} -changealias ${ARGS}  ${PASSPHRASES} >>${log_file} 2>&1
#  if [ $? != 0 ] ; then
#    echo ":: ${this_step} >>>> FAILED" | tee -a ${log_file} 
#    scriptExit 1
#  fi

}

generate_extension_files()
{
  this_step=":: Generate extensions file for self-signed CA signing"
  echo "${this_step}" | tee -a ${log_file}
  rm -f v3_ca.ext
  cat << V3_CA_EXT > v3_ca.ext 
[ v3_ca ]
subjectKeyIdentifier=hash
nsComment="OS Lockdown CA"
authorityKeyIdentifier=keyid:always,issuer
basicConstraints=CA:true
V3_CA_EXT

  this_step=":: Generate extensions file for Console certificate signing"
  echo "${this_step}" | tee -a ${log_file}
  rm -f console.ext
  cat << CONSOLE_CERT_EXT > console.ext 
[ usr_cert ]
basicConstraints=CA:FALSE
nsComment="OS Lockdown Console"
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer
CONSOLE_CERT_EXT
  
  this_step=":: Generate extensions file for Dispatcher certificate signing"
  echo "${this_step}" | tee -a ${log_file}
  rm -f dispatcher.ext
  cat << DISPATCHER_CERT_EXT > dispatcher.ext 
[ usr_cert ]
basicConstraints=CA:FALSE
nsComment="OS Lockdown Dispatcher"
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer
DISPATCHER_CERT_EXT

}

generate_certificate_lifetimes()
{
  echo " "
  echo ":: Certificate Lifetimes"
  echo " "
  
  max_days=`python -c 'import time,math; print int(math.pow(2,31)-time.time())/86400'`

  cert_days=""
  while [ -z "${cert_days}" ] ; do
    ask_for_number   "    Certificate lifetime (between 1 and ${max_days} days)            " "" cert_days
    if [  ${cert_days} -gt ${max_days} -o ${cert_days} -lt 1 ] ; then
      echo "Unable to use a value of ${cert_days} to create a valid certificate, please try again"
      cert_days=""    
    fi

  done
}

##############################################################################
generate_selfsigned_console_certs()
{
  echo " "
  echo ":: Generate Self-signed certificates"
  echo " "

  generate_certificate_lifetimes
  generate_root_ca 
  generate_webserver_certificate
  sign_webserver_certificate
  package_webserver_certificates_for_java
  generate_dispatcher_certificate
  sign_dispatcher_certificate
  package_dispatcher_certificate
}

generate_csr_files()
{
  generate_cert_base
  generate_webserver_certificate
  generate_dispatcher_certificate
  cp GUIreq.pem /tmp/SB_CSR_webserver.pem
  cp Dispreq.pem /tmp/SB_CSR_dispatcher.pem
  echo " "
  echo "The generated Certificate Signing Requests (CSR) files are:"
  echo "  Webserver  (Tomcat)      : /tmp/SB_CSR_webserver.pem"
  echo "  Dispatcher (Client Agent): /tmp/SB_CSR_dispatcher.pem"
  echo " "
  echo "Please send these two files to your Certificate Authority (CA) to be signed."
  echo "The resulting signed CSR files, and the CA's public key (with full trust "
  echo "chain), must be re-imported using this tool (Option 3) before the" 
  echo "installation can be finalized."
  echo " "
}

import_signed_certs()
{
   import_ca_certificate
   import_webserver_certificate
   import_dispatcher_certificate
}

##############################################################################
finalize_certs()
{
  cp root.pem ../
  cp GUIcert.pem ../
  cp GUIkey.pem ../
  cp Disp.pem ../
  cp cacert.pem ../
  cp GUI_keystore ../
  cp GUI_truststore ../

  lock_web_passphrases
  lock_dispatcher_passphrase

  echo ":: Restricting permissions on certificate files..."
  chmod 500 ${SSL_CERTS_DIR} ${SSL_CERTS_WORKING}
  
  # Ok, open up the top level and only those files required for the Console to run to also
  # be readable by sbwebapp
  
  chown root:sbwebapp ${SSL_CERTS_DIR}
  chmod 3750 ${SSL_CERTS_DIR}
  if [ ! -z ${SOLARIS} ] ; then
    chmod g+s ${SSL_CERTS_DIR}
  fi
  
  chown root:sbwebapp ${SSL_CERTS_DIR}/GUI_keystore ${SSL_CERTS_DIR}/GUI_truststore
  chown root:sbwebapp ${SSL_CERTS_DIR}/cacert.pem ${SSL_CERTS_DIR}/Disp.pem

  chmod 440 ${SSL_CERTS_DIR}/GUI_keystore ${SSL_CERTS_DIR}/GUI_truststore
  chmod 440 ${SSL_CERTS_DIR}/cacert.pem ${SSL_CERTS_DIR}/Disp.pem
  
  echo ""
  echo ":: Security credentials created."
  echo ""
}


lock_web_passphrases()
{

  if [ ! -z ${SB_KEYLOCKER} ] ; then
    echo ":: Storing passphrase for WebServer JAVA Truststore as tomcat_truststore..." | tee -a ${log_file}
    echo "${SB_KEYLOCKER} -e -t tomcat_truststore -p env:TRUSTSTORE_PASSPHRASE " >>  ${log_file} 
    ${SB_KEYLOCKER} -e -t tomcat_truststore -p env:TRUSTSTORE_PASSPHRASE 1>>${log_file} 2>&1 
    if [ $? != 0 ] ; then
      echo "Keystore failed" | tee -a ${log_file} 
      scriptExit 1
    fi
  fi
  if [ ! -z ${SB_KEYLOCKER} ] ; then
    echo ":: Storing passphrase for WebServer JAVA Keystore as tomcat_keystore..." | tee -a ${log_file}
    echo "${SB_KEYLOCKER} -e -t tomcat_keystore -p env:KEYSTORE_PASSPHRASE " >> ${log_file} 
    ${SB_KEYLOCKER} -e -t tomcat_keystore -p env:KEYSTORE_PASSPHRASE 1>>${log_file} 2>&1 
    if [ $? != 0 ] ; then
      echo "Keystore failed" | tee -a ${log_file} 
      scriptExit 1
    fi
  fi
}

lock_dispatcher_passphrase()
{
  if [ ! -z ${SB_KEYLOCKER} ] ; then
    echo ":: Storing passphrase for Dispatcher private key as dispatcher_keystore..." | tee -a ${log_file} 
    echo "${SB_KEYLOCKER} -e -t dispatcher_keystore -p env:DISPATCHER_PASSPHRASE  ">> ${log_file}  
    ${SB_KEYLOCKER} -e -t dispatcher_keystore -p env:DISPATCHER_PASSPHRASE >> ${log_file} 2>&1 
    if [ $? != 0 ] ; then
      echo "Keystore failed" | tee -a ${log_file} 
      scriptExit 1
    fi

    echo ":: Ensuring Dispatcher keystore file is readable by the Console..." | tee -a ${log_file} 
    echo "chmod ug+r /var/lib/oslockdown/files/certs/.sb_dispatcher_keystore.dat ">> ${log_file}  
    chmod ug+r /var/lib/oslockdown/files/certs/.sb_dispatcher_keystore.dat >> ${log_file} 2>&1 
    if [ $? != 0 ] ; then
      echo "Unable to set read permissions" | tee -a ${log_file} 
      scriptExit 1
    fi
    echo "chown root:sbwebapp /var/lib/oslockdown/files/certs/.sb_dispatcher_keystore.dat ">> ${log_file}  
    chown root:sbwebapp /var/lib/oslockdown/files/certs/.sb_dispatcher_keystore.dat >> ${log_file} 2>&1 
    if [ $? != 0 ] ; then
      echo "Unable to set ownership" | tee -a ${log_file} 
      scriptExit 1
    fi
  fi
}

##############################################################################
create_certs_directory()
{
# Create target directories if they don't exist
  echo " "
  echo ":: Looking for Certificates directory: ${SSL_CERTS_DIR}"

  if [ ! -d "${SSL_CERTS_DIR}" ] ; then
    ask_yes_or_no "   Directory does not exist, create it?" yes_or_no
    if [ "${yes_or_no}" = "YES" ] ; then
      echo " "
      mkdir -p ${SSL_CERTS_DIR}
      echo ":: Created Certificates directory: ${SSL_CERTS_DIR}"
      if [ $? -eq 1 ] ; then
          echo "   Error: Unable to create directory ${SSL_CERTS_DIR}"
          scriptExit 1
      fi
    else
      echo "Certificate creation aborted."
      scriptExit 1
    fi
  fi  

  # force the correct ownership/perms/context
  chmod 3750 ${SSL_CERTS_DIR}
  if [ ! -z ${SOLARIS} ] ; then
    chmod g+s ${SSL_CERTS_DIR}
  fi
  chown root:sbwebapp ${SSL_CERTS_DIR}
  # force SELinux context if able
  restore_context ${SSL_CERTS_DIR}

  SSL_CERTS_WORKING="${SSL_CERTS_DIR}/.working"
  mkdir -p ${SSL_CERTS_WORKING}
  chown root:root ${SSL_CERTS_WORKING}

  log_file="${SSL_CERTS_WORKING}/ssl_logs.txt"      
  if [ -f ${log_file} ] ; then 
    rm -f ${log_file}      
  fi       
  touch ${log_file}       
  echo ":: Logging to ${log_file}..."
}

get_digest_if_needed()
{
  
  if [ -z "${DIGEST}" ] ; then
    # check to see if sha-256 is available
    echo " " | ${OPENSSL} dgst -sha256 1>/dev/null 2>&1
    if [ $? -eq 0 ] ; then
      # appears SHA-256 is available, ask user 
      echo "The version of openssl provided with this system appears to support the SHA-256"
      echo "hash algorithm in addition to SHA-1. The use of SHA-1 for digests is no longer "
      echo "recommended, but may be required in environments where OS Lockdown is running on"
      echo "older versions of the operating system (such as Red Hat Enterprise Linux 4 or"
      echo "Solaris 10), or the browser does not provide SHA-256 support." 
      echo  ""
      ask_yes_or_no "  Use SHA-256 instead of SHA-1?" use_sha2
      if [ "${use_sha2}" = "YES" ] ; then
        export DIGEST="-sha256"
      else
        export DIGEST="-sha1"
      fi
    else
      # SHA-256 seems to have failed, default silently to sha1
      DIGEST="-sha1"
    fi
  fi
}

get_fqdn_if_needed()
{
    SSL_FQDN_SUFFIX=""
    ask_yes_or_no "     Use Fully Qualified Domain Name (FQDN) for hostnames" UseFQDN
    if [ "${UseFQDN}" = "YES" ] ; then
        ask_for_string "    Enter fqdn suffix to use (must start with a '.'" SSL_FQDN_SUFFIX
    fi         
}

###############################################################################
#######                     MAIN PROGRAM STARTS HERE                     ######
###############################################################################

echo ""
echo "                    .:: CREATE SECURITY CREDENTIALS ::.  "
echo "******************************************************************************"
# Setup initial environment

if [ "`uname -s`" = "SunOS" ]; then
    SOLARIS="yes"
    TR=/usr/xpg4/bin/tr
else
    SOLARIS=
    TR=tr
fi

setup_vars

# Make sure we have any extra files 

EXEC_DIR=`dirname $0`
olddir=$PWD

#try to find the sb-keylocker program 
if [ -x /usr/share/oslockdown/tools/sb-keylocker ] ; then
  SB_KEYLOCKER=/usr/share/oslockdown/tools/sb-keylocker
elif [ -x ../licensing/sb-keylocker ] ; then
  SB_KEYLOCKER=${PWD}/../licensing/sb-keylocker
else
  echo "Unable to locate sb-keylocker program, no passphrases can be stored or "
  echo "retrieved, although certificates can be generated."
fi


SSL_CERTS_DIR=/var/lib/oslockdown/files/certs

create_certs_directory
cd $SSL_CERTS_WORKING

echo ""
echo "Security credentials are used to:"
echo " * Encrypt communications from web browsers to console"
echo " * Encrypt and authenticate console-to-client communications"
echo " "
confirm_openssl
confirm_keytool

cert_mode="*"
while [ ! -z "${cert_mode}" ] ; do
  echo ""
  echo "Options:"
  echo " 1) Generate SSL Certificates using self-signed Certificate Authority (CA)"
  echo " 2) Generate Certificate Signing Requests (CSRs) for another CA to sign"
  echo " 3) Import CA public key and signed CSRs"
  echo " 4) Exit"
  echo
  ask_for_string "Your choice" cert_mode 
  
  case "${cert_mode}" in 
    1) 
       get_digest_if_needed
       get_fqdn_if_needed
       generate_extension_files
       generate_selfsigned_console_certs 
       finalize_certs
       break
       ;;
    2)
        get_digest_if_needed
        get_fqdn_if_needed
        generate_csr_files
        ;;
    3)
        import_signed_certs
        ask_for_passphrase "    WebServer passphrase                   " GUI_PASSPHRASE
        package_webserver_certificates_for_java
        ask_for_passphrase "    Dispatcher passphrase                  " DISPATCHER_PASSPHRASE
        package_dispatcher_certificate
        finalize_certs
        ;;  
    4)  break
        ;;
    *)  echo "Please try again..."
        ;;
  esac
done

scriptExit 0
