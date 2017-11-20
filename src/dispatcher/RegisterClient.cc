/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* Register a Client with the Enterprise Console
*
*/

#include <iostream>
#include <sstream>

#include <pthread.h>
#include <unistd.h>
#include <sys/stat.h>

#include "version.h"
#include "sbprops.h"
#include "SB_Dispatcher_Utils.h"
#include "SB_Info.h"
#include "SB_Status.h"
#include "SB_Tasks.h"
#include "sub_proc.h"
#include "soapAgentServiceImplPortBindingProxy.h"
#include "AgentServiceImplPortBinding.nsmap"


const int DEF_CLIENT_PORT = 6443;
const int DEF_CONSOLE_PORT = 8443;

using namespace std;

string MY_APPLICATION_SSL_CERTS = APPLICATION_SSL_CERTS;
string MY_APPLICATION_DISPATCHER_LOG = APPLICATION_DISPATCHER_LOG;

#define IF_NOT_NULL(x) (x != NULL) ? x : "(nil)"

DISPATCHER_OPTS disp_opts ;  // not used in this code, but required from SB_Dispatcher_utils

void
ask_user_for_line(string prompt, string def, string & line)
{
  cout << prompt;
  if (!def.empty())
    {
      cout << "[" << def << "]";
    }
  cout << ": ";
  getline(cin, line);
  if (line.empty())
    {
      line = def;
    }
}

void
ask_user_for_word(string prompt, string def, string & word)
{
  string line;
  ask_user_for_line(prompt, def, line);
  if (!line.empty())
    {
      stringstream s(line);
      s >> word;
    }
  else
    {
      line = def;
    }
}

void
ask_user_for_int(string prompt, int defnum, int &number)
{
  string line;
  ostringstream defline;
  defline << defnum;
  ask_user_for_line(prompt, defline.str(), line);
  stringstream s(line);
  s >> number;
  if (number <= 0)
    number = defnum;
}

void
dump_str(char *title, char *textstr, int maxlen)
{
  cout << title;
  if (textstr)
    {
      if (maxlen < 0)
        maxlen = 20;
      int len = strlen(textstr);
      cout << " (" << len << ") :";
      cout << string(textstr, min(len, maxlen));
    }
  else
    {
      cout << "(-1) : 'nil'";
    }
  cout << endl;
}


void
write_to_file(string filename, char *filedata)
{
  // first see if the file already exists.  If so, rename it with the date appended
  try
  {
    if (access(filename.c_str(), R_OK | W_OK) == 0)
      {
        char timebuffer[100];
        string newname;
        time_t now = time(NULL);
        struct tm tmObj;
	struct tm *tm = localtime_r(&now, &tmObj);
        if (tm) 
	{ 
	    (void) strftime(timebuffer, sizeof(timebuffer), "%Y%m%d_%H%M%S", tm);
        }
	else
	{
	    strcpy(timebuffer, "TIME_ERROR");
	}
	newname = filename + "_" + timebuffer;
        rename(filename.c_str(), newname.c_str());
        cout << ":: Renaming " << filename << " to " << newname << endl;
      }


    ofstream outfile(filename.c_str());
    if (outfile.is_open())
      {
        cout << ":: Writing SSL data to " << filename << endl;
        outfile << filedata;
        outfile.close();
        chmod(filename.c_str(), (S_IRUSR | S_IRGRP | S_IROTH));
      }
    else
      {
        cout << ":: Unable to write SSL data to " << filename << endl;
      }
  }
  catch(std::exception & e)
  {
    cerr << ":: Problem writing " << filename << ": " << e.what() << endl;
  }
}


