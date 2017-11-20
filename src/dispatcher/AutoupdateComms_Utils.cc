/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher utilities
*
*/

#include <cstdlib>
#include <string.h>
#include <fstream>
#include <cerrno>
#include <sys/types.h>
#include <dirent.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdarg.h>
#include <openssl/crypto.h>
#include "AutoupdateComms_Utils.h"
#include "sbprops.h"

extern string MY_APPLICATION_DISPATCHER_LOG;


bool log_to_stderr=false;

/**
 * Write to log (syslog and dedicated log)
 * @param level   Logleve
 * @param fmt     Message format (like snprintf())
 * @param ...     variables for fmt
 *
 */
void
write_log (int level, const char *fmt, ...)
{
  FILE *sblog = NULL;
  const struct tm *tm = NULL;
  struct tm tmObj;
  time_t now = 0;
  int mask = 0;
  static char time_buffer[40];
  char message[1024];

  const char *logprefix[] = {
    "Emergency: ",
    "Alert:     ",
    "Critical:  ",
    "Error:     ",
    "Warning:   ",
    "Notice:    ",
    "Info:      ",
    "DEBUG:     "
  };

  if (level < 0 && level > 7)
    level = 5;
  memset (&message, '\0', sizeof (message));
  memset (&time_buffer, '\0', sizeof (time_buffer));
  va_list arglist;
  va_start (arglist, fmt);
  vsnprintf (message, sizeof (message) - 1, fmt, arglist);
  va_end (arglist);

  /* Determine current log mask */
  mask = setlogmask (0);

  umask (027);
  if (log_to_stderr)
    {
      now = time (NULL);
      tm = localtime_r (&now, &tmObj);
      if (tm != NULL) 
      {
      	(void) strftime (time_buffer, 40, "%F %T", tm);
      }
      else 
      {
      	strcpy(time_buffer, "<TIME_ERROR>");
      }
      fprintf (stderr, "%s %s %s\n", time_buffer, logprefix[level], message);
    }
  else
    {
      if ((sblog = fopen (MY_APPLICATION_DISPATCHER_LOG.c_str(), "a")) != NULL)
        {
          now = time (NULL);
          tm = localtime_r (&now, &tmObj);
      	  if (tm != NULL) 
      	  {
      	    (void) strftime (time_buffer, 40, "%F %T", tm);
      	  }
      	  else 
      	  {
      	    strcpy(time_buffer, "<TIME_ERROR>");
      	  }
          fprintf (sblog, "%s %s %s\n", time_buffer, logprefix[level], message);
          fclose (sblog);
        }

      /* Only log messages < LOG_DEBUG to syslog to avoid cluttering it */
      if (mask < 255)
        {
          openlog ("AutoupdateComms", LOG_CONS | LOG_PID | LOG_NDELAY, LOG_DAEMON);
          (void) syslog (level, message);
          closelog ();
        }
    }
  return;
}

static struct CRYPTO_dynlock_value **my_locks;
static int num_locks;

/* public functions */
void CRYPTO_thread_setup();
void CRYPTO_thread_cleanup();

static struct CRYPTO_dynlock_value * my_lock_create(struct CRYPTO_dynlock_value *ptr,const char *file, int line)
{
  int retval;
  if (!ptr) ptr=(struct CRYPTO_dynlock_value*)calloc(1,sizeof(struct CRYPTO_dynlock_value));
  if (!ptr)
  {
//    perror("Unable to allocate mutex");
    throw (AutoupdateComms_Except(500,"Unable to allocate mutex "));
// exit(1);
  }
  retval=pthread_mutex_init(&(ptr->mutex),NULL);
  return ptr;
}


static void my_lock_core(int mode, CRYPTO_dynlock_value *ptr, const char *file, int line)
{
  if (mode &CRYPTO_LOCK)     pthread_mutex_lock(&(ptr->mutex));
  else                       pthread_mutex_unlock(&(ptr->mutex));
}
static void my_lock(int mode, int n, const char *file, int line)
{
  my_lock_core(mode,my_locks[n],file,line);
}

long unsigned int my_id()
{
  return (long unsigned int)pthread_self();
}

static void my_dyn_lock(int mode, struct CRYPTO_dynlock_value *ptr, const char *file, int line)
{
  my_lock_core(mode,ptr,file,line);
}

static struct CRYPTO_dynlock_value * my_dyn_create(const char *file, int line)
{
  return my_lock_create(NULL,file,line);
}

static void my_dyn_destroy(struct CRYPTO_dynlock_value *ptr, const char *file, int line)
{
  if (ptr) free(ptr);  
}

void CRYPTO_thread_setup()
{
  int i;
  
  if (my_locks) return;
  num_locks=CRYPTO_num_locks();
  my_locks=(struct CRYPTO_dynlock_value**)calloc(num_locks,sizeof(struct CRYPTO_dynlock_value*));
  if (!my_locks)
  { 
    throw (AutoupdateComms_Except(500,"Unable to allocate lock structures"));
//    write_log(LOG_ERR,"Unable to allocate lock structures");
//    exit(1);
  }
  for (i = 0;i!=num_locks;i++)
  {
    my_locks[i]=my_lock_create(NULL,__FILE__,__LINE__);
  }
  CRYPTO_set_id_callback(my_id);
  CRYPTO_set_locking_callback(my_lock);
  CRYPTO_set_dynlock_create_callback(my_dyn_create);
  CRYPTO_set_dynlock_lock_callback(my_dyn_lock);
  CRYPTO_set_dynlock_destroy_callback(my_dyn_destroy);
}

void CRYPTO_thread_cleanup()
{
  int i;
  CRYPTO_set_id_callback(NULL);
  CRYPTO_set_locking_callback(NULL);
  CRYPTO_set_dynlock_create_callback(NULL);
  CRYPTO_set_dynlock_lock_callback(NULL);
  CRYPTO_set_dynlock_destroy_callback(NULL);
  for (i=0;i!=num_locks;i++)
  {
    my_dyn_destroy(my_locks[i],__FILE__,__LINE__);
  }
  free(my_locks);
  my_locks = NULL;
}

