/*
 * Original file generated in 2010 by Grails v1.2.2 under the Apache 2 License.
 * Modifications are Copyright 2010-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */


package com.trustedcs.sb.services;

import org.apache.log4j.Logger;

import com.trustedcs.sb.exceptions.*;

import com.trustedcs.sb.auth.shiro.*;

import com.trustedcs.sb.license.SbLicense;

import org.apache.shiro.crypto.hash.Sha1Hash;

import com.trustedcs.sb.web.notifications.UpstreamNotificationTypeEnum;
import com.trustedcs.sb.util.SyslogAppenderLevel;
import org.apache.shiro.SecurityUtils;

import groovy.xml.StreamingMarkupBuilder;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.Result;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.stream.StreamResult;
import groovy.util.slurpersupport.GPathResult;

class RbacService {

    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.services.RbacService");

    // Transactional
    boolean transactional = true;

    // injected services
    def messageSource;
    def auditLogService;
    def upstreamNotificationService;
    
    static final String DATE_FORMAT_FOR_DB_EXPORT_IMPORT = "yyyy-MM-dd HH:mm:ss.S";

    /**
     * Saves the shiro user to the database
     *
     * @param user
     */
    def save(ShiroUser shiroUser) {
        // save group to the database
        if (!shiroUser.hasErrors() && shiroUser.save()) {
            m_log.info("User Saved");
        }
        else {
            m_log.error("Unable to save user");
            shiroUser.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new SbRbacException(shiroUser:shiroUser);
        }
    }

    /**
     * Saves the relationship between the user and its role
     *
     * @param relationship
     */
    def save(ShiroUserRoleRel relationship) {
        // save group to the database
        if (!relationship.hasErrors() && relationship.save()) {
            m_log.info("User -> Role relationship Saved");
        }
        else {
            m_log.error("Unable to save User -> Role relationship");
            relationship.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new SbRbacException(shiroUser:relationship.user,shiroRole:relationship.role);
        }
    }

    /**
    /**
     * Resets the admin user's password to 'Admin123'
     */
    def resetAdminPassword() {
        // find the admin user
        ShiroUser adminUser = ShiroUser.findByUsername("admin");
        
        def extensionsList = []
        extensionsList << "cs5Label=Result"
        extensionsList << "cs5=Admin account password reset"
        if ( adminUser ) {
            adminUser.passwordHash = new Sha1Hash("Admin123").toHex();
            // save the admin user with its reset password
            save(adminUser);
        }
        else {
            // if the admin user can't be found then there is a serious problem
            shiroUser.errors.reject("rbac.admin.not.found");
            m_log.error(messageSource.getMessage("rbac.admin.not.found",[] as Object[],null));
            extensionsList << "msg=Admin account not found"
            upstreamNotificationService.log(SyslogAppenderLevel.ERROR, UpstreamNotificationTypeEnum.USER_AUTH, "Admin Password Reset", extensionsList )
            throw new SbRbacException(shiroUser:adminUser);
        }
        upstreamNotificationService.log(SyslogAppenderLevel.WARN, UpstreamNotificationTypeEnum.USER_AUTH, "Admin Password Reset", extensionsList)

    }

    /**
     * Deletes a shiro user and role relationship
     *
     * @param relationship
     */
    def delete(ShiroUserRoleRel relationship) {
        // delete user->role relationship
        relationship.delete();
        if ( relationship.hasErrors() ) {
            relationship.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            throw new SbRbacException(message:"Unable to delete relationship",shiroRelationship:relationship);
        }
        delete(relationship.user);
    }

