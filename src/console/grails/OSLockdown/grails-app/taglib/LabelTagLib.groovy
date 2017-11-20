/*
 * Original file generated in 2010 by Grails v1.2.1 under the Apache 2 License.
 * Modifications are Copyright 2010-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

class LabelTagLib {

    static namespace = 'label';

    def importanceLevel = { attrs, body ->
        if ( attrs.type.equalsIgnoreCase("string") ) {
            out << "<div class='blockLabel ${getCssClassByString(attrs.value)}'><label>${getLabelTextByString(attrs.value)}</label></div>";
        }
        else if ( attrs.type.equalsIgnoreCase("number") ) {
            out << "<div class='blockLabel ${getCssClassByNumber(attrs.value)}'><label>${getLabelTextByNumber(attrs.value)}</label></div>";
        }
    }

    def enabledDisabled = { attrs, body ->        
        if ( attrs.value || attrs.string?.toBoolean() ) {
            // show Enabled
            out << "<div class='blockLabel enabledLabel'><label>Enabled</label></div>";
        }
        else {
            // show Disabled
            out << "<div class='blockLabel disabledLabel'><label>Disabled</label></div>";
        }

    }

    private String getCssClassByString(String level) {
        String cssClass = "green";
        if ( level.equalsIgnoreCase('high') ) {
            cssClass = "red";
        }
        else if ( level.equalsIgnoreCase('medium') ) {
            cssClass = "orange";
        }
        else if ( level.equalsIgnoreCase('low') ) {
            cssClass = "yellow";
        }
        return cssClass;
    }

    private String getCssClassByNumber(def level) {
        String cssClass = "green";
        if ( level >= 2.5 ) {
            cssClass = "red";
        }
        else if ( level >= 1.5 ) {
            cssClass = "orange";
        }
        else if ( level >= 0 ) {
            cssClass = "yellow";
        }
        return cssClass;
    }


    private String getLabelTextByString(String level) {
        String text = "Unknown";
        if ( level.equalsIgnoreCase('high') ) {
            text = "High";
        }
        else if ( level.equalsIgnoreCase('medium') ) {
            text = "Medium";
        }
        else if ( level.equalsIgnoreCase('low') ) {
            text = "Low";
        }
        return text;
    }

    private String getLabelTextByNumber(def level) {
        String text = "Unknown";
        if ( level >= 2.5 ) {
            text = "High";
        }
        else if ( level >= 1.5 ) {
            text = "Medium";
        }
        else if ( level >= 0 ) {
            text = "Low";
        }
        return text;
    }
}
