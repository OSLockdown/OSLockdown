/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
import org.apache.shiro.authc.AuthenticationException;
import org.apache.shiro.authc.ExpiredCredentialsException;
import org.apache.shiro.authc.UsernamePasswordToken;
import org.apache.shiro.SecurityUtils;
import org.apache.shiro.crypto.hash.Sha1Hash;
import javax.servlet.http.Cookie;

import com.trustedcs.sb.util.SessionAlertUtil;
import com.trustedcs.sb.util.SBFileSystemUtil;
import com.trustedcs.sb.util.SBFileSystemUtil.SB_LOCATIONS;

import com.trustedcs.sb.auth.shiro.*;
import com.trustedcs.sb.license.SbLicense;
import com.trustedcs.sb.exceptions.SbRbacException;
import com.trustedcs.sb.preferences.AccountPreferences;

import com.trustedcs.sb.web.notifications.UpstreamNotificationTypeEnum;
import com.trustedcs.sb.util.SyslogAppenderLevel;

import org.apache.log4j.Logger;

import grails.util.Environment;

class AuthController {
    // logger
    static def m_log = Logger.getLogger("com.trustedcs.sb.web.auth.AuthController");

    // injected services
    def messageSource;
    def auditLogService;
    def rbacService;
    def accountPreferencesService;
    def upstreamNotificationService;
    private static final String ADMIN_USER = "admin";
    private static final String ADMIN_DEFAULT_PASSWORD = "Admin123";

    def index = { 
        redirect(action: 'login', params: params)
    }

    /**
     * Initial login page
     */
    def login = {
        
        if ( Environment.current == Environment.DEVELOPMENT && System.getenv("SB_BYPASS_AUTH") ) {
            redirect(action:'signIn',params:['username':ADMIN_USER,'password':ADMIN_DEFAULT_PASSWORD]);
            return;
        }

    	// login banner
    	def loginBannerFile = SBFileSystemUtil.get(SB_LOCATIONS.BANNER);
    	def warningBanner;
    	if ( loginBannerFile.exists() ) {
            warningBanner = loginBannerFile.getText();
    	}
        else {
            warningBanner = "<p>This is a placeholder warning banner, <b>with embedded tags</b></p>"
        }
    	
        return [ warningBanner:warningBanner,
            username: params.username,
            rememberMe: (params.rememberMe != null),
            targetUri: params.targetUri ]
    }

    /**
     * Sign the user into the system
     */
    def signIn = {
        def authToken = new UsernamePasswordToken(params.username, params.password)
        def extensionsList = []
        
        try {
            m_log.info("Authentication attempt for user [${params.username}] from [${request.getRemoteAddr()}].");
            // Perform the actual login. An AuthenticationException
            // will be thrown if the username is unrecognised or the
            // password is incorrect.
            SecurityUtils.subject.login(authToken);
            
            // audit log
            auditLogService.logAuthAction(params.username,"login","successful");
            def shiroUser = ShiroUser.findByUsername(params.username)
            def shiroRoleName = ShiroUserRoleRel.findByUser(shiroUser).role.name
            extensionsList << "suser=${params.username}"
            extensionsList << "spriv=${shiroRoleName}"
            extensionsList << "cs5Label=Result"
            extensionsList << "cs5=Console login"
            upstreamNotificationService.log(SyslogAppenderLevel.INFO, UpstreamNotificationTypeEnum.USER_AUTH, "User Authentication", extensionsList)
            
            // last login cookie
            // cookie interaction for last login value
	        
            // get the cookie            
            def cookieValue = g.cookie(name: "tcs.sb.lastLogin");
            def lastLogin;
            
            // get the current time
            def now = Calendar.getInstance().getTime();            
            // if the cookie exists
            if ( cookieValue ) {
                lastLogin = new Date(cookieValue.toLong());            
            }
            else {
                lastLogin = now;
            }
            
            def user = ShiroUser.findByUsername(params.username);         
            
            
            // set the value of the cookie
            def cookie = new Cookie("tcs.sb.lastLogin", now.getTime().toString());
            cookie.setPath("/OSLockdown");
            cookie.setMaxAge(2592000);                      
            response.addCookie(cookie);            
            
            // set the last login time for the user
            session.lastLogin = lastLogin;	
            session.fromLogin = true;

            // look for notifications
            SessionAlertUtil.updateAutoRegistrationCount(session);
            SessionAlertUtil.updateNotificationCount(session);

            // check to see if the user is admin and if this is their first login
            if ( requiresPasswordChange() ) {            	
            	redirect(controller:'rbac',action:'changePassword');
            	return;
            }

	        user.lastLogin = now;
    	    try {            
                rbacService.save(user);
                auditLogService.logRbac("update last login",user.username);
            } 
            catch (SbRbacException rbacException) {
                rbacException.shiroUser.errors.allErrors.each { error ->
                    flash.error += messageSource.getMessage(error,null);
                }
                redirect(action: 'login', params: m)
                return;
            }

            // If a controller redirected to this page, redirect back
            // to it. Otherwise redirect to the root URI.
            def targetUri = params.targetUri ?: "/"

            log.info "Redirecting to '${targetUri}'."
            redirect(uri: targetUri)
        }
        catch (AuthenticationException ex){
            // If we'd actually authenticated - make sure we clear those credentials
            extensionsList << "suser=${params.username}"
            extensionsList << "cs5Label=Result"
            extensionsList << "cs5=Console login"
            
            def why = ex.getMessage() ?: ex.getCause() ?: ex
            extensionsList << "msg=${why}"
            
            upstreamNotificationService.log(SyslogAppenderLevel.WARN, UpstreamNotificationTypeEnum.USER_AUTH, "User Authentication", extensionsList)
            SecurityUtils.subject?.logout()
            m_log.error("Unable to login [${params.username}] reason[${ex.message}]");
            auditLogService.logAuthAction(params.username,"login",ex.message ? ex.message : "failed");
            // Authentication failed, so display the appropriate message
            // on the login page.
            m_log.info("Authentication failure for user [${params.username}].");

            flash.error = ex.message ? ex.message : "Invalid username and/or password.";

            // Keep the username and "remember me" setting so that the
            // user doesn't have to enter them again.
            def m = [ username: params.username ]
            
            // Remember the target URI too.
            if (params.targetUri) {
                m['targetUri'] = params.targetUri
            }

            // Now redirect back to the login page.
            redirect(action: 'login', params: m)
        }
    }

