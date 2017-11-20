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

import org.apache.log4j.Logger;

import com.sun.xml.ws.client.ClientTransportException;
import javax.xml.ws.WebServiceException;

import com.trustedcs.sb.services.client.reports.ReportsResponse;
import com.trustedcs.sb.services.client.reports.ReportsServiceImpl;
import com.trustedcs.sb.services.client.reports.ReportsServiceImplService;

public class ReportsCommunicator extends OSLockdownCommunicator {
	private static Logger m_log = Logger
			.getLogger("com.trustedcs.sb.ws.client.ReportsCommunicator");

	private ReportsServiceImpl m_service;

	private static final String ASSESSMENT = "assessment";
	private static final String ASSESSMENT_LIST = "assessmentList";
	private static final String APPLOG = "applog";	
	private static final String BASELINE = "baseline";
	private static final String BASELINE_LIST = "baselineList";
	private static final String APPLY = "apply";
	private static final String APPLY_LIST = "applyList";
	private static final String UNDO = "undo";
	private static final String UNDO_LIST = "undoList";

	public ReportsCommunicator() {
		super(OSLockdownCommunicationType.REPORTS);
	}

	public ReportsCommunicator(String address, int port) {
		super(address, port, OSLockdownCommunicationType.REPORTS);
	}
	
	public ReportsCommunicator(long clientId, String address, int port, boolean secureConnection) {
		super(clientId, address, port, OSLockdownCommunicationType.REPORTS,secureConnection);
	}	

	public void connect() {
		// set the url for the location of the wsdl
		URL wsdlUrl = null;
		try {
			 wsdlUrl = new URL("file:/usr/share/oslockdown/cfg/wsdl/ReportsServiceImplService.wsdl");
		}
		catch ( Exception e ) {
			m_log.error("unable to locate wsdl url: "+wsdlUrl, e);
			return;
		}
		
		m_service = new ReportsServiceImplService(wsdlUrl).getReportsServiceImplPort();
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
		ReportsResponse response = null;

		if (getCommand().equalsIgnoreCase(BASELINE)) {
			response = getBaseline(getCommandOptions()[0]);
		} else if (getCommand().equalsIgnoreCase(BASELINE_LIST)) {
			response = getBaselineList();
		} else if (getCommand().equalsIgnoreCase(ASSESSMENT)) {
			response = getAssessment(getCommandOptions()[0]);
		} else if (getCommand().equalsIgnoreCase(ASSESSMENT_LIST)) {
			response = getAssessmentList();
		} else if (getCommand().equalsIgnoreCase(APPLY)) {
			response = getApply(getCommandOptions()[0]);
		} else if (getCommand().equalsIgnoreCase(APPLY_LIST)) {
			response = getApplyList();
		} else if (getCommand().equalsIgnoreCase(UNDO)) {
			response = getUndo(getCommandOptions()[0]);
		} else if (getCommand().equalsIgnoreCase(UNDO_LIST)) {
			response = getUndoList();
		} else if (getCommand().equalsIgnoreCase(APPLOG)) {
			response = getSbAppLog();
		} else {
			StringBuffer buf = new StringBuffer();
			buf.append("command does not match list of possible commands ");
			buf.append("[");
			buf.append(BASELINE);
			buf.append("|");
			buf.append(BASELINE_LIST);
			buf.append("|");
			buf.append(ASSESSMENT);
			buf.append("|");
			buf.append(ASSESSMENT_LIST);
			buf.append("|");
			buf.append(APPLY);
			buf.append("|");
			buf.append(APPLY_LIST);
			buf.append("|");
			buf.append(UNDO);
			buf.append("|");
			buf.append(UNDO_LIST);
			buf.append("|");
			buf.append(APPLOG);			
			buf.append("]");
			System.out.println(buf.toString());
			return;
		}

		if (response != null) {			
			System.out.println("Response: " + response);
			System.out.println("Code: " + response.getCode());
			System.out.println("Reason: " + response.getReasonPhrase());
			System.out.println("Body: "+response.getBody());
			System.out.println("Content: "+response.getContent());
		}
		else {
			System.out.println ("Response was null");
		}

	}

