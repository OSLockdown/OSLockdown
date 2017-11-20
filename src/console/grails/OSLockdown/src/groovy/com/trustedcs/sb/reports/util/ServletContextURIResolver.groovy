/*
 * Copyright 2009 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * 
 */
package com.trustedcs.sb.reports.util;

import javax.xml.transform.URIResolver;
import javax.xml.transform.Source;
import javax.xml.transform.stream.StreamSource
import javax.xml.transform.TransformerException;

import org.apache.log4j.Logger;

/**
 * @author amcgrath
 *
 */
public class ServletContextURIResolver implements URIResolver {
	
	static def m_log = Logger.getLogger("com.trustedcs.sb.reports.util.ServletContextURIResolver");
	
	def servletContext;
	
	/**
	 * @param context
	 */
	ServletContextURIResolver(def context) {
		servletContext = context;
	}

	/**
	 * @param href
	 * @param base
	 */
	public Source resolve( String href, String base ) 
		throws TransformerException {
		def stream = servletContext.getResourceAsStream("/stylesheets/${href}")
		return new StreamSource(stream);		
	}
	
}
