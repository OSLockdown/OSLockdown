/*
 * Copyright 2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.xml;

import org.xml.sax.EntityResolver;
import org.xml.sax.InputSource;
import org.apache.log4j.Logger;

import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;

/**
 * Class to allow the console access to dtds that would be normally available
 * via the internet.  These dtds are specific to the operations of online help
 * currently
 */
class SBSchemaEntityResolver implements EntityResolver {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.xml.SBEntityResolver");

    // JavaHelp Map dtd
    private static String JAVA_HELP_MAP_PUBLIC_ID = "-//Sun Microsystems Inc.//DTD JavaHelp Map Version 1.0//EN";

    /**
     * Interface method to resolve the location of the entity
     * @param publicId
     * @param systemId
     */
    InputSource resolveEntity(String publicId, String systemId) {

        // if this is for the parsing of the java help map dtd then return a blank string,
	// fix based on https://stuartsierra.com/2008/05/08/stop-your-java-sax-parser-from-downloading-dtds
	// and replaces how we had been doing it....
        if ( publicId == JAVA_HELP_MAP_PUBLIC_ID ) {
            return new InputSource(new StringReader(""));
        }

        // return null if nothing is matched
        return null;
    }
}

