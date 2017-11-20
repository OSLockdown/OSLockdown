/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

public interface ReportsService {	
	
	/**
	 * Returns the sb log 
	 * @return the sb log a
	 */
	ReportsResponse getSbAppLog();
	
	/**
	 * Returns the list of baselines
	 * @return the list of baselines available
	 */
	ReportsResponse getBaselineList();
	
	/**
	 * Returns the baseline for the given name
	 * @return the baseline
	 */
	ReportsResponse getBaseline(String name);
	
	/**
	 * Returns the list of assessment reports
	 * @return the list of assessment reports
	 */
	ReportsResponse getAssessmentList();
	
	/**
	 * Returns the assessment for the given name
	 * @return the assessment
	 */
	ReportsResponse getAssessment(String name);

	/**
	 * Returns the list of apply reports
	 * @return the list of apply reports
	 */
	ReportsResponse getApplyList();

	/**
	 * Returns the apply for the given name
	 * @return the apply
	 */
	ReportsResponse getApply(String name);

	/**
	 * Returns the list of undo reports
	 * @return the list of undo reports
	 */
	ReportsResponse getUndoList();

	/**
	 * Returns the undo for the given name
	 * @return the undo
	 */
	ReportsResponse getUndo(String name);
}
