/*
*
* Copyright (c) 2009-2015 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* SOAP client to pull updates from Console
*
*/

#include <iostream>
#include <sstream>
#include <fstream>

#include <pthread.h>
#include <unistd.h>
#include <sys/stat.h>

#include "sbprops.h"
#include "AutoupdateComms_Utils.h"
#include "soapAgentServiceImplPortBindingProxy.h"
#include "AgentServiceImplPortBinding.nsmap"

const int DEF_CLIENT_PORT = 6443;
const int DEF_CONSOLE_PORT = 8443;

using namespace std;

string MY_APPLICATION_SSL_CERTS = APPLICATION_SSL_CERTS;
string MY_APPLICATION_DISPATCHER_LOG = APPLICATION_DISPATCHER_LOG;

#define IF_NOT_NULL(x) (x != NULL) ? x : "(nil)"



 /* Ugly, yes.  We're using globals to hold our results,
  * but since the *designed* interface is through SWIG
  * this should be ok
  */
  

static string stringData;
static int returnCode;

static bool SECURE=false;

string getData()
{
  return stringData;
}

int getReturnCode()
{
  return returnCode;
}

void getRemoteFile(string serviceURL,string hostname, string pkgRoot, string cpeShortName, string majorVersion, string minorVersion, string arch, bool withDocs)
{
  AgentServiceImplPortBindingProxy Agent;

  // if serviceURL[5]=='s' then assume we're https traffic
  // otherwise some sort of exception would be raised.....
  
  if (serviceURL[4]=='s')
  {
    SECURE = true;
    soap_ssl_init();
    CRYPTO_thread_setup();

    bool ssl_setup = soap_ssl_client_context(&Agent,
                                          SOAP_SSL_NO_AUTHENTICATION,
                                          NULL, NULL, NULL, NULL, NULL);
    if (ssl_setup)
    {
      cout << ":: Unable to init client ssl context" << endl;
      exit(1);
    }
  }
  
  ns1__listPackages listPackages;
  ns1__listPackagesResponse listPackagesResponse;
  Agent.soap_endpoint = serviceURL.c_str();

  listPackages.hostName =
      soap_strdup(listPackages.soap, hostname.c_str());
  listPackages.pkgRoot =
      soap_strdup(listPackages.soap, pkgRoot.c_str());
  listPackages.cpeShortName =
      soap_strdup(listPackages.soap, cpeShortName.c_str());
  listPackages.majorVersion =
      soap_strdup(listPackages.soap, majorVersion.c_str());
  listPackages.minorVersion =
      soap_strdup(listPackages.soap, minorVersion.c_str());
  listPackages.arch =
      soap_strdup(listPackages.soap, arch.c_str());
  listPackages.withDocs = &withDocs;

  if (Agent.listPackages(&listPackages, &listPackagesResponse) == SOAP_OK)
  {
    xsd__base64Binary *base64Binary = listPackagesResponse.return_;
    
    try
    {
      stringData = string((char*)base64Binary->__ptr, base64Binary->__size);
      returnCode=0;
    }
    catch (...) 
    {
      returnCode=-1;
    }
  }
  else
  {
    ostringstream omsg;
    omsg << endl << "***********************************************************" << endl;
    omsg <<         "COMMUNICATIONS ERROR: " << endl << endl;
    Agent.soap_stream_fault(omsg);
    omsg <<         "***********************************************************" << endl << endl;
    stringData = omsg.str();
    returnCode=-1;
  }
  
  if (SECURE)
    CRYPTO_thread_cleanup();

}
  
void  sendNotification(string serviceURL, string notificationText, string transactionId, bool isOK  )
{
  AgentServiceImplPortBindingProxy Agent;

  // if serviceURL[5]=='s' then assume we're https traffic
  // otherwise some sort of exception would be raised.....
  
  if (serviceURL[4]=='s')
  {
    SECURE = true;
    soap_ssl_init();
    CRYPTO_thread_setup();

    bool ssl_setup = soap_ssl_client_context(&Agent,
                                          SOAP_SSL_NO_AUTHENTICATION,
                                          NULL, NULL, NULL, NULL, NULL);
    if (ssl_setup)
    {
      cout << ":: Unable to init client ssl context" << endl;
      exit(1);
    }
  }

  ns1__notify console_notify;
  ns1__consoleNotification notice_data;
  ns1__notifyResponse notifyResponse;

  string body;
  ostringstream ostr;
  ostr << "<details success=\"" ;
  if (isOK) ostr<< "true";
  else      ostr<< "false";
  ostr <<"\">";
  
  ostr << "<data>";
  if  (!notificationText.empty())
  {
    ostr <<"<entry name=\"info\" value=\"" <<notificationText << "\"/>";
  }
  ostr << "</data>";
  ostr << "</details>";
  body = ostr.str();

  notice_data.info=         (char*)notificationText.c_str();
  notice_data.transactionId = (char*)transactionId.c_str();
  notice_data.body=         (char*)body.c_str();
  notice_data.type=          12;
  console_notify.notification=&notice_data;

  Agent.soap_endpoint = serviceURL.c_str();


  if (Agent.notify(&console_notify, &notifyResponse) != SOAP_OK)
  {
    ostringstream omsg;
    omsg << endl << "***********************************************************" << endl;
    omsg <<         "COMMUNICATIONS ERROR: " << endl << endl;
    Agent.soap_stream_fault(omsg);
    omsg <<         "***********************************************************" << endl << endl;
    stringData =  omsg.str();
    returnCode=-1;
  }
  
  if (SECURE)
    CRYPTO_thread_cleanup();

  
}

