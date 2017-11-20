<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Import Results</title>
    <meta name="layout" content="main" />  
  </head>
  <body id="administration">
    <div id="per_page_container">
      <div class="container" id="per_page_header" title="Migration">
        <div class="headerLeft">
          <h1>Import Results</h1>
        </div>
      </div>
      <div id="yui-main">
        <div id="main_content" class="subpage">
          <g:render template="/migration/importResultFragment" model="['fragmentType':'User','fragmentCollection':results['user']]"/>
          <g:render template="/migration/importResultFragment" model="['fragmentType':'Upstream Notification Preferences','fragmentCollection':results['upstreamNotificationPreferences']]"/>
          <g:render template="/migration/importResultFragment" model="['fragmentType':'Upstream Notification Flag','fragmentCollection':results['upstreamNotificationFlag']]"/>
          <g:render template="/migration/importResultFragment" model="['fragmentType':'Account Preferences','fragmentCollection':results['accountPreferences']]"/>
          <g:render template="/migration/importResultFragment" model="['fragmentType':'Security Profile','fragmentCollection':results['securityProfile']]"/>
          <g:render template="/migration/importResultFragment" model="['fragmentType':'Baseline Profile','fragmentCollection':results['baselineProfile']]"/>
          <g:render template="/migration/importResultFragment" model="['fragmentType':'Processor','fragmentCollection':results['processor']]"/>
          <g:render template="/migration/importResultFragment" model="['fragmentType':'Client','fragmentCollection':results['client']]"/>
          <g:render template="/migration/importResultFragment" model="['fragmentType':'Group' ,'fragmentCollection':results['group']]"/>
          <g:render template="/migration/importResultFragment" model="['fragmentType':'Scheduled Task','fragmentCollection':results['scheduledTask']]"/>
        </div> <!-- End of main_content -->
      </div> <!-- End of yui-main -->
    </div> <!-- End of per_page_container -->
  </body>
</html>
