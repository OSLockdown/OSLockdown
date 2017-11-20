/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.ws.client;

import java.net.URL;
import java.util.List;
import java.net.UnknownHostException;
import java.net.NoRouteToHostException;
import java.net.ConnectException;

import org.apache.log4j.BasicConfigurator;
import org.apache.log4j.Logger;

import com.sun.xml.ws.client.ClientTransportException;
import javax.xml.ws.WebServiceException;

import com.trustedcs.sb.services.client.taskverification.TaskVerificationQuery;
import com.trustedcs.sb.services.client.taskverification.TaskVerificationResponse;
import com.trustedcs.sb.services.client.taskverification.TaskVerificationServiceImpl;
import com.trustedcs.sb.services.client.taskverification.TaskVerificationServiceImplService;

public class TaskVerificationCommunicator extends OSLockdownCommunicator {

    // logger
    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.ws.client.TaskVerificationCommunicator");
    // web service
    private TaskVerificationServiceImpl m_service;
    // verification operation
    private static final String VERIFY = "verify";

    /**
     * Empty Constructor
     */
    public TaskVerificationCommunicator() {
        super(OSLockdownCommunicationType.TASK_VERIFICATION);
    }

    /**
     * Construct the communicator to the address and port specified
     *
     * @param address
     * @param port
     */
    public TaskVerificationCommunicator(String address, int port) {
        super(address, port, OSLockdownCommunicationType.TASK_VERIFICATION);
    }

    /**
     * Construct the communication with the given information
     *
     * @param clientId
     * @param address
     * @param port
     * @param secureConnection
     */
    public TaskVerificationCommunicator(long clientId, String address, int port, boolean secureConnection) {
        super(clientId, address, port, OSLockdownCommunicationType.TASK_VERIFICATION, secureConnection);
    }

    /** 
     *  If we're an IPv6 numberical address, ensure we are wrapped in '[]'
     */
    protected String wrapAddrIfIPv6(String address) {
        
        if (address != null && !address.isEmpty()) {
        
            // Check if string contains at least one colon, starts with [ and ends with ]
            if (address.contains(":")) 
            {
                if (!address.startsWith("[")) {
                    address = "[" + address;
                }
                if (!address.endsWith("]")) {
                    address = address + "]";
                }
            }        
        }
        return address;
    }

    /**
     * Creates the http url for the webservice
     * http://192.168.1.171:8080/OSLockdown/services/taskverification
     *
     * @return the created url depending on communication type
     */
    protected String createEndpointAddress() {
        StringBuffer buf = new StringBuffer();
		if (m_secure) {
			buf.append("https://");
		} else {
			buf.append("http://");
		}
//        buf.append("http://");
        
        buf.append(wrapAddrIfIPv6(getAddress()));
        buf.append(":");
        buf.append(getPort());
        buf.append("/OSLockdown/services/");
        buf.append(OSLockdownCommunicationType.TASK_VERIFICATION.getUrlString());
        return buf.toString();
    }

    /**
     * Connect the web service client to the web service
     */
    public void connect() {
        // set the url for the location of the wsdl
        URL wsdlUrl = null;
        try {
            wsdlUrl = new URL("file:/usr/share/oslockdown/cfg/wsdl/TaskVerificationServiceImplService.wsdl");
        } catch (Exception e) {
            m_log.error("unable to locate wsdl url: " + wsdlUrl, e);
            return;
        }

        m_service = new TaskVerificationServiceImplService(wsdlUrl).getTaskVerificationServiceImplPort();
        ((javax.xml.ws.BindingProvider) m_service).getRequestContext().put(
                javax.xml.ws.BindingProvider.ENDPOINT_ADDRESS_PROPERTY,
                createEndpointAddress());
        ((javax.xml.ws.BindingProvider) m_service).getRequestContext().put(
                "com.sun.xml.internal.ws.connect.timeout", 5000);
        ((javax.xml.ws.BindingProvider) m_service).getRequestContext().put(
                "com.sun.xml.internal.ws.request.timeout", 5000);
        ((javax.xml.ws.BindingProvider) m_service).getRequestContext().put(
                "com.sun.xml.ws.connect.timeout", 5000);
        ((javax.xml.ws.BindingProvider) m_service).getRequestContext().put(
                "com.sun.xml.ws.request.timeout", 5000);
        m_connected = true;
    }

