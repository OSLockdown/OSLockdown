/*
 * Copyright 2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.reports.util;

import com.trustedcs.sb.metadata.*;

import org.apache.log4j.Logger;
import groovy.xml.MarkupBuilder;
import org.codehaus.groovy.grails.commons.ApplicationHolder;

/**
 *
 * @author amcgrath
 */
class ProfileComparator {
    // logger
    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.reports.util.ProfileComparator");

    // Profiles
    private Profile profileA;
    private Profile profileB;

    /**
     * Parameterized constructor
     */
    public ProfileComparator( Profile a, Profile b ) {
        profileA = a;
        profileB = b;
    }

    /**
     * Creates the delta report and persists it to disk
     *
     * @param output
     */
    public void deltaReport( File outputFile ) {

    	// removed from profile
    	def removedModules = profileA.securityModules - profileB.securityModules;
    	m_log.debug("removed modules = ${removedModules.size()}");
    	removedModules.each { moduleName ->
            m_log.debug(moduleName);
    	}

    	// added to profile
        def addedModules = profileB.securityModules - profileA.securityModules;
    	m_log.debug("added modules = ${addedModules.size()}");
    	addedModules.each { moduleName ->
            m_log.debug(moduleName);
    	}

    	// common modules
    	def commonModules = profileA.securityModules - removedModules;
    	m_log.debug("common modules = ${commonModules.size()}");
        def changedModules = [:];
        def optionKey;
        commonModules.each { securityModule ->
            if ( securityModule.options?.size() > 0 ) {
                securityModule.options.each { option ->
                    optionKey = "${securityModule.id}.${option.id}";
                    if ( profileA.optionValues[optionKey] != profileB.optionValues[optionKey] ) {
                        if ( changedModules[securityModule.id] ) {
                            changedModules[securityModule.id] << option.id;
                        }
                        else {
                            def inner = [option.id];
                            changedModules[securityModule.id] = inner;
                        }
                    }
                }
            }
        }


        def writer = new BufferedWriter(new FileWriter(outputFile));
        def builder = new groovy.xml.MarkupBuilder(writer);

        builder.ProfileDelta(created:new Date().format(ReportsHelper.CREATED_DATE_FORMAT),
            sbVersion:ApplicationHolder.application.metadata['app.version']) {

            // profile information
            profile(name:profileA.name)
            profile(name:profileB.name)

            added() {
                addedModules.each { securityModule ->

                    module(name:securityModule.name,
                        severityLevel:securityModule.severityLevel) {
                        description(securityModule.description)
                        views() {
                            securityModule.moduleTags.each { viewTag ->
                                view(viewTag);
                            }
                        }
                        compliancy() {
                            securityModule.compliancies.each { lineItem ->
	                            'line-item'(source:lineItem.source,
                                    name:lineItem.name,
                                    version:lineItem.compVersion,
                                    item:lineItem.item)
                            }
                        }
                    }

                }
            }

            removed() {
                removedModules.each { securityModule ->

                    module(name:securityModule.name,
                        severityLevel:securityModule.severityLevel) {
                        description(securityModule.description)
                        views() {
                            securityModule.moduleTags.each { viewTag ->
                                view(viewTag);
                            }
                        }
                        compliancy() {
                            securityModule.compliancies.each { lineItem ->
	                            'line-item'(source:lineItem.source,
                                    name:lineItem.name,
                                    version:lineItem.compVersion,
                                    item:lineItem.item)
                            }
                        }
                    }

                }
            }

            changed() {                
                changedModules.each { moduleId, optionIds ->
                    SecurityModule securityModule = SecurityModule.get(moduleId);
                    module(name:securityModule.name,
                        severityLevel:securityModule.severityLevel) {
                        description(securityModule.description)
                        views() {
                            securityModule.moduleTags.each { viewTag ->
                                view(viewTag);
                            }
                        }
                        compliancy() {
                            securityModule.compliancies.each { lineItem ->
	                            'line-item'(source:lineItem.source,
                                    name:lineItem.name,
                                    version:lineItem.compVersion,
                                    item:lineItem.item)
                            }
                        }

                        optionIds.each { optionId ->
                            ModuleOption moduleOption = ModuleOption.get(optionId);
                            option(type:moduleOption.type){
                                description(moduleOption.description);
                                valueA(profileA.optionValues["${moduleId}.${optionId}"]);
                                valueB(profileB.optionValues["${moduleId}.${optionId}"]);
                                units(moduleOption.unit);
                            }
                        }

                    }

                }
            }
        }
    }
}

