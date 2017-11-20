<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Manage Account Preferences</title>
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="man-acct-prefs" />  
    <r:require modules="application"/>
    <r:script>
      // Below is the common code for Enterprise and Lock and Release

      $(document).ready(function() {
        // Mark first column header as sorted, if user did not sort any column
        markFirstColumnAsSortedIfNotUserSorted( false );

        $("table.zebra").each (function (foo,bar) {
            zebraStripTable(bar);
        });            
 
      });
    </r:script>
</head>
<body id="administration">
  <div id="per_page_container">
    <div id="per_page_header" title="Manage Account Preferences">
      <h1>Manage Account Preferences</h1>
    </div>
    <div id="yui-main">
      <div id="main_content" class="subpage">
        <g:hasErrors>
          <div class="errors">
            <g:renderErrors bean="${accprefs}" as="list" />
          </div>
        </g:hasErrors>
        <g:form controller="rbac" action="updateAccountPreferences">
          <div class="threequarters centerDiv">
            <div class="table_border">
              <fieldset>
                <legend>Password Aging</legend>
                <table class="zebra info centerDiv">
                   <tbody>
                     <tr class="stripe half">
                       <td>Aging Enabled</td>
                       <td><g:checkBox name= "agingEnabled" value="${accprefs.agingEnabled}"/></td>
                     </tr>
                     <tr class="stripe half">
                       <td>Enforce aging for the 'Admin' user also</td>
                       <td><g:checkBox name= "agingEnabledForAdmin" value="${accprefs.agingEnabledForAdmin}"/></td>
                     </tr>
                     <tr class="stripe half">
                       <td>Minimum days between changes</td>
                       <td><g:field name="minDaysBetweenChanges" type="number" value="${accprefs.minDaysBetweenChanges}" min="0" max="365"/></td>
                     </tr>
                     <tr class="stripe half">
                       <td>Maximum days between changes</td>
                       <td><g:field name="maxDaysBetweenChanges" type="number" value="${accprefs.maxDaysBetweenChanges}" min="0" max="365"/></td>
                     </tr>
                     <tr class="stripe half">
                       <td>Number of days to start warning users</td>
                       <td><g:field name="numWarningDays" type="number" value="${accprefs.numWarningDays}" min="0" max="365"/></td>
                     </tr>
                     <tr class="stripe half">
                       <td>Password reuse limit</td>
                       <td><g:field name="maxReuse" type="number" value="${accprefs.maxReuse}" min="0" max="10"/></td>
                     </tr>
                   </tbody>
                </table>
              </fieldset>
            </div>
            <div class="table_border">
              <fieldset>
                <legend>Password Complexity</legend>
                <table class="zebra info centerDiv">
                   <tbody>
                     <tr class="stripe half">
                       <td>Complexity Enabled</td>
                       <td><g:checkBox name= "complexityEnabled" value="${accprefs.complexityEnabled}"/></td>
                     </tr>
                     <tr class="stripe half">
                       <td>Enforce complexity for the 'Admin' user also</td>
                       <td><g:checkBox name= "complexityEnabledForAdmin" value="${accprefs.complexityEnabledForAdmin}"/></td>
                     </tr>
                     <tr class="stripe half">
                       <td>Minimum number of characters</td>
                       <td><g:field name="minimumLength" type="number" value="${accprefs.minimumLength}" min="0"/></td>
                     </tr>
                     <tr class="stripe half">
                       <td>Minimum number of lower case characters</td>
                       <td><g:field name="minimumLower" type="number" value="${accprefs.minimumLower}" min="0"/></td>
                     </tr>
                     <tr class="stripe half">
                       <td>Minimum number of upper case characters</td>
                       <td><g:field name="minimumUpper" type="number" value="${accprefs.minimumUpper}" min="0"/></td>
                     </tr>
                     <tr class="stripe half">
                       <td>Minimum number of numeric characters</td>
                       <td><g:field name="minimumNumber" type="number" value="${accprefs.minimumNumber}" min="0"/></td>
                     </tr>
                     <tr class="stripe half">
                       <td>Minimum number of special characters</td>
                       <td><g:field name="minimumSpecial" type="number" value="${accprefs.minimumSpecial}" min="0"/></td>
                     </tr>
                   </tbody>
                </table>
              </fieldset>
            </div>
            <div class="pad1TopBtm" style="text-align:center;">
                <g:submitButton name="exportButton" value="Update Password Preferences" class="btninput" title="Click to update the password preferences"/>
            </div>
          </g:form>


        </div>
      </div> <!-- End of main_content -->
    </div> <!-- End of yui-main -->
  </div> <!-- End of per_page_container -->
</body>
</html>
