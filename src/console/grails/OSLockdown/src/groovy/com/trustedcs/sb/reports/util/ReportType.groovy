/*
 * Copyright 2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.reports.util;

public enum ReportType {
	
    ASSESSMENT("Assessment","assessmentReport","assessment-generic.xsl","assessment-report.css"),
    ASSESSMENT_FAILURES("Assessment Failures Only","assessmentReport","assessment-failures-only.xsl","assessment-report.css"),
    BASELINE("Baseline","baselineReport","baseline-generic.xsl","baseline-report.css"),
    BASELINE_COMPARISON("Baseline Comparison","baselineCompare","baseline-comparison-generic.xsl","baseline-report.css"),
    APPLY("Apply","applyReport","apply-generic.xsl","apply-report.css"),
    UNDO("Undo","undoReport","undo-generic.xsl","undo-report.css"),
    GROUP_ASSESSMENT("Group Assessment","groupAssessmentReport","group-assessment-generic.xsl","assessment-report.css"),
    ASSESSMENT_COMPARISON("Assessment Comparison","assessmentCompare","assessment-comparison-generic.xsl","assessment-comparison.css"),
    GROUP_ASSET("Group Asset","groupAssetReport","group-asset-generic.xsl","asset-report.css"),
    PROFILE_COMPARISON("Profile Comparison","profileCompare","profile-comparison-generic.xsl","assessment-comparison.css");

    // report type fields
    private final String displayString;
    private final String viewLocation;
    private final String xslFile;
    private final String cssFile;
	
    /**
     * Enum Constructor
     * @param display
     * @param location
     */
    ReportType(String display, String location, String xsl, String css) {
        displayString = display
        viewLocation = location;
        xslFile = xsl;
        cssFile = css;
    }
	
    /**
     * Returns the display string for the enum
     * @return
     */
    public String getDisplayString() {
        return displayString;
    }
	
    /**
     * Returns the view string that is used by controllers to show the report
     * @return
     */
    public String getViewLocation() {
        return viewLocation;
    }

    /**
     * Returns the xsl string
     */
    public String getXslFile() {
        return xslFile;
    }

    public String getCssFile() {
        return cssFile;
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
     * Returns an enum for the given ordinal
     * @param ordinal
     * @return the enum
     */
    public static ReportType getEnumFromOrdinal(int ordinal) {
        for (ReportType n : ReportType.values() ) {
            if ( n.ordinal() == ordinal ) {
                return n;
            }
        }
        return null;
    }
}
