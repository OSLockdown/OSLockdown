/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.ws.client;

import com.trustedcs.sb.services.client.console.ConsoleNotification;
import com.trustedcs.sb.services.client.console.ConsoleResponse;
import com.trustedcs.sb.services.client.console.ConsoleServiceImpl;
import com.trustedcs.sb.services.client.console.ConsoleServiceImplService;

import java.io.File;

public class ConsoleCommunicator extends OSLockdownCommunicator {

	private ConsoleServiceImpl m_service;

	private static final String INFO = "info";
	private static final String NOTIFY = "notify";
	private static final String STATUS = "status";

	public ConsoleCommunicator() {
		super(OSLockdownCommunicationType.CONSOLE);
	}

	public ConsoleCommunicator(String address, int port) {
		super(address, port, OSLockdownCommunicationType.CONSOLE);
	}
	
	/**
	 * Creates the http url for the webservice
	 * http://192.168.1.171:8080/OSLockdown/services/console
	 * 
	 * @return the created url depending on communication type
	 */
	protected String createEndpointAddress() {
		StringBuffer buf = new StringBuffer();
		buf.append("http://");
		buf.append(getAddress());
		buf.append(":");
		buf.append(getPort());
		buf.append("/OSLockdown/services/");
		buf.append(OSLockdownCommunicationType.CONSOLE.getUrlString());
		return buf.toString();
	}

	public void connect() {
		m_service = new ConsoleServiceImplService().getConsoleServiceImplPort();
		((javax.xml.ws.BindingProvider) m_service).getRequestContext().put(
				javax.xml.ws.BindingProvider.ENDPOINT_ADDRESS_PROPERTY,
				createEndpointAddress());
	}
	
	public void execute() {
		System.out.println("connecting to:"+createEndpointAddress());
		ConsoleResponse response = null;		
		if ( getCommandOptions().length < 3 ) {
			System.out.println( "console notification requires three options 'type <int> info <string> body <string>");
			return;
		}
		
		// create the notification
		ConsoleNotification notification = new ConsoleNotification();
		notification.setType(Integer.parseInt(getCommandOptions()[0]));
		notification.setTransactionId(generateTransactionId());
		notification.setInfo(getCommandOptions()[1]);
		try {			
			String fileName = getCommandOptions()[2];
			System.out.println(fileName);
			File file = new File(fileName);
			if ( !file.exists() ) {
				System.out.println("file: "+file.getAbsolutePath() + "does not exist");
			}
			else {
				notification.setBody(getContentsAsString(file));
			}
		}
		catch (Exception e ) {
			e.printStackTrace();
		}
		
		System.out.println("BODY");
		System.out.println(notification.getBody());
		
		// find the correct method
		if (getCommand().equalsIgnoreCase(NOTIFY)) {
			response = notify(notification);
		} else if (getCommand().equalsIgnoreCase(INFO)) {
			response = reportInfo(notification);
		} else if (getCommand().equalsIgnoreCase(STATUS)) {
			response = reportInfo(notification);
		} else {
			StringBuffer buf = new StringBuffer();
			buf.append("command does not match list of possible commands ");
			buf.append("[");
			buf.append(NOTIFY);
			buf.append("|");
			buf.append(INFO);
			buf.append("|");
			buf.append(STATUS);
			buf.append("]");
			System.out.println(buf.toString());
			return;
		}

		System.out.println("Response: " + response);
		System.out.println("Code: " + response.getCode());
		System.out.println("Reason: " + response.getReasonPhrase());
	}

	public static void main(String argv[]) {

		try {
			// create wrapper
			ConsoleCommunicator proxyWrapper = new ConsoleCommunicator();

			// configure wrapper
			proxyWrapper.configure(argv);

			// execute methods specified on the command line
			proxyWrapper.execute();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}

	/**
	 * 
	 * @param notification
	 * @return
	 */
	public ConsoleResponse notify(ConsoleNotification notification) {
		if ( !m_connected ) {
			connect();
		}
		return m_service.notify(notification);
	}

	/**
	 * 
	 * @param notification
	 * @return
	 */
	public ConsoleResponse reportInfo(ConsoleNotification notification) {
		if ( !m_connected ) {
			connect();
		}
		return m_service.reportInfo(notification);
	}

	/**
	 * 
	 * @param notification
	 * @return
	 */
	public ConsoleResponse reportStatus(ConsoleNotification notification) {
		if ( !m_connected ) {
			connect();
		}
		return m_service.reportStatus(notification);
	}
}
