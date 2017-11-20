/*
 * Copyright 2014-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.services

import org.apache.log4j.Logger;

import com.trustedcs.sb.preferences.AccountPreferences;
import com.trustedcs.sb.exceptions.AccountPreferencesException;

import groovy.xml.StreamingMarkupBuilder;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.Result;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.stream.StreamResult;
import groovy.util.slurpersupport.GPathResult

class AccountPreferencesService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services");

    // Transactional
    boolean transactional = true

    // Reference to Grails application.
    def grailsApplication
    def auditLogService;
    def messageSource;

    // AccountPreferences related methods
    AccountPreferences getAccountPreferences()
    {
        // Don't log it, hidden application domain object
        boolean found = false
        AccountPreferences accountPreferences = AccountPreferences.get( 1 )
        if( accountPreferences != null ) {
            found = true
        }
        else{
            //
            // Create AccountPreferences 
            //
            accountPreferences = new AccountPreferences( )
            if( accountPreferences.save( flush: true ) )
            {
                found = true
            }
        }

        if( found ){
            return accountPreferences
        }
        else {
            AccountPreferencesException accountPreferencesException = new AccountPreferencesException( accountPreferences:accountPreferences )
            throw accountPreferencesException
        }
        accountPreferences.clearErrors()
    }

    /**
     * Saves the account preferences
     *
     * @param user
     */
    def save(AccountPreferences accountPreferences) {
        // save group to the database
        accountPreferences.clearErrors()
        if (accountPreferences.validate() && !accountPreferences.hasErrors() && accountPreferences.save()) {
            m_log.info("Account Preferences Saved");
        }
        else {
            m_log.error("Unable to save Account Preferences");
            accountPreferences.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new AccountPreferencesException(AccountPreferences:accountPreferences);
        }
    }

    def updateAccountPreferences(params )
    {
        AccountPreferences accountPreferences = AccountPreferences.get( 1 )
        m_log.info("Updating account password preferences")
        try {
          accountPreferences.properties = params
	      accountPreferences.lastChanged = Calendar.getInstance().getTime();
          if (accountPreferences.validate()) {
            accountPreferences.save(flush: true)
          }
        }         
        catch (Exception e) {
          AccountPreferencesException accountPreferencesException = new AccountPreferencesException( accountPreferences:accountPreferences )
          throw accountPreferencesException
        }
        return accountPreferences
    }



// We don't really care (although we probably should) about the version of the DB that created an export, but we do need the
// password aging/expiration data....

    /**
     * Creates a client from an xml fragment
     *
     * @param xmlFragment
     */
    def fromXml(GPathResult xmlFragment) {
        // create the client

    	AccountPreferences accountPreferences = getAccountPreferences();

        accountPreferences.agingEnabled              = xmlFragment?.agingEnabled.text().toBoolean();
        accountPreferences.agingEnabledForAdmin      = xmlFragment?.agingEnabledForAdmin.text().toBoolean();
        accountPreferences.minDaysBetweenChanges     = xmlFragment?.minDaysBetweenChanges.text().toInteger();
        accountPreferences.maxDaysBetweenChanges     = xmlFragment?.maxDaysBetweenChanges.text().toInteger();
        accountPreferences.numWarningDays            = xmlFragment?.numWarningDays.text().toInteger();
	    accountPreferences.maxReuse                  = xmlFragment?.maxReuse.text().toInteger();
        accountPreferences.complexityEnabled         = xmlFragment?.complexityEnabled.text().toBoolean();
        accountPreferences.complexityEnabledForAdmin = xmlFragment?.complexityEnabledForAdmin.text().toBoolean();
        accountPreferences.minimumLower              = xmlFragment?.minimumLower.text().toInteger();
        accountPreferences.minimumUpper              = xmlFragment?.minimumUpper.text().toInteger();
        accountPreferences.minimumNumber             = xmlFragment?.minimumNumber.text().toInteger();
        accountPreferences.minimumSpecial            = xmlFragment?.minimumSpecial.text().toInteger();
        accountPreferences.minimumLength             = xmlFragment?.minimumLength.text().toInteger();


        // save the preferences
	    accountPreferences.lastChanged = Calendar.getInstance().getTime();
        accountPreferences.clearErrors()
        save(accountPreferences)
        auditLogService.log("import AccountPreferences");
        // return the created group
    	return accountPreferences;
    }

    /**
    
    /**
     * Convert the client instance to xml
     *
     * @param clientInstance
     * @param includePreamble
     * @param writer
     */
    void toXml(AccountPreferences accountPreferencesInstance,boolean includePreamble,Writer writer) throws Exception {    	

        // create the builder
        def builder = new StreamingMarkupBuilder();

        // create the xml
        def createdXml = builder.bind {
            if ( includePreamble ) {
                mkp.xmlDeclaration();
            }
            accountPreferences() {
                agingEnabled(accountPreferencesInstance.agingEnabled)
                agingEnabledForAdmin(accountPreferencesInstance.agingEnabledForAdmin)
                minDaysBetweenChanges(accountPreferencesInstance.minDaysBetweenChanges)
                maxDaysBetweenChanges(accountPreferencesInstance.maxDaysBetweenChanges)
                numWarningDays(accountPreferencesInstance.numWarningDays)
		maxReuse(accountPreferencesInstance.maxReuse)
                complexityEnabled(accountPreferencesInstance.complexityEnabled)
                complexityEnabledForAdmin(accountPreferencesInstance.complexityEnabledForAdmin)
                minimumLower(accountPreferencesInstance.minimumLower)
                minimumUpper(accountPreferencesInstance.minimumUpper)
                minimumNumber(accountPreferencesInstance.minimumNumber)
                minimumSpecial(accountPreferencesInstance.minimumSpecial)
                minimumLength(accountPreferencesInstance.minimumLength)

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
     * Convert the client to be xml
     *
     * @param client
     * @param includePreamble
     * @return returns a String representation of the client's xml
     */
    String toXmlString(AccountPreferences accountPreferencesInstance, boolean includePreamble)
    throws Exception {
        StringWriter prefWriter = new StringWriter();
        toXml(accountPreferencesInstance,false,prefWriter);
        return prefWriter.toString();
    }
}
