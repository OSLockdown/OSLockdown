/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.taskverification;

import com.trustedcs.sb.services.sei.TaskVerificationQuery;
import com.trustedcs.sb.services.sei.TaskVerificationResponse;

public class TaskVerificationEngine {
	
	// the singleton instance
	static TaskVerificationEngine m_instance= null;
	
	private QueryHandlerInterface m_handler = null;
	
	/**
	 * Private Constructor for the singleton instance
	 */
	private TaskVerificationEngine() {
		
	}
	
	/**
	 * Singleton get method
	 * @return the singleton instance
	 */
	public static TaskVerificationEngine getInstance() {
		if ( m_instance == null ) {
			m_instance = new TaskVerificationEngine();
		}
		return m_instance;
	}
	
	public TaskVerificationResponse query(TaskVerificationQuery query) {
		if ( m_handler == null ) {
			TaskVerificationResponse response = new TaskVerificationResponse();
			response.setCode(200);
			response.setReasonPhrase("Okay");
			response.setQueryResultCode(1);
			response.setQueryResultInfo("Query Handler not set. License could be invalid.");
			return response;
		}
		return m_handler.query(query);		
	}
	
	public void setQueryHandler(QueryHandlerInterface handler) {
		m_handler = handler;
	}
}
