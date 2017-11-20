/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services;

import com.trustedcs.sb.services.sei.ReportsResponse;
import com.trustedcs.sb.services.sei.ReportsService;

import javax.jws.WebParam;
import javax.jws.WebService;

@WebService
public class ReportsServiceImpl implements ReportsService {	
	
	/**
	 * Returns the sb appo log
	 * @return the audit log as a string 
	 */
	public ReportsResponse getSbAppLog() {
		return new ReportsResponse(200,"get sb app log");
	}
	
	/**
	 * Returns the list of baselines
	 * @return the list of baselines available
	 */
	public ReportsResponse getBaselineList() {
		return new ReportsResponse(200,"list baselines");
	}
	
	/**
	 * Returns the baseline for the given name
	 * @return the baseline
	 */
	public ReportsResponse getBaseline(@WebParam(name = "fileName") String name) {
		return new ReportsResponse(200,"get baseline");
	}
	
	/**
	 * Returns the list of assessment reports
	 * @return the list of assessment reports
	 */
	public ReportsResponse getAssessmentList() {
		return new ReportsResponse(200,"get assessments");
	}

	/**
	 * Returns the assessment for the given name
	 * @return the assessment
	 */
	public ReportsResponse getAssessment(@WebParam(name = "fileName") String name) {
		return new ReportsResponse(200,"get assessment");
	}

	/**
	 * Returns the list of apply reports
	 * @return the list of apply reports
	 */
        public ReportsResponse getApplyList() {
                return new ReportsResponse(200,"get applies");
        }

	/**
	 * Returns the apply for the given name
	 * @return the apply
         */
        public ReportsResponse getApply(@WebParam(name = "fileName") String name) {
		return new ReportsResponse(200,"get apply");
        }

	/**
	 * Returns the list of undo reports
	 * @return the list of undo reports
	 */
        public ReportsResponse getUndoList() {
                return new ReportsResponse(200,"get undos");
        }

	/**
	 * Returns the undo for the given name
	 * @return the undo
         */
        public ReportsResponse getUndo(@WebParam(name = "fileName") String name) {
		return new ReportsResponse(200,"get undo");
        }
}
