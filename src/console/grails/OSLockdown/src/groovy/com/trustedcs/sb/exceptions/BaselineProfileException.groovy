/*
 * Original file generated in 2010 by Grails v1.2.1 under the Apache 2 License.
 * Modifications are Copyright 2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.exceptions;

import com.trustedcs.sb.metadata.baseline.BaselineProfile;

/**
 * Runtime exception for baseline profile service transactional stop
 * @author amcgrath@trustedcs.com
 */
class BaselineProfileException extends RuntimeException {

    // message string created with i18n
    String message;
    // object to show errors with
    BaselineProfile baselineProfileInstance;
}