    /**
     * Sign the user out of the system
     */
    def signOut = {
        // audit log
        def subject = SecurityUtils.getSubject()
        def extensionsList = []
        extensionsList << "suser=${subject.principal}"
        extensionsList << "cs5Label=Result"
        extensionsList << "cs5=Console logout"
        upstreamNotificationService.log(SyslogAppenderLevel.INFO, UpstreamNotificationTypeEnum.USER_AUTH, "User Authentication", extensionsList)
        auditLogService.logAuthAction(SecurityUtils.subject?.principal,"logout","successful");
        
        // Log the user out of the application.        
        SecurityUtils.subject?.logout()

        // For now, redirect back to the home page.
        redirect(uri: '/')
    }

    /**
     * User does not have access to the page that they are trying to reach
     */
    def unauthorized = {
        render "You do not have permission to access this page."

    	auditLogService.logAccessAction("unauthorized","failed",params.targetUri);
    }

    def expiredLicense = {
        // Ok, quickly try and reread the license, if we're really expired then
        // say so...
        SbLicense.instance.reloadLicense();
        if (SbLicense.instance.isValid()) {
            redirect(uri: '/')
        }
    }
    
    /**
     * Returns if the user requires a password change
     * @return true if the user is admin and the password is Admin123
     */
    private boolean requiresPasswordChange() {
        // if development don't require a password change
//        if ( Environment.current == Environment.DEVELOPMENT ) {
//            return false;
//        }

        // check old password
        def subject = SecurityUtils.getSubject();
        
        def user;
        user = ShiroUser.findByUsername(subject.principal);         

        AccountPreferences accountPreferences = accountPreferencesService.getAccountPreferences()
        Date now = Calendar.getInstance().getTime()
        Date lastChange = user.lastChange
        Date expireDate = lastChange + accountPreferences.maxDaysBetweenChanges
        Date warnDate = lastChange + accountPreferences.maxDaysBetweenChanges - accountPreferences.numWarningDays
        
        def delta = now.getTime() - lastChange.getTime()
        // for our use we're going to function on integral *days*, so divide the delta (in ms) by ms/day to get 
        // how many days out we are from the last change.
        def deltaToExpire = (int)(delta/86400000)
//        println "Delta      " + deltaToExpire
//        println "Now        " + now.format("E yyyy-MM-dd HH:mm z")
//        println "lastChange " + lastChange.format("E yyyy-MM-dd HH:mm z")
//        println "expireDate " + expireDate.format("E yyyy-MM-dd HH:mm z")
//        println "WarnDate   " + warnDate.format("E yyyy-MM-dd HH:mm z")
        // do password checks *only* if they are enabled, the max days between changes is at least 1 day
        // and *either* we aren't the admin user or the admin user *IS* subject to expiration

        if ( accountPreferences.agingEnabled && accountPreferences.maxDaysBetweenChanges > 1 &&
             (subject.principal != ADMIN_USER || accountPreferences.agingEnabledForAdmin) ) {
          
          def expireText = expireDate.format("'at' hh:mm a 'on' EEEE MMMM dd, yyyy")
          // for our use, we're assuming each day has 86400000 (86400 sec/day * 1000 msec/sec) milliseconds
          // first things first - are we *expired*
	  if (now > expireDate) {
             throw new ExpiredCredentialsException("Your password expired ${expireText}.  Please contact the OS Lockdown Administrator to have your password reset")
          }
          // Ok, if we're within the Warning period days of expiring, put a flash message up
          // so we can see if 
          if ((accountPreferences.numWarningDays > 0) && (now > warnDate)){
             flash.warning = "Your password expires ${expireText}.  Please change your password.  If you do not, your Console account will be locked when your password expires."
          }
        }

        if (subject.authenticated && subject.principal == ADMIN_USER) {            
            def passwordHash;
            passwordHash = new Sha1Hash(ADMIN_DEFAULT_PASSWORD).toHex();
            if ( passwordHash == user?.passwordHash ) {
                flash.warning = "${subject.principal} password is still set to default. Please change it.";
                flash.forcePasswordChange = true;
                return true;
            }        
        }
        return false;
    }

    /**
     * Sets the Notification count for the user's session so that on login the user
     * will see if they have any pending notifications
     */
    private void setNotificationCount() {
    
    }

    /**
     * Sets the auto registration count for the user's session so that on login the user
     * will see if they have any pending registration requests
     */
    private void setAutoRegistrationCount() {

    }
}
