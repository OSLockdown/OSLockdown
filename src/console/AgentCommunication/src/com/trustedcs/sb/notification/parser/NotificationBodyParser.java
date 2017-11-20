/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.notification.parser;

import java.io.FileInputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;

import org.apache.log4j.Logger;
import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;

public class NotificationBodyParser extends DefaultHandler {

	/* element and attribute constants */
	private static final String DETAILS_ELEMENT = "details";
	private static final String DATA_ELEMENT = "data";
	private static final String ENTRY_ELEMENT = "entry";
	private static final String EXCEPTION_ELEMENT = "exception";
	private static final String SUCCESS_ATTRIBUTE = "success";
	private static final String ABORTED_ATTRIBUTE = "aborted";
	private static final String NAME_ATTRIBUTE = "name";
	private static final String VALUE_ATTRIBUTE = "value";
	private static final String EXCEPTIONS_ELEMENT = "exceptions";
	private static final String LEVEL_ATTRIBUTE = "level";
	private static final String MESSAGE_ATTRIBUTE = "message";

	/* logger */
	private static Logger m_log = Logger
			.getLogger("com.trustedcs.sb.notification.parser.NotificationBodyParser");

	/* parser */
	private SAXParser parser = null;
	
	// parsed values
	private boolean m_success = false;
	// parsed values
	private boolean m_aborted = false;
	// <String, String>
	private Map<String, String> m_dataMap = null;
	// <String, List<String>>
	private Map<String,List<String>> m_exceptions = null;	

	/**
	 * Parameterless constructor
	 */
	public NotificationBodyParser() {
		try {
			SAXParserFactory factory = SAXParserFactory.newInstance();
			parser = factory.newSAXParser();
		} catch (ParserConfigurationException e) {
			// TODO Auto-generated catch block
			m_log.error("Unable to configure parser", e);
		} catch (SAXException e) {
			// TODO Auto-generated catch block
			m_log.error("Unable to create parser", e);
		}
	}

	/**
	 * Parse the given input stream
	 * 
	 * @param stream
	 */
	public void parse(InputStream stream) throws Exception {
		parser.parse(stream, this);
	}

	@Override
	public void characters(char[] arg0, int arg1, int arg2) throws SAXException {
		// TODO Auto-generated method stub
		super.characters(arg0, arg1, arg2);
	}

	@Override
	public void endDocument() throws SAXException {
		// TODO Auto-generated method stub
		super.endDocument();
	}

	@Override
	public void endElement(String uri, String localName, String qName)
			throws SAXException {
	}

	@Override
	public void startDocument() throws SAXException {
		// TODO Auto-generated method stub
		super.startDocument();
	}

	@Override
	public void startElement(String uri, String localName, String qName, 
			Attributes attributes) throws SAXException {
		String tmp = null;
		if ( qName.equalsIgnoreCase(DETAILS_ELEMENT) ) {
			tmp = attributes.getValue(SUCCESS_ATTRIBUTE);			
			m_success = Boolean.parseBoolean(tmp);

                        tmp = attributes.getValue(ABORTED_ATTRIBUTE);
                        if( tmp != null ){
                            m_aborted = Boolean.parseBoolean(tmp);
                        }
		}
		else if ( qName.equalsIgnoreCase(DATA_ELEMENT) ) {
			m_dataMap = new LinkedHashMap<String,String>();			
		}
		else if ( qName.equalsIgnoreCase(EXCEPTIONS_ELEMENT) ) {
			m_exceptions = new LinkedHashMap<String,List<String>>();			
		}
		else if ( qName.equalsIgnoreCase(ENTRY_ELEMENT)) {
			String name = attributes.getValue(NAME_ATTRIBUTE);
			String value = attributes.getValue(VALUE_ATTRIBUTE);
			if ( name != null ) {
				m_dataMap.put(name,value);
			}
		}		
		else if ( qName.equalsIgnoreCase(EXCEPTION_ELEMENT) ) {
			String level = attributes.getValue(LEVEL_ATTRIBUTE);
			String message = attributes.getValue(MESSAGE_ATTRIBUTE);
			if ( !m_exceptions.containsKey(level) ) {
				m_exceptions.put(level, new ArrayList<String>());
			}
			m_exceptions.get(level).add(message);			
		}
	}
	
	/**
	 * Returns if the body indicates there was a successful result
	 * @return boolean
	 */
	public boolean wasSuccessful() {
		return m_success;
	}

	/**
	 * Returns if the body indicates that the operation was aborted
	 * @return boolean
	 */
        public boolean wasAborted(){
            return m_aborted;
        }

	/**
	 * Get the created datamap
	 * @return the datamap
	 */
	public Map getDataMap() {
		return m_dataMap;
	}
	
	/**
	 * Get the create exception map
	 * @return the exception map
	 */
	public Map getExceptionMap() {
		return m_exceptions;
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) {

		// TODO Auto-generated method stub
		NotificationBodyParser bodyParser = new NotificationBodyParser();
		for (String fileName : args) {
			try {
				bodyParser.parse(new FileInputStream(fileName));
				System.out.println("Successful: "+ bodyParser.wasSuccessful() );
				System.out.println("DataMap: "+bodyParser.getDataMap());
			} catch (Exception e) {
				m_log.error("Unable to parse file: " + fileName, e);
			}
		}

	}

}
