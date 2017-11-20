/*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* Generate a SHA1 hash of a specified file
*
*/

#include <iostream>
#include <sstream>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <openssl/ssl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include "fingerprints.h"
#include "SB_Dispatcher_Utils.h"

using namespace std;
/**
  * Compute SHA1 of Regular file
  * @param filename File to fingerprint
  */
void
get_file_sha1 (const char *filename, char sha1_fingerprint[145])
{

  EVP_MD_CTX md;
  unsigned char md_value[EVP_MAX_MD_SIZE];
  int fd = 0;
  unsigned int n = 0, i = 0, md_len = 0;
  unsigned char buf[1024];
  char hexbuf[4];

  memset (&md, '\0', sizeof (EVP_MD_CTX));

  EVP_MD_CTX_init (&md);
  EVP_DigestInit_ex (&md, EVP_sha1 (), NULL);

  memset (&md_value, '\0', EVP_MAX_MD_SIZE);
  memset (&buf, '\0', 1024);
  memset (&hexbuf, '\0', 4);
  
  memset (sha1_fingerprint, '\0', 145);

  if ((fd = open (filename, O_RDONLY)) == -1)
    {
      EVP_MD_CTX_cleanup (&md);
      strcpy (sha1_fingerprint, "error");
      return;
    }
  else
    {
      while ((n = read (fd, buf, 1024)) > 0)
        EVP_DigestUpdate (&md, buf, n);
      close (fd);

      memset (&buf, '\0', sizeof (&buf));

      if (EVP_DigestFinal_ex (&md, md_value, &md_len) != 1)
        {
          EVP_MD_CTX_cleanup (&md);
          strcpy (sha1_fingerprint, "error");
	  return;
        }
      else
        {
          for (i = 0; i < md_len; i++)
            {
              snprintf (hexbuf, 3, "%02x", md_value[i]);
              strncat (sha1_fingerprint, hexbuf, 3);
            }
        }
    }
  EVP_MD_CTX_cleanup (&md);

    /** I don't want pass a pointer back to a local variable **/
  return ;
}

/**
  * Compute SHA1 of Regular file
  * @param filename File to fingerprint
  */
char *
get_buffer_sha1 (char *buf,size_t bsize)
{

  EVP_MD_CTX md;
  unsigned char md_value[EVP_MAX_MD_SIZE];
  int fd = 0;
  unsigned int n = 0, i = 0, md_len = 0;
  char hexbuf[4];
  char sha1_fingerprint[145];

  memset (&md, '\0', sizeof (EVP_MD_CTX));

  EVP_MD_CTX_init (&md);
  EVP_DigestInit_ex (&md, EVP_sha1 (), NULL);

  memset (&md_value, '\0', EVP_MAX_MD_SIZE);
  memset (&hexbuf, '\0', 4);
  memset (&sha1_fingerprint, '\0', 145);

  EVP_DigestUpdate (&md, buf, bsize);
  if (EVP_DigestFinal_ex (&md, md_value, &md_len) != 1)
    {
      cout <<"\n\n\nERROR get_buffer_sha1\n\n\n";
      EVP_MD_CTX_cleanup (&md);
      return (strdup ("error"));
    }
  else
    {
      for (i = 0; i < md_len; i++)
  	{
  	  snprintf (hexbuf, 3, "%02x", md_value[i]);
  	  strncat (sha1_fingerprint, hexbuf, 3);
  	}
  }
  

  EVP_MD_CTX_cleanup (&md);

    /** I don't want pass a pointer back to a local variable **/
  return (strdup (sha1_fingerprint));
}

static bool SB_Integrity_check(string filename, string expected_sha1)
{
  bool sha1_match=true;
  char calculated_sha1[145];
  
  get_file_sha1(filename.c_str(),calculated_sha1);
  if (strcmp(calculated_sha1,expected_sha1.c_str())!=0)
  {
    ostringstream msg;
    msg <<filename<< " SHA1 fingerprint mismatch : ";
    msg <<"Expected "<<expected_sha1<<" but calculated "<<calculated_sha1<<endl;
    throw (SBDispatcher_Except(500,msg.str()));
    sha1_match=false;
  }
  return sha1_match;
  
}

bool SB_Integrity(bool integrity_check)
{
  if (integrity_check)
  {
    if (!SB_Integrity_check(SB_SHA1_FILENAME,SB_SHA1)) exit(1);
    if (!SB_Integrity_check(SB_SCRIPT_SHA1_FILENAME, SB_SCRIPT_SHA1)) exit(1);
  }
  return true;
}
