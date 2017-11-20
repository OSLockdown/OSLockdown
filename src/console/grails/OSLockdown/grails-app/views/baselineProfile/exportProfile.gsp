<html>
  <head>  
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
  <meta name="layout" content="main" />
  <meta name="contextSensitiveHelp" content="exporting-a-baseline-profile" />
  <title>Export Baseline Profile</title>  
  <r:require modules="application, tcs_sbmodules"/>
  <r:script>
     function changeProfileName() {
       if ( $("#profileId").val() != '' ) {
         var text = $("#profileId option:selected").text();
         $("#profileName").val(text+' (export)');
       }
     }
  </r:script>

</head>
<body id="exportBaselineProfile">
  <div id="per_page_container">
    <g:form name="exportProfile" action="performExportProfile">
      <!-- PER-PAGE HEADER ABOVE BOTH LEFT MARGIN AND MAIN CONTENT -->
      <div class="container" id="per_page_header" title="Export Baseline Profile">
        <div class="headerLeft">
          <h1>Export Baseline Profile</h1>
        </div>
        <div class="headerRight">
          <g:link class="btn btn_blue" controller="baselineProfile" action="list">Cancel</g:link>
        </div>
      </div>
      <div id="yui-main">
        <div id="main_content" class="subpage">
          <div class="info half centerDiv">
            <div class="info_header">
              <h2>Select a baseline profile to export</h2>
            </div>
            <table>
              <tr class="prop">
                <td valign="top" class="propName" title="Profile">
                  <label for="Profile">Profile:</label>
                </td>
                <td valign="top" class="propValue">
              <g:select onChange="changeProfileName()" id="profileId" name="profileId" from="${profileList}" optionKey="id" optionValue="name" noSelection="['':'[-Select a baseline profile-]']"/>
              </td>
              </tr>
            </table>
            <div id="new" style="padding-top:0.5em;" class="buttons">
              <g:submitButton action="performExportProfile" class="btninput" style="padding-bottom:0.5em;" name="Export" value="Export Baseline Profile" title="Click to export the selected baseline profile" />
            </div>
            <div id="new" style="padding-top:0.5em;" class="buttons">
              <g:actionSubmit action="list"  value="Return to List" />
            </div>
          </div>
          </g:form>
        </div><!-- main_content -->
      </div><!-- yui-main -->
  </div><!-- per_page_container -->
</body>
</html>    
