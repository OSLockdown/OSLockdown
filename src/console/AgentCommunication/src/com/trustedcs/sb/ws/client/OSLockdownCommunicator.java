/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.ws.client;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.OptionBuilder;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.PosixParser;

//import com.trustedcs.sb.ssl.IgnoreHostnameVerifier;

/**
 * <p>
 * This class is the base implementation for all the web service client
 * connections that will be done either to the agent or the console. The console
 * clients are created just so that we have something to test against the
 * console other than the c-agent clients.
 * <p>
 * 
 * <p>
 * As a commandline program the synatax is as follows...
 * </p>
 * 
 * <p>
 * client -c <command> [-help] [-a <address>] [-p <port>] [-o <option1 option2
 * ... optionN>]
 * </p>
 * 
 * <p>
 * The extending classes are responsible for implementing the connect() method
 * which will establish the client proxy object and set its endpoint to that of
 * the configured address and port in the super class. The extended class should
 * leverage the createEndpointAddress() method to build the url to set the
 * ENDPOINT_ADDRESS_PROPERTY on the requestContext of the dynamic proxy.
 * </p>
 * 
 * @author amcgrath
 * 
 */
public abstract class OSLockdownCommunicator {

    private long m_clientId = 1;
    private String m_address = "127.0.0.1";
    private int m_port = 8080;
    private int m_loggingLevel = 7;
    private String m_notificationAddress = "localhost:8080";
    private OSLockdownCommunicationType m_type = OSLockdownCommunicationType.UNKNOWN;
    private CommandLine m_commandLine;
    private String m_command = "unknown";
    private String[] m_commandOptions = new String[0];
    protected boolean m_connected = false;
    protected boolean m_secure = false;

    public OSLockdownCommunicator() {
    }

    public OSLockdownCommunicator(OSLockdownCommunicationType type) {
        m_type = type;
    }

    public OSLockdownCommunicator(String address, int port,
                                       OSLockdownCommunicationType type) {
        m_address = address;
        m_port = port;
        m_type = type;
    }

    public OSLockdownCommunicator(long clientId, String address, int port,
                                       OSLockdownCommunicationType type) {
        m_clientId = clientId;
        m_address = address;
        m_port = port;
        m_type = type;
    }

    public OSLockdownCommunicator(long clientId, String address, int port,
                                       OSLockdownCommunicationType type, boolean secureConnection) {
        m_clientId = clientId;
        m_address = address;
        m_port = port;
        m_type = type;
        m_secure = secureConnection;
    }

    public void setNotificationAddress(String address, String port) {
        StringBuffer buffer = new StringBuffer();
        buffer.append(wrapAddrIfIPv6(address));
        buffer.append(":");
        buffer.append(port);
        
        m_notificationAddress = buffer.toString();
    }

    public String getNotificationAddress() {
        return m_notificationAddress;
    }

    public int getLoggingLevel() {
        return m_loggingLevel;
    }

    public void setLoggingLevel(int loggingLevel) {
        m_loggingLevel = loggingLevel;
    }

    public String getAddress() {
        return m_address;
    }

    protected void setAddress(String address) {
        m_address = address;
    }

    public int getPort() {
        return m_port;
    }

    protected void setPort(int port) {
        m_port = port;
    }

    public String getCommand() {
        return m_command;
    }

    protected void setCommand(String command) {
        m_command = command;
    }

    public String[] getCommandOptions() {
        return m_commandOptions;
    }

    public void setCommandOptions(String[] commandOptions) {
        m_commandOptions = commandOptions;
    }

    public String generateTransactionId() {
        StringBuffer buffer = new StringBuffer();
        buffer.append(m_clientId);
        buffer.append(":");
        buffer.append(m_address);
        buffer.append(":");
        buffer.append(m_port);
        buffer.append(":");
        buffer.append(System.currentTimeMillis());
        return buffer.toString();
    }

    public abstract void connect();

    public abstract void execute();

    protected String createNotificationAddress() {
        StringBuffer buf = new StringBuffer();
        
        if (m_secure) {
            buf.append("https://");

        } else {
            buf.append("http://");
        }
        buf.append(m_notificationAddress);
        buf.append("/OSLockdown/services/console");
        return buf.toString();
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
	
	protected String createVerificationAddress() {
		StringBuffer buf = new StringBuffer();
		if (m_secure) {
			buf.append("https://");
		} else {
			buf.append("http://");
		}
//		buf.append(wrapAddrIfIPv6(getNotificationAddress()));
        buf.append(m_notificationAddress);
		buf.append("/OSLockdown/services/taskverification");
		return buf.toString();		
	}

    protected String destinationUnreachableString() {
        return "destination " + getAddress() + ":" + getPort() + " unreachable";
    }

    /**
     * Creates the http url for the webservice
     * http[s]://192.168.1.171:8080/agentws/services/agent
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
        buf.append(m_address);
        buf.append(":");
        buf.append(m_port);
        buf.append("/agentws/services/");
        buf.append(m_type.getUrlString());
        return buf.toString();
    }

    protected void configure(String argv[]) throws Exception {
        Options options = new Options();
        options.addOption(OptionBuilder.hasArg(false).withDescription(
                "ssl connection").create("s"));
        options.addOption(OptionBuilder.hasArg().withDescription(
                "ip address for the endpoint").withArgName("address").create(
                "a"));
        options.addOption(OptionBuilder.hasArg().withDescription(
                "port number for the endpoint").withArgName("port").create("p"));
        options.addOption(OptionBuilder.hasArg().withDescription(
                "logging level").withArgName("level").create("l"));
        options.addOption(OptionBuilder.hasArg().withDescription(
                "command to execute").withArgName("command").create("c"));
        options.addOption(OptionBuilder.hasArgs().withValueSeparator(' ').withDescription("options for command").withArgName("options").create("o"));
        options.addOption(OptionBuilder.withLongOpt("help").withDescription(
                "prints this message").create("h"));

        CommandLineParser parser = new PosixParser();
        m_commandLine = parser.parse(options, argv);

        if (m_commandLine.hasOption("h")) {
            // automatically generate the help statement
            HelpFormatter formatter = new HelpFormatter();
            formatter.printHelp(m_type.getUrlString(), options, true);
            return;
        }

        m_secure = m_commandLine.hasOption("s");
        if (m_secure) {
            IgnoreHostnameVerifier myHv = new IgnoreHostnameVerifier();
            javax.net.ssl.HttpsURLConnection.setDefaultHostnameVerifier(myHv);
        }
        setCommandOptions(m_commandLine.getOptionValues("o"));
        setCommand(m_commandLine.getOptionValue("c"));
        setLoggingLevel(Integer.parseInt(m_commandLine.getOptionValue("l", "7")));
        setAddress(m_commandLine.getOptionValue("a", "127.0.0.1"));
        setPort(Integer.parseInt(m_commandLine.getOptionValue("p", "8080")));
    }

    /**
     * Convenience method for testing via main
     *
     * @param file
     * @return
     * @throws IOException
     */
    public static String getContentsAsString(File file) throws IOException {
        StringBuffer sb = new StringBuffer();
        BufferedReader in = null;
        try {
            in = new BufferedReader(new FileReader(file));
            String str;
            while ((str = in.readLine()) != null) {
                sb.append(str);
            }
            in.close();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (in != null) {
                in.close();
            }
        }

        return sb.toString();
    }
}