    @Override
    public void execute() {
        TaskVerificationResponse response = null;

        if (getCommand().equalsIgnoreCase(VERIFY)) {
            // option[0] id "${task.id}:${client.id}:${group.id}"
            // option[0] profile fingerprint
            TaskVerificationQuery query = new TaskVerificationQuery();
            query.setId(getCommandOptions()[0]);
            query.setSecurityProfileFingerprint(getCommandOptions()[1]);
            query.setBaselineProfileFingerprint(getCommandOptions()[2]);
            System.out.println("Id : " + query.getId());
            System.out.println("Security Fingerprint : " + query.getSecurityProfileFingerprint());
            System.out.println("Baseline Fingerprint : " + query.getBaselineProfileFingerprint());
            response = verify(query);
        } else {
            StringBuffer buf = new StringBuffer();
            buf.append("command does not match list of possible commands ");
            buf.append("[");
            buf.append(VERIFY);
            buf.append("]");
            System.out.println(buf.toString());
            return;
        }

        if (response != null) {
            System.out.println("Response: " + response);
            System.out.println("Code: " + response.getCode());
            System.out.println("Reason: " + response.getReasonPhrase());
            System.out.println("Query Result Code : " + response.getQueryResultCode());
            System.out.println("Query Result Info : " + response.getQueryResultInfo());
            System.out.println("DispatcherTask : " + response.getTask());
            System.out.println("Security Profile : \n" + response.getTask().getSecurityProfile());
            System.out.println("Baseline Profile : \n" + response.getTask().getBaselineProfile());
        } else {
            System.out.println("Response was null");
        }

    }

    public static void main(String argv[]) {

        try {
            // log4j setup
            BasicConfigurator.configure();

            // create wrapper
            TaskVerificationCommunicator proxyWrapper = new TaskVerificationCommunicator();

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
     * @param fileName
     * @return
     */
    public TaskVerificationResponse verify(TaskVerificationQuery query) {
        TaskVerificationResponse response = null;
        try {
            if (!m_connected) {
                connect();
            }
            response = m_service.verifyTask(query);
        } catch (ClientTransportException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[verify] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
        } catch (WebServiceException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[verify] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
        } catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
            m_log.error("[verify] failed : ", e);
        }
        return response;
    }

    /**
     * Creates the error response for the Communicator
     * @param code
     * @param reason
     * @param t
     * @return
     */
/*
    private TaskVerificationResponse createErrorResponse(int code, String reason, Throwable t) {
        TaskVerificationResponse response = new TaskVerificationResponse();
        response.setCode(code);
        if (t != null && t.getMessage() != null && !t.getMessage().equals("")) {
            response.setReasonPhrase(reason + " : " + t.getMessage());
        } else {
            response.setReasonPhrase(reason);
        }
        return response;
    }
*/
    private TaskVerificationResponse createErrorResponse(int code, String reason, Throwable t) {
        TaskVerificationResponse response = new TaskVerificationResponse();
        response.setCode(code);

        if (t != null && t.getMessage() != null && !t.getMessage().equals("")) {

            if (t.getCause() instanceof UnknownHostException) {
                response.setReasonPhrase(reason
                        + " : Unable to resolve the destination name. Check /etc/hosts file or DNS entries.");
            } else if (t.getCause() instanceof NoRouteToHostException) {
                response.setReasonPhrase(reason
                        + " : Unable to connect to the destination address. Check to see if "
                        + "a network firewall is blocking access or if there are network problems.");
            } else if (t.getCause() instanceof ConnectException) {
                response.setReasonPhrase(reason
                        + " : Connection refused by client. Check to see if client's dispatcher is "
                        + "running, verify its TCP port, and no host-based firewall is blocking access.");
            } else {
                response.setReasonPhrase(reason + " : " + t.getMessage());
            }

        } else {
            response.setReasonPhrase(reason);

        }
        return response;

    }


}
