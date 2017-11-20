/*
 * Copyright 2015-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.util
import java.util.concurrent.TimeUnit;
import grails.util.Environment;

enum ConsoleTaskPeriodicity {
    // discrete elements
    //  'enum'          prodOnly    name              prod mode only crontasking details   
    //                                                              valid,    Sec  Min  Hour DoM Mon DoW 
    DEFAULT               ( false,   "Default"                     , false  , "DEFAULT"),                  
    ON_OCCURANCE          ( false,   "(devOnly) When event occurs" , false  , "-"),                 
    ONCE_EVERY_5_SECONDS  ( false,   "(devOnly) Every 5 seconds"   , true   , "*/5  *    *    *   *  ?  "), 
    ONCE_EVERY_30_SECONDS ( false,   "(devOnly) every 30 seconds"  , true   , "*/30 *    *    *   *  ?  "), 
    ONCE_EVERY_MINUTE     ( false,   "(devOnly) Every minute"      , true   , "0    *    *    *   *  ?  "), 
    ONCE_EVERY_5_MINUTES  ( false,   "(devOnly) Every 5 minutes"   , true   , "0    */5  *    *   *  ?  "), 
    ONCE_EVERY_HOUR       ( true,    "Every hour"                  , true   , "0    0    *    *   *  ?  "), 
    ONCE_EVERY_3_HOURS    ( true,    "Every 3 hours"               , true   , "0    0    */3  *   *  ?  "), 
    ONCE_EVERY_6_HOURS    ( true,    "Every 6 hours"               , true   , "0    0    */3  *   *  ?  "), 
    ONCE_EVERY_12_HOURS   ( true,    "Every 12 hours"              , true   , "0    0    */3  *   *  ?  "), 
    ONCE_EVERY_SUNDAY     ( true,    "Every Sunday(midnight)"      , true   , "0    0    0    ?   *  SUN"), 
    ONCE_EVERY_MONDAY     ( true,    "Every Monday(midnight)"      , true   , "0    0    0    ?   *  MON"), 
    ONCE_EVERY_TUESDAY    ( true,    "Every Tuesday(midnight)"     , true   , "0    0    0    ?   *  TUE"),
    ONCE_EVERY_WEDNESDAY  ( true,    "Every Wednesday(midnight)"   , true   , "0    0    0    ?   *  WED"),
    ONCE_EVERY_THURSDAY   ( true,    "Every Thursday(midnight)"    , true   , "0    0    0    ?   *  THU"),
    ONCE_EVERY_FRIDAY     ( true,    "Every Friday(midnight)"      , true   , "0    0    0    ?   *  FRI"),
    ONCE_EVERY_SATURDAY   ( true,    "Every Saturday(midnight)"    , true   , "0    0    0    ?   *  SUN"),
    AT_MIDNIGHT           ( true,    "Daily at midnight"           , true   , "0    0    0    *   *  ?  "),
    AT_1AM                ( true,    "Daily at 1 AM"               , true   , "0    0    1    *   *  ?  "),
    AT_2AM                ( true,    "Daily at 2 AM"               , true   , "0    0    2    *   *  ?  "),
    AT_3AM                ( true,    "Daily at 3 AM"               , true   , "0    0    3    *   *  ?  "),
    AT_4AM                ( true,    "Daily at 4 AM"               , true   , "0    0    4    *   *  ?  "),
    AT_5AM                ( true,    "Daily at 5 AM"               , true   , "0    0    5    *   *  ?  "),
    AT_6AM                ( true,    "Daily at 6 AM"               , true   , "0    0    6    *   *  ?  "),
    AT_7AM                ( true,    "Daily at 7 AM"               , true   , "0    0    7    *   *  ?  "),
    AT_8AM                ( true,    "Daily at 8 AM"               , true   , "0    0    8    *   *  ?  "),
    AT_9AM                ( true,    "Daily at 9 AM"               , true   , "0    0    9    *   *  ?  "),
    AT_10AM               ( true,    "Daily at 10 AM"              , true   , "0    0   10    *   *  ?  "),
    AT_11AM               ( true,    "Daily at 11 AM"              , true   , "0    0   11    *   *  ?  "),
    AT_NOON               ( true,    "Daily at 12 noon"            , true   , "0    0   12    *   *  ?  "),
    AT_1PM                ( true,    "Daily at 1 PM"               , true   , "0    0   13    *   *  ?  "),
    AT_2PM                ( true,    "Daily at 2 PM"               , true   , "0    0   14    *   *  ?  "),
    AT_3PM                ( true,    "Daily at 3 PM"               , true   , "0    0   15    *   *  ?  "),
    AT_4PM                ( true,    "Daily at 4 PM"               , true   , "0    0   16    *   *  ?  "),
    AT_5PM                ( true,    "Daily at 5 PM"               , true   , "0    0   17    *   *  ?  "),
    AT_6PM                ( true,    "Daily at 6 PM"               , true   , "0    0   18    *   *  ?  "),
    AT_7PM                ( true,    "Daily at 7 PM"               , true   , "0    0   19    *   *  ?  "),
    AT_8PM                ( true,    "Daily at 8 PM"               , true   , "0    0   20    *   *  ?  "),
    AT_9PM                ( true,    "Daily at 9 PM"               , true   , "0    0   21    *   *  ?  "),
    AT_10PM               ( true,    "Daily at 10 PM"              , true   , "0    0   22    *   *  ?  "),
    AT_11PM               ( true,    "Daily at 11 PM"              , true   , "0    0   23    *   *  ?  "),
    
	
    // attributes
	String displayName
    String cronexpr;
    Boolean prodOnly;
	Boolean valid;
    
    String getKey() {
        name()
    }

    String getcronexpr() {
        cronexpr
    }
    
    String toString() {
        displayName
    }

    static ConsoleTaskPeriodicity byDisplayName(String enumString) {
        values().find {it.displayName == enumString}
    }
    
    static List<ConsoleTaskPeriodicity> listTimingOptions() 
    {
        def list
        
        if (Environment.current == Environment.PRODUCTION)
        {
            list = ConsoleTaskPeriodicity.values().findAll { it.prodOnly == true}
        }
        else
        {
            list = ConsoleTaskPeriodicity.values()
        }
        return list
    }
    
    
    // constructor per element
    ConsoleTaskPeriodicity(Boolean prodOnly, String name, Boolean valid, String cronexpr) {
	  this.prodOnly = prodOnly;
      this.displayName = name;
      this.cronexpr = cronexpr;
      this.valid = valid;
	}
}
