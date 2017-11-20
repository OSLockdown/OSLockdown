/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher
**
*/

#include <iostream>
#include <sstream>
#include <sys/time.h>
#include <time.h>

#include "SB_time_code.h"

using namespace std;





void task_it(time_t nowtime,int hour, int minute, int periodType, int periodIncrement,int how_many)
{
  time_t newtime;
  ostringstream msg;
  static string dayname[8]={"Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"};
  for (int i=0;i!=how_many; i++)
  {
    msg.str("");
    msg.fill('0');
    if (periodType==0) 
    {
  
      msg<<"a daily task scheduled ";
    }
    else if (periodType==1)
    {
      msg<<"a weekly task scheduled for "<<periodIncrement<<"("<<dayname[periodIncrement]<<")";
    }
    else if (periodType==2)
    {
      msg<<"a monthly task scheduled for day "<<periodIncrement;
    }
    msg <<" at ";
    msg.width(2);
    msg<<hour<<":";
    msg.width(2);
    msg<<minute<<" ";
    cout <<msg.str()<<endl;
    show_time("If now is ",nowtime);
    newtime=CalculateStartTime(hour,minute,periodType,periodIncrement,nowtime);
    show_time("Task should be scheduled for ",newtime);
    cout <<endl;
    nowtime=newtime+5; // offset by 5 seconds to ensure we 'started'
  }  
}

void show_series()
{
  struct timeval tv;
  struct tm fakefields;
  time_t nowtime; 
  
  gettimeofday(&tv,NULL);
  nowtime=tv.tv_sec;

  localtime_r(&nowtime,&fakefields);
  // test daily for 1 week for February 25 of this year, then for the next 4 years
  cout << "<<<<<<<<<<<<<    TESTING DAILY CALCS ACROSS END-OF-FEBRUARY BOUNDARY OVER 4 YEARS"<<endl<<endl;
  
  for (size_t i=0 ; i!= 4; i++)
  {
    fakefields.tm_mon=1;
    fakefields.tm_mday=25;
    nowtime=mktime(&fakefields);

    task_it(nowtime,17,0,0,0,7);
    fakefields.tm_year++;
  }
  cout <<endl<<endl<<endl;


  // task something once a week for 52 weeks
  cout << "<<<<<<<<<<<<<    TESTING WEEKLY CALCS OVER 1 YEAR"<<endl<<endl;
  nowtime=tv.tv_sec;
  task_it(nowtime,17,0,1,3,52);
  cout <<endl<<endl;
  cout <<endl<<endl<<endl;

  // task something once a month on the 29 for 4 years.  Tests leap-years, plus past-end-of-month for February non-leap years
  cout << "<<<<<<<<<<<<<    TESTING MONTHLY CALSC OVER 4 YEARS"<<endl<<endl;
  nowtime=tv.tv_sec;
  task_it(nowtime,17,0,2,29,48);
  cout <<endl<<endl<<endl;

  // task something once a minute for 10 minutes. 
  cout << "<<<<<<<<<<<<<    DEBUG testing once per minute from now for 10 minutes"<<endl<<endl;
  nowtime=tv.tv_sec;
  task_it(nowtime,17,0,-1,0,10);
  cout <<endl<<endl<<endl;


}

main()
{
  show_series();
}
