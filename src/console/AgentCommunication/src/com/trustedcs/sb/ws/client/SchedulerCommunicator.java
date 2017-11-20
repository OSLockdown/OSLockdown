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

import com.trustedcs.sb.services.client.scheduler.DispatcherTask;
import com.trustedcs.sb.services.client.scheduler.SchedulerResponse;
import com.trustedcs.sb.services.client.scheduler.SchedulerServiceImpl;
import com.trustedcs.sb.services.client.scheduler.SchedulerServiceImplService;

public class SchedulerCommunicator extends OSLockdownCommunicator {
	
	private static Logger m_log = Logger.getLogger("com.trustedcs.sb.ws.client.SchedulerCommunicator");

	private SchedulerServiceImpl m_service;
	
	private static final String ADD = "add";
	private static final String REMOVE = "remove";
	private static final String UPDATE = "update";
	
	
	public SchedulerCommunicator() {
		super(OSLockdownCommunicationType.SCHEDULER);
	}

	public SchedulerCommunicator(String address, int port) {
		super(address, port, OSLockdownCommunicationType.SCHEDULER);
	}
	
	public SchedulerCommunicator(long clientId, String address, int port) {
		super(clientId, address, port, OSLockdownCommunicationType.SCHEDULER);
	}
	
	public SchedulerCommunicator(long clientId, String address, int port, boolean secureConnection) {
		super(clientId, address, port, OSLockdownCommunicationType.SCHEDULER, secureConnection);
	}	

	public void connect() {
		// set the url for the location of the wsdl
		URL wsdlUrl = null;
		try {
			 wsdlUrl = new URL("file:/usr/share/oslockdown/cfg/wsdl/SchedulerServiceImplService.wsdl");
		}
		catch ( Exception e ) {
			m_log.error("unable to locate wsdl url: "+wsdlUrl, e);
			return;
		}
		
		m_service = new SchedulerServiceImplService(wsdlUrl)
				.getSchedulerServiceImplPort();
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
		SchedulerResponse response = null;
		DispatcherTask task = new DispatcherTask();
		
		task.setId(getCommandOptions()[0]);
		task.setActions(getCommandOptions()[1]);
		task.setLoggingLevel(Integer.parseInt(getCommandOptions()[2]));
		task.setPeriodType(Integer.parseInt(getCommandOptions()[3]));
		task.setPeriodIncrement(Integer.parseInt(getCommandOptions()[4]));
		task.setHour(Integer.parseInt(getCommandOptions()[5]));
		task.setMinute(Integer.parseInt(getCommandOptions()[6]));		
		
		if (getCommand().equalsIgnoreCase(REMOVE)) {
			response = removeTask(task);
		} else if (getCommand().equalsIgnoreCase(UPDATE)) {
			response = updateTask(task);
		} else {
			StringBuffer buf = new StringBuffer();
			buf.append("command does not match list of possible commands ");
			buf.append("[");			
			buf.append(REMOVE);
			buf.append("|");
			buf.append(UPDATE);
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
			SchedulerCommunicator proxyWrapper = new SchedulerCommunicator();

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
	 * Removes a task
	 * @param task
	 * @return
	 */
	public SchedulerResponse removeTask(DispatcherTask task) {
		SchedulerResponse response = null;
		try {
			if (!m_connected) {
				connect();
			}
			response = m_service.removeTask(task);
		} catch (ClientTransportException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[removeTask] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (WebServiceException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[removeTask] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
			m_log.error("[removeTask] failed : ", e);
		}
		return response;
	}

	/**
	 * Updates a task 
	 * @param task
	 * @return
	 */
	public SchedulerResponse updateTask(DispatcherTask task) {
		SchedulerResponse response = null;
		try {
			if (!m_connected) {
				connect();
			}
			response = m_service.updateTask(createNotificationAddress(),createVerificationAddress(),task);
		} catch (ClientTransportException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[updateTask] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (WebServiceException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[updateTask] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
			m_log.error("[updateTask] failed : ", e);
		}
		return response;
	}
	
	/**
	 * Updates a task 
	 * @param task
	 * @return
	 */
	public SchedulerResponse updateTaskList(List<DispatcherTask> taskList) {
		SchedulerResponse response = null;
		try {
			if (!m_connected) {
				connect();
			}
			response = m_service.updateTaskList(createNotificationAddress(),createVerificationAddress(),taskList);
		} catch (ClientTransportException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[updateTaskList] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (WebServiceException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[updateTaskList] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
			m_log.error("[updateTaskList] failed : ", e);
		}
		return response;
	}	
	
	/**
	 * Clears all tasks on the client
	 * @return
	 */
	public SchedulerResponse clearTasks() {
		SchedulerResponse response = null;
		try {
			if (!m_connected) {
				connect();
			}
			response = m_service.clearTasks();
		} catch (ClientTransportException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[clearTasks] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (WebServiceException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[clearTasks] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
			m_log.error("[clearTasks] failed : ", e);
		}
		return response;
	}
	
	/**
	 * Verifies that the tasks on the client are those that are passed
	 * @param taskList
	 * @return
	 */
	public SchedulerResponse verifyTaskList(List<DispatcherTask> taskList ) {
		SchedulerResponse response = null;
		try {
			if (!m_connected) {
				connect();
			}
			response = m_service.verifyTaskList(createNotificationAddress(),createVerificationAddress(),taskList);
		} catch (ClientTransportException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[verifyTaskList] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (WebServiceException te) {
			response = createErrorResponse(404,destinationUnreachableString(),te);
			m_log.error("[verifyTaskList] unable to connect to (" + createEndpointAddress() + ") : "+ response.getReasonPhrase());
		} catch (Exception e) {
            response = createErrorResponse(500, "internal error (" + e +") : consult log for details", e);
			m_log.error("[verifyTaskList] failed : ", e);
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
	private SchedulerResponse createErrorResponse(int code, String reason, Throwable t) {
		SchedulerResponse response = new SchedulerResponse();
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
    private SchedulerResponse createErrorResponse(int code, String reason, Throwable t) {
        SchedulerResponse response = new SchedulerResponse();
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
