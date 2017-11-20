
<%@ page import="com.trustedcs.sb.help.OnlineHelp" %>
<%@ page import="com.trustedcs.sb.license.SbLicense" %>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
  <head>
    <title><g:layoutTitle default="OS Lockdown" /></title>
  <r:require modules="application" />
  <sbweb:styleResources/>  
  <sbweb:scriptResources/>
  <g:layoutHead />
  <r:layoutResources/>
  <r:script>
    var timeout    = 500;
    var closetimer = 0;
    var ddmenuitem = 0;

    function jsddm_open() {
      jsddm_canceltimer();
      jsddm_close();
      ddmenuitem = $(this).find('ul').css('visibility', 'visible');
    }

    function jsddm_close() {
      if(ddmenuitem) {
        ddmenuitem.css('visibility', 'hidden');
      }
    }

    function jsddm_timer() {
      closetimer = window.setTimeout(jsddm_close, timeout);
    }

    function jsddm_canceltimer() {
      if(closetimer) {
        window.clearTimeout(closetimer);
        closetimer = null;
      }
    }

    $(document).ready(function() {
      $('#jsddm > li').bind('mouseover', jsddm_open)
      $('#jsddm > li').bind('mouseout',  jsddm_timer)
    });

    <g:set var="notificationInterval" value="${grailsApplication.config?.tcs?.sb?.console?.notification?.poll?.interval?.toInteger() * 1000}"/>
    <g:set var="registrationInterval" value="${grailsApplication.config?.tcs?.sb?.console?.registration?.poll?.interval?.toInteger() * 1000}"/>

    $(document).ready(function() {
      <g:if test="${notificationInterval > 0}">
      setInterval("checkForNotifications()",${notificationInterval});
      </g:if>

      <g:if test="${registrationInterval > 0}">
      setInterval("checkForClientRegistrations()",${registrationInterval});
      </g:if>
    });
    
    $(document).ready(function() {
      var inputArray = $(":checkbox,input[type=text],input[type=password],input[type=textArea],select,input[type=radio]");
      if ( inputArray.size() > 0 ) {
        inputArray[0].focus();
      }
    });

    function checkForNotifications() {
      <shiro:hasAnyRole in="['Administrator','User','Security Officer']">
        //Create AjaxRequest object
        var ajaxRequest = new AjaxRequest("${resource(dir:'')}/notifications/hasNew");
        //Send the request
        ajaxRequest.sendRequest();
      </shiro:hasAnyRole>
    }

    function checkForClientRegistrations() {
      <shiro:hasAnyRole in="['Administrator','User']">
        //Create AjaxRequest object
        var ajaxRequest = new AjaxRequest("${resource(dir:'')}/clientRegistrationRequest/hasNew");
        //Send the request
        ajaxRequest.sendRequest();
      </shiro:hasAnyRole>
    }
  </r:script>

  <g:if test="${flash.error || error}">
    <r:script >
      $(document).ready(function() {
        alert("An error occurred - Please consult the error bar at the top of the page.");
      });
    </r:script>
  </g:if>
</head>

