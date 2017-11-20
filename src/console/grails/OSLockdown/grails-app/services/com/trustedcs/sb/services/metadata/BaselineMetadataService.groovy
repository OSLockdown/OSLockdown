/*
 * Original file generated in 2010 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2010-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.services.metadata;

import org.apache.log4j.Logger;

import com.trustedcs.sb.exceptions.BaselineMetadataException;

import groovy.util.slurpersupport.GPathResult;

import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;

import com.trustedcs.sb.metadata.baseline.BaselineSection;
import com.trustedcs.sb.metadata.baseline.BaselineModule;

class BaselineMetadataService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.metadata.BaselineMetadataService");

    // Transactional
    boolean transactional = true;

    // injected services
    def messageSource;

    /**
     * Delete the passed metadata object
     *
     * @param metadataObject
     */
    def delete(def metadataObject) {
        metadataObject.delete();
        if ( metadataObject.hasErrors() ) {
            metadataObject.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new BaselineMetadataException(message:"Unable to delete baseline metadata object",metadataObject:metadataObject);
        }
    }

    /**
     * Save the passed metadata object
     *
     * @param metadataObject
     */
    def save(def metadataObject) {
        // save Client to the database
        if (!metadataObject.hasErrors() && metadataObject.save()) {
            m_log.debug("Metadata Object Saved");
        }
        else {
            m_log.error("Unable to save metadata object");
            metadataObject.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new BaselineMetadataException(message:"Unable to save baseline metadata object",metadataObject:metadataObject);
        }
    }

    /**
     * Loads the baseline metadata from the default file location for oslockdown
     */
    def fromXml() {

        // get the security metadata file from the file system util
        File baselineMetadataFile = SBFileSystemUtil.get(SB_LOCATIONS.BASELINE_METADATA);
        m_log.info("Using default location baseline module metadata (${baselineMetadataFile})");

        // does the default security metadata file exist
        if ( baselineMetadataFile.exists() ) {
            m_log.info("Loading Baseline Modules");
        }
        else {
            m_log.fatal("${baselineMetadataFile} : missing");
            thow new BaselineMetadataException(message:"${baselineMetadataFile.absolutePath} Missing");
        }
        // load the file using the default file location
        fromXml(baselineMetadataFile);
    }

    /**
     * Load module metadata from a specified location this will usually be
     * located in /usr/share/oslockdown/cfg
     *
     * @param fileLocation
     */
    def fromXml(File fileLocation) {

        // parse the document using slurper
        XmlSlurper slurper = new XmlSlurper();
        GPathResult parsedMeta = slurper.parse(fileLocation);

        def baselineSection;
        // iterate over the sections
        for ( xmlSection in parsedMeta.section ) {
            // find the baseline section if it exists already
            baselineSection = BaselineSection.findByName(xmlSection.@name.text());
            // baseline section doesn't exist
            if ( !baselineSection ) {
                // create the baseline section
                baselineSection = BaselineSection.fromXml(xmlSection);
                // save the created baseline section and its children
                save(baselineSection);
            }
        }
    }

    /**
     * Removes the baseline module's non-head metadata information,  which are:
     * a. BaselineSuboption (1-to-Many relationship with BaselineModule, where BaselineModule being the "owning" side)
     * b. BaselineSections (1-to-Many relationship with BaselineModule, where BaselineSections being the "owning" side
     *      but the no cascading is set)
     */
    def removeAll() {

        def subOptionIds;
        def subOptionInstance;

        def baselineSectionIds;
        def baselineSectionInstance;

        // 1. BaselineSuboptions.
        BaselineModule.findAll().each { baselineModule ->

            m_log.info("Removing sub options from baseline module ${baselineModule.name}");

            // 1. BaselineModule to BaselineSuboption
            subOptionIds = [];
            baselineModule.subOptions.each { subOption ->
                subOptionIds << subOption.id;
            }
            subOptionIds.each { subOptionId ->
                subOptionInstance = BaselineSuboption.get(subOptionId);
                // For this to work (return true) BaselineSuboption is required to have an equals() method.
                baselineModule.subOptions.remove( subOptionInstance );
            }
        }

        // 2. BaselineSections
        baselineSectionIds = [];
        BaselineSection.findAll().each { baselineSection ->
            baselineSectionIds << baselineSection.id;
        }
        for( def baselineSectionId : baselineSectionIds )
        {
            def baselineSection = BaselineSection.get( baselineSectionId );

            m_log.info("Removing baseline section ${baselineSection.name}");

            // Note: since there is no cascading in BaselineSection->BaselineModule relationship
            // (i.e. there is no belongTo=BaselineSection in BaselineModule), deleting BaselineSection,
            // does *not* delete all of its BaselineModules.
            delete( baselineSection );
        }
    }
}
