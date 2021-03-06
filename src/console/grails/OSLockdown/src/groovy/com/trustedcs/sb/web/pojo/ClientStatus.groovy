/*
 * Copyright 2009 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.web.pojo

enum ClientStatus {
	
	OK("OK"),
	UNRESPONSIVE("Unresponsive"),
	BUSY("Busy")
	
	private String name
	ClientStatus(String name) {
		this.name = name
	}
	
	String getName() {
		return this.name
	}
}
