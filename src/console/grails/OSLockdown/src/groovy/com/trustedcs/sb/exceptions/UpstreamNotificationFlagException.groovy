/*
 *Copyright 2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.exceptions;

import com.trustedcs.sb.preferences.UpstreamNotificationFlag;

/**
 *
 * @author rsanders
 */
class UpstreamNotificationFlagException extends RuntimeException {
    UpstreamNotificationFlag upstreamNotificationFlag;
}

