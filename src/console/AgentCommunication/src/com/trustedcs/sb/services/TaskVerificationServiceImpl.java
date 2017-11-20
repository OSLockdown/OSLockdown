/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services;

import javax.jws.WebParam;
import javax.jws.WebService;

import com.trustedcs.sb.services.sei.TaskVerificationQuery;
import com.trustedcs.sb.services.sei.TaskVerificationResponse;
import com.trustedcs.sb.services.sei.TaskVerificationService;
import com.trustedcs.sb.taskverification.TaskVerificationEngine;

@WebService
public class TaskVerificationServiceImpl implements TaskVerificationService {

    /**
     * Returns if a task is up to date and if it still is valid
     * @param query
     */
    public TaskVerificationResponse verifyTask(@WebParam(name = "query") TaskVerificationQuery query) {
        return TaskVerificationEngine.getInstance().query(query);
    }
}
