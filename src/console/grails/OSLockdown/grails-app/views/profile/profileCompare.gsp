<%@ page import="com.trustedcs.sb.reports.util.ReportRenderType" %>
<%@ page import="com.trustedcs.sb.reports.util.ReportType" %>
<html>
  <head>    
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="compare-profiles" />
    <title>Compare Profiles</title>
    <r:require modules="application,tcs_sbmodules"/>
    <r:script>

      function viewOrCreate(divId) {
        if ( divId == 'existing' ) {
          $('#existingReports').hide()
          $('#createReports').show()
        }
        else {
          $('#existingReports').show()
          $('#createReports').hide()
        }
      }

    </r:script>

</head>
<body id="reports">
  <div id="per_page_container">
    <div class="container" id="per_page_header" title="Compare Profiles">
      <div class="headerLeft">
        <h1>Compare Profiles</h1>
      </div>
    </div>
    <div id="yui-main">
      <div id="main_content" class="subpage">
        <div class="info half centerDiv">
          <div class="reports info_body">
            <g:form controller="profile" action="viewProfileComparison" target="_blank">
              <g:hiddenField name="reportType" value="${ReportType.PROFILE_COMPARISON.ordinal()}" />

              <div class="pad1TopBtm">
                <fieldset style="text-align:center;">
                  <legend>Selection Type</legend>
                  <div class="pad1TopBtm center">
                    <g:radio onChange="javascript:viewOrCreate('new')" title="Already created assessment comparisons." name="reportSource" value="existing" checked="true"/>&nbsp;View Existing Comparison&nbsp;&nbsp;&nbsp;&nbsp;
                    <g:radio onChange="javascript:viewOrCreate('existing')" title="Create new assessment comparisons." name="reportSource" value="new"/>&nbsp;Create New Comparison
                  </div>
                </fieldset>
              </div>

              <div id="existingReports" class="pad1Btm">
                <fieldset style="text-align: left;">
                  <legend>Existing Comparison</legend>
                  <div class="pad1TopBtm center">
                    <g:select name="dataSet" class="paddedSelect" from="${existingComparisons.descendingMap().entrySet()}" optionKey="key" optionValue="value" noSelection="['':'[-Choose a Comparison-]']"/>
                  </div>
                </fieldset>
              </div>

              <div id="createReports" style="padding-bottom:1em;display:none;">
                <div style="padding-bottom:1em;">
                  <fieldset style="text-align: left;">
                    <legend>Profile A</legend>
                    <div id="profileDiv1" class="pad1TopBtm center">
                      <label>Profile:</label><g:select class="paddedSelect" name="profile1" from="${profileList}" optionKey="id" optionValue="name" noSelection="['':'-Select a Profile-']" value="${params.profile1}" />
                    </div>
                  </fieldset>
                </div>
                <div>
                  <fieldset style="text-align: left;">
                    <legend>Profile B</legend>
                    <div id="profileDiv2" class="pad1TopBtm center">
                      <label>Profile:</label><g:select class="paddedSelect" name="profile2" from="${profileList}" optionKey="id" optionValue="name" noSelection="['':'-Select a Profile-']" value="${params.profile2}"/>
                    </div>
                  </fieldset>
                </div>
              </div>

              <div class="pad1Btm">
                <fieldset>
                  <legend>Render As</legend>
                  <div class="pad1TopBtm center">
                    <g:select class="paddedSelect" name="renderAs" from="${ReportRenderType.values()}" optionValue="displayString"/>
                  </div>
                </fieldset>
              </div>

              <div style="text-align:center;padding-bottom:0.5em;">
                <input type="submit" class="btninput" value="Create / View" title="Click to Create / View a Report" />
              </div>
            </g:form>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
