/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services;

import java.util.List;
import com.trustedcs.sb.services.sei.AgentService;
import com.trustedcs.sb.services.sei.AgentResponse;
import javax.jws.WebService;
import javax.jws.WebParam;

@WebService
public class AgentServiceImpl implements AgentService {

    /**
     * The agent should execute a scan on the host
     *
     * @param profile
     *            The profile xml as a string that is to be used as the scan
     */
    public AgentResponse scan(@WebParam(name = "transactionId") String transactionId,
                              @WebParam(name = "notificationAddress") String notificationAddress,
                              @WebParam(name = "productType") int productType,
                              @WebParam(name = "profile") String profile,
                              @WebParam(name = "scanLevel") int scanLevel,
                              @WebParam(name = "procinfo") List<String> procs,
                              @WebParam(name = "loggingLevel") int loggingLevel) {
        return new AgentResponse(200, "action Initiated");
    }

    /**
     * The agent should execute an apply on the host
     *
     * @param profile
     *            The profile xml as a string that is to be used as the apply
     */
    public AgentResponse apply(@WebParam(name = "transactionId") String transactionId,
                               @WebParam(name = "notificationAddress") String notificationAddress,
                               @WebParam(name = "productType") int productType,
                               @WebParam(name = "profile") String profile,
                               @WebParam(name = "procinfo") List<String> procs,
                               @WebParam(name = "loggingLevel") int loggingLevel) {
        return new AgentResponse(200, "action Initiated");
    }

    /**
     * The agent should execute an undo on the host
     *
     * @param profile
     *            The profile xml as a string that is to be used as the undo
     */
    public AgentResponse undo(@WebParam(name = "transactionId") String transactionId,
                              @WebParam(name = "notificationAddress") String notificationAddress,
                              @WebParam(name = "productType") int productType,
                              @WebParam(name = "profile") String profile,
                              @WebParam(name = "procinfo") List<String> procs,
                              @WebParam(name = "loggingLevel") int loggingLevel) {
        return new AgentResponse(200, "action Initiated");
    }

    /**
     * The agent should execute a baseline on the host
     */
    public AgentResponse baseline(@WebParam(name = "transactionId") String transactionId,
                                  @WebParam(name = "notificationAddress") String notificationAddress,
                                  @WebParam(name = "productType") int productType,
                                  @WebParam(name = "procinfo") List<String> procs,
                                  @WebParam(name = "loggingLevel") int loggingLevel) {
        return new AgentResponse(200, "action Initiated");
    }

    /**
     * The agent should execute a baseline on the host
     */
    public AgentResponse baselineWithProfile(@WebParam(name = "transactionId") String transactionId,
                                             @WebParam(name = "notificationAddress") String notificationAddress,
                                             @WebParam(name = "productType") int productType,
                                             @WebParam(name = "baselineProfile") String baselineProfile,
                                             @WebParam(name = "procinfo") List<String> procs,
                                             @WebParam(name = "loggingLevel") int loggingLevel) {
        return new AgentResponse(200, "action Initiated");
    }

    /**
     * The agent should abort all actions in progress
     * 
     * @param transactionId
     * @return
     */
    public AgentResponse abort(@WebParam(name = "transactionId") String transactionId,
                               @WebParam(name = "notificationAddress") String notificationAddress,
                               @WebParam(name = "loggingLevel") int loggingLevel) {
        return new AgentResponse(200, "Action in progress Aborted");
    }

    /**
     * The agent should return its status
     */
    public AgentResponse status(@WebParam(name = "transactionId") String transactionId,
                                @WebParam(name = "notificationAddress") String notificationAddress) {
        return new AgentResponse(200, "action Initiated");
    }

    /**
     * The agent should return its info
     */
    public AgentResponse info(@WebParam(name = "transactionId") String transactionId,
                              @WebParam(name = "notificationAddress") String notificationAddress) {
        return new AgentResponse(200, "action Initiated");
    }

    /**
     * The agent should attempt to update its current version this is a
     * placeholder function at this point.
     */
    public AgentResponse updateAgent(@WebParam(name = "transactionId") String transactionId,
                                     @WebParam(name = "notificationAddress") String notificationAddress,
                                     @WebParam(name = "version") String version,
                                     @WebParam(name = "updater") byte [] updater,
                                     @WebParam(name = "forceFlag") boolean forceFlag,
                                     @WebParam(name = "loggingLevel") int loggingLevel) {
        return new AgentResponse(200, "action Initiated");
    }
}
