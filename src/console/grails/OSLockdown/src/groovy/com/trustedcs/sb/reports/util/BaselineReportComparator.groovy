/*
 * Copyright 2009-2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.reports.util;

import javax.xml.xpath.*;
import javax.xml.parsers.DocumentBuilderFactory;
import com.trustedcs.sb.reports.baseline.*;
import org.codehaus.groovy.grails.commons.ApplicationHolder;
import org.apache.log4j.Logger;

class BaselineReportComparator {
	
    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.reports.util.BaselineReportComparator");
	
    // Fri May 22 10:33:48 EDT 2009
    static final String MTIME_DATE_FORMAT = "E MMM dd HH:mm:ss z yyyy";
		
    def oldBaseline; // pojo
    def oldBaselineXML; // slurped
	
    def newBaseline; // pojo
    def newBaselineXML; //slurped
	
    /**
     * Constructor
     * @param oldReport location of the old report ( string path )
     * @param newReport location of the new report ( string path )
     */
    BaselineReportComparator(String oldReport, String newReport) {
        init(oldReport,newReport);
    }
	
    /**
     * Constructor
     * @param oldReport file location
     * @param newReport file location
     */
    BaselineReportComparator(File oldReport, File newReport) {
        init(oldReport,newReport);
    }
	
    /**
     * Init method using file paths as strings
     * @param oldReport
     * @param newReport
     */
    private init(String oldReport, String newReport) {
        init ( new File(oldReport), new File(newReport) );
    }
	
    /**
     * Init method using file objects
     * @param oldReport
     * @param newReport
     */
    private init(File oldReport, File newReport ) {
		
        oldBaselineXML = new XmlSlurper().parse(oldReport);
        oldBaseline = new BaselineReport(oldBaselineXML);
        
        newBaselineXML = new XmlSlurper().parse(newReport);
        newBaseline = new BaselineReport(newBaselineXML);
    }
	
    /**
     * Compare the files for a given section,subsection,and file path
     * @param section
     * @param subSection
     * @param path
     */
    def filesDiff(String section, String subSection, String path) {
        m_log.info("filesDiff($section,$subSection,$path)");
        // results
        def results = new DiffResults();
		 
        // find files node
        def oldFilesXML = oldBaselineXML.sections.section.find {it.'@name' == section
        }.subSection.find {it.'@name' == subSection}.files.find {it.'@path' == path}

        def newFilesXML = newBaselineXML.sections.section.find {it.'@name' == section
        }.subSection.find {it.'@name' == subSection}.files.find {it.'@path' == path}
        	
        // if nothing has changed we should return here
        if ( oldFilesXML.@fingerprint.text() == newFilesXML.@fingerprint.text() ) {
            // return cause everything is the same
            results.hasChanged = false;
            return results;
        }
         
        // the fingerprints are different so we must investigate
         
        // old files
        def oldFiles = [:];
        def fileInfo;
        oldFilesXML.file.each { file ->
            fileInfo = new FileInfo(file);
            oldFiles[fileInfo.path] = fileInfo;
        }
         
        // new files
        def newFiles = [:];
        newFilesXML.file.each { file ->
            fileInfo = new FileInfo(file);
            newFiles[fileInfo.path] = fileInfo;
        }
         
        // changed files
        def newFile;
        oldFiles.each { key, file ->
            newFile = newFiles[key];
            if ( newFile && ( file != newFile ) ) {
                results.changed << new DiffDelta(file,newFile);
            }
        }
         
        // deleted files
        def deletedFilesList = oldFiles.keySet() - newFiles.keySet();
        deletedFilesList.each { key ->
            results.removed << oldFiles[key];
        }
         
        // added files
        def addedFilesList = newFiles.keySet() - oldFiles.keySet();
        addedFilesList.each { key ->
            results.added << newFiles[key];
        }
        m_log.info("results added[${results.added.size()}] removed[${results.removed.size()}] changed[${results.changed.size()}]");
        return results;
    }
	
    /**
     * @param section
     * @param subSection
     */
    def packagesDiff(String section, String subSection) {
        m_log.info("packagesDiff($section,$subSection)");
        // results
        def results = new DiffResults();
        
        // find packages node
        def oldPackagesXML = oldBaselineXML.sections.section.find {it.'@name' == section      
        }.subSection.find {it.'@name' == subSection}.packages;
        def newPackagesXML = newBaselineXML.sections.section.find {it.'@name' == section        
        }.subSection.find {it.'@name' == subSection}.packages;
           
        // packages fingerprint check ???
        /*
        if ( oldPackagesXML.@fingerprint.text() == newPackagesXML.@fingerprint.text() ) {
        // prints match
        results.hasChanged = false;
        return results;
        }
         */
           
        // variable
        def packageInfo;
        
        // old packages
        def oldPackages = [:];        
        oldPackagesXML.'package'.each {
            packageInfo = new PackageInfo(it);
            oldPackages[packageInfo.name] = packageInfo;
        }        
        
        // new packages
        def newPackages = [:];        
        newPackagesXML.'package'.each {
            packageInfo = new PackageInfo(it);            
            newPackages[packageInfo.name] = packageInfo;
        }
        
        // changed packages
        def newPkg;
        oldPackages.each { name, pkg ->        	
            newPkg = newPackages[name]
            if ( newPkg && ( pkg != newPkg ) ) {
                results.changed << new DiffDelta(pkg,newPkg);
            }
        }
        
        // deleted packages
        def deletedPackagesList = oldPackages.keySet() - newPackages.keySet();
        deletedPackagesList.each { name ->
            results.removed << oldPackages[name];
        }
        
        // added packages
        def addedPackagesList = newPackages.keySet() - oldPackages.keySet();
        addedPackagesList.each { name ->
            results.added << newPackages[name];
        }
        m_log.info("results added[${results.added.size()}] removed[${results.removed.size()}] changed[${results.changed.size()}]");
        return results;
    }
	
    /**
     * @param section
     * @param subSection
     */
    def patchesDiff(String section, String subSection) {
        m_log.info("patchesDiff($section,$subSection)");
        // results
        def results = new DiffResults();
        
        // find packages node
        def oldPatchesXML = oldBaselineXML.sections.section.find {it.'@name' == section      
        }.subSection.find {it.'@name' == subSection}.patches;
        def newPatchesXML = newBaselineXML.sections.section.find {it.'@name' == section        
        }.subSection.find {it.'@name' == subSection}.patches;
           
        /* fingerprint diff ???
        if ( oldPatchesXML.@fingerprint.text() == newPatchesXML.@fingerprint.text() ) {
        // prints match
        results.hasChanged = false;
        return results;
        }
         */
           
        // variable
        def patchInfo;
        
        // old Patches
        def oldPatches = [:];        
        oldPatchesXML.'patch'.each {
            patchInfo = new PatchInfo(it);
            oldPatches[patchInfo.name] = patchInfo;
        }
        
        // new Patches
        def newPatches = [:];
        newPatchesXML.'patch'.each {
            patchInfo = new PatchInfo(it);
            newPatches[patchInfo.name] = patchInfo;
        }        
        
        // changed Patches
        def newPatch;
        oldPatches.each { name, patch ->
            newPatch = newPatches[name]
            if ( newPatch && ( patch != newPatch ) ) {
                results.changed << new DiffDelta(patch,newPatch);
            }
        }
        
        // deleted Patches
        def deletedPatchesList = oldPatches.keySet() - newPatches.keySet();
        deletedPatchesList.each { name ->
            results.removed << oldPatches[name];
        }
        
        // added Patches
        def addedPatchesList = newPatches.keySet() - oldPatches.keySet();
        addedPatchesList.each { name ->
            results.added << newPatches[name];
        }
        m_log.info("results added[${results.added.size()}] removed[${results.removed.size()}] changed[${results.changed.size()}]");
        return results;		
    }
	
    /**
     * @param section
     * @param subSection
     */
    def contentDiff(String section, String subSection) {
    	m_log.info("contentDiff($section,$subSection)");
        // results
        def results = new DiffResults();
        
        // find packages node
        def oldContentXML = oldBaselineXML.sections.section.find {it.'@name' == section      
        }.subSection.find {it.'@name' == subSection}.content;
        def newContentXML = newBaselineXML.sections.section.find {it.'@name' == section        
        }.subSection.find {it.'@name' == subSection}.content;
           
        // fingerprint diff
        if ( oldContentXML.@fingerprint.text() != newContentXML.@fingerprint.text() ) {
            results.hasChanged = true;
        }
        else {
            results.hasChanged = false;
        }     
        m_log.info("results deltaExists[${results.hasChanged}]");
        return results;		
    }
	
    /**
     * Delta Report
     * Examine deltas and write XML document to TARGETFILE
     */
    void deltaReport(File outputFile) {
        m_log.info("comparison starting: outputFile[${outputFile.absolutePath}]");
    	// create the builder
    	def writer = new BufferedWriter(new FileWriter(outputFile));
    	def builder = new groovy.xml.MarkupBuilder(writer);
    	
    	// missing sections    	
    	def missingSections = oldBaseline.sections.keySet() - newBaseline.sections.keySet();
    	// added sections
    	def addedSections = newBaseline.sections.keySet() - oldBaseline.sections.keySet();    	
    	
    	// objects needed to display dates in a human readable format
    	// when mtime is created for the changed files
    	def hasChanged;
    	def subsectionType;
    	def results;   	
    	   	
        // xml document creation
        builder.BaselineReportDelta(created:new Date().format(ReportsHelper.CREATED_DATE_FORMAT),
            sbVersion:ApplicationHolder.application.metadata['app.version']) {
	    	
            // describe the two reports
            report(hostname:oldBaselineXML.report.@hostname.text(),
                dist:oldBaselineXML.report.@dist.text(),
                distVersion:oldBaselineXML.report.@distVersion.text(),
                arch:oldBaselineXML.report.@arch.text(),
                kernel:oldBaselineXML.report.@kernel.text(),
                cpuInfo:oldBaselineXML.report.@cpuInfo.text(),
                totalMemory:oldBaselineXML.report.@totalMemory.text(),
                created:oldBaselineXML.report.@created.text());
	    	
            report(hostname:newBaselineXML.report.@hostname.text(),
                dist:newBaselineXML.report.@dist.text(),
                distVersion:newBaselineXML.report.@distVersion.text(),
                arch:newBaselineXML.report.@arch.text(),
                kernel:newBaselineXML.report.@kernel.text(),
                cpuInfo:newBaselineXML.report.@cpuInfo.text(),
                totalMemory:newBaselineXML.report.@totalMemory.text(),
                created:newBaselineXML.report.@created.text());
	    	
            sections() {
                // multiple sections
                oldBaseline.sections.each { sectionName, sectionObj -> // closure
	    		
                    section(name:sectionName) { // xml
	    				
                        sectionObj.subsections.each { subsectionName, subsection -> // closure
                            // get the subsection type
                            subsectionType = oldBaseline.sections[sectionName].subsections[subsectionName].type;
                            // multiple subsections
                            subSection(name:subsectionName) {

                                switch(subsectionType) {
                                    case BaselineSubSection.SubSectionType.FILES:
                                    fileGroups() {
                                        subsection.children.each {
                                            // results of files diff.
                                            results = filesDiff(sectionName,subsectionName,it);
                                            // xml element for changes
                                            fileGroup(name:it,hasChanged:results.deltaExists()) {

                                                added() {
                                                    results.added.each { addedFile ->
                                                        file(path : addedFile.path,
                                                            mode : addedFile.mode,
                                                            mtime : new Date(addedFile.mtime.toLong()*1000L).format(MTIME_DATE_FORMAT),
                                                            uid : addedFile.uid,
                                                            suid : addedFile.suid,
                                                            gid : addedFile.gid,
                                                            sgid : addedFile.sgid,
                                                            xattr : addedFile.xattr,
                                                            sha1 : addedFile.sha1)
                                                    }
                                                } // added
                                                removed() {
                                                    results.removed.each { removedFile ->
                                                        file(path : removedFile.path,
                                                            mode : removedFile.mode,
                                                            mtime : new Date(removedFile.mtime.toLong()*1000L).format(MTIME_DATE_FORMAT),
                                                            uid : removedFile.uid,
                                                            suid : removedFile.suid,
                                                            gid : removedFile.gid,
                                                            sgid : removedFile.sgid,
                                                            xattr : removedFile.xattr,
                                                            sha1 : removedFile.sha1)
                                                    }
                                                } // removed
                                                changed() {
                                                    results.changed.each { delta ->
                                                        fileDelta() {
                                                            file(path : delta.older.path,
                                                                mode : delta.older.mode,
                                                                mtime : new Date(delta.older.mtime.toLong()*1000L).format(MTIME_DATE_FORMAT),
                                                                uid : delta.older.uid,
                                                                suid : delta.older.suid,
                                                                gid : delta.older.gid,
                                                                sgid : delta.older.sgid,
                                                                xattr : delta.older.xattr,
                                                                sha1 : delta.older.sha1)
                                                            file(path : delta.newer.path,
                                                                mode : delta.newer.mode,
                                                                mtime : new Date(delta.newer.mtime.toLong()*1000L).format(MTIME_DATE_FORMAT),
                                                                uid : delta.newer.uid,
                                                                suid : delta.newer.suid,
                                                                gid : delta.newer.gid,
                                                                sgid : delta.newer.sgid,
                                                                xattr : delta.newer.xattr,
                                                                sha1 : delta.newer.sha1)
                                                        } // fileDelta
                                                    } // results.changed.each
                                                } // changed()
                                            } // fileGroup
                                        } // subsection.children.each
                                    } // fileGroups
                                    break;
                                    case BaselineSubSection.SubSectionType.PATCHES:
                                    results = patchesDiff(sectionName,subsectionName);
                                    patches(hasChanged:results.deltaExists()) {
                                        added() {
                                            results.added.each { addedPatch ->
                                                patch(name:addedPatch.name,pkg:addedPatch.pkg)
                                            }
                                        }
                                        removed() {
                                            results.removed.each { removedPatch ->
                                                patch(name:removedPatch.name,pkg:removedPatch.pkg)
                                            }
                                        }
                                        changed() {
                                            results.changed.each { changedPatch ->
                                                patchDelta() {
                                                    patch(name:changedPatch.older.name,pkg:changedPatch.older.pkg)
                                                    patch(name:changedPatch.newer.name,pkg:changedPatch.newer.pkg)
                                                }
                                            }
                                        }
                                    }
                                    break;
                                    case BaselineSubSection.SubSectionType.PACKAGES:
                                    results = packagesDiff(sectionName,subsectionName);
                                    packages(hasChanged:results.deltaExists()) {
                                        added() {
                                            results.added.each { addedPackage ->
	    											'package'(name:addedPackage.name,
                                                    release:addedPackage.release,
                                                    version:addedPackage.version,
                                                    install_localtime:addedPackage.installLocaltime,
                                                    installtime:addedPackage.installTime,
                                                    epoch:addedPackage.epoch,
                                                    summary:addedPackage.summary)
                                            }
                                        }
                                        removed() {
                                            results.removed.each { removedPackage ->
                                                    'package'(name:removedPackage.name,
                                                    release:removedPackage.release,
                                                    version:removedPackage.version,
                                                    install_localtime:removedPackage.installLocaltime,
                                                    installtime:removedPackage.installTime,
                                                    epoch:removedPackage.epoch,
                                                    summary:removedPackage.summary)
                                            }
                                        }
                                        changed() {
                                            results.changed.each { changedPackage ->
                                                packageDelta() {
                                                    	'package'(name:changedPackage.older.name,
                                                        release:changedPackage.older.release,
                                                        version:changedPackage.older.version,
                                                        install_localtime:changedPackage.older.installLocaltime,
                                                        installtime:changedPackage.older.installTime,
                                                        epoch:changedPackage.older.epoch,
                                                        summary:changedPackage.older.summary);
                                                        'package'(name:changedPackage.newer.name,
                                                        release:changedPackage.newer.release,
                                                        version:changedPackage.newer.version,
                                                        install_localtime:changedPackage.newer.installLocaltime,
                                                        installtime:changedPackage.newer.installTime,
                                                        epoch:changedPackage.newer.epoch,
                                                        summary:changedPackage.newer.summary);
                                                }
                                            }
                                        }
                                    }
                                    break;
                                    case BaselineSubSection.SubSectionType.CONTENT:
                                    results = contentDiff(sectionName,subsectionName);
                                    content(hasChanged:results.deltaExists());
                                    break;
                                } // switch()
                            } // subSection
                        } // section.subsections.each
                    } // section()
                } // sections.each
            } // sections()
        }
        m_log.info("Comparison Complete");
    }
	
    /**
     * Main method for testing
     * @param args
     * <p> args[0] the 'older' baseline</p>
     * <p> args[1] the 'newer' baseline</p>
     * <p> args[2] if specified this will be the output file</p>
     */
    static void main(args) {
        BaselineReportComparator comparator = new BaselineReportComparator(args[0],args[1]);
        def outputFile;
        if ( args.size() > 2 ) {
            outputFile = new File(args[2]);
        }
        else {
            outputFile = File.createTempFile("baseline-compare-temp",".xml");
        }
        comparator.deltaReport(outputFile);
    }
}
