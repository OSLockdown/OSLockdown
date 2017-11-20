/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown - Time Encoding
*
*/
#include <iostream>
#include <sys/time.h>
#include <time.h>

#include "SB_time_code.h"

using namespace std;
void show_time(string text,struct tm *fields)
{
  char buff[100];
  
  cout <<text<<endl;
  cout <<"DOY="<<fields->tm_yday;
  cout <<" DOW="<<fields->tm_wday;
  cout <<" DOM="<<fields->tm_mday;
  cout <<" Mon="<<fields->tm_mon;
  cout <<" YEAR="<<(fields->tm_year+1900);
  time_t tval=mktime(fields);
  strftime(buff,sizeof(buff),"%a %B %d, %Y at %H:%M:%S",fields);
  cout <<"   Time="<<tval<<" represents "<<buff<<endl;
}

void show_time(string text,time_t nowtime)
{
  struct tm nowfields;
  
  localtime_r(&nowtime,&nowfields);
  show_time(text, &nowfields);
}



/*
  periodType= enum { daily=0, weekly=1, monthly=2, every minute=-1 }
  periodIncrement is which day/month to execute on 
      weekly -> Sunday=0, Mon=1... Sat=6, Sun=7
      monthly -> 1st of month=1  (so what happens if task scheduled for 30 Feb?)  

  we'll take the current time, turn it into a broken down time struct, update the individual
  elements to the next trigger time, and then create a new time_t value from that and return it

  For testharness, supply a non-zero nowtime so we can *verify* the timestamping
 */
int CalculateStartTime(int hour, int minute, int periodType, int periodIncrement, time_t nowtime)
{
  struct timeval tv;
  struct tm nowfields, nextfields;
  time_t nexttime;
  if (nowtime==0)
  {
    gettimeofday(&tv,NULL);   // should *never* fail
    nowtime=tv.tv_sec;
  }
  localtime_r(&nowtime,&nowfields);
  nextfields=nowfields; // copy now to our working structure

  
  // set the actual hour:minute execution time 
  nextfields.tm_hour=hour; 
  nextfields.tm_min=minute;
  nextfields.tm_sec=0;
  
  if (periodType==-1)   // DEBUG PURPOSES ONLY - EXECUTE ONE PER MINUTE
  {
    nextfields=nowfields;
    nextfields.tm_sec=0;
    nextfields.tm_min++;
    nexttime=mktime(&nextfields);
  }
  else if (periodType==0)
  {
    for(;;)
    {
      nexttime=mktime(&nextfields);
      if (nexttime> nowtime) break;
      nextfields.tm_mday++;
    }	    
  }
  else if (periodType==1)
  {
    nextfields.tm_wday=periodIncrement;
    for(;;)
    {
      nextfields.tm_hour=hour; 
      nextfields.tm_min=minute;
      nextfields.tm_sec=0;
      nexttime=mktime(&nextfields);
      if ((nexttime> nowtime) && (nextfields.tm_wday==periodIncrement)) break;
      nextfields.tm_mday++;
    }	    
  }
  else
  {
    // generate an initial time for the indicated day this month
    nextfields.tm_mday=periodIncrement;
    nexttime=mktime(&nextfields);
    
    for(;;)
    {
      nextfields.tm_hour=hour; 
      nextfields.tm_min=minute;
      nextfields.tm_sec=0;
      // is this time prior to now?
      if (nexttime<nowtime) // yes, so we need to advance the month by one and try again
      {
        nextfields.tm_mon++;
	nextfields.tm_mday=periodIncrement;
        nexttime=mktime(&nextfields);
	continue;
      }
      // day-of-the month of the new time the same as the scheduled day?
      if (nextfields.tm_mday==periodIncrement) // yes, so this should be a valid day, we're done
      {
        break;
      }
      // if we've gotten here, then we have a future time with a different date
      // which means we're past the end of the current month and into the next.
      // So back up to the last day of the previous month and make sure the time is 
      // still in the future...
      nextfields.tm_mday=0;
      nexttime=mktime(&nextfields);
      if (nowtime<nexttime) // ok, we've got a valid future time, break out
      {
        break;
      }
    } 
  }
  return nexttime;
}
