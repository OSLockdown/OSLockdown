/*
 * Copyright 2010-2013 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.metadata.util;

import org.apache.log4j.Logger;
/**
 * Helper for creation of Baseline and Security Profiles
 * @author amcgrath@trustedcs.com
 */
class SbProfileHelper {
    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.metadata.util.SbProfileHelper");

    private static final def specialCharList = [
' ','\\(','\\)','\\\\','/',':',';',
'#','\\*','\\?','<','>','\\|','@','&',
'\\!','\\$','\'','\"','\\^'];

    /**
     * Returns a file name that has no special characters or spaces with
     * the extension of .xml
     * @param profileName the name of the profile to be converted to a legal file name
     * @return the filename
     */
    static String createFilename(String profileName) {
    	def str = profileName;
    	specialCharList.each {
    	    str = str.replaceAll(it,'');
    	}
    	return "${str}.xml";
    }

}

