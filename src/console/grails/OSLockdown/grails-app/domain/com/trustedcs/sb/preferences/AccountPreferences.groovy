/*
 * Copyright 2014 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.preferences;

class AccountPreferences {

    // Password aging fields 
    Boolean agingEnabled = false;
    Boolean agingEnabledForAdmin = false;
    Integer minDaysBetweenChanges = 0;    // minimum number of days between changes
    Integer maxDaysBetweenChanges = 60;   // maximum number of days between changes
    Integer numWarningDays = 7;           // number of days before the password must be changed to start telling the user
    Integer maxReuse = 3;                 // number of passwords to 'remember' and to prevent reuse of
 
    // Complexity fields - legacy is 6 characters, 1 upper, 1 number
    Boolean complexityEnabled = true;
    Boolean complexityEnabledForAdmin = true;
    Integer minimumLower = 0;
    Integer minimumUpper = 1;
    Integer minimumNumber = 1;
    Integer minimumSpecial = 0;
    Integer minimumLength = 6;
     
    // When was the last time we changed....
    Date lastChanged=new Date();

    static constraints = {
        lastChanged(nullable: true, blank: true);
        agingEnabled(nullable:true)
        agingEnabledForAdmin(nullable:true)
        minDaysBetweenChanges(nullable:true, range:0..60)
        maxDaysBetweenChanges(nullable:true, range:0..365)
        numWarningDays(nullable:true, range:0..60)
        maxReuse(nullable:true,range:0..24)
        complexityEnabled(nullable:true)
        complexityEnabledForAdmin(nullable:true)
        minimumLower(nullable:true, range:0..5)
        minimumUpper(nullable:true, range:0..5)
        minimumNumber(nullable:true, range:0..5)
        minimumSpecial(nullable:true, range:0..5)
        minimumLength(nullable:true, range:0..50)
        
        // enforce following relation ship between min/warn/max Days:
        //   numWarningDays < maxDaysBetweenChanges
        //   minDaysBetweenChanges < maxDaysBetweenChanges - numWarningDays
        //   minDaysBetweenChanges < maxDaysBetweenChanges

        minDaysBetweenChanges(validator: {val, obj, errors ->
             if ((obj.minDaysBetweenChanges > 0) &&  (obj.maxDaysBetweenChanges > 0 ) && (obj.minDaysBetweenChanges  >= obj.maxDaysBetweenChanges))
             {
             	 errors.rejectValue("minDaysBetweenChanges", "accountPreferences.minDaysBeforeChange.must.be.less.than.maxDaysBeforeChange")
             }
        })
        numWarningDays(validator: {val, obj, errors ->
             if (obj.numWarningDays != 0 && obj.maxDaysBetweenChanges != 0) {
               if (obj.numWarningDays >= obj.maxDaysBetweenChanges) errors.rejectValue("numWarningDays", "accountPreferences.numWarningDays.must.be.less.than.maxDaysBeforeChange")
               if ((obj.minDaysBetweenChanges !=0) && (obj.minDaysBetweenChanges >= (obj.maxDaysBetweenChanges- obj.numWarningDays)))
               {
                   errors.rejectValue("numWarningDays", "accountPreferences.show.warning.only.after.minDaysBeforeChange")
               }
             }
        })
        
    }
    static mapping = {
        autoTimestamp false
    }
    String toString()
    {
      return "id [$id] agingEnabled[$agingEnabled] agingEnabledForAdmin[$agingEnabledForAdmin] minDaysBetweenChanges[$minDaysBetweenChanges] maxDaysBetweenChanges[$maxDaysBetweenChanges] numWarningDays[$numWarningDays] complexityEnabled[$complexityEnabled] complexityEnabledForAdmin[$complexityEnabledForAdmin] minimumLower[$minimumLower] minimumUpper[$minimumUpper] minimumNumber[$minimumNumber] minimumSpecial[$minimumSpecial] minimumLength[$minimumLength]"
      
    }
    def checkMinWarnMaxDays()
    {
      println "${minDaysBetweenChanges}, ${numWarningDays}, ${maxDaysBetweenChanges}"
      return 0;
    }
}
