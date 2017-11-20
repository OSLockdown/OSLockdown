/*
 * Copyright 2013-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.web.pojo;

import org.apache.log4j.Logger;

import grails.util.Environment;
import grails.orm.PagedResultList;

import com.trustedcs.sb.license.SbLicense;


import org.apache.commons.io.FileUtils;
import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;
import com.trustedcs.sb.util.SBJavaToJavaScriptUtil;

import com.trustedcs.sb.exceptions.ProcessorException;
import com.trustedcs.sb.util.ClientType;
import org.hibernate.criterion.Order

class ProcessorController {
	
    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.web.processor");

    // inject services
    def messageSource;
    def processorService;
    def auditLogService;
    def grailsApplication;
    
    // the delete, detach, save and update actions only accept POST requests
    static allowedMethods = [delete:'POST', detach:'POST', save:'POST', update:'POST'];

    static final String DETACHED_DATE_FORMAT = "MMM-dd-yyyy";

    // index redirect
    def index = { 
        redirect(action:list,params:params);
    }

    def list = {

        // params.max = Math.min( params.max ? params.max.toInteger() : 25,  100)

        m_log.info( "Processor List Parameters: ${params}");

        def offset       = params.offset ? params.offset : "0"
        def max          = params.max    ? params.max    : "25"
        // sort and sortOrder parameters are optional and will only be set
        // if user clicks on column headers in the table
        def sort         = (  params.sort == "name" || params.sort == "clientType" ) ? params.sort  : "name"
        def sortOrder    = ( params.order == "asc" || params.order == "desc" ) ? params.order : "asc"


        PagedResultList processorResultList =
            Processor.createCriteria().list( offset:offset, max:max ){                
              order( new Order (sort, sortOrder == "asc").ignoreCase())
            }

        // These are common parameters for both Enterprise and Bulk ...
        def finalResultMap = [ processorResultList:processorResultList, maxPerPage:max,
           isEnterprise:SbLicense.instance.isEnterprise() ]


        // render list template with finalResultMap
        finalResultMap
    }


    def show = {
        def processorInstance = Processor.get( params.id )

        if(!processorInstance) {
            flash.error = messageSource.getMessage("processor.not.found",[params.id] as Object[],null);
            redirect(action:list);
            return;
        }
        
        return [ processorInstance : processorInstance, 
             isEnterprise:SbLicense.instance.isEnterprise() ]
    }

    /**
     * Delete an individual processor
     */
    def delete = {
        clearFlash();
        Processor processorInstance = Processor.get(params.id);
        if ( processorInstance ) {
            try {
                processorService.delete(processorInstance);
                auditLogService.logProcessor("delete",processorInstance.name);
            }
            catch ( ProcessorException e ) {
                flash.error += g.renderErrors(bean:e.processorInstance);
                redirect(action:'show',id:'id');
            }
        }
        else {
            flash.error += messageSource.getMessage("processor.not.found",[id] as Object[],null);
        }
        redirect(action:'list');
    }
    
    /**
     * Removes multiple processors from the list
     */
    def deleteMulti = {
        // clear flash
        clearFlash();

        // get the ids of processors that will be deleted
        def ids = request.getParameterValues('processorList')?.collect { id ->
            id.toLong();
        }

        // delete each processor in the list
        m_log.info("delete processor ids" + ids);
        def processorInstance;
        ids.each { id ->
            processorInstance = Processor.get(id);
            if ( processorInstance ) {
                try {
                    processorService.delete(processorInstance);
                    auditLogService.logProcessor("delete",processorInstance.name);
                }
                catch ( ProcessorException e ) {
                    flash.error += g.renderErrors(bean:e.processorInstance);
                }
                }
            else {
                flash.error += messageSource.getMessage("processor.not.found",[id] as Object[],null);
            }
        }
        redirect(action:'list');
    }

    /**
     * Edit the processor's configuration
     */
    def edit = {
    	m_log.info("Inside edit: ${params.id}");    		
        Processor processorInstance = Processor.get( params.id )
        if(!processorInstance) {
            flash.error = messageSource.getMessage("processor.not.found",[params.id] as Object[],null);
            redirect(action:list);
            return;
        }
        else {
            m_log.info("Processor found")
            processorInstance.properties = params
            return [ processorInstance : processorInstance ]
        }
    }

    /**
     * Creating a new processor.
     */
    def create = {
    	
        Processor processorInstance = new Processor()
        processorInstance.properties = params
        return ['processorInstance':processorInstance]
    }

    /**
     * Save created processor
     */
    def save = {
    	clearFlash();
        // create the processor instance
        Processor processorInstance = new Processor(params);
        processorInstance.dateAdded = Calendar.getInstance().getTime()
        try {
	        processorInstance.clientType = ClientType.byName(params.clientTypeId);
            processorService.save(processorInstance);
            auditLogService.logProcessor("add",processorInstance.name);
        }
        catch( ProcessorException e ) {
            flash.error += g.renderErrors(bean:e.processorInstance,as:"list");
            // redirect to create action rather than render so that the error stored in flash is
            // only shown once. If render() is used rather than redirect() and the user clicks on Processors->List
            // (processor/list) next, then the error is also shown there which is bad. Can't call clearFlash() in the beginning
            // of list action as then error won't be displayed if get an error in the allowMulti() case.
            redirect(action:'create',params:params);
            return;
        }

        // show the newly created instance
        redirect(action:list)
//        redirect(action:show,id:processorInstance.id)
    }



    /**
     * update processor
     */
    def update = {
    	clearFlash();
        def processorInstance = Processor.get( params.id )
        if(processorInstance) {
            print "Modified Params are +${params}"
	    processorInstance.properties = params;
            try {
                processorService.save(processorInstance);
                auditLogService.logProcessor("modify",processorInstance.name);
            }
            catch( ProcessorException e ) {
                flash.error += g.renderErrors(bean:e.processorInstance,as:"list");
                // redirect to edit action rather than render so that the error stored in flash is
                // only shown once. If render() is used rather than redirect() and the user clicks on Processors->List
                // (processor/list) next, then the error is also shown there which is bad. Can't call clearFlash() in the beginning
                // of list action as then error won't be displayed if get an error in the allowMulti() case.
                redirect(action:'edit',params:params);
                return;
            }

            // Show the updated instance.
            // Fix for bugzilla #Bug 11015 - Editing (updating) processor information from the console produces 500 exception
            // 1. MUST have a non-blank line here, as otherwise will get big problems
            // as there are no corresponding update.gsp and Grails throws No SecurityManager accessible exceptions.
            // 2. redirect to the show action as update() and save() are POST methods.
            redirect(action:show,id:processorInstance.id)
        }
        else {
            flash.error = messageSource.getMessage("processor.not.found",[params.id] as Object[],null);
            redirect(action:'list');
        }
    }
    
    /**
     * Clears the flash of all messages that are currently set on it
     */
    private void clearFlash() {
        flash.message = "";
        flash.warning = "";
        flash.error = "";
    }


}
