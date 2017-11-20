/*
 * Copyright 2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.xsl;

import javax.xml.transform.URIResolver;
import javax.xml.transform.Source;
import javax.xml.transform.stream.StreamSource
import javax.xml.transform.TransformerException;

import com.trustedcs.sb.reports.util.ReportRenderType;

import org.apache.log4j.Logger;
import org.xml.sax.EntityResolver
import org.xml.sax.InputSource

/**
 * This resolver is used to find the xsl files that are imported by our reports
 * It is used to find the common other base xsl(s) which are used via includes.
 */
public class SbURIResolver implements URIResolver, EntityResolver {
	
    static def m_log = Logger.getLogger("com.trustedcs.sb.xsl.SbUriResolver");
	
    private ReportRenderType m_renderType;
    private static File stylesheetsDir = new File("/usr/share/oslockdown/cfg/stylesheets");
	
    /**
     * Pass the subtype to the constructor so the path to the xsl can be found
     * under the /usr/share/oslockdown/cfg/stylesheets/${subtype}/${xslfile}
     * @param subtype
     */
    SbURIResolver(ReportRenderType type) {
        m_renderType = type;
    }

    /**
     * Method the attempts to find the xsl references that are done with the xi:includes
     * for our xsl stylesheets.
     * @param href
     * @param base
     */
    public Source resolve( String href, String base ) throws TransformerException {
        m_log.info("href[${href}] base[${base}]");
        File file = new File(stylesheetsDir,"${m_renderType.getXslSubDirectory()}/${href}");
        if ( !(file.exists()) ) {
            // check to see if the entity is in common
            file = new File(stylesheetsDir,"common/${href}");
            if (!(file.exists()) ) {
                m_log.error("could not resolve ${href}");
                return null;
            }
        }
		
        FileInputStream fis = new FileInputStream(file);
        return new StreamSource(fis);
    }

    /**
     * Resolver for entities
     * @param publicId
     * @param systemId
     */
    public InputSource resolveEntity(String publicId, String systemId) {        
        m_log.info("publicId[${publicId}] systemId[${systemId}]");
        return null;
    }
	
}
