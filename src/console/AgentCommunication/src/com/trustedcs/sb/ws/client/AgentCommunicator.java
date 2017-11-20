/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.ws.client;

import com.trustedcs.sb.services.client.agent.AgentResponse;
import com.trustedcs.sb.services.client.agent.AgentServiceImpl;
import com.trustedcs.sb.services.client.agent.AgentServiceImplService;

// imports for custom header
import javax.xml.namespace.QName;
import com.sun.xml.ws.developer.WSBindingProvider;
import com.sun.xml.ws.api.message.Header;
import com.sun.xml.ws.api.message.Headers;
import javax.xml.ws.soap.SOAPFaultException;

import com.sun.xml.ws.client.ClientTransportException;
import javax.xml.ws.WebServiceException;

import org.apache.log4j.Logger;
import org.apache.log4j.BasicConfigurator;

import java.util.ArrayList;
import java.util.List;

import java.net.URL;
import java.net.UnknownHostException;
import java.net.NoRouteToHostException;
import java.net.ConnectException;
import java.util.Collections;
public class AgentCommunicator extends OSLockdownCommunicator {

    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.ws.client.AgentCommunicator");
    
    // This was initially equivalent to the type of the license, but really should be tied to the type of *Client*, hence the renaming
    // of the enum values
    public enum ProductType {

        STANDALONE_CLIENT, ENTERPRISE_CLIENT, BULK_CLIENT, POOLED_CLIENT;
    }

    public enum AgentAction {

        SCAN("Scan", true), QUICK_SCAN("Quick-Scan", true), APPLY("Apply", true), UNDO("Undo", true), BASELINE(
                "Baseline", true), INFO("Info", false), AUTOUPDATE("AutoUpdate", false);

        AgentAction(String display, boolean needsProfile) {
            displayString = display;
            requiresProfile = needsProfile;
        }

        private String displayString;
        private boolean requiresProfile;

        public String getDisplayString() {
            return displayString;
        }

        public boolean getRequiresProfile() {
            return requiresProfile;
        }

        public static List<String> displayList() {
            ArrayList<String> list = new ArrayList<String>();
            for (AgentAction action : AgentAction.values()) {
                list.add(action.getDisplayString());
            }
            return list;
        }

        public static AgentAction createEnum(String enumString) {
            if (enumString.equals(AgentAction.SCAN.getDisplayString())) {
                return AgentAction.SCAN;
            } else if (enumString.equals(AgentAction.QUICK_SCAN.getDisplayString())) {
                return AgentAction.QUICK_SCAN;
            } else if (enumString.equals(AgentAction.APPLY.getDisplayString())) {
                return AgentAction.APPLY;
            } else if (enumString.equals(AgentAction.UNDO.getDisplayString())) {
                return AgentAction.UNDO;
            } else if (enumString.equals(AgentAction.BASELINE.getDisplayString())) {
                return AgentAction.BASELINE;
            } else if (enumString.equals(AgentAction.INFO.getDisplayString())) {
                return AgentAction.INFO;
            } else if (enumString.equals(AgentAction.AUTOUPDATE.getDisplayString())) {
                return AgentAction.AUTOUPDATE;
            }
            return null;
        }
    }

    private AgentServiceImpl m_service;
    private static final String APPLY = "apply";
    private static final String BASELINE = "baseline";
    private static final String INFO = "info";
    private static final String SCAN = "scan";
    private static final String STATUS = "status";
    private static final String PING = "ping";
    private static final String UNDO = "undo";
    private static final String AUTOUPDATE = "autoupdate";
    private int m_productType = 1;  // ClientType.CLIENT_ENTERPRISE enum value would be ordinal 1
    
    public AgentCommunicator() {
        super(OSLockdownCommunicationType.AGENT);
    }

    public AgentCommunicator(String address, int port) {
        super(address, port, OSLockdownCommunicationType.AGENT);
    }

    public AgentCommunicator(long clientId, String address, int port) {
        super(clientId, address, port, OSLockdownCommunicationType.AGENT);
    }

    public AgentCommunicator(long clientId, String address, int port, boolean secureConnection) {
        super(clientId, address, port, OSLockdownCommunicationType.AGENT, secureConnection);
    }

