/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services;

import java.util.List;
import com.trustedcs.sb.services.sei.DispatcherTask;
import com.trustedcs.sb.services.sei.SchedulerResponse;
import com.trustedcs.sb.services.sei.SchedulerService;

import javax.jws.WebParam;
import javax.jws.WebService;
import javax.jws.WebMethod;

@WebService
public class SchedulerServiceImpl implements SchedulerService {
	
	/**
	 * Removes a task from the dispatcher
	 * @param task
	 */
	public SchedulerResponse removeTask(@WebParam(name = "task") DispatcherTask task) {
		return new SchedulerResponse(200,"okay");
	}
	
	/**
	 * Clears all tasks that are on the dispatcher
	 * @return response
	 */
	@WebMethod(operationName = "clearTasks")
	public SchedulerResponse clearTasks() {
		return new SchedulerResponse(200,"okay");
	}
	
	/**
	 * Updates a task on the dispatcher
	 * @param task
	 * @return response
	 */
	public SchedulerResponse updateTask(@WebParam(name = "notificationAddress") String notificationAddress,
										@WebParam(name = "verificationAddress") String verificationAddress,
										@WebParam(name = "task") DispatcherTask task) {
		return new SchedulerResponse(200,"okay");
	}

	/**
	 * Updates a list of tasks on the dispatcher
	 * @param notificationAddress
	 * @param taskList
	 * @return response
	 */
	public SchedulerResponse updateTaskList(@WebParam(name = "notificationAddress") String notificationAddress,
											@WebParam(name = "verificationAddress") String verificationAddress,
											@WebParam(name = "taskList") List<DispatcherTask> taskList) {
		return new SchedulerResponse(200,"okay");
	}
	
	/**
	 * Checks to make sure the client knows its tasks updated tasks.
	 * @param taskList
	 * @return
	 */
	public SchedulerResponse verifyTaskList(@WebParam(name = "notificationAddress") String notificationAddress,
											@WebParam(name = "verificationAddress") String verificationAddress,
											@WebParam(name = "taskList") List<DispatcherTask> taskList ) {
		return new SchedulerResponse(200,"okay");
	}

}