    /**
     * Deletes the user
     *
     * @param shiroUser
     */
    def delete(ShiroUser shiroUser) {
        // delete the user
        def extensionsList = []
        shiroUser.delete();
        extensionsList << "suser=${SecurityUtils.getSubject().principal}"
        extensionsList << "duser=${shiroUser.username}"
        extensionsList << "cs5Label=Result"
        extensionsList << "cs5=Delete user account"
        if ( shiroUser.hasErrors() ) {
            shiroUser.errors.allErrors.each { error ->
                m_log.error(messageSource.getMessage(error,null));
            }
            extensionsList << "msg=Unable to delete account"
            upstreamNotificationService.log(SyslogAppenderLevel.ERROR, UpstreamNotificationTypeEnum.USER_AUTH, "User Accounts", extensionsList)
            throw new SbRbacException(message:"Unable to delete user",shiroUser:shiroUser);
        }
        upstreamNotificationService.log(SyslogAppenderLevel.INFO, UpstreamNotificationTypeEnum.USER_AUTH, "Account Deletion", extensionsList)
    }

    /**
     * Creates a user from an xml fragment
     *
     * @param xml
     */
    def fromXml(GPathResult xmlFragment) {

        m_log.info("${xmlFragment.@role.text()} ${xmlFragment.@name.text()} ${xmlFragment.@password.text()}");

        // find the user's role
        ShiroRole shiroRole = ShiroRole.findByName(xmlFragment.@role.text());
        // create the new user

        ShiroUser shiroUser = new ShiroUser(username: xmlFragment.@name.text(), passwordHash: xmlFragment.@password.text());

        if (xmlFragment.@lastChange.text() != "") {
           shiroUser.lastChange = Date.parse( DATE_FORMAT_FOR_DB_EXPORT_IMPORT, xmlFragment.@lastChange.text())
        }
        
        if (xmlFragment.@lastLogin.text() != "" ) {
           shiroUser.lastLogin = Date.parse( DATE_FORMAT_FOR_DB_EXPORT_IMPORT, xmlFragment.@lastLogin.text())
        }

        // go pull any old hashes from the snapshot
        for ( hash in xmlFragment.oldHash) {
	   def prevHash = hash.@previousHash.text()
           def lastChange = Date.parse( DATE_FORMAT_FOR_DB_EXPORT_IMPORT, hash.@lastChange.text()) 
           shiroUser.addToOldHashes(previousHash:prevHash, lastChange:lastChange)
        }   
        // save the user
        save(shiroUser);
        // create the user -> role relationship
        ShiroUserRoleRel userRoleRelationship = new ShiroUserRoleRel(user:shiroUser,role:shiroRole);
        // save ther user -> role relationship
        save(userRoleRelationship);

        // audit trail
        auditLogService.logRbac("add","${shiroUser.username}=${shiroRole.name}");

        return userRoleRelationship;
    }

    /**
     * Convert the user->role relationship into an xml fragment
     *
     * @param relationship
     */
    def toXml(ShiroUserRoleRel relationship, boolean includePreamble, Writer writer) {
        // create the builder
        def builder = new StreamingMarkupBuilder();

        // create the xml
        def createdXml = builder.bind {
            if ( includePreamble ) {
                mkp.xmlDeclaration();
            }
            def lastChangeText=null
            def lastLoginText=null
            if (relationship.user.lastChange) {
            	lastChangeText = relationship.user.lastChange.format( DATE_FORMAT_FOR_DB_EXPORT_IMPORT )
            }
            if (relationship.user.lastLogin) {
            	lastLoginText = relationship.user.lastLogin.format( DATE_FORMAT_FOR_DB_EXPORT_IMPORT )
            }
            user(name:relationship.user.username,
                role:relationship.role.name,
                password:relationship.user.passwordHash,
                lastChange:lastChangeText,
                lastLogin:lastLoginText) {
                      relationship.user.oldHashes.each { hash ->
            	      lastChangeText = hash.lastChange.format( DATE_FORMAT_FOR_DB_EXPORT_IMPORT )
                      oldHash( previousHash:hash.previousHash, lastChange:lastChangeText)
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
     * @param relationship
     * @param includePreamble
     * @return string representation
     */
    String toXmlString(ShiroUserRoleRel relationship, boolean includePreamble) throws Exception {
        StringWriter relationshipWriter = new StringWriter();
        toXml(relationship,false,relationshipWriter);
        return relationshipWriter.toString();
    }
}
