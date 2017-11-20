/*
 * Original file generated in 2010 by Grails v1.2.1 under the Apache 2 License.
 * Modifications are Copyright 2010-2011 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.metadata.baseline;

import org.apache.log4j.Logger;
import com.trustedcs.sb.exceptions.BaselineProfileException;
import com.trustedcs.sb.metadata.util.SbProfileHelper;
import org.hibernate.criterion.Order

class BaselineProfileController {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.metadata.baseline.BaselineProfileController");

    // service injection
    def baselineProfileService;
    def messageSource;
    def auditLogService;

    // the delete, save and update actions only accept POST requests
    static allowedMethods = [save: "POST", update: "POST", delete: "POST"]

    def index = {
        redirect(action: "list", params: params)
    }

    def list = {

        def offset       = params.offset ? params.offset : "0"
        def max          = params.max ? params.max : "25"

        // sort and sortOrder parameters are optional and will only be set
        // if user clicks on column headers in the table. Default is writeProtected
        // ordered in a desc order (i.e. Industry Profiles first)
        def sort
        def sortOrder
        if( params.sort && params.order &&
            // sort (columns) that are user sortable (user can pass different invalid values on the url)
            ( params.sort == "name" || params.sort == "summary" || params.sort == "writeProtected" ) &&
            // valid sortOrder values (user can pass different invalid values on the url)
            ( params.order == "asc" || params.order == "desc" )
          ){
            sort = params.sort
            sortOrder = params.order
        }

        // params.max = Math.min(params.max ? params.max.toInteger() : 10,  100)
        def baselineProfileList = BaselineProfile.createCriteria().list( max:max,
            offset:offset) {

            // User sorted the columns with valid sort column and valid sort order. Use it for sorting
            if( sort && sortOrder ){
		        order (new Order(sort, sortOrder=="asc").ignoreCase())
            }
            // Either user did not sort, or he changed columns to invalid once, sort by Industry Profile and then by name (default)
            else {
                order("writeProtected","desc");
            }
            order(new Order("name",sortOrder =="asc").ignoreCase()) 
        }
        [baselineProfileInstanceList: baselineProfileList, maxPerPage:max]
    }

    def create = {
        def baselineProfileInstance = new BaselineProfile()
        baselineProfileInstance.properties = params
        def baselineSections = BaselineSection.listOrderByName();

        return [baselineProfileInstance: baselineProfileInstance, baselineSections: baselineSections]
    }

    def save = {
        m_log.info(params);
        def baselineProfileInstance = new BaselineProfile(params);
        try {
            baselineProfileService.save(baselineProfileInstance,params);
            auditLogService.logBaselineProfile("add",baselineProfileInstance.name);
        }
        catch ( BaselineProfileException e ) {
            render(view: "create", model: [baselineProfileInstance: e.baselineProfileInstance,
                    baselineSections:BaselineSection.listOrderByName()]);
            return;
        }

        flash.message = messageSource.getMessage("baselineProfile.saved",null,null);
        redirect(action: "show", id: baselineProfileInstance.id);
    }

    def show = {
        def baselineProfileInstance = BaselineProfile.get(params.id);
        if (!baselineProfileInstance) {
            flash.message = messageSource.getMessage("baselineProfile.not.found",[params.id] as Object[],null);
            redirect(action: "list")
        }
        else {
            return [baselineProfileInstance: baselineProfileInstance,
                baselineSections: BaselineSection.listOrderByName()]
        }
    }

    def edit = {
        def baselineProfileInstance = BaselineProfile.get(params.id)
        if (!baselineProfileInstance) {
            flash.message = messageSource.getMessage("baselineProfile.not.found",[params.id] as Object[],null);
            redirect(action: "list")
        }
        else {
            return [baselineProfileInstance: baselineProfileInstance,
                baselineSections: BaselineSection.listOrderByName()]
        }
    }

    def update = {
        def baselineProfileInstance = BaselineProfile.get(params.id)
        if (baselineProfileInstance) {
            try {
                baselineProfileService.update(baselineProfileInstance,params);
                auditLogService.logBaselineProfile("modify",baselineProfileInstance.name);
            }
            catch ( BaselineProfileException e ) {
                render(view: "edit", model: [baselineProfileInstance: e.baselineProfileInstance,
                        baselineSections:BaselineSection.listOrderByName()]);
                return;
            }

            flash.message = messageSource.getMessage("baselineProfile.updated",null,null);
            redirect(action: "show", id: baselineProfileInstance.id);
        }
        else {
            flash.message = messageSource.getMessage("baselineProfile.not.found",[params.id] as Object[],null);
            redirect(action: "edit", id: params.id)
        }
    }

    def importBaselineProfile = {

        try {
            flash.error = "";
            m_log.info(request);
            def file = request.getFile('profileFile');
            if ( file.isEmpty() ) {
                m_log.error("File is empty");
                flash.error = "File to import is empty";
            }
            else {
                BaselineProfile importedProfile = baselineProfileService.fromXml(file.getInputStream());
                auditLogService.logProfile("import",importedProfile);
            }
        }
        catch ( BaselineProfileException baselineProfileException ) {
            m_log.error("Unable to import baseline profile",baselineProfileException);
            if ( baselineProfileException.baselineProfileInstance ) {
                baselineProfileException.baselineProfileInstance.errors.allErrors.each { baselineProfileError ->
                    flash.error += messageSource.getMessage(baselineProfileError,null);
                }
            }
            else {
                flash.error = baselineProfileException.message;
            }
        }
        redirect(action: "list")
    }

    def copyProfile = {

        def profileList = BaselineProfile.withCriteria {
            order("writeProtected","desc");
            order("name","asc");
        }

        [profileList: profileList]
    }

    def performCopyProfile = {

        // Performs the copy of baseline profile

        def initialProfile;
        def clonedProfile;
        try {
            if ( params.profileId ) {
                if ( params.profileName ) {
                    initialProfile = BaselineProfile.get(params.profileId);
                    clonedProfile = baselineProfileService.clone(initialProfile);
                    clonedProfile.name = params.profileName;
                    clonedProfile.fileName = SbProfileHelper.createFilename(clonedProfile.name);
                    try {
                        baselineProfileService.save(clonedProfile);
                    }
                    catch ( BaselineProfileException baselineProfileException ) {
                        flash.error = g.renderErrors(bean:baselineProfileException.baselineProfileInstance,as:"list");
                    }
                }
                else {
                    flash.error = "No baseline profile name was given<br/>";
                }
            }
            else {
                flash.error = "No baseline profile was selected<br/>";
            }
        }
        catch ( Exception e ) {
            m_log.error("unable to copy",e);
            flash.error = "Unable to copy Baseline Profile ${initialProfile?.name}: ${e.message}<br/>";
        }
        redirect(action: "list")
    }

    def delete = {
        def baselineProfileInstance = BaselineProfile.get(params.id)
        if (baselineProfileInstance) {
            try {
                baselineProfileService.delete(baselineProfileInstance);
                auditLogService.logBaselineProfile("delete",baselineProfileInstance.name);
                redirect(action: "list");
            }
            catch (BaselineProfileException e) {
                render(view: "show", model: [baselineProfileInstance: e.baselineProfileInstance,
                        baselineSections:BaselineSection.listOrderByName()]);
            }
        }
        else {
            flash.error = messageSource.getMessage("baselineProfile.not.found",[params.id] as Object[],null);
            redirect(action: "list")
        }
    }

    def deleteMulti = {
        // clear flash error
        flash.error = "";

        // get the ids of baseline profile
        def ids = request.getParameterValues('baselineProfileList')?.collect { id ->
            id.toLong();
        }

        // delete each baseline profile in the list
        m_log.info("delete baseline profiles " + ids);
        def baselineProfile;
        ids.each { id ->
            baselineProfile = BaselineProfile.get(id);
            if ( baselineProfile ) {
                try {
                    baselineProfileService.delete(baselineProfile);
                    auditLogService.logBaselineProfile("delete",baselineProfile.name);
                }
                catch ( BaselineProfileException e ) {
                    flash.error += g.renderErrors(bean:e.baselineProfileInstance);
                }
            }
            else {
                flash.error += messageSource.getMessage("baselineProfile.not.found",[params.id] as Object[],null);
            }
        }
        redirect(action:'list');
    }

    def ajaxUpdateLevels = {
        // Note: the Ajax call to this method from inside _baselineProfleJavascript.gsp is commented out.

        def estimatedForensicImportance = new BigDecimal(params.estimatedForensicImportance);
        def estimatedSystemLoad = new BigDecimal(params.estimatedSystemLoad);
        def moduleCount = new BigDecimal(params.moduleCount);
        [estimatedForensicImportance:estimatedForensicImportance,
            estimatedSystemLoad:estimatedSystemLoad,
            moduleCount:moduleCount]
    }
    def exportProfile = {

        def profileList = BaselineProfile.withCriteria {
            order("writeProtected","desc");
            order("name","asc");
        }

        [profileList: profileList]
    }

    def performExportProfile = {

        // Performs the export of baseline profile

        def initialProfile;
        try {
            if ( params.profileId ) {
                initialProfile = BaselineProfile.get(params.profileId);
                def profileXML = baselineProfileService.toXmlString(initialProfile, true)
                response.setHeader('Content-disposition', "attachment; filename=\"${initialProfile.name}\"");
                response.contentType = "text/xml"
                response.outputStream << profileXML
                response.outputStream.flush()
            }
            else {
                flash.error = "No profile was selected<br/>";
            }
        }
        catch ( Exception e ) {
            m_log.error("unable to export",e);
            flash.error = "Unable to export ${initialProfile?.name}: ${e.message}<br/>";
        }

// Can't redirect with a response also, so just return.  GSP has a return button.
//        redirect( action: "list" )
    }
}
