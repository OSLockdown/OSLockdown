/*
 * Copyright 2009 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.reports.util;

public class DiffDelta {
	 def older;
	 def newer;
	 
	 public DiffDelta() {
		 
	 }
	 
	 public DiffDelta(def o, def n) {
		 older = o;
		 newer = n;
	 }
}