    public void connect() {
        // set the url for the location of the wsdl
        URL wsdlUrl = null;
        try {
            wsdlUrl = new URL(
                    "file:/usr/share/oslockdown/cfg/wsdl/AgentServiceImplService.wsdl");
        } catch (Exception e) {
            m_log.error("unable to locate wsdl url: " + wsdlUrl, e);
            return;
        }

        // get the service port
        m_service = new AgentServiceImplService(wsdlUrl).getAgentServiceImplPort();

        // set the client endpoint
        ((javax.xml.ws.BindingProvider) m_service).getRequestContext().put(
                javax.xml.ws.BindingProvider.ENDPOINT_ADDRESS_PROPERTY, createEndpointAddress());
        ((javax.xml.ws.BindingProvider) m_service).getRequestContext().put(
                "com.sun.xml.internal.ws.connect.timeout", 5000);
        ((javax.xml.ws.BindingProvider) m_service).getRequestContext().put(
                "com.sun.xml.internal.ws.request.timeout", 5000);
        ((javax.xml.ws.BindingProvider) m_service).getRequestContext().put(
                "com.sun.xml.ws.connect.timeout", 5000);
        ((javax.xml.ws.BindingProvider) m_service).getRequestContext().put(
                "com.sun.xml.ws.request.timeout", 5000);

        // custom header ???
        /*
         * ((WSBindingProvider)m_service).setOutboundHeaders( Headers.create(new
         * QName("simpleHeader"),"stringValue"));
         */
        m_connected = true;
    }

    public void execute() {
        System.out.println("connecting to:" + createEndpointAddress());
        AgentResponse response = null;
        if (getCommand().equalsIgnoreCase(APPLY)) {
            response = apply(getCommandOptions()[0], Collections.<String>emptyList(),getLoggingLevel());
        } else if (getCommand().equalsIgnoreCase(BASELINE)) {
            response = baseline("", Collections.<String>emptyList(), getLoggingLevel());
        } else if (getCommand().equalsIgnoreCase(INFO)) {
            response = info();
        } else if (getCommand().equalsIgnoreCase(SCAN)) {
            response = scan(getCommandOptions()[0], Collections.<String>emptyList(), getLoggingLevel());
        } else if (getCommand().equalsIgnoreCase(STATUS)) {
            response = status();
        } else if (getCommand().equalsIgnoreCase(PING)) {
            response = ping();
        } else if (getCommand().equalsIgnoreCase(UNDO)) {
            response = undo(getCommandOptions()[0], Collections.<String>emptyList(), getLoggingLevel());
        } else if (getCommand().equalsIgnoreCase(AUTOUPDATE)) {
            boolean forceFlag = false;
            byte [] updater = new byte [] {} ;
            response = updateAgent(getCommandOptions()[0], updater, forceFlag,
                    getLoggingLevel());
        } else {
            StringBuffer buf = new StringBuffer();
            buf.append("command does not match list of possible commands ");
            buf.append("[");
            buf.append(APPLY);
            buf.append("|");
            buf.append(BASELINE);
            buf.append("|");
            buf.append(INFO);
            buf.append("|");
            buf.append(SCAN);
            buf.append("|");
            buf.append(STATUS);
            buf.append("|");
            buf.append(PING);
            buf.append("|");
            buf.append(UNDO);
            buf.append("|");
            buf.append(AUTOUPDATE);
            buf.append("]");
            System.out.println(buf.toString());
            return;
        }

        System.out.println("Response: " + response);
        System.out.println("Code: " + response.getCode());
        System.out.println("Reason: " + response.getReasonPhrase());
        System.out.println("Body: " + response.getBody());
    }

    public void setProductType(int type) {
        m_productType = type;
    }

    public int getProductType() {
        return m_productType;
    }