<body>
  <!-- Id of "doc" specifies 57.69em (equal to 750px if not scaled) width in YUI -->
  <!-- Class of "yui-t1" specifies 160px left column for nav bar in YUI -->
  <div id="doc4" class="yui-t1">
    <div id="container">
      <!-- ********************************************************* -->
      <!-- HEADER -->
      <!-- ********************************************************* -->

      <div id="hd">
        <a name="top"></a>
        <!-- This div's have images in the background and fixed sizes. -->
        <div id="head_logos">
          <div id="AppID">
            <img src="${resource(dir:'images',file:'OSLockdown_main.png')}" alt="OS Lockdown" title="OS Lockdown">
          </div>
        </div><!-- end of "head_logos" -->

        <!--User login - change password - logout-->
        <shiro:isLoggedIn>
          <div class="loggedrt" style="text-align:right;" title="Logged in as <shiro:principal/>">
            <g:render template="/dashboard/notificationHeader"/><g:render template="/dashboard/clientRegistrationHeader"/>Logged in as: <shiro:principal/>&nbsp;<g:link class="btn" controller="rbac" action="changePassword" title="Click to change your password">change password</g:link>&nbsp;<g:link class="btn"  controller="auth" action="signOut" title="Click to logout">logout</g:link></div>
        </shiro:isLoggedIn>

        <div id="navHolder">
          <ul id="jsddm">
            <!-- resource ( dir : '' ) is equivalent to the Root of the Web App -->
            <li><a title="Home" href="${resource(dir:'')}" class="home">Home</a></li>
            <shiro:isLoggedIn>

              <shiro:hasAnyRole in="['Administrator','User']">
                <li><a style="cursor:default;" href="#" title="Profiles" class="profiles">Profiles</a>
                  <ul>
                    <li><g:link title="List Security Profiles" controller="profile"         action="list"           class="profiles">Security Profiles</g:link></li>
                    <li><g:link title="List Baseline Profiles" controller="baselineProfile" action="list"           class="profiles">Baseline Profiles</g:link></li>
                    <li><g:link title="Compare Profiles"       controller="profile"         action="profileCompare" class="profiles">Compare Security Profiles</g:link></li>
                </ul>
                </li>
              </shiro:hasAnyRole>

              <sbauth:isEnterpriseOrBulk>
                <shiro:hasAnyRole in="['Administrator','User','Security Officer']">
                  <li><a style="cursor:default;" title="Clients" href="#" class="clients">Clients</a>
                    <ul>
                      <li><g:link controller="client" action="list" title="List Clients" class="clients">List Clients</g:link></li>
                  <shiro:hasAnyRole in="['Administrator','User']">
                    <li><g:link controller="clientRegistrationRequest" action="list" title="Auto Registration Requests" class="clients">Auto-Registration Requests</g:link></li>
                  </shiro:hasAnyRole>
<!--
                  <sbauth:isEnterprise>
                    <shiro:hasAnyRole in="['Administrator','User']">
                      <g:if test="${SbLicense.instance.allowProcessors()}">
                          <li><g:link controller="processor" action="list" title="List Processors" class="processors">List Processors</g:link></li>
                      </g:if>
                    </shiro:hasAnyRole>
                  </sbauth:isEnterprise>
