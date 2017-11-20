/*
 * Original file generated in 2013 by Grails v2.2.2 under the Apache 2 License.
 * Modifications are Copyright 2013-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.services;
import org.apache.log4j.Logger;
import org.apache.commons.io.FileUtils;
import com.trustedcs.sb.license.SbLicense;
import com.trustedcs.sb.web.pojo.Processor;
import com.trustedcs.sb.util.ClientType;
import com.trustedcs.sb.clientregistration.ClientRegistrationRequest;
import com.trustedcs.sb.exceptions.ProcessorException;

import org.codehaus.groovy.grails.commons.GrailsApplication;
import groovy.xml.StreamingMarkupBuilder;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.Result;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.stream.StreamResult;
import groovy.util.slurpersupport.GPathResult

class ProcessorService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.ProcessorService");

    // Reference to Grails application.
    def grailsApplication    

    // transactional
    boolean transactional = true;

    // injected services
    def messageSource;
    def auditLogService;

    static final String DATE_FORMAT_FOR_DB_EXPORT_IMPORT = "yyyy-MM-dd HH:mm:ss.S";

    /**
    *  Check to see if a prospective Processor *could* be allowable based on current license counts...
    *  This method will return if so, otherwise an exception is raised.
    */
    def verifyProcessorCanBeAdded(Processor processorInstance) {
        def isAllowable = true

        m_log.info("${processorInstance.clientType.name} processor '${processorInstance.name}' will be registered.");
    }        

    /**
     * Saves the instance of the processor to the database
     * @param processorInstance
     * @param flush - if flush is true immediately flushes the object to the db
     */
    def save(Processor processorInstance) {
        // save Processor to the database
        
	
        if (!processorInstance.hasErrors() && processorInstance.save() ) {
            m_log.info("Processor Saved");
        }
        else {
            m_log.error("Unable to save Processor");
            processorInstance.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new ProcessorException(processorInstance:processorInstance);
        }
    }


    def save(String processorName, ClientType clientType) {
        Processor processorInstance = new Processor(name:processorName, clientType:clientType);

	// new instance, *VERIFY* if can be saved first
        verifyProcessorCanBeAdded(processorInstance)
        print "PASSED VERIFICATION"

        save(processorInstance);

    }

    /**
     * Deletes the instance of the processor 
     *
     * @param processorInstance
     */
    def delete(Processor processorInstance) {
        // double cascade problem: if we delete the processor it tries to delete a
        // group , showed up during upgrade to 1.2.2        

        // processor is not associated
        m_log.info("processor is not associated");

        // delete
        processorInstance.delete();
        if ( processorInstance.hasErrors() ) {
            processorInstance.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new ProcessorException(processorInstance:processorInstance);
        }

    }


    /**
     * Creates a processor from an xml fragment
     *
     * @param xmlFragment
     */
    def fromXml(GPathResult xmlFragment) {
        // create the processor
    	Processor processorInstance = new Processor();
        // set properties on the processor
        processorInstance.name = xmlFragment.name.text();
        processorInstance.description = xmlFragment?.description?.text();
        processorInstance.clientType = ClientType.byName(xmlFragment?.clientType?.text());
        processorInstance.dateAdded = Date.parse( DATE_FORMAT_FOR_DB_EXPORT_IMPORT, xmlFragment?.dateAdded?.text())

        // verify this one can be saved
        verifyProcessorCanBeAdded(processorInstance)

        // save the processor
        save(processorInstance);
        auditLogService.logProcessor("import",processorInstance.name);
    	return processorInstance;
    }

    
    /**
     * Convert the processor instance to xml
     *
     * @param processorInstance
     * @param includePreamble
     * @param writer
     */
    void toXml(Processor processorInstance,boolean includePreamble,Writer writer) throws Exception {    	

        // create the builder
        def builder = new StreamingMarkupBuilder();

        // create the xml
        def createdXml = builder.bind {
            if ( includePreamble ) {
                mkp.xmlDeclaration();
            }
            print "Dumping processorInstance -> ${processorInstance.allInfo()}"
            processor(id:processorInstance.id) {
                name(processorInstance.name)
                clientType(processorInstance.clientType.name)
                description(processorInstance.description)
                dateAdded(processorInstance.dateAdded.format(DATE_FORMAT_FOR_DB_EXPORT_IMPORT))

            }
        }

        // create the transformer
        Transformer transformer = TransformerFactory.newInstance().newTransformer();
        transformer.setOutputProperty(OutputKeys.INDENT, 'yes');
        transformer.setOutputProperty('{http://xml.apache.org/xslt}indent-amount', '4');
        transformer.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION, includePreamble ? "no" : "yes");

        // create the output stream
        Result result = new StreamResult(writer);

        // transform
        transformer.transform(new StreamSource(new StringReader(createdXml.toString())), result);
    }


    /**
     * Convert the processor to be xml
     *
     * @param processor
     * @param includePreamble
     * @return returns a String representation of the processor's xml
     */
    String toXmlString(Processor processorInstance, boolean includePreamble)
    throws Exception {
        StringWriter processorWriter = new StringWriter();
        toXml(processorInstance,false,processorWriter);
        return processorWriter.toString();
    }
}
