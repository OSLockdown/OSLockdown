
<%@ page import="com.trustedcs.sb.util.LoggingLevel" %>
<%@ page import="com.trustedcs.sb.reports.util.ReportRenderType" %>
<%@ page import="com.trustedcs.sb.reports.util.ReportType" %>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="group-assessments" />
    <title>Group Assessments</title>
    <r:require modules="application"/>
    <r:script >

      function choseGroup(groupId) {
        //Create AjaxRequest object
        var ajaxRequest = new AjaxRequest('ajaxGroupSelection');
        ajaxRequest.addNameValuePair('reportType',"${ReportType.GROUP_ASSESSMENT.ordinal()}");
        ajaxRequest.addNameValuePair('id',groupId);
        //Send the request
        ajaxRequest.sendRequest();
      }

      function setFormTarget(target) {
        $('#viewReportForm').attr('target',target);
      }

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
  <body>
    <div id="per_page_container">
      <div class="container" id="per_page_header" title="Reports">
        <div class="headerLeft">
          <h1>Group Assessments</h1>
        </div>
      </div>
      <div id="yui-main">
        <div id="main_content" class="subpage">
          <div class="info sixty centerDiv">
            <div class="reports info_body">
              <g:form target="_blank" name="viewReportForm" controller="report" action="viewGroupAssessment">
                <div class="pad1TopBtm">
                  <fieldset style="text-align:center;">
                    <legend>Selection Type</legend>
                    <div class="pad1TopBtm">
                      <g:radio onChange="javascript:viewOrCreate('new')" title="Already created group assessment report." name="reportSource" value="existing" checked="true"/>&nbsp;View Existing Group Assessment&nbsp;&nbsp;&nbsp;&nbsp;
                      <g:radio onChange="javascript:viewOrCreate('existing')" title="Create new group assessment report." name="reportSource" value="new"/>&nbsp;Create New Group Assessment
                    </div>
                  </fieldset>
                </div>
                <div id="existingReports" class="pad1Btm">
                  <fieldset>
                    <legend>Report</legend>
                    <div class="pad1TopBtm">
                      <table>
                        <tr>
                          <td><label>Group:</label></td>
                          <td><g:select class="paddedSelect" onChange="javascript:choseGroup(this.value);" name="group" from="${groupList}" optionKey="id" optionValue="name" noSelection="['':'[-Choose a Group-]']" value="${params.group}"/></td>
                        </tr>
                        <tr>
                          <td><label>Report:</label></td>
                          <td><g:select class="paddedSelect" id="reportSelectList" name="report" from="${reportMap.descendingMap().entrySet()}" optionKey="key" optionValue="value" noSelection="['':'[-Choose a Report-]']" value="${params.report}"/></td>
                        </tr>
                      </table>
                    </div>
                  </fieldset>
                </div>
                <div id="createReports" class="pad1Btm" style="display:none;">
                  <div>
                    <fieldset style="text-align: left;">
                      <legend>Report</legend>
                      <div class="pad1TopBtm">
                        <table>
                          <tr>
                            <td style="width:25%;"><label>Group:</label></td>
                            <td><g:select class="paddedSelect" onChange="javascript:choseGroup(this.value);" name="groupId" from="${groupList}" optionKey="id" optionValue="name" noSelection="['':'[-Choose a Group-]']" value="${params.group}"/></td>
                          </tr>
                          <shiro:hasAnyRole in="['Administrator','User','Security Officer']">
                          <tr>
                            <td style="width:25%;"><g:radio onchange="javascript:setFormTarget('_top');" title="New scans are done on the clients and those reports are used." name="infoSource" value="newScansOnClient" checked="true"/></td>
                            <td>From new Scans with logging level&nbsp;<g:select class="paddedSelect" name="loggingLevel" from="${LoggingLevel.displayMap().entrySet()}" title="Logging Level" optionKey="key" optionValue="value" value="${params.loggingLevel ? params.loggingLevel : 5}"/></td>
                          </tr>
                          </shiro:hasAnyRole>
                          <tr>
                            <td style="width:25%;"><g:radio onchange="javascript:setFormTarget('_blank');" title="Latest scan is retreived from the clients." name="infoSource" value="existingScansOnClient"/></td>
                            <td>Latest Scan Pulled From Client</td>
                          </tr>
                          <tr>
                            <td style="width:25%;"><g:radio onchange="javascript:setFormTarget('_blank');" title="No connection to clients." name="infoSource" value="existingScansOnDisk" /></td>
                            <td>Most Recent Scans On Disk</td>
                          </tr>
                        </table>                        
                      </div>
                    </fieldset>
                  </div>
                </div>
                <div class="pad1Btm">
                  <fieldset>
                    <legend>Render As</legend>
                    <div style="text-align:center;" class="pad1TopBtm">
                      <g:select class="paddedSelect" name="renderAs" from="${ReportRenderType.values()}" optionValue="displayString"/>
                    </div>
                  </fieldset>
                </div>
                <div style="text-align:center;">
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