    /**
     * 
     * @param argv
     */
    public static void main(String argv[]) {

        try {
            // log4j setup
            BasicConfigurator.configure();

            // create wrapper
            AgentCommunicator proxyWrapper = new AgentCommunicator();

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
     * Send soap request for the agent to apply the given profile.
     * 
     * @param profile
     * @param loggingLevel
     * @return
     */
    public AgentResponse apply(String profile, List<String> procs, int loggingLevel) {
        AgentResponse response = null;
        try {
            if (!m_connected) {
                connect();
            }
            response = m_service.apply(generateTransactionId(), createNotificationAddress(),
                    m_productType, profile, procs, loggingLevel);
        } catch (ClientTransportException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[apply] unable to connect to (" + createEndpointAddress() + ") : " + response.getReasonPhrase());
        } catch (WebServiceException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[apply] unable to connect to (" + createEndpointAddress() + ") : " + response.getReasonPhrase());
        } catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
            m_log.error("[apply] failed : " , e);
        }
        return response;
    }

    /**
     * Send a soap request for the agent to do a baseline
     * 
     * @param loggingLevel
     * @return
     */
    public AgentResponse baseline(List<String> procs, int loggingLevel) {
        AgentResponse response = null;
        try {
            if (!m_connected) {
                connect();
            }
            response = m_service.baseline(generateTransactionId(), createNotificationAddress(),
                    m_productType, procs, loggingLevel);
        } catch (ClientTransportException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[baseline] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
        } catch (WebServiceException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[baseline] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
        } catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
            m_log.error("[baseline] failed : " , e);
       }
        return response;
    }

