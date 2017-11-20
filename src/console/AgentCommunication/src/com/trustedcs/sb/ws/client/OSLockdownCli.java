/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.ws.client;

public class OSLockdownCli extends OSLockdownCommunicator {

	public void connect() {
		System.out.println("Connection Stub");
	}

	public void execute() {
		System.out.println("Execution stub");
	}

	/**
	 * @param args
	 */
	public static void main(String[] argv) {
		try {
			OSLockdownCli cli = new OSLockdownCli();
			cli.configure(argv);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

}
