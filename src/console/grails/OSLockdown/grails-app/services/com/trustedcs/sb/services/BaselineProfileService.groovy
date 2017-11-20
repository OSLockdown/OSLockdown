/*
 * Original file generated in 2010 by Grails v1.2.1 under the Apache 2 License.
 * Modifications are Copyright 2010-2011 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.services;

import org.apache.log4j.Logger;
import com.trustedcs.sb.metadata.util.SbProfileHelper;
import com.trustedcs.sb.exceptions.BaselineProfileException;
import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;
import com.trustedcs.sb.web.pojo.Group;

import groovy.xml.StreamingMarkupBuilder;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.Result;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.stream.StreamResult;
import groovy.util.slurpersupport.GPathResult;

import com.trustedcs.sb.metadata.baseline.BaselineProfile;
import com.trustedcs.sb.metadata.baseline.BaselineModule;
import com.trustedcs.sb.metadata.baseline.BaselineSection;
import com.trustedcs.sb.metadata.baseline.BaselineSuboption;

import org.xml.sax.SAXException;

class BaselineProfileService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.BaselineProfileService");

    static final String MODULE_PREFIX = "baselineModule_";

    // injected service
    def messageSource;
    def auditLogService;

    // transactional
    boolean transactional = true;

    /**
     * Saves the baseline profile to the database and persists it out as an
     * xml file in the correct directory
     * 
     * @param baselineProfile
     */
    def save(BaselineProfile baselineProfile) {
        // save baseline profile to the database
        if (!baselineProfile.hasErrors() && baselineProfile.save()) {
            // persist the baseline profile to disk
            if ( !(baselineProfile.writeProtected) ) {
                try {
                    File file = new File(SBFileSystemUtil.get(SB_LOCATIONS.BASELINE_PROFILES),baselineProfile.fileName);
                    FileWriter fileWriter = new FileWriter(file);
                    toXml(baselineProfile,true,fileWriter);
                }
                catch ( Exception e ) {
                    baselineProfile.errors.reject("baselineProfile.persist.error");
                    throw new BaselineProfileException(message:e.message,baselineProfileInstance:baselineProfile);
                }
                m_log.info("Baseline Profile Persisted To Disk");
            }            
            m_log.info("Baseline Profile Saved");
        }
        else {
            m_log.error("Unable to save Baseline Profile");
            baselineProfile.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new BaselineProfileException(baselineProfileInstance:baselineProfile);
        }
    }

    /**
     * @params baselineProfile
     * @params params
     */
    def save(BaselineProfile baselineProfile, Map params) {

        // collect all the modules that have been enabled
        def moduleIds = getModuleIdsFromParams(params);

        m_log.info("Enabled Baseline Modules: ${moduleIds}");
        def baselineModule;

        // add the correct modules
        moduleIds.each { moduleId ->
            baselineModule = BaselineModule.get(moduleId);
            baselineProfile.addToBaselineModules(baselineModule);
        }

        // file name
        baselineProfile.fileName = SbProfileHelper.createFilename(baselineProfile.name);

        // sub option values
        baselineProfile.subOptionValues = getSuboptionsFromParams(params);

        // save baseline profile to the database
        save(baselineProfile);
    }

    /**
     * @param baselineProfile
     * @param params
     */
    def update(BaselineProfile baselineProfile, Map params) {

        // update baseline profile properties
        baselineProfile.properties = params;

        // collect all the modules that have been enabled
        def newModuleIds = getModuleIdsFromParams(params);
        def oldModuleIds = baselineProfile.baselineModules.collect {
            it.id;
        }

        // logging
        def baselineModule;
        m_log.debug("New Modules: ${newModuleIds}");
        m_log.debug("Old Modules: ${oldModuleIds}");

        // removed baseline modules
        def removedIds = [];
        if ( oldModuleIds ) {
            removedIds = oldModuleIds - newModuleIds;
        }
        
        m_log.info("removed : ${removedIds}");
        removedIds.each { id ->
            baselineModule = BaselineModule.get(id);
            baselineProfile.removeFromBaselineModules(baselineModule);
        }

        // added baseline modules
        def addedIds = [];
        if ( newModuleIds ) {
            addedIds = newModuleIds - oldModuleIds;
        }
        m_log.info("added : ${addedIds}");
        addedIds.each { id ->
            baselineModule = BaselineModule.get(id);
            baselineProfile.addToBaselineModules(baselineModule);
        }

        // sub option values
        baselineProfile.subOptionValues = getSuboptionsFromParams(params);

        // save baseline profile
        save(baselineProfile);
    }

    /**
     * @param baselineProfile
     */
    def delete(BaselineProfile baselineProfile) {
        // check to see if the baseline profile is associated anywhere
        def groupsWithProfile = Group.withCriteria {
            eq("baselineProfile",baselineProfile);
        }
        // if there are groups with this profile reject the delete
        if ( groupsWithProfile.size() > 0 ) {
            baselineProfile.errors.reject("baselineProfile.delete.association.error",[baselineProfile.name] as Object[],"Baseline Profile still associated with a group")
            throw new BaselineProfileException(baselineProfileInstance:baselineProfile)
        }
        // find the baseline profile location
        File file = new File(SBFileSystemUtil.get(SB_LOCATIONS.BASELINE_PROFILES),baselineProfile.fileName);
        baselineProfile.delete();
        if (baselineProfile.hasErrors()) {
            m_log.error("Unable to delete Baseline Profile");
            baselineProfile.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new BaselineProfileException(baselineProfileInstance:baselineProfile);
        }
        if (!file.delete()) {
            m_log.error(messageSource.getMessage("baselineProfile.delete.file.error",[file.absolutePath] as Object[],null));
        }        
    }

    /**
     * This is a deep clone of the profile but the name of the profile
     * will change to include the string '(copy)' at the end of it
     * @return the cloned copy
     */
    BaselineProfile clone(BaselineProfile baselineProfile) {

    	BaselineProfile clonedBaselineProfile = new BaselineProfile();
    	clonedBaselineProfile.name = "${baselineProfile.name} (copy)";
        clonedBaselineProfile.fileName = baselineProfile.fileName;
    	clonedBaselineProfile.summary = baselineProfile.summary;
    	clonedBaselineProfile.description = baselineProfile.description;
    	clonedBaselineProfile.comments = baselineProfile.comments;
    	clonedBaselineProfile.subOptionValues = baselineProfile.subOptionValues;
    	def baselineModule;
    	baselineProfile.baselineModules.each {
            baselineModule = BaselineModule.get(it.id);
            // add the module to the profile
            clonedBaselineProfile.addToBaselineModules(baselineModule);
    	}
    	return clonedBaselineProfile;
    }

    BaselineProfile fromXml(GPathResult parsedProfile) {
        return fromXml(parsedProfile, false);
    }

    /**
     * Returns a BaselineProfile from the xml node
     * @param parsedProfile
     */
    BaselineProfile fromXml(GPathResult parsedProfile, boolean isUpgrade) {
        return fromXml(null,parsedProfile, isUpgrade);
    }

    BaselineProfile fromXml(File fileLocation) {
        return fromXml( fileLocation, false );
    }

    /**
     * Create a baseline profile from an xml file
     * @param fileLocation
     * @return the created baseline profile
     */
    BaselineProfile fromXml(File fileLocation, boolean isUpgrade) {
        // file location
        m_log.info("baseline profile location : ${fileLocation}");
        // parse the profile
        XmlSlurper slurper = new XmlSlurper();
        slurper.setKeepWhitespace(true);
    	def parsedProfile = slurper.parse(fileLocation);

        // use parsed xml to create profile
        return fromXml(fileLocation.name,parsedProfile, isUpgrade);
    }

    BaselineProfile fromXml(InputStream inputStream) {
        return fromXml(inputStream, false );
    }

    /**
     * Create a baseline profile from an xml stream
     *
     * @param inputStream
     */
    BaselineProfile fromXml(InputStream inputStream, boolean isUpgrade ) {
        try {
            XmlSlurper slurper = new XmlSlurper();
            slurper.setKeepWhitespace(true);
            def xml = slurper.parse(inputStream);
            return fromXml( null, xml, isUpgrade );
    	}
        catch ( SAXException saxException ) {
            m_log.error("Unable to parse baseline profile",saxException);
            throw new BaselineProfileException(message:saxException.message);
        }
    	catch ( IOException ioe ) {
            m_log.error("IO error parsing baseline profile",ioe);
            throw new BaselineProfileException(message:ioe.message);
    	}
    }

    BaselineProfile fromXml(String fileName, GPathResult parsedProfile) {
        return fromXml( fileName, parsedProfile, false);
    }

    /**
     * Create a baseline profile from an xml parsed xml fragment
     * @param String fileName
     * @param parsedProfile
     * @param isUpgrade - boolean flag signifying whether the db upgrade is done or not
     * @return the baseline profile
     */
    BaselineProfile fromXml(String fileName, GPathResult parsedProfile, boolean isUpgrade) {

        BaselineProfile baselineProfile
        
        String profileName = parsedProfile.@name.text()

        if( isUpgrade ){
            // load existing baseline profile from db
            baselineProfile = BaselineProfile.findByName( profileName );
            if( baselineProfile ){
                //
                // Note: baselineModule.subOptions are not set since they are not in the baselines-modules.xml.
                // (but they are still in the baseline-profile.xml and should probably be removed from there).
                //
                // Clear the subOptionValues map as its keys (with format ${baselineModule.id}.${subOption.id}") contain
                // old option (ModuleOption) ids which were deleted and recreated on upgrade. The subOptionValues map
                // will be populated below with new BaselineSuboption ids.
                baselineProfile.subOptionValues.clear();
            }
            else {
                // This baseline profile is new so it does not exist on the db yet. Create new baseline Profile for it.
                baselineProfile = new BaselineProfile();
            }
        }
        else {
            // create new profile
            baselineProfile = new BaselineProfile();
        }

        // follow the xpath of the profile
        baselineProfile.name = profileName;
        
        // if the file name exists already then use it
        if ( fileName ){
            baselineProfile.fileName = fileName;
        }
        else {
            baselineProfile.fileName = SbProfileHelper.createFilename(baselineProfile.name);
        }
        baselineProfile.writeProtected = parsedProfile.@sysProfile.text().toBoolean();
        baselineProfile.summary = parsedProfile.info.description.summary.text();
        baselineProfile.description = parsedProfile.info.description.verbose.text();
        baselineProfile.comments = parsedProfile.info.description.comments.text();

        // find the modules that are enabled
        def baselineModule;
        def subOptionMap = [:];
        String subOptionKey;
        parsedProfile.section.module.each { xmlModule ->
            if ( xmlModule.@enabled.text().toBoolean() ) {
                // lookup baseline module by name
                baselineModule = BaselineModule.findByName(xmlModule.@name.text());

                if ( baselineModule ) {
                    // sub options -- see the Note above. baselineModule.subOptions are *always* empty now.
                    baselineModule.subOptions.each { subOption ->
                        subOptionKey = "${baselineModule.id}_${subOption.id}";
                        subOptionMap[subOptionKey] = xmlModule.subOption.find {
                            it.@name == subOption.name;
                        }.@enabled.text();
                    }
                    baselineProfile.addToBaselineModules(baselineModule);
                }
                else {
                    m_log.error("Baseline Module [${xmlModule.@name.text()}] not found");
                }                
            }
        }
        // assign the sub option map to the values of the profile
        m_log.debug("sub option map ${subOptionMap}");
        baselineProfile.subOptionValues = subOptionMap;

        // save the baseline profile
        save(baselineProfile);
        auditLogService.logBaselineProfile("import",baselineProfile.name);

        // return the baseline profile
        return baselineProfile;
    }

    /**
     * Returns the list of enabled modules from the params map
     * @param params
     */
    private List getModuleIdsFromParams(Map params) {
        // collect all the modules that have been enabled
        def moduleIds = params.findAll { paramName, paramValue ->
            paramName.startsWith(MODULE_PREFIX) && paramValue == "true"
        }?.collect { key, value ->
            key.substring(MODULE_PREFIX.length()).toLong();
        }

        return moduleIds;
    }

    /**
     * Returns the map of suboption values for the profile
     * @param params
     */
    private Map getSuboptionsFromParams(Map params) {
        // empty map
        def subOptionsMap = [:];

        // get the modules
        def moduleIds = params.findAll { paramName, paramValue ->
            paramName.startsWith(MODULE_PREFIX) && paramValue == "true"
        }?.collect { key, value ->
            key.substring(MODULE_PREFIX.length());
        };

        // find all suboptions that match the module ids
        def prefix;
        def subOptionParams;
        moduleIds.each { moduleId ->
            prefix = "baselineSuboption_${moduleId}_";
            params.findAll { paramName, paramvalue ->
                paramName.startsWith(prefix);
            }.each { subOptionIdWithPrefix, subOptionValue ->
                subOptionsMap["${moduleId}_${subOptionIdWithPrefix.substring(prefix.length())}"] = subOptionValue;
            }
        }
        m_log.info("Sub Option Values: ${subOptionsMap}");
        return subOptionsMap;
    }

    /**
     * @param baselineProfile
     * @param includePreamble
     * @param writer
     */
    void toXml(BaselineProfile baselineProfile,
        boolean includePreamble,
        Writer writer) throws Exception {

        // create the builder
        def builder = new StreamingMarkupBuilder();

        // get the list of baseline sections
        def baselineSections = BaselineSection.listOrderByName();

        // create the xml
        def createdXml = builder.bind {
            if ( includePreamble ) {
                mkp.xmlDeclaration();
            }
            BaselineProfile(name:baselineProfile.name,sysProfile:baselineProfile.writeProtected) {
                info() {
                    description() {
                        summary(baselineProfile.summary)
                        verbose(baselineProfile.description)
                        comments(baselineProfile.comments)
                    }
                }
                // iterate over sections
                baselineSections.each { baselineSection ->
                    // section xml
                    section(name:baselineSection.name) {
                        // iterate over the modules in the section
                        for( BaselineModule baselineModule : baselineSection.baselineModules) {
                            // module xml
                            module(name:baselineModule.name,
                                enabled: baselineProfile.baselineModules.contains(baselineModule)) {
                                // iterate over the suboptions
                                for ( BaselineSuboption baselineSuboption : baselineModule.subOptions ) {
                                    // suboption xml
                                    def subOptionKey = "${baselineModule.id}_${baselineSuboption.id}";
                                    def subOptionValue = baselineProfile.subOptionValues[subOptionKey];
                                    subOption(name:baselineSuboption.name,
                                        enabled: subOptionValue ? subOptionValue : "false");
                                }
                            }
                        }
                    }
                }
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
     * Convert the baseline profile to be xml
     *
     * @param baselineProfile
     * @param includePreamble
     * @return returns a String representation of the baseline profile as xml
     */
    String toXmlString(BaselineProfile baselineProfile, boolean includePreamble) 
    throws Exception {
        StringWriter baselineProfileWriter = new StringWriter();
        toXml(baselineProfile,false,baselineProfileWriter);
        return baselineProfileWriter.toString();
    }

    /**
     * Returns the File location of the baseline profile in question
     *
     * @param baselineProfile
     */
    File getXmlLocation(BaselineProfile baselineProfile) {
        File fileLocation = new File(SBFileSystemUtil.get(SB_LOCATIONS.BASELINE_PROFILES),baselineProfile.fileName);
        return fileLocation;
    }
}
