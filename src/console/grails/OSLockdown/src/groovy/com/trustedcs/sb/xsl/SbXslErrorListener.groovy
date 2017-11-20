/*
 * Copyright 2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.xsl

import javax.xml.transform.ErrorListener;
import javax.xml.transform.TransformerException;
import org.apache.log4j.Logger

/**
 *
 * @author amcgrath
 */
class SbXslErrorListener implements ErrorListener {

    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.xsl.ErrorListener");
    
    public SbXslErrorListener() {
        
    }

    public void error(TransformerException exception) {        
        m_log.error(exception.messageAndLocation);        
    }

    public void fatalError(TransformerException exception) {
        m_log.fatal(exception.messageAndLocation);
    }

    public void warning(TransformerException exception) {
        m_log.warn(exception.messageAndLocation);
    }

	
}

