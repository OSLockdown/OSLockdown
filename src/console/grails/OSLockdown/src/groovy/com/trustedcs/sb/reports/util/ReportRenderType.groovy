/*
 * Copyright 2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.reports.util;

public enum ReportRenderType {
	
    HTML("HTML","xhtml",".html"),
    PDF("PDF","fo",".pdf"),
    TXT("TXT","txt",".txt"),
    CSV("CSV","csv",".csv");

    private final String displayString;
    private final String xslSubDirectory;
    private final String fileExtension;
	
    ReportRenderType(String display, String directory, String extension) {
        displayString = display
        xslSubDirectory = directory
        fileExtension = extension;
    }
	
    /**
     * Returns the display string
     */
    public String getDisplayString() {
        return displayString;
    }
	
    /**
     * Returns the xsl subdirectory
     */
    public String getXslSubDirectory() {
        return xslSubDirectory;
    }

    /**
     * Returns the file extension
     */
    public String getFileExtension() {
        return fileExtension;
    }
	
    /**
     * Returns the string representation of the given enum ordinal
     * @param ordinal
     * @return the string
     */
    public static String getDisplayString(int ordinal) {
        def tmp = getEnumFromOrdinal(ordinal);
        if ( tmp ) {
            return tmp.getDisplayString();
        }
        return "Unknown"
    }
	
    /**
     * Returns the xsl subdirectory of the given enum ordinal
     * @param ordinal
     * @return the string
     */
    public static String getXslSubDirectory(int ordinal) {
        def tmp = getEnumFromOrdinal(ordinal);
        if ( tmp ) {
            return tmp.getXslSubDirectory();
        }
        return ""
    }
	
    /**
     * Returns an enum for the given ordinal
     * @param ordinal
     * @return the enum
     */
    public static ReportRenderType getEnumFromOrdinal(int ordinal) {
        for (ReportRenderType n : ReportRenderType.values() ) {
            if ( n.ordinal() == ordinal ) {
                return n;
            }
        }
        return null;
    }
	
    /**
     * Returns an enum for the given display string
     * @param displayString
     * @return the enum
     */
    public static ReportRenderType getEnumFromString(String displayString) {
        for (ReportRenderType n : ReportRenderType.values() ) {
            if ( n.displayString == displayString ) {
                return n;
            }
        }
        return null;
    }
}
