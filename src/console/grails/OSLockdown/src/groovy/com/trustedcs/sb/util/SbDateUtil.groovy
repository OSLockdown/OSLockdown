/*
 * Copyright 2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.util;

import org.apache.log4j.Logger;

/**
 *
 * @author amcgrath@trustedcs.com
 */
class SbDateUtil {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.util.SbDateUtil");

    public static final Map<Integer,String> daysOfTheWeekMap = [0:"Sunday",1:"Monday",2:"Tuesday",3:"Wednesday",4:"Thursday",5:"Friday",6:"Saturday"]
    public static def hoursMap = [:];
    public static def minutesMap = [:];
    public static def daysOfTheMonthRange = 1..31;

    static {
        // hours
    	(1..23).each { hour ->
            hoursMap[hour] = hour < 10 ? "0" + hour : hour;
    	}
        // minutes
    	(0..59).each { minute ->
            minutesMap[minute] = minute < 10 ? "0" + minute : minute;
    	}
    }


    /**
     * Returns a string representation using the day of the month
     *
     * @param day
     */
    public static String dayOfMonth(def day) {
        // output string
        String output = "${day}";

        // get the last digit since its most often used to figure out
        // tense of days
        int lastDigit = day % 10;

        // 10th -> 19th
        if ( day >= 10 && day <= 19 ) {
            output += "th";
        }
        else {
            switch( lastDigit ) {
                case 1:
                output += "st"
                break;
                case 2:
                output += "nd"
                break;
                case 3:
                if ( day != 13 ) {
                    output += "rd"
                    break;
                }
                default:
                output += "th"
                break;
            }
        }
        return output;
    }

    /**
     * Returns the string representation of the day of the week
     * 0 : Sunday
     * 6 : Saturday
     *
     * @param day
     */
    public static String dayOfWeek(def day) {        
        String resultingDayOfWeek = daysOfTheWeekMap[ day ];
        if( !resultingDayOfWeek ){
            resultingDayOfWeek = "Unknown";
        }
        return resultingDayOfWeek;
    }

    /**
     * Returns the hours and minutes in a formatted string
     *
     * @param hours
     * @param minutes
     */
    public static String hoursAndMinutes(def hours, def minutes) {
        def output = "";
        if ( hours > 12 ) {
            output +=  hours - 12;
        }
        else if ( hours == 0 ) {
            output +=  12;
        }
        else {
            output += hours;
        }
        output += ":"
    	output += minutes < 10 ? "0${minutes}" : minutes;
        output += hours > 11 ? "pm" : "am";
        return output;
    }
}
