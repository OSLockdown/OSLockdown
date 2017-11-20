/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

public interface TaskVerificationService {

    /**
     * Querys the service to find out if a task is up to date.
     * @param query
     * @return
     */
    public TaskVerificationResponse verifyTask(TaskVerificationQuery query);
}
