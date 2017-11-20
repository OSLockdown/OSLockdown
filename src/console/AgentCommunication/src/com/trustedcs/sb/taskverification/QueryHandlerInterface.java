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

public interface QueryHandlerInterface {

    public TaskVerificationResponse query(TaskVerificationQuery query);
}
