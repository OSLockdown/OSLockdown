<html>
  <head>  
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
  <meta name="layout" content="main" />
  <meta name="contextSensitiveHelp" content="copying-a-sec-profile" />
  <title>Copy Profile</title>  
  <r:require modules="application, tcs_sbmodules"/>
  <r:script>
     function changeProfileName() {
       if ( $("#profileId").val() != '' ) {
         var text = $("#profileId option:selected").text();
         $("#profileName").val(text+' (copy)');
       }
     }
  </r:script>

</head>
<body id="copyProfile">
  <div id="per_page_container">
    <g:form name="copyProfile" action="performCopyProfile">
      <!-- PER-PAGE HEADER ABOVE BOTH LEFT MARGIN AND MAIN CONTENT -->
      <div class="container" id="per_page_header" title="Copy Profile">
        <div class="headerLeft">
          <h1>Copy Profile</h1>
        </div>
        <div class="headerRight">
          <g:link class="btn btn_blue" controller="profile" action="list">Cancel</g:link>
        </div>
      </div>
      <div id="yui-main">
        <div id="main_content" class="subpage">
          <div class="info half centerDiv">
            <div class="info_header">
              <h2>Select a profile to copy</h2>
            </div>
            <table>
              <tr class="prop">
                <td valign="top" class="propName" title="Profile">
                  <label for="Profile">Profile:</label>
                </td>
                <td valign="top" class="propValue">
              <g:select onChange="changeProfileName()" id="profileId" name="profileId" from="${profileList}" optionKey="id" optionValue="name" noSelection="['':'[-Select a profile-]']"/>
              </td>
              </tr>
              <tr class="prop">
                <td valign="top" class="propName" title="Copied Profile Name">
                  <label for="Location">Copied Profile Name:</label>
                </td>
                <td valign="top" class="propValue">
              <g:textField id="profileName" name="profileName" onKeyUp="limitText(this.form.profileName,35);" size="35"/>
              </td>
              </tr>
            </table>
            <div id="new" style="padding-top:0.5em;" class="buttons">
              <g:submitButton action="performCopyProfile" class="btninput" style="padding-bottom:0.5em;" name="copy" value="Copy Profile" title="Click to copy the selected profile" />
            </div>
          </div>
          </g:form>
        </div><!-- main_content -->
      </div><!-- yui-main -->
  </div><!-- per_page_container -->
</body>
</html>    
