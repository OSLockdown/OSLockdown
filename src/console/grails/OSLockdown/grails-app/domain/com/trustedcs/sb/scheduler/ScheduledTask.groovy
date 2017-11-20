/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.scheduler;

import org.apache.log4j.Logger;
import com.trustedcs.sb.web.pojo.Group;
import com.trustedcs.sb.web.pojo.Client;
import com.trustedcs.sb.services.client.scheduler.DispatcherTask;

// import quartz scheduler classes to provide 'nextFireTime' method
import org.quartz.CronExpression
import org.quartz.CronScheduleBuilder
import org.quartz.TriggerBuilder

import com.trustedcs.sb.util.SbDateUtil;

class ScheduledTask {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.scheduler.ScheduledTask");
	
    // the logging level the actions will be executed with
    int loggingLevel = 4;
	
    // 0 = daily
    // 1 = weekly
    // 2 = monthly
    int periodType = 0;
    
    // days of the week starts at 0
    // day of the month starts at 1
    int periodIncrement=0;	

    //
    // a. Time persistent properties
    //
    // hour is stored in the DB and has values in range [0..23] encompassing both AM and PM values
    int hour = 0;
    // min stored in the DB as well as has values in range [0..23]
    int minute = 0;

    //
    // b. Time transient (non-persistent) properties
    //
    int hoursAmPm;
    // Make sure to default hoursOffset to -1 and not 0, as 0 is valid value set from the UI
    // however, getHoursOffset() method was checking if( hoursOffset ) and if( 0 ) is always false.
    // During Scheduled Task creation or update hoursOffset is set from the UI to either 0 (for AM) or 12 (for PM)
    // and hour is set to be in the range [12, 1, 2..11]. Then hour and hoursOffset set from UI are adjusted
    // to be in the [0..23] hour range for persistence in ScheduledTaskService.computeHoursForSavingBasedOnAmPm() method.
    int hoursOffset = -1;
	
    // the list of actions strings in combination of 's','a','b'
    String actions;

    // transients
    String actionsString;
    String taskIdentifier;
    String verboseDescription;
	Boolean genDelta = false;

    // relationship
    static belongsTo = [group:Group];


    static transients = ['actionsString','taskIdentifier','verboseDescription','hoursAmPm','hoursOffset'];

    // constraints
    static constraints = {
        loggingLevel(range:0..7);
        periodType(range:0..2);
        periodIncrement(nullable:false);
    	hour(range:0..23);
    	minute(range:0..59);    	
    	actions(blank:false,nullable:false);
    	group(nullable:false);
        genDelta(nullable:false);
    }
    
    /**
     * Returns a string represenation of the action list
     * @return the pretty string
     */
    def getActionsString() {
    	def buf = "";
    	if ( actions ) {
            for (int i = 0; i < actions?.length(); i++) {
                if ( i > 0 ) {
                    buf += ",";
                }
                if ( actions[i] == "s" ) {
                    buf += "Scan";
                }
                else if ( actions[i] == "a" ) {
                    buf += "Apply";
                }
                else if ( actions[i] == "b") {
                    buf += "Baseline";
                }
            }           		
    	}    	
    	return buf;
    }
	
    def isDaily() {
        return periodType == 0 ? true : false;
    }
	
    def isWeekly() {
        return periodType == 1 ? true : false;
    }
	
    def isMonthly() {
        return periodType == 2 ? true : false;
    }

    String toString() {
return """
id[$id]
  genDelta[$genDelta]
  logLevel[$loggingLevel] periodType[$periodType] periodIncrement[$periodIncrement]
  hour[$hour] minute[$minute] offset[$hoursOffset]
  actions[$actions]
  group[$group]""";
    }
    
    /**
     * Returns a string that represents what the task will be doing
     */
    String getTaskIdentifier() {
        def str = group.name;
        str += " runs ";
    	str += "( ${getActionsString()} ) ";
    	switch (periodType) {
            case 0:
            str += "daily";
            break;
            case 1:
            str += "weekly";
            str += " on ${SbDateUtil.dayOfWeek(periodIncrement)}";
            break;
            case 2:
            str += "monthly";
            str += " on the ${SbDateUtil.dayOfMonth(periodIncrement)}";
            break;
            default:
            break;
    	}
    	str += " at ";
        str += SbDateUtil.hoursAndMinutes(hour,minute);
        str += " (Comparison "
        if (genDelta) {
            str += "enabled"
        } else {
            str += "disabled"
        }
        str += ")"
    	return str;
    }

    /**
     * Get a verbose description for the scheduled task
     *
     * @return the verbose description
     */
    String getVerboseDescription() {    	
    	def str = "( ${getActionsString()} ) ";
        str += " runs ";
    	switch (periodType) {
            case 0:
            str += "daily";
            break;
            case 1:
            str += "weekly";
            str += " on ${SbDateUtil.dayOfWeek(periodIncrement)}";
            break;
            case 2:
            str += "monthly";
            str += " on the ${SbDateUtil.dayOfMonth(periodIncrement)}";
            break;
            default:
            break;
    	}
    	str += " at ";
        str += SbDateUtil.hoursAndMinutes(hour,minute);

        str += " (Autocomparison "
        if (genDelta) {
            str += "enabled"
        } else {
            str += "disabled"
        }
        str += ")"

    	return str;
    }

    /**
     * Returns the hours for the task between 1 and 12 based on AM / PM time converted from a 24 hour clock
     *
     * @return
     */
    int getHoursAmPm() {
        if ( hour > 12 ) {
            return hour - 12;
        }
        else if ( hour == 0 ) {
            return 12;
        }
        return hour;
    }

    /**
     * Returns the offset of hours
     * am = 0
     * pm = 12
     *
     * @return
     */
    int getHoursOffset() {
        // if the offset has been set from an external call then return that 
        // value
        // BUG: can't check if ( hoursOffset ) as hoursOffset is allowed to be == 0 however, if( 0 ) is FALSE !!!
        // so instead of 0 use -1 as the default value, and return 0 since it's a valid value passed from UI
        if ( hoursOffset != -1 ) {
            return hoursOffset;
        }

        // otherwise use the hour set in the database :
        // a. AM hours from the DB are [0..11] and their offset is 0 to signify it's AM
        // b. PM hourse are [12..23] (hence hour==12 belongs to the PM hours (so need to use >= below)) and their offset is 12 to signify it's PM
        if ( hour >= 12 ) {
            return 12;
        }
        else {
            return 0;
        }
    }

    /**
     * @param offset
     */
    void setHoursOffset(int offset) {
        hoursOffset = offset;
    }   

    def listClientsForTask() {
        return Client.findByGroup(group).collect {
            it.id
        }
    }
        
    Date getNextFireTime() {
        def trigger
        def now = new Date()
        // assuming here that task setup is *VALID* - ie all numbers within valid ranges.
        if (isDaily())
        {
          trigger = TriggerBuilder
              .newTrigger()
              .withSchedule(CronScheduleBuilder.dailyAtHourAndMinute(hour,minute))
              .build()
        }
        else if (isWeekly())
        {
          trigger = TriggerBuilder
              .newTrigger()
              .withSchedule(CronScheduleBuilder.weeklyOnDayAndHourAndMinute(periodIncrement+1, hour,minute))
              .build()
        }
        else // monthly
        {
          trigger = TriggerBuilder
              .newTrigger()
              .withSchedule(CronScheduleBuilder.monthlyOnDayAndHourAndMinute(periodIncrement, hour,minute))
              .build()
        }
        def fireTime = trigger.getFireTimeAfter(now)
        return fireTime
    }
}
