/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

import org.apache.shiro.crypto.hash.Sha1Hash;
import org.apache.shiro.SecurityUtils;
import org.apache.log4j.Logger;

import java.util.regex.Pattern
import com.trustedcs.sb.auth.shiro.*;

import com.trustedcs.sb.exceptions.SbRbacException;

import com.trustedcs.sb.license.SbLicense;
import org.hibernate.criterion.Order
import org.codehaus.groovy.grails.commons.DefaultGrailsDomainClass

import com.trustedcs.sb.preferences.AccountPreferences;
import com.trustedcs.sb.preferences.UpstreamNotificationPreferences;
import com.trustedcs.sb.preferences.UpstreamNotificationFlag;

import com.trustedcs.sb.util.SyslogAppenderLevel
import com.trustedcs.sb.web.notifications.UpstreamNotificationTypeEnum;
class RbacController {
    
    //  logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.web.rbac");

    // injected services
    def messageSource;
    def rbacService;
    def auditLogService;
    def accountPreferencesService;
    def upstreamNotificationPreferencesService;
    def upstreamNotificationService
    def periodicService
    
    private static final String ADMIN_USER = "admin";
    
    def index = { 
        redirect(action: 'list', params: params)
    }
    
    def list = {

        def offset = params.offset ? params.offset : "0"
        def max    = params.max    ? params.max    : "25"

        // sort and sortOrder parameters are optional and will only be set
        // if user clicks on column headers in the table. However, only use valid sort and sortOrder in case user enters invalid values
        def sort         = ( params.sort == "username" || params.sort == "role" ) ? params.sort : "username"
        def sortOrder    = ( params.order == "asc" || params.order == "desc" ) ? params.order : "asc"

        def userRoleList =
            ShiroUserRoleRel.createCriteria().list( offset:offset, max:max ) {
                if( sort == "role" ){
                    createAlias('role', '_role',org.hibernate.criterion.CriteriaSpecification.LEFT_JOIN)
                    order( new Order("_role.name", sortOrder=="asc").ignoreCase() )
                }
                createAlias ('user', '_user',org.hibernate.criterion.CriteriaSpecification.LEFT_JOIN)
                order( new Order("_user.username", sortOrder=="asc").ignoreCase() ) 
            }

        [userRoleList:userRoleList, maxPerPage:max]
    }
    
    def deleteMulti = {
        clearFlash();
        def ids = request.getParameterValues('idList')?.collect {
            it.toLong();
        }
        
        m_log.info("Ids to delete $ids");
        ShiroUserRoleRel relationship;
        ids.each { id ->
            // find the relationshipo
            relationship = ShiroUserRoleRel.get(id);
            try {
                // delete using the service
                rbacService.delete(relationship);
                // audit trail
                auditLogService.logRbac("delete",relationship.user.username);
            }
            catch ( SbRbacException rbacException ) {
                // check to see if the relationship has errors deleteing
                rbacException.shiroRelationship?.errors.allErrors.each { error ->
                    flash.error += messageSource.getMessage(error,null);
                }
                // check to see if the user has errors deleteing
                rbacException.shiroUser?.errors.allErrors.each { error ->
                    flash.error += messageSource.getMessage(error,null);
                }
            }
        }
        // redirect back the list
        redirect(controller:"rbac",action:"list")
    }

    /**
     * Displays the change password page
     */
    def changePassword = {
    // nothing to send in the model
        m_log.info("changePassword");
    }

    boolean newPasswordAcceptable(ShiroUser user, String candidate, String candidateHash) {
        
        AccountPreferences accountPreferences = accountPreferencesService.getAccountPreferences()
         
        def agingSatisfied      = (accountPreferences.agingEnabled)      ? checkPasswordAging(accountPreferences, user, candidate, candidateHash) : true;

        def complexitySatisfied = (accountPreferences.complexityEnabled) ? checkPasswordComplexity(accountPreferences, candidate) : true;
        def passwordAcceptable = true
        
        if (!agingSatisfied || !complexitySatisfied ) passwordAcceptable = false
        return passwordAcceptable
    }
        
