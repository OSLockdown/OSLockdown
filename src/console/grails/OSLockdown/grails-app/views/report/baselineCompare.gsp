
<%@ page import="com.trustedcs.sb.reports.util.ReportRenderType" %>
<%@ page import="com.trustedcs.sb.reports.util.ReportType" %>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="compare-baselines" />
    <title>Compare Baseline Reports</title>
    <r:require modules="application"/>
    <r:script modules="application">

      function showReportList(clientId,comparisonId) {
        //Create AjaxRequest object
        var ajaxRequest = new AjaxRequest('ajaxComparisonSelection');
        ajaxRequest.addNameValuePair('reportType',"${ReportType.BASELINE.ordinal()}");
        ajaxRequest.addNameValuePair('clientId',clientId);
        ajaxRequest.addNameValuePair('comparisonId',comparisonId);
        //Send the request
        ajaxRequest.sendRequest();
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
  <body id="reports">
    <div id="per_page_container">
      <div class="container" id="per_page_header" title="Compare Baseline Reports">
        <div class="headerLeft">
          <h1>Compare Baseline Reports</h1>
        </div>
      </div>
      <div id="yui-main">
        <div id="main_content" class="subpage">
          <div class="info sixty centerDiv">
            <div class="reports info_body">
              <g:form controller="report" action="compareBaselineReports" target="_blank">
                <g:hiddenField name="reportType" value="${ReportType.BASELINE_COMPARISON.ordinal()}" />
                <div class="pad1TopBtm">
                  <fieldset style="text-align:center;">
                    <legend>Selection Type</legend>
                    <div class="pad1TopBtm">
                      <g:radio onChange="javascript:viewOrCreate('new')" title="Already created baseline comparisons." name="reportSource" value="existing" checked="true"/>&nbsp;View Existing Comparison&nbsp;&nbsp;&nbsp;&nbsp;
                      <g:radio onChange="javascript:viewOrCreate('existing')" title="Create new baseline comparisons." name="reportSource" value="new"/>&nbsp;Create New Comparison
                    </div>
                  </fieldset>
                </div>
                <div id="existingReports" class="pad1Btm">
                  <fieldset style="text-align: left;">
                    <legend>Existing Report</legend>
                    <div class="pad1TopBtm center">
                      <g:select class="paddedSelect" name="dataSet" from="${existingComparisons.descendingMap().entrySet()}" optionKey="key" optionValue="value" noSelection="['':'[-Choose-]']"/>
                    </div>
                  </fieldset>
                </div>
                <div id="createReports" style="display:none;">
                  <div class="pad1Btm">
                    <fieldset style="text-align: left;">
                      <legend>Report A</legend>
                      <div class="pad1TopBtm">
                        <table>
                          <sbauth:isEnterpriseOrBulk>
                            <tr>
                              <td><label>Client:</label></td>
                              <td><g:select class="paddedSelect" onChange="javascript:showReportList(this.value,'1');" name="client1" from="${clientList}" optionKey="id" optionValue="name" noSelection="['':'-Select a Client-']" value="${params.client1}"/></td>
                            </tr>
                          </sbauth:isEnterpriseOrBulk>
                          <tr>
                            <td><label>Report:</label></td>
                            <td id="reportDiv1"><g:select class="paddedSelect" name="report1" from="${clientReportMap1.descendingMap().entrySet()}" optionKey="key" optionValue="value" noSelection="['':'-Select a Report-']" value="${params.report1}" /></td>
                          </tr>
                        </table>
                      </div>
                    </fieldset>
                  </div>
                  <div class="pad1Btm">
                    <fieldset style="text-align: left;">
                      <legend>Report B</legend>
                      <div class="pad1TopBtm">
                        <table>
                          <sbauth:isEnterpriseOrBulk>
                            <tr>
                              <td><label>Client:</label></td>
                              <td><g:select class="paddedSelect" onChange="javascript:showReportList(this.value,'2');" name="client2" from="${clientList}" optionKey="id" optionValue="name" noSelection="['':'-Select a Client-']" value="${params.client2}"/></td>
                            </tr>
                          </sbauth:isEnterpriseOrBulk>
                          <tr>
                            <td><label>Report:</label></td>
                            <td id="reportDiv2"><g:select class="paddedSelect" name="report2" from="${clientReportMap2.descendingMap().entrySet()}" optionKey="key" optionValue="value" noSelection="['':'-Select a Report-']" value="${params.report2}"/></td>
                          </tr>
                        </table>
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
