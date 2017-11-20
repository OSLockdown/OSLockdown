/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.stream.StreamResult;

import com.trustedcs.sb.reports.util.ServletContextURIResolver;

import org.apache.log4j.Logger;

class XmlTagLib {
	
	static def m_log = Logger.getLogger("com.trustedcs.sb.taglib.xml");
	
	def donuts = { attrs ->
	    // parameters
	    if ( attrs.params instanceof Map ) {
	        attrs.params.each { paramName , paramValue -> 
	            out << paramName + " TACO " + paramValue;
	        }
	    }	
	}
	
	/** 
	 * Applies an XSL stylesheet to a source DOM document or file and 
	 * writes the result to the output stream. 
	 */	 
	def transform = { attrs -> 
	 	// Check that some XML to transform has been provided. 
	 	def input = attrs['source'] 
	 	if (!input) { 
	 		throwTagError('Tag [transform] missing required attribute [source].') 
 		}

	 	// Check the various attributes. 
	 	// 
	 	// We must have one of 'transformer' or 'stylesheet'. 
	 	def transformer = attrs['transformer'] 
	 	if (!transformer) { 
	 		// No transformer specified, so use a stylesheet instead. 
	 		def stylesheet = attrs['stylesheet']

	 		// If there's no stylesheet either, then we're stuck. 
	 		if (!stylesheet) { 
	 			throwTagError('Tag [transform] missing required attribute [transformer] or [stylesheet].') 
 			}

	 		// See whether a factory class has been specified. If so, 
	 		// we use that one to create a transformer. Otherwise, we 
	 		// just use the default factory. 
	 		def factory 
	 		if (attrs['factory']) { 
	 			factory = Class.forName(attrs['factory']).newInstance() 
 			} 
	 		else { 
	 			factory = TransformerFactory.newInstance()
	 			factory.setURIResolver(new ServletContextURIResolver(servletContext));
 			}

	 		// Load up the stylesheet into a transformer instance. 
	 		try {
	 			def xslStream = servletContext.getResourceAsStream("/stylesheets/${stylesheet}.xsl") 
	 			transformer = factory.newTransformer(new StreamSource(xslStream))
	 		}
	 		catch(Exception e) {
	 			m_log.error("unable to create xsl transformer",e);
	 			throw e;
	 		}
 		} 
	 	else if (attrs['stylesheet']) { 
	 		throwTagError('Tag [transform]: [stylesheet] attribute can not be used with [transformer].') 
 		}
	 	
	 	// parameters
	 	if ( attrs.params instanceof Map ) {
	 		attrs.params.each { paramName , paramValue -> 
	 			transformer.setParameter(paramName,paramValue);
	 		}
	 	}

	 	// We have the transformer set up, so now prepare the source 
	 	// XML and wrap the output writer in a Result. 
	 	def output = new StreamResult(out) 
	 	if (input instanceof Node) { 
	 		input = new DOMSource(input) 
 		} 
	 	else if (input instanceof InputStream || input instanceof Reader) { 
	 		// Create a StreamSource for the given file. 
	 		input = new StreamSource(input) 
	 	} 
	 	else { 
	 		input = new StreamSource(new File(input)) 
 		}

	 	// Perform the transformation! 
	 	transformer.transform(input, output); 
 	} 
}