    boolean checkPasswordAging(AccountPreferences accountPreferences, ShiroUser user, String candidate, String candidateHash) {
    
        def errorList = []
        boolean agingSatisfied = true

        // need to see if we *are* the 'admin' user - not just an administrator....
        
        def subject = SecurityUtils.getSubject();

        // if we are the administrator, and password/aging does *not* apply to us, then blindly accept it
    
        if (subject.principal == ADMIN_USER && !accountPreferences.agingEnabledForAdmin) return true;

        Date now = Calendar.getInstance().getTime()
        Date lastChange = user.lastChange
        def deltaTime = now - lastChange
        if ((accountPreferences.minDaysBetweenChanges > 0) && (deltaTime < accountPreferences.minDaysBetweenChanges)) {
            errorList << messageSource.getMessage("rbac.password.aging.too.soon", [accountPreferences.minDaysBetweenChanges] as Object[], null)
        }

//        user.oldHashes.each { 
//            println "Old -> " + it.previousHash
//        }
//        println "FOO = "+user.hashUsed(candidateHash)
        if ((accountPreferences.maxReuse > 0 ) && (candidateHash) && user.hashUsed(candidateHash)) 
        {
          errorList << messageSource.getMessage("rbac.password.aging.password.already.used",null, null)
          
        }        
        if (errorList)
        {
          flash.error.addAll(errorList)
          agingSatisfied = false
        }
        
        return agingSatisfied;
    }

        boolean checkPasswordComplexity(AccountPreferences accountPreferences, String candidate) {
        List errorList = []
        boolean complexitySatisfied = true
        def subject = SecurityUtils.getSubject();

        // if we are the administrator, and complexity/aging does *not* apply to us, then blindly accept it
        if (subject.principal == ADMIN_USER && !accountPreferences.complexityEnabledForAdmin) return true;

        def countLength = candidate.length()

        def countNumbers = Pattern.compile("\\p{Digit}").matcher(candidate).getCount()
        def countUpper   = Pattern.compile("\\p{Upper}").matcher(candidate).getCount()
        def countLower   = Pattern.compile("\\p{Lower}").matcher(candidate).getCount()
        def countSpecial = Pattern.compile("\\p{Punct}").matcher(candidate).getCount()

        if ((countLength - accountPreferences.minimumLength) < 0) {
          errorList << messageSource.getMessage("rbac.password.complexity.error.length",[accountPreferences.minimumLength] as Object[], null)
        }
        if ((countNumbers - accountPreferences.minimumNumber) < 0) {
          errorList << messageSource.getMessage("rbac.password.complexity.error.number",[accountPreferences.minimumNumber] as Object[], null)
        }
        if ((countUpper - accountPreferences.minimumUpper) < 0) {
          errorList << messageSource.getMessage("rbac.password.complexity.error.upper",[accountPreferences.minimumUpper] as Object[], null)
        }
        if ((countLower - accountPreferences.minimumLower) < 0) {
          errorList << messageSource.getMessage("rbac.password.complexity.error.lower",[accountPreferences.minimumLower] as Object[], null)
        }
        if ((countSpecial - accountPreferences.minimumSpecial) < 0) {
          errorList << messageSource.getMessage("rbac.password.complexity.error.special",[accountPreferences.minimumSpecial] as Object[], null)
        }
//        println("Password length=${countLength}, numbers=${countNumbers}, upper=${countUpper}, lower=${countLower}, special=${countSpecial}")

        // Old complexity requirements
//        complex = candidate ==~ /^.*(?=.{6,})(?=.*[A-Z])(?=.*[\d]).*$/;
//        if (!complex)
//           errorList << messageSource.getMessage("rbac.password.complexity.error",null,null);

        if (errorList)
        {
          flash.error.addAll(errorList)
          complexitySatisfied = false
        }
        
    return complexitySatisfied
    }


