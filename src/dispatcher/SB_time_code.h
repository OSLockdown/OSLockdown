/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher
*/
#ifndef SB_TIME_CODE_H
#define SB_TIME_CODE_H
#include <iostream>
using namespace std;

void show_time(string text,struct tm *fields);
void show_time(string text,time_t nowtime);
extern int CalculateStartTime(int hour, int minute, int periodType, int periodIncrement,time_t nowtime=0);  // if nowtime=0 use system time

#endif // SB_TIME_CODE_H
