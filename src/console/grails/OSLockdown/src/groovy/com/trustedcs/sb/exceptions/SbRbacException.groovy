/*
 * Copyright 2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.exceptions;

import com.trustedcs.sb.auth.shiro.ShiroUser;
import com.trustedcs.sb.auth.shiro.ShiroRole;
import com.trustedcs.sb.auth.shiro.ShiroUserRoleRel;

/**
 *
 * @author amcgrath@trustedcs.com
 */
class SbRbacException extends RuntimeException {
    String message;
    ShiroUser shiroUser;
    ShiroRole shiroRole;
    ShiroUserRoleRel shiroRelationship;
}

