/*
 * Copyright 2009-2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * 
 */
package com.trustedcs.sb.reports.groupassessment;

/**
 * @author amcgrath
 *
 */
public class GroupAssessmentTransaction {
    String id;
    boolean terminatedState;
    boolean successful;
    String info;
	
    public Long getClientId() {
        return id.tokenize(":")[0].toLong();
    }
	
    public String toString() {
        return "id[${id}] finalState[${terminatedState}] success[${successful}] info[${info}]";
    }
}