void
usage(char *execarg)
{
  cout << "Usage " << execarg << " [...args]" << endl;
  cout << "       -c        Request updated SSL certificates, but do not reregister" << endl;
  cout << "       -l        Register as the local client, do not overwrite certificates" << endl;
  cout << "       -h        This usage output" << endl;
  cout << "       -n        Do not ask for missing parameters - if required args missing fail"<<endl;
  cout << endl;
  cout <<"        -s address     Name/address of Enterprise Console - required" << endl;
  cout <<"        -p port        {ort of Enterprise Console (defaults to 8443)" << endl;
  cout <<"        -D name        Descriptive name to use for this Client (defaults to hostname)" << endl;
  cout <<"        -A address     Name/address to use for this Client (defaults to hostname)" << endl;
  cout <<"        -P port        Port for this Client (defaults to 6443)" << endl;
  cout <<"        -L location    Location to use for this Client" << endl;
  cout <<"        -C contact     Contact name for this Client" << endl;
  cout << endl;
  exit(0);
}



// Verify that if we are an IPv6 address we are enclosed by brackets '[]'
// hostnames and IPv4 address should be unchanged.
// To do this, look for one or more embedded colons (:) in the address.  
// If you find one/more, make sure the address is wrapped in '[]'

void wrapAddrIfIPv6(string &addr)
{
  if (!addr.empty() && addr.find(":")!=string::npos)
  {
     if (*addr.begin() != '[')
     {
       addr.insert(addr.begin(),'[');
     }
     if (*addr.rbegin() != ']')
     {
       addr.append("]");
     }
   }
}

