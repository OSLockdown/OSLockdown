import com.trustedcs.sb.license.SbLicense;
import com.trustedcs.sb.util.SBDetachmentUtil;

/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2013 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
class SecurityFilters {

    def filters = {
        
        // Ensure that all controllers and actions require an authenticated user,
        // except for the "public" controller
        auth(controller: "*", action: "*") {
            before = {
                // Exclude the "public" controller.
                if (controllerName == "public") return true

                // Note: accessControl() method always returns true and does NOT do any authentication
                // or authorization checks, if (controllerName == "auth") here is how the ShiroPlugin is actually coded up :
                //
                //    // If we're accessing the auth controller itself, we don't
                //    // want to check whether the user is authenticated, otherwise
                //    // we end up in an infinite loop of redirects.
                //    if (filter.controllerName == "auth") return true
                //

                // This just means that the user must be authenticated. He does 
                // not need any particular role or permission.
                //
                //  accessControl { true }
                //
                // the { true } is the closure (Closure c below) that gets passed to the accessControlMethod()
                // and which is executed for authorization (authcRequired is true by default so it's passed as true
                // by the plugin itself); since it just returns true it's guaranteed to succeeed.
                // See line 230 of the ShiroGrailsPlugin.groovy
                //      mc.accessControl << { Closure c -> return accessControlMethod(delegate, authcRequired, [:], c) }
                //
                // BTW the default implementation done by the Shiro plugin (which is installed by default) of
                //      accessControl()
                // is actually passes no arguments, hence it's using the
                //      mc.accessControl << { -> return accessControlMethod(delegate, authcRequired) }
                // version, which uses Closure c = null (default of the accessControlMethod()). Hence, the
                // usual logic kicks in via
                //      isPermitted = subject.isPermitted(permString.toString())
                // which actually calls ShiroDbRealm.isPermitted() method that does actual heavy checks
                // for permissions on Users directly as well as their Roles.

                // Pass ensureValidLicense closure (defined later in this class), so make use of the
                //      mc.accessControl << { Closure c -> return accessControlMethod(delegate, authcRequired, [:], c) }
                // version that still checks for authentication, but executes ensureValidLicense for authorization
                // to check whether user's license is valid.

// Note: request.xhr boolean will be true (for Ajax requests) if HeaderName=X-Requested-With to Value=XMLHttpRequest is set in the request.
// 1. Using $.ajax() already sets it for Ajax requests
// 2. All usages of Taconites's AjaxRequest objects have also been updated so they set this header as well
// println " ^^^^ SecurityFilters auth section #1 ["+(new Date()).toString()+"] request ["+request+"] request.xhr ["+request.xhr+"]"

                accessControl ( ensureValidLicense )
            } 
        }
        	
        /////////////////////////////////////////////////////
        //                    PROFILE
        /////////////////////////////////////////////////////
    	// Creating, modifying, or deleting a profile requires the "Administrator" // role. 
    	profileEditing(controller: "profile", action: "*") { 
            before = {
                accessControl {
                    role("Administrator") || role("User")
                }
            }
    	}
        
        /////////////////////////////////////////////////////
        //          STANDALONE POLICY APPLICATION
        /////////////////////////////////////////////////////
        policyApplication(controller: "policyApplication", action: "*") { 
            before = {
                accessControl { 
                    role("Administrator") || role("User") || role("Security Officer") 
                } 
            } 
        }
        
        /////////////////////////////////////////////////////
        //                    CLIENT
        /////////////////////////////////////////////////////
        clientEditing(controller: "client" , action: "(delete|deleteMulti|detach|checkDetachStatus|stopDetachClients|edit|update|create|save|apply|applyMulti|undo|undoMulti)") {
            before = {
                accessControl {
                    role("Administrator") || role("User")
                }
            }
        }
        
        clientAction(controller: "client" , action: "(index|list|search|show|scan|scanMulti|baseline|baselineMulti|updateClientStatus|showAssessmentReport|showBaselineReport|autoUpdate|autoUpdateMulti)") {
            before = {
                accessControl {
                    role("User") || role("Administrator") || role("Security Officer")
                }
            }
        }
        
        clientRegistration(controller: "clientRegistrationRequest", action: "(allow|allowMulti|deny|denyMulti|hasNew)") {
            before = {
                accessControl {
                    role("User") || role("Administrator")
                }
            }
        }
        /////////////////////////////////////////////////////
        //                    PROCESSOR
        /////////////////////////////////////////////////////
        processorEditing(controller: "processor" , action: "(delete|deleteMulti|edit|update|create|save)") {
            before = {
                accessControl {
                    role("Administrator") || role("User")
                }
            }
        }
        
        processorAction(controller: "processor" , action: "(index|list|show)") {
            before = {
                accessControl {
                    role("User") || role("Administrator") || role("Security Officer")
                }
            }
        }
        
        /////////////////////////////////////////////////////
        //                    GROUPS
        /////////////////////////////////////////////////////
        groupEditing(controller: "group" , action: "(create|edit|saveGroup|deleteMulti|detach|applyMulti|undoMulti)") {
            before = {
                accessControl {
                    role("User") || role("Administrator")
                }
            }
        }
        
        groupAction(controller: "group" , action: "(index|list|scanMulti|baselineMulti|autoUpdateMulti)") {
            before = {
                accessControl {
                    role("User") || role("Administrator") || role("Security Officer")
                }
            }
        }
        
        /////////////////////////////////////////////////////
        //                   SCHEDULER
        /////////////////////////////////////////////////////
        schedulerActions(controller: "scheduler" , action: "*") {
            before = {
                accessControl {
                    role("User") || role("Administrator")
                }
            }
        }
        
        /////////////////////////////////////////////////////
        //                    REPORTS
        /////////////////////////////////////////////////////
        reportsShow(controller: "reports", action: "*") { 
            before = { 
                accessControl { 
                    role("User") || role("Administrator")  || 
                    role("Security Officer") || role("Management") 
                } 
            } 
        } 
        
        /////////////////////////////////////////////////////
        //                    HELP
        /////////////////////////////////////////////////////        
        helpInformation(controller: "help", action: "*") { 
            before = { 
                accessControl { 
                    role("User") || role("Administrator")  || 
                    role("Security Officer") || role("Management") 
                } 
            } 
        } 
    	
    	/////////////////////////////////////////////////////
    	//                    RBAC
    	/////////////////////////////////////////////////////
    	// all users should be allowed to modify their password
    	passwordModification(controller: "rbac", action: "(changePassword|savePassword)" ) {
            before = {
                accessControl {
                    role("User") || role("Administrator")  ||
                    role("Security Officer") || role("Management")
                }
            }
    	}
    	
    	// user creation and modification should be left to the administator role.
    	rbacEditing(controller: "rbac", 
            action: "(listUsers|editUser|saveUser|deleteUser|updateUser|deleteMulti)") {
            before = {
                accessControl {
                    role("Administrator")
                }
            }
    	}
    }

