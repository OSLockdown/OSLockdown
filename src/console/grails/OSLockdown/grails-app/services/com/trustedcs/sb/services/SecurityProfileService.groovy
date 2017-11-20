/*
 * Original file generated in 2010 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2010-2013 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.services;

import org.apache.log4j.Logger;

import groovy.xml.StreamingMarkupBuilder;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.Result;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.stream.StreamResult;
import groovy.util.slurpersupport.GPathResult;

import com.trustedcs.sb.web.pojo.Group;
import com.trustedcs.sb.metadata.*;
import com.trustedcs.sb.metadata.util.SbProfileHelper;

import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;

import com.trustedcs.sb.exceptions.SecurityProfileException;

import org.xml.sax.SAXException;

class SecurityProfileService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.SecurityProfileService");

    // Transactional
    boolean transactional = true;

    // injected services
    def messageSource;
    def auditLogService;

    /**
     * @param securityProfile
     */
    def save(Profile securityProfile) {
        // save group to the database
        if (!securityProfile.hasErrors() && securityProfile.save()) {
            // persist the security profile to disk
            if ( !(securityProfile.writeProtected) ) {
                try {
                    File file = new File(SBFileSystemUtil.get(SB_LOCATIONS.PROFILES),securityProfile.fileName);
                    FileWriter fileWriter = new FileWriter(file);
                    toXml(securityProfile,true,fileWriter);
                }
                catch ( Exception e ) {
                    m_log.error("Unable to persist: ${e.message}");
                    securityProfile.errors.reject("securityProfile.persist.error");
                    throw new SecurityProfileException(message:e.message,securityProfile:securityProfile);
                }
                m_log.info("Security Profile Persisted to Disk");
            }
            m_log.info("Security Profile Saved");
        }
        else {
            m_log.error("Unable to save Security Profile");
            securityProfile.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new SecurityProfileException(securityProfile:securityProfile);
        }
    }

    /**
     * Deletes the security profile from the database and removes it from the
     * profiles directory
     *
     * @param securityProfile
     */
    def delete(Profile securityProfile) {
       // check to see if the baseline profile is associated anywhere
        def groupsWithProfile = Group.withCriteria {
            eq("profile",securityProfile);
        }
        // if there are groups with this profile reject the delete
        if ( groupsWithProfile.size() > 0 ) {
            securityProfile.errors.reject("securityProfile.delete.association.error",[securityProfile.name] as Object[],"Security Profile still associated with a group")
            throw new SecurityProfileException(securityProfile:securityProfile)
        }
        // find the baseline profile location
        File file = new File(SBFileSystemUtil.get(SB_LOCATIONS.PROFILES),securityProfile.fileName);
        securityProfile.delete();
        if (securityProfile.hasErrors()) {
            m_log.error("Unable to delete Security Profile");
            securityProfile.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new SecurityProfileException(securityProfile:securityProfile);
        }
        if (!file.delete()) {
            m_log.error(messageSource.getMessage("securityProfile.delete.file.error",[file.absolutePath] as Object[],null));
        }
    }

    /**
     * This is a deep clone of the profile but the name of the profile
     * will change to include the string '(copy)' at the end of it
     * @return the cloned copy
     */
    def clone(Profile securityProfile) {
    	Profile clonedProfile = new Profile();
    	clonedProfile.name = "${securityProfile.name} (copy)";
    	clonedProfile.shortDescription = securityProfile.shortDescription;
    	clonedProfile.description = securityProfile.description;
    	clonedProfile.comments = securityProfile.comments;
    	clonedProfile.optionValues = securityProfile.optionValues;
    	def securityModule;
    	securityProfile.securityModules.each {
            securityModule = SecurityModule.get(it.id);
            // add the module to the profile
            clonedProfile.addToSecurityModules(securityModule);
    	}
    	return clonedProfile;
    }

    def fromXml(File file) {
        return fromXml(file, false );
    }

    /**
     * Create a security profile from an xml file
     *
     * @param file
     */
    def fromXml(File file, boolean isUpgrade) {
        try {
            XmlSlurper slurper = new XmlSlurper();
            slurper.setKeepWhitespace(false);
            def xml = slurper.parse(file);
            return fromXml(file.name,xml, isUpgrade );
    	}
        catch ( SAXException saxException ) {
            m_log.error("Unable to parse security profile",saxException);
            throw new SecurityProfileException(message:saxException.message);
        }
    	catch ( IOException ioe ) {
            m_log.error("IO error parsing security profile",ioe);
            throw new SecurityProfileException(message:ioe.message);
    	}
    }

    def fromXml(InputStream inputStream) {
        return fromXml(inputStream, false );
    }

    /**
     * Create a security profile from an xml stream
     *
     * @param inputStream
     */
    def fromXml(InputStream inputStream, boolean isUpgrade ) {
        try {
            XmlSlurper slurper = new XmlSlurper();
            slurper.setKeepWhitespace(false);
            def xml = slurper.parse(inputStream);
            return fromXml(null,xml, isUpgrade );
    	}
        catch ( SAXException saxException ) {
            m_log.error("Unable to parse security profile",saxException);
            throw new SecurityProfileException(message:saxException.message);
        }
    	catch ( IOException ioe ) {
            m_log.error("IO error parsing security profile",ioe);
            throw new SecurityProfileException(message:ioe.message);
    	}
    }

    /**
     * Creates a new security profile from an xml fragment
     *
     * @param xml
     */
    def fromXml(String fileName, GPathResult parsedProfile ) {
        return fromXml( fileName, parsedProfile, false );
    }

    /**
     * Creates a new or updates an existing security profile (during upgrade, in which case isUpgrade=true)
     * from an xml fragment.
     * @param String fileName
     * @param parsedProfile
     * @param isUpgrade - oolean flag signifying whether the db upgrade is done or not
     * @return the security profile
     */
    def fromXml(String fileName, GPathResult parsedProfile, boolean isUpgrade ) {
    	def profile

        String profileName = parsedProfile.@name.text()

        if( isUpgrade ){
            // load existing security profile from db
            profile = Profile.findByName( profileName );

            if( profile ){
                // Clear the optionValues map as its keys (with format ${securityModule.id}.${option.id}") contain
                // old option (ModuleOption) ids which were deleted and recreated on upgrade. The optionValues map
                // will be populated below with new ModuleOptions ids.
                profile.optionValues.clear();
                                
            }
            else {
                // This security profile is new so it does not exist on the db yet. Create new Profile for it.
                // This is the case for the new "NSA Guide" Profile added in the 4.0.3.
                profile = new Profile();
            }
        }
        else {
            // create new profile
            profile = new Profile();
        }

        // name
        profile.name = profileName;
        profile.writeProtected = Boolean.valueOf(parsedProfile.@sysProfile.text());
        if ( fileName ) {
            profile.fileName = fileName;
        }
        else {
            profile.fileName = SbProfileHelper.createFilename(profile.name);
        }

        // module holder
        def securityModule;

        // info
        profile.shortDescription = parsedProfile.info?.description?.summary?.text()
        profile.description = parsedProfile.info?.description?.verbose?.text()
        profile.comments = parsedProfile.info?.description?.comments?.text()

        // iterate over modules in the configuration
        
        // On upgrade - See if the in-DB Profile and the on-disk Profile agree on what profiles are present.
        // We're more concerned about the in-DB DB having modules that aren't in the on-disk Profile
        // and correctly calling these out and deleting them frmo the in-DB Profile
        
        if ( isUpgrade) {
            def idsInProfileDB
            idsInProfileDB = profile.securityModules.collect {
              it.id;
            }
            m_log.info("Profile in DB has ${idsInProfileDB.size()} module(s)")
        
            def idsInProfileDisk
            idsInProfileDisk = parsedProfile.security_module.collect {
              try {
                  SecurityModule.findByName(it.@name.text()).id
               }
               catch (Exception e) {
                 m_log.error("Unable to locate id for module '${it.@name.text()}'")
               }
            }
            m_log.info("Profile on disk has ${idsInProfileDisk.size()} module(s)")
        
            def DB_minus_Profile = idsInProfileDB - idsInProfileDisk
            def Profile_minus_DB = idsInProfileDisk - idsInProfileDB
        
            m_log.info("Modules in DB but not Profile = ${DB_minus_Profile.size()}")
            for (modId in DB_minus_Profile) {
              m_log.info("Removing Module '${SecurityModule.get(modId).name}' from Console DB")
              profile.removeFromSecurityModules(SecurityModule.get(modId));
            }

            m_log.info("Modules in Profile but not DB = ${Profile_minus_DB.size()}")
            for (modId in Profile_minus_DB) {
              m_log.info(" Module '${SecurityModule.get(modId).name}' will be added to Console DB")
              profile.removeFromSecurityModules(SecurityModule.get(modId));
            }
        }
        
        for ( xmlModule in parsedProfile.security_module) {

            // get the module from the db and add it the module id list
            securityModule = SecurityModule.findByName(xmlModule.@name.text());
            
           
            if ( securityModule ) {

                // get the value of the options
                // Note that options *can* be one of two basic formats:
                //   option element w/o name  IE  <option></option>
                //   option element(s) with name   IE <option name='loginBanner'></option>
                // The option element w/o a name is legacy.  We will process such and assume that positional elements (comma separated)
                //   map to the same positional elements out of security-modules.xml
                // The option elements WITH a name are the new format, the value of the option will map to the named element.

                profile.addToSecurityModules(securityModule);

                // get the value of the options
                
                def optName;

//                print "${profile.name} -> Possible Options size = ${securityModule.options?.size()}, found ${xmlModule.option?.size()} in profile\n"
                if ( securityModule.options?.size() > 0  ) {
                    def secOpts = [:];
                    def fields = [:];
                    for (option in securityModule.options) {
                        fields = [:];
                        fields["id"] = option.id;
                        fields["defaultValue"] = option.defaultValue;
                        fields["value"] = null;
                        secOpts["${option.name}"] = fields;
                    }
                    
                    // if we have *any* option data in the profile, try and parse it
                    
//                    m_log.info("Module '${securityModule.name}' - xml doc contains ${xmlModule.option?.size()} args")
//                    m_log.info("Module '${securityModule.name}' - profile contains ${securityModule.options?.size()} args")
//                    m_log.info("Module '${securityModule.name}' - ignoreLegacyOptions marked as ${securityModule.ignoreLegacyOptions}")
                    
                    if (xmlModule.option?.size() > 0) {
                        // if the first option holds a name attribute then it is newstyle, so loop through the list of
                        // named options setting those we find and know about, yell about unknown options found in the *profile* 
                        if (xmlModule.option[0].@name != "") {
                            
                            for (opt in xmlModule.option) {
                                optName = opt.@name;
                                if (secOpts["${optName}"] == null) {
                                    m_log.error("Module '${securityModule.name}' references unknown option name '${optName}'");
                                }
                                else {
                                    secOpts["${optName}"]['value'] = opt.text();
                                }
                            }
                        }
                        
                        // Ok, not new style, so first see if we're supposed to drop any legacy option values (for example, on 'Crontab Perms'
                        else if ( securityModule.ignoreLegacyOptions) {
                            m_log.error("Module '${securityModule.name}' - dropping all legacy options in favor of default new option values");
                        }    
                    
                        // if the module has more than one newstyle value, then split the legacy arg on a comma (as it *was* being processed) and
                        // do step wise assignment of the old value to the new ones.  Make sure you stop when you have either no more legacy args to
                        // process, or no named new value argument to assign to.
                        else if ( securityModule.options.size() > 1 ) {
                            // multi option string
                            def optionStrings = xmlModule.option[0].text().split(",");
                            def optData;
                            int optionCount = 0;
                            
                            if (optionStrings.length > securityModule.options.size()) {
                                m_log.error("Mismatch in configuration for imported profile '${securityModule.name}' has ${securityModule.options.size()} options and ${optionStrings.length} exist in the profile.  Extra options ignored.");
                            }
                            
                            for (int i = 0; i < securityModule.options.size() && i<optionStrings.length ; i++) {
                                m_log.info("Module '${securityModule.name}' - assigning legacy option ${i} to '${securityModule.options[i].name}'")
                                secOpts["${securityModule.options[i].name}"]['value'] = optionStrings[i];
                            }
                        }
                        
                        // if you have a single new value argument, assign the entire legacy value to it
                        else if (securityModule.options.size() == 1) {
                            secOpts["${securityModule.options[0].name}"]['value'] = xmlModule[0].text();
                        }
                    }
                    // Now vet for missing parameters, or extra ones
                    def optVal;
                    secOpts.each  { key, value ->
                        if ( value['id'] == null) {
                            m_log.error("Module '${securityModule.name}' references unknown option name '${key}'");
                        }
                        else {
                            optVal = value['value'];
                            if (optVal == null) {
                                m_log.error("Module '${securityModule.name}' no value for '${key}' defined, using default value : ${value['defaultValue']}");
                                optVal = value['defaultValue'];                        
                            }
                        
                            m_log.debug("${securityModule.id}.${value['id']} = ${optVal}");
                            profile.optionValues["${securityModule.id}.${value['id']}"] = optVal;
                        }
                    }
                }
            }
            else {
                m_log.fatal("${xmlModule.@name.text()} does not exist in internal DB: ${parsedProfile.@name.text()}");
            }
        }

        save(profile);
        auditLogService.logProfile("import",profile.name);

    	// return the created Profile
    	return profile;
    }

    /**
     * Convert the security profile to xml
     *
     * @param securityProfile
     * @param includePreamble
     * @param writer
     */
    void toXml(Profile securityProfile,boolean includePreamble,Writer writer) throws Exception {

    	// moduleId -> optionValue
    	def optionNameMapping = [:];

        // csv option string used for each module
    	def optionString;
        def optionNames;
        
        // iterate over the modules so that we can build up the CSV list for the
        // modules options
    	securityProfile.securityModules.each { securityModule ->

            // check to see if the module has any configuration
            optionString = "";
            optionNames = [:];
            if ( securityModule.options?.size() > 0 ) {
                boolean first = true;

                securityModule.options.each {
                    optionNames [ "${it.name}" ] = securityProfile.optionValues["${securityModule.id}.${it.id}"];
                }
                optionNameMapping[securityModule.name] = optionNames;
            }
    	}

        // create the builder
        def builder = new StreamingMarkupBuilder();

        // create the xml
        def createdXml = builder.bind {
            if ( includePreamble ) {
                mkp.xmlDeclaration();
            }
            profile(name:securityProfile.name,sysProfile:securityProfile.writeProtected) {
                info() {
                    description() {
                        summary(securityProfile.shortDescription)
                        verbose(securityProfile.description)
                        comments(securityProfile.comments)
                    }
                }
                securityProfile.securityModules.each { module ->
                    security_module(name:module.name) {
                        optionNameMapping[module.name].each {
                           option(name:it.key,it.value);
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
     * Convert the security profile to be xml
     *
     * @param securityProfile
     * @param includePreamble
     * @return returns a String representation of the security profile as xml
     */
    String toXmlString(Profile securityProfile, boolean includePreamble)
    throws Exception {
        StringWriter securityProfileWriter = new StringWriter();
        toXml(securityProfile,false,securityProfileWriter);
        return securityProfileWriter.toString();
    }

    /**
     * Returns the File location of the security profile in question
     *
     * @param securityProfile
     */
    File getXmlLocation(Profile securityProfile) {
        File fileLocation = new File(SBFileSystemUtil.get(SB_LOCATIONS.PROFILES),securityProfile.fileName);
        return fileLocation;
    }
}