    /**
     * Send a soap request for the agent to do a baseline
     * 
     * @param loggingLevel
     * @return
     */
    public AgentResponse baseline(String baselineProfile, List<String> procs, int loggingLevel) {
        AgentResponse response = null;
        try {
            if (!m_connected) {
                connect();
            }
            response = m_service.baselineWithProfile(generateTransactionId(),
                    createNotificationAddress(), m_productType, baselineProfile,
                    procs, loggingLevel);
        } catch (SOAPFaultException soapException) {
            response = createErrorResponse(500, "internal error", soapException);
            if (soapException.getMessage().indexOf("not implemented") != -1) {
                response = createErrorResponse(501, "Method Not Implemented", soapException);
            } else {
                response = createErrorResponse(500, "internal error", soapException);
            }
        } catch (ClientTransportException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[baseline] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
        } catch (WebServiceException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[baseline] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
        } catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
            m_log.error("[baseline] failed : ", e);
        }
        return response;
    }

    /**
     * Send a soap request for the agent to respond to an info request
     * 
     * @return
     */
    public AgentResponse info() {
        AgentResponse response = null;
        try {
            if (!m_connected) {
                connect();
            }
            response = m_service.info(generateTransactionId(), createNotificationAddress());
        } catch (ClientTransportException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[info] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
        } catch (WebServiceException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[info] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
        } catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
            m_log.error("[info] failed : ", e);
        }
        return response;
    }

    /**
     * 
     * @param profile
     * @param loggingLevel
     * @return
     */
    public AgentResponse quickScan(String profile, List<String> procs, int loggingLevel) {
        AgentResponse response = null;
        try {

            if (!m_connected) {
                connect();
            }
            // setting the scan level to 5 makes it a quick scan
            response = m_service.scan(generateTransactionId(), createNotificationAddress(),
                    m_productType, profile, 5, procs, loggingLevel);
        } catch (ClientTransportException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[quickScan] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
        } catch (WebServiceException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[quickScan] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
        } catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
            m_log.error("[quickScan] failed : ", e);
        }
        return response;
    }

    /**
     * Sends a scan request to the dispatcher. The transaction id for request is
     * automatically created.
     * 
     * @param profile
     * @param loggingLevel
     * @return
     */
    public AgentResponse scan(String profile, List<String> procs, int loggingLevel) {
        String transactionId = generateTransactionId();
        return scan(transactionId, profile, procs, loggingLevel);
    }

    /**
     * Sends a scan request to the dispatcher. This method is used when we want
     * to have a record of the transaction id. The id should be created before
     * the method is called with the <link>#generateTransactionId</link> method,
     * and the this method should be invoked with that returned string.
     * 
     * @param transactionId
     * @param profile
     * @param loggingLevel
     * @return
     */
    public AgentResponse scan(String transactionId, String profile, List<String> procs, int loggingLevel) {
        AgentResponse response = null;
        
        try {
            if (!m_connected) {
                connect();
            }
            response = m_service.scan(transactionId, createNotificationAddress(),
                    m_productType, profile, 10, procs, loggingLevel);
            response.setTransactionId(transactionId);
        } catch (ClientTransportException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[scan] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
        } catch (WebServiceException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[scan] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
        } catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
            m_log.error("[scan] failed : ", e);
        }
        return response;
    }

    /**
     * 
     * @return
     */
    public AgentResponse abort(int loggingLevel) {
        AgentResponse response = null;
        try {
            if (!m_connected) {
                connect();
            }
            response = m_service.abort(generateTransactionId(), createNotificationAddress(),
                    loggingLevel);
        } catch (SOAPFaultException soapException) {
            response = createErrorResponse(500, "internal error", soapException);
            if (soapException.getMessage().indexOf("not implemented") != -1) {
                response = createErrorResponse(501, "Method Not Implemented", soapException);
            } else {
                response = createErrorResponse(500, "internal error", soapException);
            }
        } catch (ClientTransportException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[abort] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
        } catch (WebServiceException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[abort] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
        } catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
            m_log.error("[abort] failed : ", e);
        }
        return response;
    }

    /**
     * 
     * @return
     */
    public AgentResponse status() {
        AgentResponse response = null;

        try {
            if (!m_connected) {
                connect();

            }
            response = m_service.status(generateTransactionId(), createNotificationAddress());

        } catch (ClientTransportException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[status] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());

        } catch (WebServiceException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[status] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());

        } catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
            m_log.error("[status] failed : ", e);

        }
        return response;

    }

    /**
     * 
     * @return
     */
    public AgentResponse ping() {
        AgentResponse response = null;

        try {

            if (!m_connected) {
                connect();

            }
            response = m_service.status(generateTransactionId(), createNotificationAddress());

        } catch (ClientTransportException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[ping] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());

        } catch (WebServiceException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[ping] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());

        } catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
            m_log.error("[ping] failed : ", e);

        }
        return response;

    }

    /**
     * 
     * @param profile
     * @param loggingLevel
     * @return
     */
    public AgentResponse undo(String profile, List<String> procs, int loggingLevel) {
        AgentResponse response = null;

        try {

            if (!m_connected) {
                connect();

            }
            response = m_service.undo(generateTransactionId(), createNotificationAddress(),
                    m_productType, profile, procs, loggingLevel);

        } catch (ClientTransportException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[undo] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());

        } catch (WebServiceException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[undo] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());

        } catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
            m_log.error("[undo] failed : ", e);

        }
        return response;

    }

    /**
     * 
     * @param version
     * @param updateAddress
     * @param loggingLevel
     * @return
     */
    public AgentResponse updateAgent(String version, byte [] updater, boolean forceFlag, int loggingLevel) {
        AgentResponse response = null;
        
        try {

            if (!m_connected) {
                connect();

            }
            String transID = generateTransactionId();
            String notifyAddr = createNotificationAddress();
            
            System.out.println("transid      = " + transID);
            System.out.println("notifyAddr   = " + notifyAddr);
            System.out.println("forceFlag    = " + forceFlag);
            if ((updater != null)  && (updater.length > 0 )) 
            {
              System.out.println("updater      = Populated");
            }
            else
            {
              System.out.println("updater      = Empty");
            }
            System.out.println("version      = " + version);
            System.out.println("loggingLevel = " + loggingLevel);
            
            response = m_service.updateAgent(transID, notifyAddr,
                     version, updater, forceFlag, loggingLevel);

        } catch (ClientTransportException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[updateAgent] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());

        } catch (WebServiceException te) {
            response = createErrorResponse(404, destinationUnreachableString(), te);
            m_log.error("[updateAgent] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());

        } catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
            m_log.error("[updateAgent] failed : ", e);

        }
        return response;

    }

    /**
     * Creates the error response for the Communicator
     * 
     * @param code
     * @param reason
     * @param t
     * @return
     */
    private AgentResponse createErrorResponse(int code, String reason, Throwable t) {
        AgentResponse response = new AgentResponse();
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
            }
             else {
                response.setReasonPhrase(reason + " : " + t.getMessage());
            }

        } else {
            response.setReasonPhrase(reason);

        }
        return response;

    }
}
