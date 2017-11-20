/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

import java.util.List;

public interface SchedulerService {	
	
	/**
	 * Removes a task from the dispatcher
	 * @param task
	 */
	public SchedulerResponse removeTask(DispatcherTask task);
	
	/**
	 * Clears all tasks that are on the dispatcher
	 * @return response
	 */
	public SchedulerResponse clearTasks();
	
	/**
	 * Updates a task on the dispatcher
	 * @param task
	 * @return response
	 */
	public SchedulerResponse updateTask(String notificationAddress, String verificationAddress, DispatcherTask task);
	
	/**
	 * Updates a list of tasks on the dispatcher
	 * @param notificationAddress
	 * @param taskList
	 * @return
	 */
	public SchedulerResponse updateTaskList(String notificationAddress, String verificationAddress, List<DispatcherTask> taskList);
	
	/**
	 * Checks to make sure the client knows its tasks updated tasks.
	 * @param taskList
	 * @return
	 */
	public SchedulerResponse verifyTaskList(String notificationAddress, String verificationAddress, List<DispatcherTask> taskList );
}
