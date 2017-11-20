/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.ws.client;

import com.trustedcs.sb.services.client.clientregistration.ClientRegistrationResponse;
import com.trustedcs.sb.services.client.clientregistration.ClientRegistrationServiceImpl;
import com.trustedcs.sb.services.client.clientregistration.ClientRegistrationServiceImplService;

import java.io.File;

public class ClientRegistrationCommunicator extends OSLockdownCommunicator {

	private ClientRegistrationServiceImpl m_service;

	private static final String REGISTER = "register";

	public ClientRegistrationCommunicator() {
		super(OSLockdownCommunicationType.CLIENT_REGISTRATION);
	}

	public ClientRegistrationCommunicator(String address, int port) {
		super(address, port, OSLockdownCommunicationType.CLIENT_REGISTRATION);
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
		buf.append(OSLockdownCommunicationType.CLIENT_REGISTRATION.getUrlString());
		return buf.toString();
	}

	public void connect() {
		m_service = new ClientRegistrationServiceImplService().getClientRegistrationServiceImplPort();
		((javax.xml.ws.BindingProvider) m_service).getRequestContext().put(
				javax.xml.ws.BindingProvider.ENDPOINT_ADDRESS_PROPERTY,
				createEndpointAddress());
	}
	
	public void execute() {
		System.out.println("connecting to:"+createEndpointAddress());
		ClientRegistrationResponse response = null;		
		if ( getCommandOptions().length < 3 ) {
			System.out.println( "console notification requires three options 'name <String> hostname <String> port <int> location[string] contact[string]");
			return;
		}
		
		
		// find the correct method
		if (getCommand().equalsIgnoreCase(REGISTER)) {			
			String optionalCert="";
			if ( getCommandOptions().length > 5) {
				optionalCert=getCommandOptions()[5];
			}
			response =
register(getCommandOptions()[0],getCommandOptions()[1],Integer.parseInt(getCommandOptions()[2]),getCommandOptions()[3],getCommandOptions()[4],getCommandOptions()[5],optionalCert);	
		} 
		else {
			StringBuffer buf = new StringBuffer();
			buf.append("command does not match list of possible commands ");
			buf.append("[");
			buf.append(REGISTER);
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
			ClientRegistrationCommunicator proxyWrapper = new ClientRegistrationCommunicator();

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
	public ClientRegistrationResponse register(String name, String hostName, int port, String location, String contact, String procinfo, String clientCertificate) {
		if ( !m_connected ) {
			connect();
		}
		return m_service.registerClient(name,hostName,port,location,contact,procinfo,clientCertificate);
	}


}