    /**
     * Updates the currently logged in user's password with the information
     * passed to the controller
     */
    def updatePassword = {
        clearFlash();
        // check old password
        def subject = SecurityUtils.getSubject();
        def user;
        def passwordHash;
        passwordHash = new Sha1Hash(params.currentPassword).toHex();
        
        if (subject.authenticated) {
            user = ShiroUser.findByUsername(subject.principal)
        }
        if ( passwordHash != user.passwordHash ) {
            flash.error += messageSource.getMessage("rbac.password.current.error",null,null);
            redirect(controller:"rbac",action:"changePassword");
            return;
        }
        
        // Users may not assign empty passwords
        if ( params.newPassword == "")
        {
            flash.error += messageSource.getMessage("rbac.password.empty.forbidden",null,null);
            redirect(controller:"rbac",action:"changePassword");
            return;        }
        
        // check new password against reentered password
        if ( params.newPassword != params.reenteredPassword ) {
            flash.error += messageSource.getMessage("rbac.password.reenter.error",null,null);
            redirect(controller:"rbac",action:"changePassword");
            return;
        }

       
        // update the password in the database
        passwordHash = new Sha1Hash(params.newPassword).toHex();

        // test new password
        if ( !newPasswordAcceptable(user, params.newPassword, passwordHash) ) {
            redirect(controller:"rbac",action:"changePassword");
            return;
        }
        
        // update password history
        updatePasswordFields(user, passwordHash)
        
        def shiroUser = ShiroUser.findByUsername(user.username)
        def shiroRoleName = ShiroUserRoleRel.findByUser(shiroUser).role.name
        try {            
            rbacService.save(user);
            auditLogService.logRbac("change password",user.username);
        } 
        catch (SbRbacException rbacException) {
            rbacException.shiroUser.errors.allErrors.each { error ->
                flash.error += messageSource.getMessage(error,null);
            }
            redirect(controller:"rbac",action:"changePassword");
            return;
        }
        def extensionsList = []
        extensionsList << "suser=${SecurityUtils.getSubject().principal}"
        extensionsList << "duser=${user.username}"
        extensionsList << "dpriv=${shiroRoleName}"
        extensionsList << "cs5Label=Result"
        extensionsList << "cs5=Password changed"
        upstreamNotificationService.log(SyslogAppenderLevel.INFO, UpstreamNotificationTypeEnum.USER_AUTH, "User Accounts", extensionsList)
        
        auditLogService.logRbac('change password',user.username);
        redirect(uri: '/');
    }

    /**
     * Create a new user
     */
    def create = {
        ShiroUserRoleRel userRoleRel = new ShiroUserRoleRel();
        [userRoleRel:userRoleRel,roles:ShiroRole.list()]
    }


    void updatePasswordFields(ShiroUser user, String newHash)
    {

        AccountPreferences accountPreferences = accountPreferencesService.getAccountPreferences()
       // Trim *existing* count of retained passwords to at most maxReuse

//        println "updateFields ${user.countOldHashes()} ${accountPreferences.maxReuse}"
        if (user.countOldHashes() >= accountPreferences.maxReuse) 
        {
          // get all of our previous hashes, sorted by when it was set
          def allPreviousHashesForUser = user.oldHashes.asList().sort{it.lastChange}

          // now figure out what elements need to go away
          // do this by starting at the beginning and walkup up until we are 'maxReuse' from the end, and give us those ids
          def idsToDelete = allPreviousHashesForUser[0..-accountPreferences.maxReuse].collect { it.id }
          
          // Get *those* elements
          def hashesToDelete = OldHash.getAll(idsToDelete)
          
          // And delete 'em
          hashesToDelete.each { oldHash ->
            user.removeFromOldHashes(oldHash)
          }
        }

        user.addToOldHashes(previousHash:user.passwordHash, lastChange:user.lastChange)
        user.passwordHash = newHash
        user.lastChange = Calendar.getInstance().getTime();
        
    }