	public static void main(String argv[]) {

		try {
			// create wrapper
			ReportsCommunicator proxyWrapper = new ReportsCommunicator();

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
	public ReportsResponse getAssessment(String fileName) {
		ReportsResponse response = null;
		try {
			if (!m_connected) {
				connect();
			}
			response = m_service.getAssessment(fileName);
		} catch (ClientTransportException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getAssessment] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (WebServiceException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getAssessment] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
			m_log.error("[getAssessment] failed : ", e);
		}
		return response;
	}

	/**
	 * 
	 * @return
	 */
	public ReportsResponse getAssessmentList() {
		ReportsResponse response = null;
		try {
			if (!m_connected) {
				connect();
			}
			response = m_service.getAssessmentList();
		} catch (ClientTransportException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getAssessmentList] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (WebServiceException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getAssessmentList] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
			m_log.error("[getAssessmentList] failed : ", e);
		}
		return response;
	}

	/**
	 * 
	 * @param fileName
	 * @return
	 */
	public ReportsResponse getSbAppLog() {
		ReportsResponse response = null;
		try {
			if (!m_connected) {
				connect();
			}
			response = m_service.getSbAppLog();
		} catch (ClientTransportException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getAuditLog] unable to connect to (" + createEndpointAddress() + ") : " + response.getReasonPhrase());
		} catch (WebServiceException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getAuditLog] unable to connect to (" + createEndpointAddress() + ") : " + response.getReasonPhrase());
		} catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
			m_log.error("[getAuditLog] failed : " , e);
		}
		return response;
	}

	/**
	 * 
	 * @param fileName
	 * @return
	 */
	public ReportsResponse getBaseline(String fileName) {
		ReportsResponse response = null;
		try {
			if (!m_connected) {
				connect();
			}
			response = m_service.getBaseline(fileName);
		} catch (ClientTransportException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getBaseline] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (WebServiceException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getBaseline] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
			m_log.error("[getBaseline] failed : ", e);
		}
		return response;
	}

	/**
	 * 
	 * @return
	 */
	public ReportsResponse getBaselineList() {
		ReportsResponse response = null;
		try {
			if (!m_connected) {
				connect();
			}
			response = m_service.getBaselineList();
		} catch (ClientTransportException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getBaselineList] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (WebServiceException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getBaselineList] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
			m_log.error("[getBaselineList] failed : ", e);
		}
		return response;
	}	

	/**
	 *
	 * @param fileName
	 * @return
	 */
	public ReportsResponse getApply(String fileName) {
		ReportsResponse response = null;
		try {
			if (!m_connected) {
				connect();
			}
			response = m_service.getApply(fileName);
		} catch (ClientTransportException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getApply] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (WebServiceException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getApply] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
			m_log.error("[getApply] failed : ", e);
		}
		return response;
	}

	/**
	 *
	 * @return
	 */
	public ReportsResponse getApplyList() {
		ReportsResponse response = null;
		try {
			if (!m_connected) {
				connect();
			}
			response = m_service.getApplyList();
		} catch (ClientTransportException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getApplyList] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (WebServiceException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getApplyList] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
			m_log.error("[getApplyList] failed : ", e);
		}
		return response;
	}

	/**
	 *
	 * @param fileName
	 * @return
	 */
	public ReportsResponse getUndo(String fileName) {
		ReportsResponse response = null;
		try {
			if (!m_connected) {
				connect();
			}
			response = m_service.getUndo(fileName);
		} catch (ClientTransportException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getUndo] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (WebServiceException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getUndo] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
			m_log.error("[getUndo] failed : ", e);
		}
		return response;
	}

	/**
	 *
	 * @return
	 */
	public ReportsResponse getUndoList() {
		ReportsResponse response = null;
		try {
			if (!m_connected) {
				connect();
			}
			response = m_service.getUndoList();
		} catch (ClientTransportException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getUndoList] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (WebServiceException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[getUndoList] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
			m_log.error("[getUndoList] failed : ", e);
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
	private ReportsResponse createErrorResponse(int code, String reason, Throwable t) {
		ReportsResponse response = new ReportsResponse();
		response.setCode(code);
		if ( t != null && t.getMessage() != null && !t.getMessage().equals("") ) {			
			response.setReasonPhrase(reason+" : "+ t.getMessage());
		}
		else {
			response.setReasonPhrase(reason);
		}
		return response;
	}
*/
    private ReportsResponse createErrorResponse(int code, String reason, Throwable t) {
        ReportsResponse response = new ReportsResponse();
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
