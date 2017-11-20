/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.services.sei;

import java.util.List;


public interface AgentService {

    /**
     * The agent should execute a scan on the host
     * @param profile The profile xml as a string that is to be used as the scan
     */
    public AgentResponse scan(String transactionId,
                              String notificationAddress,
                              int productType,
                              String profile,
                              int scanLevel,
                              List<String> procs,
                              int loggingLevel);

    /**
     * The agent should execute an apply on the host
     * @param profile The profile xml as a string that is to be used as the apply
     */
    public AgentResponse apply(String transactionId,
                               String notificationAddress,
                               int productType,
                               String profile,
                               List<String> procs,
                               int loggingLevel);

    /**
     * The agent should execute an undo on the host
     * @param profile The profile xml as a string that is to be used as the undo
     */
    public AgentResponse undo(String transactionId,
                              String notificationAddress,
                              int productType,
                              String profile,
                              List<String> procs,
                              int loggingLevel);

    /**
     * The agent should execute a baseline on the host
     */
    public AgentResponse baseline(String transactionId,
                                  String notificationAddress,
                                  int productType,
                                  List<String> procs,
                                  int loggingLevel);

    /**
     * The agent should execute a baseline on the host with given profile
     */
    public AgentResponse baselineWithProfile(String transactionId,
                                             String notificationAddress,
                                             int productType,
                                             String baselineProfile,
                                             List<String> procs,
                                             int loggingLevel);

    /**
     * The agent should abort any action that it is currently doing.
     * @param transactionId
     * @return
     */
    public AgentResponse abort(String transactionId,
                               String notificationAddress,
                               int loggingLevel);

    /**
     * The agent should return its status
     */
    public AgentResponse status(String transactionId,
                                String notificationAddress);

    /**
     * The agent should return its info
     */
    public AgentResponse info(String transactionId,
                              String notificationAddress);

    /**
     * The agent should attempt to update its current version
     * this is a placeholder function at this point.
     */
    public AgentResponse updateAgent(String transactionId,
                                     String notificationAddress,
                                     String version,
                                     byte [] updater,
                                     boolean forceFlag,
                                     int loggingLevel);
}