    // Closure that gets passed to the accessControl method for all actions and which checks whether the license is valid
    // (i.e. in the auth(controller: "*", action: "*") ). If this closure returns true, def onUnauthorized( subject, filter )
    // is *NOT* called; if this closure returns false, then def onUnauthorized( subject, filter ) *is* called
    def ensureValidLicense = {

        // If a Detach operation has already started and is in progress then don't check the validity of the license
        // (i.e. allow the Detach operation to complete even if the license expired after the Detach operation was started; this
        // will also allow these actions :
        // 1. allow the user to Stop the Detach (even if the license expired after the Detach operation started)
        // 2. allow the checkDetachStatus() checks done from ajax calls from the pages to go thru (even if the license expired after the Detach operation started)
        if( SBDetachmentUtil.getInstance().isDetachmentInProgress() ){
            return true
        } else {
            // Make a call to check if the license is valid (i.e. hasn't expired)
            return SbLicense.instance.isValid()
        }
    }

    // Define def onUnauthorized() method, so that the ShiroPlugin will call it rather than redirecting to the /auth/unauthorized.
    // This method will get called if ensureValidLicense() returns false (such as in the case of an expired license)
    //
    // ShiroPlugin checks for the existence of this method and calls it in the below lines of the plugin
    // (see ~/.grails/1.2.2/projects/OSLockdown/plugins/shiro-1.0.1/ShiroGrailsPlugin.groovy, starting at line 465
    // at the very end of the boolean accessControlMethod(filter, boolean authcRequired, Map args = [:], Closure c = null) :
    //
    //    if (!isPermitted) {
    //        // User does not have the required permission(s)
    //        if (filtersClass.metaClass.respondsTo(filtersClass, "onUnauthorized")) {   // filtersClass.metaClass is this class with onUnauthorized method defined
    //            filtersClass.onUnauthorized(subject, filter)
    //        }
    //        else {
    //            // Default behaviour is to redirect to the 'unauthorized' page.
    //            filter.redirect(controller: "auth", action: "unauthorized")
    //        }
    //
    //        return false
    //    }
    //    else {
    //        return true
    //    }
    //
    def onUnauthorized( subject, filter ){

        boolean nonExpiredLicense = SbLicense.instance.isValid()

        // filter.request.xhr == true means it's a request from an AJAX call (which will be true (for Ajax requests)
        // if HeaderName=X-Requested-With with Value=XMLHttpRequest is set in the request).
        // Don't redirect as the source AJAX page won't be changed. Instead, need to pass in special "failure" String to the
        // source AJAX page which itself would need to replace window.location (redirect) using JavaScript.
        // See tcs/common.js function checkAjaxResponseForValidity( xhr ) function that does this for BOTH :
        // a. all Ajax requests done with jQuery $.ajax()
        // b. all Taconite's Ajax requests done via AjaxRequest tcs wrapper objects (see taconite-client.js)
        if( filter.request.xhr ){

            // render (return to the $.ajax(){ complete() } logic) either an Unauthorized (not due to expired license) or
            // ExpiredLicense if license has expired String; this will be checked by the checkAjaxResponseForValidity()
            // method in the /tcs/common.js file, and if a match is found will replace the window appropriately
            // to go to either to /auth/unauthorized or /auth/expiredLicense, which will then just go thru the
            // very first auth(controller: "*", action: "*") { accessControl ( ensureValidLicense ) } *without* any
            // authentication or autorization checks and won't call onUnauthorized() again as the controllerName == "auth"
            // (which is shortcircuited, i.e. return true in the plugin)
            filter.render( nonExpiredLicense ? "unauthorized" : "expiredLicense" )
        }
        else {

            // Non-AJAX call. Redirect to the proper unauthorized page based on nonExpiredLicense; which will then just go thru the
            // very first auth(controller: "*", action: "*") { accessControl ( ensureValidLicense ) } *without* any
            // authentication or autorization checks and won't call onUnauthorized() again as the controllerName == "auth"
            // (which is shortcircuited, i.e. return true in the plugin)
            filter.redirect( controller: "auth", action: nonExpiredLicense ? "unauthorized" : "expiredLicense" )
        }
    }
}
