/*
 * Original file generated in 2010 by Grails v1.2.1 under the Apache 2 License.
 * Modifications are Copyright 2010-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

class SbWebTagLib {

    // namespace for the tag library
    static namespace = "sbweb"

    static String REQ_ATTRIB_RESOURCES_LOADED = "sbweb.resources.loaded";

    /**
     * Tag to pull in the CSS
     */
    def styleResources = { attrs ->
        if ((attrs.override != 'true') && !Boolean.valueOf(attrs.override)) {
            out << "<!-- Start OS Lockdown Styling -->\n";
            out << "<link rel=\"stylesheet\" type=\"text/css\" href=\"${resource(dir:'css', file:'yui-reset-fonts-grids.css')}\"/>\n";
            out << "<link rel=\"stylesheet\" type=\"text/css\" href=\"${resource(dir:'css', file:'sb_main_layout.css')}\"/>\n";
            out << "<link rel=\"stylesheet\" type=\"text/css\" href=\"${resource(dir:'css', file:'submenu.css')}\"/>\n";
            out << "<link rel=\"stylesheet\" type=\"text/css\" href=\"${resource(dir:'css', file:'sb_pages.css')}\"/>\n";
            out << "<link rel=\"stylesheet\" type=\"text/css\" href=\"${resource(dir:'css', file:'actionbar.css')}\"/>\n";
            out << "<link rel=\"shortcut icon\" type=\"image/x-icon\" href=\"${resource(dir:'images', file:'faviconForcepoint.ico')}\"/>\n";
            out << "<link rel=\"icon\" type=\"image/x-icon\" href=\"${resource(dir:'images', file:'faviconForcepoint.ico')}\"/>\n";
            out << "<!-- End OS Lockdown Styling -->\n";
        }
        request[REQ_ATTRIB_RESOURCES_LOADED] = true;
    }

    /**
     * Tag to pull in the JavaScript
     */
    def scriptResources = { attrs ->
        if ((attrs.override != 'true') && !Boolean.valueOf(attrs.override)) {
            out << "<!-- OS Lockdown Scripting -->\n";
            out << "<r.require modules=\"application\"> \n"; 
            out << "<!-- End OS Lockdown Scripting -->\n";
        }
        request[REQ_ATTRIB_RESOURCES_LOADED] = true;
    }
}
