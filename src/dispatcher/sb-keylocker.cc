/*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 * Utility to generate time based license keys
 *    If told via -l or -s what machine to generate for will display base64 encoded license
 *    otherwise will assume local machine install license key directly
 */

#include <iostream>
#include <sstream>
#include <fstream>
#include <exception>
#include <cstdlib>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>


#include <ctime>
#include <string.h>


using namespace std;

class SBTime_Except: public exception
{
  private:
    string text;
  public:
   ~SBTime_Except() throw() {};
   const char* what() const throw()  { return text.c_str(); }
   SBTime_Except() {text="no details";};
   SBTime_Except(string details) { text=details;};
};

struct details_struct
{
  string passphrase;
  string action;
  string keytype;
  string keyfile;
  bool verbose;
};

// forward definitions
void usage(char *execname);
void process_args(details_struct& details,int argc, char **argv);
void main_code (details_struct &details);



void
usage(char *execname)
{
   cerr <<  "Usage: "<<execname<<" [-q] -d -t <KEYTYPE> " <<endl;
   cerr <<  "       "<<execname<<" [-q] -e -t <KEYTYPE> -p <passphrase>" << endl;
   cerr <<  endl;
/*
   cerr <<  "  If <OS> and <ID> are *NOT* present, then the program will generate a license" << endl;
   cerr <<  "  for the current host and write it to /var/lib/oslockdown/files/.sbauth," << endl;
   cerr <<  "  and this program must be run as root to set the correct permissions." << endl;
*/
}

void
process_args(details_struct& details,int argc, char **argv)
{
  int args_processed=1;
  int c;

  if ( argc < 2 ) 
  {
    usage(argv[0]);
  }
  opterr=0;
  optind=1;
  args_processed=1;  /* assume arg 0 is already processed... */
  /* remember, a letter followed by one colon == argument required
               a letter followed by two colons == optional argument
               otherwise no argument */

  details.action="none";
  details.keytype="";
  details.passphrase="";
  details.verbose=true;
  while ((c = getopt (argc, argv, "qdet:p:ah")) != -1)
  {
      switch (c)
      {
        case 'p':
          if (strncmp(optarg,"env:",4)==0)
          {
            if (getenv(optarg+4))
            {
              details.passphrase=getenv(optarg+4);
            }
          }
          else
          {
            details.passphrase=optarg;
          }
          args_processed+=2;
          break;
        case 'd':
          details.action="decrypt";
          args_processed+=1;
          break;
        case 'e':
          details.action="encrypt";
          args_processed+=1;
          break;
        case 't':
          details.keytype=optarg;
          args_processed+=2;
          break;
        case 'h':                  // generate a permanent license (not a trial)
          usage(argv[0]);
          exit(0);
          break;
        case 'q':
          details.verbose=false;
          args_processed+=1;
          break;
        default:
           ostringstream message;
           message<<"Unexpected argument or missing argument value : '-" << (char)optopt << "' found"<<endl;
           message<<"  Type '"<<argv[0]<<" -h' for a list of valid arguments";
           throw (SBTime_Except(message.str()));
      }
  }
  /* ok, processed raw args, do some sanity checking before returning */
  if (details.keytype=="tomcat_truststore")        details.keyfile = "/var/lib/oslockdown/files/certs/.sb_tomcat_truststore.dat";
  else if (details.keytype=="tomcat_keystore")     details.keyfile = "/var/lib/oslockdown/files/certs/.sb_tomcat_keystore.dat";
  else if (details.keytype=="dispatcher_keystore") details.keyfile = "/var/lib/oslockdown/files/certs/.sb_dispatcher_keystore.dat";
  else
  {
    throw(SBTime_Except("-t <keytype> must specify one of tomcat_truststore, tomcat_keystore, or dispatcher_keystore"));
  }
  if (args_processed != argc)  
  {
    ostringstream message;
    message<<"Argument count mismatch - processed "<<args_processed<<" out of "<<argc;
    throw (SBTime_Except(message.str()));
  }
  if ( ((getuid()!=0) && (geteuid()!=0) && details.action=="encrypt"))
  {
    throw (SBTime_Except("Encrypting a passphrase requires *root* access to write file."));
  }
}


int
main (int argc, char **argv)
{
  details_struct details;
  int exitval=1;

  try 
  {
    process_args(details,argc,argv);
    if (details.action=="encrypt")
    {
      ostringstream lictext;
      
      string authtext=details.passphrase;
      ofstream storefile;
      storefile.open(details.keyfile.c_str());
      storefile<<authtext;
      storefile.close();
      chmod(details.keyfile.c_str(),(S_IRUSR|S_IRGRP));
      exitval=0;
    }
    else 
    {
      string passphrase;
      ifstream storefile;
      storefile.open(details.keyfile.c_str());
      storefile >> passphrase;
      storefile.close();
      if (!passphrase.empty())
      {
        if (details.verbose) cout <<"Passphrase for "<<details.keytype<<" is ";
        cout <<passphrase << endl;
        if (passphrase.find("Unable to open and read passfile") == 0)
        {
          exitval=1;  
        }
        else
        {
          exitval=0;  
        } 
      }

    }
  }
  catch (SBTime_Except &e)
  {
    cerr << e.what() <<endl;
  }
  catch (std::exception & e)
  {
    cerr << e.what() <<endl;
  }
  return exitval;
}