-->
                  </ul>
                  </li>
                  <li><a title="Groups" href="${resource(dir:'group')}" class="groups">Groups</a></li>
                </shiro:hasAnyRole>
              </sbauth:isEnterpriseOrBulk>

              <shiro:hasAnyRole in="['Administrator','User','Security Officer']">
                <li><a title="Notifications" href="${resource(dir:'notifications')}" class="notifications">Notifications</a></li>
              </shiro:hasAnyRole>

              <li><a style="cursor:default;" href="#" title="Reports" class="reports">Reports</a>
                <ul>
                  <li><g:link controller="report" action="assessmentReport" title="Assessment Reports" class="reports">Assessment</g:link></li>
                  <li><g:link controller="report" action="assessmentCompare" title="Compare Assessments" class="reports">Compare Assessments</g:link></li>
                  <li><g:link controller="report" action="baselineReport" title="Baseline Reports" class="reports">Baseline</g:link></li>
                  <li><g:link controller="report" action="baselineCompare" title="Compare Baselines" class="reports">Compare Baselines</g:link></li>
                  <li><g:link controller="report" action="applyReport" title="Apply Reports" class="reports">Apply</g:link></li>
                  <li><g:link controller="report" action="undoReport" title="Undo Reports" class="reports">Undo</g:link></li>
                  <sbauth:isEnterpriseOrBulk>
                    <li><g:link controller="report" action="groupAssessmentReport" title="View Group Assessments" class="reports">Group Assessments</g:link></li>
                    <li><g:link controller="report" action="groupAssetReport" title="View Group Assets" class="reports">Group Assets</g:link></li>
                  </sbauth:isEnterpriseOrBulk>
                </ul>
              </li>

          <li><a style="cursor:default;" href="#" title="Logging" class="logging">Logging</a>
            <ul>
              <shiro:hasAnyRole in="['Administrator']">
                <li><g:link controller="logging" action="viewAuditLog" title="Console Audit Log" class="reports">Console Audit Log</g:link></li>
              </shiro:hasAnyRole>
              <sbauth:isEnterpriseOrBulk>
                <li><g:link controller="logging" action="viewSbLog" title="Client Application Logs" class="reports">Client Application Logs</g:link></li>
              </sbauth:isEnterpriseOrBulk>
              <sbauth:isStandalone>
                <li><g:link controller="logging" action="viewSbLog" title="Client Application Log" class="reports">Client Application Log</g:link></li>
              </sbauth:isStandalone>
            </ul>                                
          </li>

          <!-- Scheduler is only available in Enterprise mode, not in Bulk mode -->
          <sbauth:isEnterprise>
            <shiro:hasAnyRole in="['Administrator','User']">
              <li><g:link controller="scheduledTask" action="list" title="Scheduler" class="scheduler">Scheduler</g:link></li>
            </shiro:hasAnyRole>
          </sbauth:isEnterprise>

          <shiro:hasRole name="Administrator">
            <li><a style="cursor:default;" href="#" title="Administration" class="administration">Administration</a>
              <ul>
                <li><g:link title="Manage Users" controller="rbac" action="list" class="administration">Manage Users</g:link></li>
            <sbauth:isEnterpriseOrBulk>
              <li><g:link title="Manage Database" controller="migration" action="index" class="administration">Manage Database</g:link></li>
            </sbauth:isEnterpriseOrBulk>
              <li><g:link title="Manage Account Preferences" controller="rbac" action="accountPreferences" class="administration">Manage Account Preferences</g:link></li>
              <li><g:link title="Manage Upstream Notification Preferences" controller="rbac" action="upstreamNotificationPreferences" class="administration">Manage Upstream Notification Preferences</g:link></li>
                <li><g:link title="Refresh License" controller="auth" action="expiredLicense" class="administration">Refresh License</g:link></li>
            </ul>
            </li>
          </shiro:hasRole>

          </shiro:isLoggedIn>
          <li><a target="_blank" style="cursor:help;" href="${resource(dir:'sbhelp/admin',file:OnlineHelp.adminHtmlFile(pageProperty(name:'meta.contextSensitiveHelp')?.toString()))}" title="Help" class="help">Help</a>
            <ul>
              <li><g:link controller="help" action="info" title="General Information" class="help">General Information</g:link></li>
          </ul>
          </li>
          </ul>
        </div><!-- navHolder -->
      </div><!-- end of "hd" -->

      <!-- ********************************************************* -->
      <!-- BODY -->
      <!-- ********************************************************* -->

      <div id="bd">
        <!-- Merge in the body from the specific page into this SiteMesh layout template -->
        <g:render template="/common/flashMessage"/>
        <noscript>
          <div class="errors">
            <p>Javascript has been disabled on this browser.</p>
            <p>The OS Lockdown Console requires Javascript in order to function fully.</p>
            <p>Please enable this feature on your browser.</p>
          </div>
        </noscript>
        <g:layoutBody />
      </div><!-- end of "bd" -->


      <!-- ********************************************************* -->
      <!-- FOOTER -->
      <!-- ********************************************************* -->

      <div id="ft">
        <p>
	  OS Lockdown <g:meta name="app.version"/>
        </p>
      </div><!-- end of "ft" -->
    </div><!-- end of "container" -->
  </div><!-- end of "doc" -->

<r:layoutResources />
</body>	
</html>
