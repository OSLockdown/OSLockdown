/*
*
* Copyright (c) 2009-2015 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher
*
*/

#ifndef AUTOUPDATECOMMS_UTILS_H
#define AUTOUPDATECOMMS_UTILS_H

#include <pthread.h>
#include <iostream>
#include <sstream>
#include <vector>
#include <exception>
#include <syslog.h>
#include <openssl/crypto.h>
using namespace std;


class AutoupdateComms_Except: public exception
{
  private:
    void gen_text(){ ostringstream message ; message << "Code:"<<m_code<<" Reason:"<< m_text; m_fulltext=message.str(); }; 
  public:
    int m_code;
    string m_text;
    string m_fulltext;
    ~AutoupdateComms_Except() throw() {};
    const char* what() const throw()  { return m_fulltext.c_str();}
    AutoupdateComms_Except() {m_code = 200; m_text="no details"; gen_text();};
    AutoupdateComms_Except(int code, string details) { m_code=code; m_text=details; gen_text();};
};


struct CRYPTO_dynlock_value
{
  pthread_mutex_t mutex;
};


/* treat all this crypto/lock stuff for SSL with with C linkage...*/
#ifdef __cplusplus
extern "C" 
{
#endif

/* public functions */
void CRYPTO_thread_setup();
void CRYPTO_thread_cleanup();

/* static/private functions */

static void my_lock_core(int mode, CRYPTO_dynlock_value *ptr, const char *file, int line);
static void my_lock(int mode, int n, const char *file, int line);
static long unsigned int my_id();
static void my_dyn_lock(int mode, struct CRYPTO_dynlock_value *ptr, const char *file, int line);
static struct CRYPTO_dynlock_value * my_dyn_create(const char *file, int line);
static struct CRYPTO_dynlock_value *my_lock_create(const char *file, int line);
static void my_dyn_destroy(struct CRYPTO_dynlock_value *ptr, const char *file, int line);
#ifdef __cplusplus
}
#endif

extern bool log_to_stderr;
extern void write_log (int level, const char *fmt, ...);
#endif // AUTOUPDATECOMMS_UTILS_H