    /**
     * Edit the selected user
     */
    def edit = {
        def userRoleRel;
        def user;
        if ( params.id ) {
            userRoleRel = ShiroUserRoleRel.get(params.id);
            user = ShiroUser.get(params.id);
        }
        [userRoleRel:userRoleRel,roles:ShiroRole.list(), isBulk:SbLicense.instance.isBulk(), lastLogin:user.lastLogin, lastChange:user.lastChange]
    }

    /**
     * Save the newly created user
     */
    def save = {
        clearFlash();
        ShiroUserRoleRel relationship = new ShiroUserRoleRel();
        ShiroRole shiroRole = ShiroRole.get(params.role);

        // password complexity
        // check password
        if ( params.password != params.reenteredPassword ) {
            flash.error = messageSource.getMessage("rbac.password.reenter.error",null,null);
            redirect(controller:"rbac",action:"create",params:params);
            return;
        }

        // mini trial does not use hashed passwords
        ShiroUser shiroUser
        shiroUser = new ShiroUser(username: params.name, passwordHash: new Sha1Hash(params.password).toHex());

        if ( !newPasswordAcceptable(shiroUser, params.password, null)) {
            redirect(controller:"rbac",action:"create",params:params);
            return;
        }

        // save the user
        try {
            shiroUser.lastChange = Calendar.getInstance().getTime()
            rbacService.save(shiroUser);
        }
        catch ( SbRbacException rbacException ) {
            rbacException.shiroUser.errors.allErrors.each { error ->
                flash.error += messageSource.getMessage(error,null);
            }
            redirect(controller:"rbac",action:"create",params:params);
            return;
        }

        // save the relationship
        try {
            relationship = new ShiroUserRoleRel(user:shiroUser,role:shiroRole);
            rbacService.save(relationship);
        }
        catch ( SbRbacException rbacException ) {
            rbacException.shiroRelationship.errors.allErrors.each { error ->
                flash.error += messageSource.getMessage(error,null);
            }
            redirect(controller:"rbac",action:"create",params:params);
            return;
        }

        auditLogService.logRbac("add","${shiroUser.username}=${shiroRole.name}");
        def extensionsList =  []
        extensionsList << "suser=${SecurityUtils.getSubject().principal}"
        extensionsList << "duser=${shiroUser.username}"
        extensionsList << "dpriv=${shiroRole.name}"
        extensionsList << "cs5Label=Result"
        extensionsList << "cs5=Account creation"
        upstreamNotificationService.log(SyslogAppenderLevel.INFO, UpstreamNotificationTypeEnum.USER_AUTH, "User Accounts", extensionsList)
        redirect(controller:"rbac",action:"list",params:params);
    }

