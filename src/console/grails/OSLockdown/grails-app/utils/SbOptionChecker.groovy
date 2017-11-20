/*
 * Original file generated in 209 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 209-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * Groovy script to validate security-modules.xml and optionTypes.xml
 * 
 * This script checks to make sure that all module option types that are
 * referenced in security-modules.xml exist in optionTypes.xml
 * 
 * If the type doesn't exist in optionTypes then the gui throws exceptions
 * when it tries to display the module list.
 */

 // argument check
 if ( args.size() < 2 ) {
	 println "the script requires two arguements the first being the optionTypes.xml and the second being the security-modules.xml";
	 System.exit(1);
 }

// grab the correct file
File optionsFile = new File(args[0]);
if ( !optionsFile.exists() ) {
	println "${args[0]} does not exist";
	System.exit(1);
}

File metadataFile = new File(args[1]);
if ( !metadataFile.exists() ) {
	println "${args[1]} does not exist";
	System.exit(1);
}

// parse the security-modules.xml
def xml = new XmlSlurper().parse(metadataFile);
def moduleTypes = [];

xml.'security_modules'.'module_group'.'security_module'.configurationOptions.option.each {
	moduleTypes << it.@type.text();
}

// parse the optionTypes.xml
xml = new XmlSlurper().parse(optionsFile);
def optionTypes = [];
xml.optionType.each {
	optionTypes << it.@name.text();
}

// diff the two xml files for types that are missing
def missingOptions = moduleTypes - optionTypes;
if ( missingOptions.size() > 0 ) {
	println "There are module option types that are not described in the optionTypes.xml";
	missingOptions.each { 
		println it;
	}
}
else {
	println "No missing options";
}
