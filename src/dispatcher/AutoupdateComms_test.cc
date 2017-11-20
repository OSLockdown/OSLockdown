/*
*
* Copyright (c) 2009-2015 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* Register a Client with the Enterprise Console
*
*
*/

#include <iostream>
#include <sstream>
#include <fstream>

#include <pthread.h>
#include <unistd.h>
#include <sys/stat.h>

#include "sbprops.h"


using namespace std;

extern string getData();
extern int getReturnCode();
extern void sendNotification(string serviceURL, string notificationText, string transactionId, bool isOK);
extern void getRemoteFile(string serviceURL,string hostname, string pkgRoot, string cpeShortName, string majorVersion, string minorVersion, string arch, bool withDocs);


void
write_to_stdout()
{
  try
  {
    cout << getData() << endl;
  }
  catch(std::exception & e)
  {
    cout << ":: Problem writing to stdout: " << e.what() << endl;
    exit(1);
  }
}

void
write_to_file(string filename)
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
    }

    ofstream outfile(filename.c_str());
    if (outfile.is_open())
    {
      outfile<<getData();
      outfile.close();
      chmod(filename.c_str(), (S_IRUSR | S_IRGRP | S_IROTH));
    }
  }
  catch(std::exception & e)
  {
    cout << ":: Problem writing " << filename << ": " << e.what() << endl;
    exit(1);
  }
}

void
usage(char *execarg)
{
  cout << "Usage " << execarg << " -h | [-g  [...args]] | -n [ ...args]]"<< endl;
  cout << "   -h "<< endl;
  cout << "   -g "<< endl;
  cout << "      -c ServiceURL" << endl;
  cout << "      -H Hostname" << endl;
  cout << "      -p pkgRoot" << endl;
  cout << "      -s shortCPE" << endl;
  cout << "      -M majorVersion" << endl;
  cout << "      -m minorVersion" << endl;
  cout << "      -a arch" << endl;
  cout << "      -d docsFlag (optional - defaults to false)" << endl;
  cout << "      -f outputFile (optional name to write results to - stdout otherwise)"<<endl;
  cout << "  -n "<< endl;
  cout << "      -c ServiceURL" << endl;
  cout << "      -i transactionId"<<endl;
  cout << "      -t notificationText"<<endl;
  cout << "      -o isOK (optional - defaults to false)"<<endl; 
  exit(1);
}


main(int argc, char *argv[])
{
  ostringstream message;

  int command=0;
  
  char * hostname = NULL;
  char * notificationText =  NULL;
  char * serviceURL = NULL;
  char * pkgRoot = NULL;
  char * cpeShortName = NULL;
  char * majorVersion = NULL;
  char * minorVersion = NULL;
  char * arch = NULL;
  bool withDocs = false;
  char * transactionId = NULL;
  bool  isOK = false;
  int c;
  int returnCode;
  bool ssl_setup = false;
  char *outFile = NULL;
  
  while ((c = getopt(argc, argv, "c:H:p:s:M:m:a:d:ngt:i:of:")) != -1)
    {
      switch (c)
      {
        case 'f':
            outFile = optarg;
            break;
        case 't':
            notificationText = optarg;
            break;
        case 'i':
            transactionId = optarg;
            break;
        case 'o':
            isOK = true;
            break;
        case 'n':
        case 'g':
            if (command != 0) 
            {  
              cout <<"Only one of '-g' or '-n' is allowed"<<endl;
              usage(0);
            }
            command = c;
            break;
        case 'c':
          serviceURL = optarg;
          break;
        case 'H':
          hostname = optarg;
          break;
        case 'p':
          pkgRoot = optarg;
          break;
        case 's':
          cpeShortName = optarg;
          break;
        case 'M':
          majorVersion = optarg;
          break;
        case 'm':
          minorVersion = optarg;
          break;
        case 'a':
          arch = optarg;
          break;
        case 'd':
          withDocs = true;
          break;
        case 'h':
        default:
          usage(argv[0]);
          break;
      }
    }

  if (command == 'g')
  {
    getRemoteFile(serviceURL, hostname, pkgRoot, cpeShortName, majorVersion, minorVersion, arch, withDocs);
    returnCode = getReturnCode();
    if (returnCode)
    {
      cout<<getData()<<endl;
    }
    else
    {
      int len = getData().length();
      if (outFile) 
      {
        
        write_to_file(outFile);
        cout <<"Wrote "<< len <<" bytes to "<< outFile << endl;
      }
      else
      {
        cout <<"Received file of size "<< len << endl;
      }
    }
    getRemoteFile(serviceURL, hostname, pkgRoot, cpeShortName, majorVersion, minorVersion, arch, withDocs);
    returnCode = getReturnCode();
    if (returnCode)
    {
      cout<<getData()<<endl;
    }
    else
    {
      int len = getData().length();
      if (outFile) 
      {
        
        write_to_file(outFile);
        cout <<"Wrote "<< len <<" bytes to "<< outFile << endl;
      }
      else
      {
        cout <<"Received file of size "<< len << endl;
      }
    }
  }
  else if (command == 'n')
  {
    sendNotification(serviceURL, notificationText, transactionId, isOK);
    returnCode = getReturnCode();
    if (returnCode)
    {
      cout<<getData()<<endl;
    }
    else
    {
      cout <<"Send notification to "<< serviceURL<<endl;
    }
  }
  else
  {
    cout << ":: must either request packages ('-g') or send notification ('-n')" << endl;
    returnCode=1;
  } 

  
  
  exit(returnCode);
}
