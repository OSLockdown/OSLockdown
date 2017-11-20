/*
 * Copyright 2014 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.exceptions;

import com.trustedcs.sb.preferences.AccountPreferences;

/**
 *
 * @author kloyevsky
 */
class AccountPreferencesException extends RuntimeException {
    AccountPreferences accountPreferences;
}

