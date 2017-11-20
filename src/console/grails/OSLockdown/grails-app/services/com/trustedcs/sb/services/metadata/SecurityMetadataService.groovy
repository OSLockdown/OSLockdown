/*
 * Original file generated in 2010 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2010-2013 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.services.metadata;

import org.apache.log4j.Logger;

import com.trustedcs.sb.exceptions.SecurityMetadataException;

import com.trustedcs.sb.metadata.CommonPlatformEnumeration;
import com.trustedcs.sb.metadata.Compliancy;
import com.trustedcs.sb.metadata.ModuleLibraryDependency;
import com.trustedcs.sb.metadata.ModuleOption;
import com.trustedcs.sb.metadata.ModuleTag;
import com.trustedcs.sb.metadata.SecurityModule;

import groovy.util.slurpersupport.GPathResult;

import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;

class SecurityMetadataService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.metadata.SecurityMetadataService");

    // Transactional
    //boolean transactional = false;
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
            throw new SecurityMetadataException(message:"Unable to delete security metadata object",metadataObject:metadataObject);
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
            throw new SecurityMetadataException(message:"Unable to save security metadata object",metadataObject:metadataObject);
        }
    }

    /**
     * Removes the security module's non-head metadata information, which are:
     * a. ModuleOptions (1-to-Many relationship with SecurityModule, where SecurityModule being the "owning" side)
     * b. ModuleLibraryDependency (1-to-Many relationship with SecurityModule, where SecurityModule being the "owning" side)
     * c. Compliancies (Many-to-Many relationship with SecurityModule, where SecurityModule being the "owning" side)
     * d. CommonPlatformEnumerations (Many-to-Many relationship with SecurityModule, where SecurityModule being the "owning" side)
     * e. ModuleTags (Many-to-Many relationship with SecurityModule, where SecurityModule being the "owning" side)
     */
    def removeAll() {

        def optionIds;
        def optionInstance;

        def libraryDependencyIds;
        def libraryDependencyInstance;

        def compliancyIds;
        def compliancyInstance;

        def cpeIds;
        def cpeInstance;

        def moduleTagIds;
        def moduleTagInstance;
        
        SecurityModule.findAll().each { module ->

            //
            // First handle 1-to-Many relationships :
            //  1. SecurityModule to ModuleOption and
            //  2. SecurityModule to ModuleLibraryDependency
            //

            m_log.info("Removing module options from module ${module.name}");

            // 1. SecurityModule to ModuleOption
            optionIds = [];
            module.options.each { option ->
                optionIds << option.id;
            }
            optionIds.each { moduleOptionId ->
                optionInstance = ModuleOption.get(moduleOptionId);
                // For this to work (return true) ModuleOption is required to have an equals() method.
                module.options.remove( optionInstance )

// Having the 2 lines at the of the commented out section does not delete the object. On next session flush
// get below exception. To fix this :
//
// 1. add to the owning side (i.e. SecurityModule class)
//  static mapping = {
//      options cascade: "all-delete-orphan"
//  }
// 2. and in here just remove optionInstance from module.options list.
//
// This same approach also works on lists in the Many-to-Many relationship as well.
//
//Caused by: org.springframework.dao.InvalidDataAccessApiUsageException: deleted object would be re-saved by cascade (remove deleted object from associations): [com.trustedcs.sb.metadata.ModuleOption#1]; nested exception is org.hibernate.ObjectDeletedException: deleted object would be re-saved by cascade (remove deleted object from associations): [com.trustedcs.sb.metadata.ModuleOption#1]
//	at com.trustedcs.sb.services.metadata.SecurityMetadataService.removeAll(SecurityMetadataService.groovy:147)
//	at com.trustedcs.sb.services.metadata.SecurityMetadataService$$FastClassByCGLIB$$14fc27ec.invoke(<generated>)
//	at net.sf.cglib.proxy.MethodProxy.invoke(MethodProxy.java:149)
//	at com.trustedcs.sb.services.metadata.SecurityMetadataService$$EnhancerByCGLIB$$9f8e2093.removeAll(<generated>)
//	at com.trustedcs.sb.services.metadata.SecurityMetadataService$removeAll.call(Unknown Source)
//	at BootStrap.loadSecurityModules(BootStrap.groovy:512)
//	at BootStrap.this$2$loadSecurityModules(BootStrap.groovy)
//	at BootStrap$_closure1.doCall(BootStrap.groovy:169)
//
//                module.removeFromOptions(optionInstance);
//                optionInstance.delete( / flush:true / )

            }

            m_log.info("Removing library dependencies from module ${module.name}");

            // 2. SecurityModule to ModuleLibraryDependency
            libraryDependencyIds = [];
            module.libraryDependencies.each { libraryDependency ->
                libraryDependencyIds << libraryDependency.id;
            }
            libraryDependencyIds.each { libraryDependencyId ->
                libraryDependencyInstance = ModuleLibraryDependency.get(libraryDependencyId);
                // For this to work (return true) ModuleLibraryDependency is required to have an equals() method.
                module.libraryDependencies.remove( libraryDependencyInstance )
            }

            //
            // Then handle Many-to-Many relationships :
            //  3. SecurityModule to Compliancy and
            //  4. SecurityModule to CommonPlatformEnumeration and
            //  5. SecurityModule to ModuleTag
            //

            m_log.info("Removing compliancies from module ${module.name}");

            // 3. SecurityModule to Compliancy
            compliancyIds = [];
            module.compliancies.each { compliancy ->
                compliancyIds << compliancy.id;
            }
            compliancyIds.each { compliancyId ->
                compliancyInstance = Compliancy.get(compliancyId);
                // For this to work (return true) Compliancy is required to have an equals() method.
                module.compliancies.remove( compliancyInstance )
            }

            m_log.info("Removing cpes from module ${module.name}");

            // 4. SecurityModule to CommonPlatformEnumeration
            cpeIds = [];
            module.cpes.each { cpe ->
                cpeIds << cpe.id;
            }
            cpeIds.each { cpeId ->
                cpeInstance = CommonPlatformEnumeration.get(cpeId);
                // For this to work (return true) CommonPlatformEnumeration is required to have an equals() method.
                module.cpes.remove( cpeInstance )
            }

            m_log.info("Removing module tags from module ${module.name}");

            // 5. SecurityModule to ModuleTag
            moduleTagIds = [];
            module.moduleTags.each { moduleTag ->
                moduleTagIds << moduleTag.id;
            }
            moduleTagIds.each { moduleTagId ->
                moduleTagInstance = ModuleTag.get(moduleTagId);
                // For this to work (return true) ModuleTag is required to have an equals() method.
                module.moduleTags.remove( moduleTagInstance )
            }
        }
    }

    /**
     * Finds the existing tag in the DB
     * @param tagName
     */
    ModuleTag findTag(String tagName) {
        def criteria = ModuleTag.createCriteria();
        return criteria.get {
            eq('name',tagName)
        };
    }

    /**
     * Creates the module tag ( view ) or finds it from existing entries
     *
     * @param tagName
     */
    ModuleTag createTag(String tagName) {
        ModuleTag moduleTag = findTag(tagName);
        if ( !moduleTag ) {
            moduleTag = new ModuleTag(name:tagName);
            save(moduleTag);
        }
        return moduleTag;
    }

    /**
     * Finds the compliancy object for the given parameters
     * @param source
     * @param name
     * @param version
     * @param item
     * @param option
     */
    Compliancy findCompliancy(String source,
        String name,
        String version,
        String item,
        String option) {
        def criteria = Compliancy.createCriteria();
        return criteria.get {
            eq('source',(!source ? "*" : source))
            eq('name',(!name ? "*" : name))
            eq('compVersion',(!version ? "*" : version))
            eq('item',(!item ? "*" : item))
        }
    }

    /**
     * Creates the compliancy DB entry for the given parameters
     * @param source
     * @param name
     * @param version
     * @param item
     * @param option
     */
    Compliancy createCompliancy(String source,
        String name,
        String version,
        String item,
        String option) {

        Compliancy compliancy = findCompliancy(source,name,version,item,option);
        if ( !compliancy ) {
            compliancy = new Compliancy(source:(!source ? "*" : source),
                name:(!name ? "*" : name),
                compVersion:(!version ? "*" : version),
                item:(!item ? "*" : item),
                option:(!option ? "*" : option));
            save(compliancy);
        }

        return compliancy;
    }

    /**
     *  Finds the cpe for the given string
     *
     *  @param part
     *  @param vendor
     *  @param product
     *  @param productVersion
     */
    CommonPlatformEnumeration findCpe(String part, String vendor, String product, String productVersion) {

        def criteria = CommonPlatformEnumeration.createCriteria();
        CommonPlatformEnumeration cpe = criteria.get {
            eq('part',part)
            eq('vendor',vendor)
            eq('product',product)
            eq('productVersion',productVersion)
        }
        return cpe;
    }

    /**
     * Locates the cpe using its full string instead of its parts
     *
     * @param cpeString
     */
    CommonPlatformEnumeration findCpe(String cpeString) {
        // split the cpe item into its parts
        String[] tokens = cpeString.substring(5).split(":");
        // missing identifiers that should be added as "*"
        String[] cpeVals = new String[4];
        for ( int i = 0 ; i < 4 ; i++) {
            cpeVals[i] = i+1 > tokens.length ? "*" : tokens[i];
        }
        // find the cpe
        return findCpe(cpeVals[0],cpeVals[1],cpeVals[2],cpeVals[3]);
    }

    /**
     * Creates the CPE for a given string
     *
     * @para cpeItem
     */
    CommonPlatformEnumeration createCpe(String cpeItem) {

        // split the cpe item into its parts
        String[] tokens = cpeItem.substring(5).split(":");
        // missing identifiers that should be added as "*"
        String[] cpeVals = new String[4];
        for ( int i = 0 ; i < 4 ; i++) {
            cpeVals[i] = i+1 > tokens.length ? "*" : tokens[i];
        }
        // find the cpe
        CommonPlatformEnumeration cpe = findCpe(cpeVals[0],cpeVals[1],cpeVals[2],cpeVals[3]);
        // does not exist
        if ( !cpe ) {
            cpe = new CommonPlatformEnumeration(part:cpeVals[0],
                vendor:cpeVals[1],
                product:cpeVals[2],
                productVersion:cpeVals[3]);
            save(cpe);
        }
        return cpe;
    }

    /**
     * Loads the security metadata from the defaul file location for oslockdown
     */
    def fromXml() {

        // get the security metadata file from the file system util
        File securityMetadataFile = SBFileSystemUtil.get(SB_LOCATIONS.MODULES_METADATA);
        m_log.info("Using default location security module metadata (${securityMetadataFile})");

        // does the default security metadata file exist
        if ( securityMetadataFile.exists() ) {
            m_log.info("Loading Security Modules");
        }
        else {
            m_log.fatal("${securityMetadataFile} : missing");
            thow new SecurityMetadataException(message:"${securityMetadataFile.absolutePath} Missing");
        }
        // load the file using the default file location
        fromXml(securityMetadataFile);
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

        // iterate over the module groups and modules to create domain class objects
        
        // create the CPE objects so they can be associated down in the module
        HashSet<String> cpeSet = new HashSet<String>();
        for ( cpeItem in parsedMeta.security_modules.module_group.security_module.platforms.'cpe-item') {
            cpeSet.add(cpeItem.@name.text());
            //createCpe(cpeItem.@name.text());
        }
        cpeSet.each { cpeString ->
            createCpe(cpeString);
        }
        m_log.info("Finished Generating CPE List");

        // create compliancy objects so they can be associated down in the module
        for ( compliancyItem in parsedMeta.security_modules.module_group.security_module.compliancy.'line-item' ) {
            createCompliancy(compliancyItem.@source.text(),
                compliancyItem.@name.text(),
                compliancyItem.@version.text(),
                compliancyItem.@item.text(),
                compliancyItem.@option.text());
        }
        m_log.info("Finished Generating Compliancy List");

        // create tag objects so they can be associated down in the module
        HashSet<String> tagSet = new HashSet<String>();
        for ( tagItem in parsedMeta.security_modules.module_group.security_module.views.member ) {
            tagSet.add(tagItem.text());
        }
        tagSet.each { tagString ->
            createTag(tagString);
        }
        m_log.info("Finished Generated Tag List");

        SecurityModule secModule;
        m_log.info("Importing Security Modules");
        
        // quickly get our total count...
        int totalModules = 0
        int moduleCount = 0 
        Boolean ignoreLegacyOptions = false
        
        for ( moduleGroup in parsedMeta.security_modules.module_group) {
            totalModules += moduleGroup.security_module.size();            
        }
        for ( moduleGroup in parsedMeta.security_modules.module_group ) {

            // create the security modules for that group
            for ( module in moduleGroup.security_module ) {
                moduleCount ++;
                // see if the module already exists
                secModule = SecurityModule.findByLibrary( module.library.text() );
                m_log.info("Importing ${moduleCount} of ${totalModules} - '" + module.@name.text()+"'");

                ignoreLegacyOptions = false
                try {
                    String tempValue = module.configurationOptions.@ignoreLegacyOptions
//                    m_log.info("Found ignoreLegacyOptions for module with value -> ${tempValue}")
                    if (tempValue.equalsIgnoreCase("true")) {
                        ignoreLegacyOptions = true;
                    }
                }
                catch ( Exception e ) {
//                    m_log.info("Caught exception looking for ignoreLegacyOptions")
//                  println (e)
                }
                
                if ( !secModule ) {
                    secModule = new SecurityModule(name:module.@name.text(),
                        library:module.library.text(),
                        description:module.description.text(),
                        scanWeight:module.scan_weight.text(),
                        actionWeight:module.action_weight.text(),
                        severityLevel:module.severity_level.text(),
                        ignoreLegacyOptions:ignoreLegacyOptions);
                }
                else
                {
                    // Assign new values for already existing modules
                    secModule.properties = [description:module.description.text(),
                                            scanWeight:module.scan_weight.text(),
                                            actionWeight:module.action_weight.text(),
                                            severityLevel:module.severity_level.text(),
                                            ignoreLegacyOptions:ignoreLegacyOptions]
                }                
                
                // options
                for ( moduleOption in module.configurationOptions.option ) {
                    ModuleOption mOption = new ModuleOption( name:moduleOption.@name.text(),
                        description:moduleOption.description.text(),
                        type:moduleOption.@type.text(),
                        defaultValue:moduleOption.'default'.text(),
                        unit:moduleOption.units.text() );
                    save(mOption);
                    secModule.addToOptions(mOption);
                }

                // cpe
                for ( cpeItem in module.platforms.'cpe-item' ) {
                    secModule.addToCpes(findCpe(cpeItem.@name.text()));
                }

                // compliancy
                for ( compliancyItem in module.compliancy.'line-item') {
                    secModule.addToCompliancies(findCompliancy(compliancyItem.@source.text(),
                            compliancyItem.@name.text(),
                            compliancyItem.@version.text(),
                            compliancyItem.@item.text(),
                            compliancyItem.@option.text()));
                }

                // module dependencies
                if ( module.dependencies.'module_library'.size() > 0 ) {
                    for ( moduleLibrary in module.dependencies.'module_library' ) {
                        secModule.addToLibraryDependencies( selected:moduleLibrary.@selected.text(),
                            moduleLib:moduleLibrary.text());
                    }
                }

                // view / tag
                for ( tagItem in module.views.member ) {
                    secModule.addToModuleTags(findTag(tagItem.text()));
                }

                // save the module
                m_log.debug("Security Module[${secModule.name}] imported.");
                save(secModule);
            }
        }
    }
}
