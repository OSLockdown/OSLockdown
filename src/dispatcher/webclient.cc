/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher
* 
*/

#include <iostream>
#include <sstream>
#include <pthread.h>
#include "soapAgentServiceImplPortBindingProxy.h"
#include "AgentServiceImplPortBinding.nsmap"
#include "ssl_thr_utils.h"

using namespace std;

main(int argc,char *argv[])
{
  AgentServiceImplPortBindingProxy Agent;
  ns1__info info_cmd;
  ns1__infoResponse info_reply;
  int port=8080;
  string endpoint;
  string remotehost="localhost";
  bool SECURE=false;
  bool SSL_FULL_HOSTNAME_CHECK=false;
  bool ssl_setup=false;
  int c,intarg;
  
  while ((c = getopt (argc, argv, "Sa:p:H")) != -1)
  {
    switch (c)
    {
      case 'H':
        SSL_FULL_HOSTNAME_CHECK=true;
	break;
      case 'S':
        SECURE=true;
	break;
      case 'p': 
        intarg=atoi(optarg);
        port=intarg;
//        if (intarg>8080) port=intarg;
        break;
      case 'a':
        remotehost=optarg;
	break;
    }
    
  }
  ostringstream message;

  message<<"http";

  if (SECURE)
  {
    message <<"s";
    soap_ssl_init();
    CRYPTO_thread_setup();

    if (SSL_FULL_HOSTNAME_CHECK)
    {
      ssl_setup=soap_ssl_client_context(&Agent,
      					 SOAP_SSL_DEFAULT,
      					 "certs/gui.pem",
      					 "2222",
      					 "certs/root.pem",
      					 NULL,
      					 NULL);
    }
    else
    {
      ssl_setup=soap_ssl_client_context(&Agent,
      					SOAP_SSL_NO_AUTHENTICATION,
      					NULL,
      					NULL,
      					NULL,
      					NULL,
      					NULL);
    }
    if (ssl_setup)
    {
      cerr <<"Unable to init client ssl context"<<endl;
      exit(1);
    }
  }
  message<<"://"<<remotehost<<":"<<port<<"/agentws/services/agent";
  endpoint=message.str();
  Agent.soap_endpoint=endpoint.c_str();
  cout <<"Attempting to contact "<< endpoint.c_str()<<endl;  
  info_cmd.transactionId="Hello";
  info_cmd.notificationAddress="FOOBAR";
  if (Agent.info(&info_cmd,&info_reply)==SOAP_OK)
  {
    printf("Got  -> %d %s\n",info_reply.return_->code,info_reply.return_->body);
  }
  else
  {
    Agent.soap_stream_fault(cerr);
  }
  CRYPTO_thread_cleanup();
}