main(int argc, char *argv[])
{
  ostringstream message;
  AgentServiceImplPortBindingProxy Agent;
  ns1__registerClient registerClient;
  ns1__registerClientResponse registerClientResponse;
  string console_host = "";
  int console_port = DEF_CONSOLE_PORT;
  int client_port = DEF_CLIENT_PORT;
  string client_description = "";
  string client_hostname = "";
  string endpoint = "";
  string client_location = "";
  string client_contact = "";
  string client_certificate = "";
  string client_procinfo = "";   
  string tempstr;
  bool SECURE = true;
  bool certs_only = false;
  bool ssl_setup = false;
  bool interactive = true;
  int c, intarg;
  char hostname_c[256];
  bool is_local_client = false;

  gethostname(hostname_c, sizeof(hostname_c));
  tempstr = hostname_c;
  client_description = tempstr;
  client_hostname = tempstr;
  
  while ((c = getopt(argc, argv, "lhScns:p:D:A:P:L:C:z:")) != -1)
    {
      switch (c)
      {
        case 'l':
          is_local_client = true;
          console_host = "localhost";
          break;
        case 'c':
          certs_only = true;
          break;
        case 'S':
          SECURE = false;
          break;
        case 'n':
          interactive = false;
          break;
        case 's':
          console_host = optarg;
          break;
        case 'p':
          console_port = atoi(optarg);
          break;
        case 'D':
          client_description = optarg;
          break;
        case 'A':
          client_hostname = optarg;
          break;
        case 'P':
           client_port = atoi(optarg);
           break;
        case 'L':
          client_location = optarg;
           break;
        case 'C':
           client_contact = optarg;
           break;
        case 'z':
           client_procinfo = optarg;
           break;
        case 'h':
        default:
          usage(argv[0]);
          break;
      }
    }

// We need to be root for this to work
  
  if (SECURE) 
  {
      try
    {
      Verify_Am_Root();
    }
    catch(SBDispatcher_Except & exc)
    {
      cerr << exc.m_text << endl;
      exit(1);
    }
  }
// Verify that the /var/lib/oslockdown/files/certs directory exists,
// try to create it if it doesn't
  if (!is_local_client) {
    try
    {
      SB_make_full_path("/var/lib/oslockdown/files/certs/");
    }
    catch(SBDispatcher_Except & exc)
    {
      cerr << exc.m_text << endl;
      exit(1);
    }
  }
  cout << endl;
  
  if (interactive || console_host.empty()) 
  {
    cout <<"What Enterprise Console would you like to register this client with?" << endl;
    do
    {
      ask_user_for_line("    Console's host address      ", console_host, console_host);
      if (console_host.empty())
      {
        cout << "::Console host name must not be blank." << endl;
      }
    }
    while (console_host.empty());
  }
  
  if (interactive) 
  {
    ask_user_for_int("    Console's TCP port    ", console_port, console_port);
  }
  

  if (certs_only == false)
  {
    
    if (interactive )
    {
      ask_user_for_line("    Client's descriptive name ", client_description, client_description);
    }
    if (interactive )
    {
      ask_user_for_line("    Client's host address     ", client_hostname, client_hostname);
    }
    
    if (interactive)
    {
      ask_user_for_int("    Client's TCP port         ", client_port, client_port);
    }

    if (interactive && client_location.empty())
    {
      ask_user_for_line("    Client's location         ", "", client_location);
    }
    
    if (interactive && client_contact.empty())
    {
      ask_user_for_line("    Client's contact          ", "", client_contact);
    }

  }
  else
  {
    client_hostname = tempstr;
    client_description = tempstr;
    client_port = 0;
    client_location = "";
    client_contact = "";
  }
  
  
  // Ok, verify that any IPv6 *ADDRESS* is encased in '[]'
  wrapAddrIfIPv6(client_hostname);
  wrapAddrIfIPv6(console_host);
  
  message << "http";
  if (SECURE)
  {
    message << "s";
    soap_ssl_init();
    CRYPTO_thread_setup();

    ssl_setup = soap_ssl_client_context(&Agent,
                                          SOAP_SSL_NO_AUTHENTICATION|SOAP_TLSv1,
                                          NULL, NULL, NULL, NULL, NULL);
    if (ssl_setup)
    {
      cerr << ":: Unable to init client ssl context" << endl;
      exit(1);
    }
  }
  message << "://" << console_host << ":" << console_port <<
    "/OSLockdown/services/clientregistration";
  endpoint = message.str();
  Agent.soap_endpoint = endpoint.c_str();
  cout << endl << ":: Attempting to register with " << endpoint.c_str() << endl;

  registerClient.name =
    soap_strdup(registerClient.soap, client_description.c_str());
  registerClient.hostName =
    soap_strdup(registerClient.soap, client_hostname.c_str());
  registerClient.port = client_port;
  registerClient.location =
    soap_strdup(registerClient.soap, client_location.c_str());
  registerClient.contact =
    soap_strdup(registerClient.soap, client_contact.c_str());
  registerClient.procinfo = 
    soap_strdup(registerClient.soap, client_procinfo.c_str());
  registerClient.clientCertificate =
    soap_strdup(registerClient.soap, client_certificate.c_str());

  if (Agent.registerClient(&registerClient, &registerClientResponse) == SOAP_OK)
  {
    cout << ":: Response for Console -> " <<
      registerClientResponse.return_->reasonPhrase << endl;
    if (!is_local_client && SECURE)
    {
      write_to_file("/var/lib/oslockdown/files/certs/cacert.pem",
                    registerClientResponse.return_->caCert);
      write_to_file("/var/lib/oslockdown/files/certs/Disp.pem",
                    registerClientResponse.return_->dispatcherCert);
      write_to_file("/var/lib/oslockdown/files/certs/.sb_dispatcher_keystore.dat",
                         registerClientResponse.return_->dispatchPassphrase);
    }
    if (certs_only) 
    {
      write_log(LOG_INFO,"Requesting latest SSL certs from Enteprise Console at %s", endpoint.c_str());
    }
    else
    {
      write_log(LOG_INFO,"Registration request sent to Enterprise Console at %s", endpoint.c_str());
    }
  }
  else
  {
    cout << endl <<
      "***********************************************************" << endl;
    cout << "COMMUNICATIONS ERROR: " << endl << endl;
    Agent.soap_stream_fault(cerr);
    cout << "***********************************************************" <<
      endl << endl;
    exit(1);
  }
  cout << ":: Shutting down" << endl;
  if (SECURE)
    CRYPTO_thread_cleanup();

  exit(0);
}