    /**
     * Update the user with any configuration changes
     */
    def update = {      
        clearFlash();
        
        // get the relationship, user, role
        ShiroUserRoleRel relationship = ShiroUserRoleRel.get(params.id);
        ShiroUser shiroUser = relationship.user;
        ShiroRole shiroRole = ShiroRole.get(params.role);
        def extensionsList = []
        extensionsList << "suser=${SecurityUtils.getSubject().principal}"
        extensionsList << "duser=${shiroUser.username}"
        extensionsList << "dpriv=${shiroRole.name}"
        
        // check to see if the password is going to be changed
        // Note that means that an *empty* password is forbidden here
        if ( params.password ) {
            // password complexity

            // the hashed password
            String passwordHash;
            // passwords for mini trials are not hash encoded
            passwordHash = new Sha1Hash(params.password).toHex();


            // check password
            if ( params.password != params.reenteredPassword ) {
                flash.error += messageSource.getMessage("rbac.password.reenter.error",null,null);
                redirect(controller:"rbac",action:"edit",params:params);
                return;
            }

            // if the password changed then we need to save the shiro user
            if ( shiroUser.passwordHash != passwordHash ) {
                // set the hashed password on the shiro user
                if ( !newPasswordAcceptable(shiroUser, params.password, passwordHash) ) {
                    redirect(controller:"rbac",action:"edit",params:params);
                    return;
                }
                updatePasswordFields(shiroUser, passwordHash)
                try {
                    // save the user using the service
                    rbacService.save(shiroUser);
                    auditLogService.logRbac("change password",shiroUser.username);
                    def extras=[]
                    extras << "cs5Label=Result"
                    extras << "cs5=Password changed"
                    upstreamNotificationService.log(SyslogAppenderLevel.INFO, UpstreamNotificationTypeEnum.USER_AUTH, "User Accounts", extensionsList + extras)
                }
                catch ( SbRbacException rbacException ) {
                    rbacException.shiroUser.errors.allErrors.each { error ->
                        flash.error += messageSource.getMessage(error,null);
                    }
                    redirect(controller:"rbac",action:"edit",params:params);
                    return;
                }
            }
            else
            {
              flash.error += messageSource.getMessage("rbac.password.same.as.current",null,null);
              redirect(controller:"rbac",action:"edit",params:params);
              return;
            }
        }

        // save the user role relationship for the tuple
        try {
            if (relationship.role != shiroRole)
            {
              def extras = []
              extras << "cs5Label=Result"
              extras << "cs5=Role changed"
              upstreamNotificationService.log(SyslogAppenderLevel.INFO, UpstreamNotificationTypeEnum.USER_AUTH, "User Accounts",  extensionsList + extras)
            }
            relationship.user = shiroUser;
            relationship.role = shiroRole;

            rbacService.save(relationship);
        } 
        catch (Exception e) {
            rbacException.shiroRelationship.errors.allErrors.each { error ->
                flash.error += messageSource.getMessage(error,null);
            }
            redirect(controller:"rbac",action:"edit",params:params);
            return;
        }

        auditLogService.logRbac("modify","${shiroUser.username}=${shiroRole.name}");
        redirect(controller:"rbac",action:"list");
    }

    /**
     * Clear the flash of any messages that could have been from before
     */
    void clearFlash() {
        flash.message = [];
        flash.warning = [];
        flash.error = [];
    }

    /**
     *  Next two closures are for dealing with account preferences
     */
    
    def accountPreferences = {
        def currentPreferences = accountPreferencesService.getAccountPreferences()
        [ accprefs:currentPreferences ]        
    }
    
    def updateAccountPreferences = {
        def accprefs =  accountPreferencesService.updateAccountPreferences(params)
        if (accprefs.hasErrors()) {
            render (view: "accountpreferences", model:[accprefs:accprefs])
        }
        else
        {
          redirect(controller:"rbac",action:"list");
        }
    }

    /**
     *  Next two closures are for dealing with upstream notifications preferences
     */
    
    def upstreamNotificationPreferences = {
        def currentPreferences = upstreamNotificationPreferencesService.getUpstreamNotificationPreferences()
        def (triggerFlags, periodicFlags)  = upstreamNotificationPreferencesService.getUpstreamNotificationFlags()
        [ upstreamprefs:currentPreferences , triggerFlags:triggerFlags, periodicFlags:periodicFlags]        
    }
    
    def updateUpstreamNotificationPreferences = {
        def upstreamprefs =  upstreamNotificationPreferencesService.updateUpstreamNotificationPreferences(params)
        if (upstreamprefs.hasErrors()) {
            render (view: "upstreamnotificationpreferences", model:[upstreamprefs:upstreamprefs])
        }
        else
        {
          redirect(controller:"rbac",action:"upstreamNotificationPreferences");
        }
    }
}

