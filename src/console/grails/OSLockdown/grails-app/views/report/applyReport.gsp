
<%@ page import="com.trustedcs.sb.reports.util.ReportRenderType" %>
<%@ page import="com.trustedcs.sb.reports.util.ReportType" %>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="apply" />
    <title>Apply Report</title>
    <r:require modules="application"/>
    <r:script>
   			
      function choiceMade() {
        //Create AjaxRequest object
        var ajaxRequest = new AjaxRequest('ajaxClientSelection');
        ajaxRequest.addNameValuePair('reportType','${ReportType.APPLY.ordinal()}');
        ajaxRequest.addNameValuePair('clientId',$('#clientId').val());
        //Send the request
        ajaxRequest.sendRequest();
      }
   											
    </r:script>
  </head>
  <body id="reports">
    <div id="per_page_container">
      <div class="container" id="per_page_header" title="Reports">
        <div class="headerLeft">
          <h1>Apply Report</h1>
        </div>
      </div>
      <div id="yui-main">
        <div id="main_content" class="subpage">
          <div class="info sixty centerDiv">
            <div class="info_body">
              <g:form name="viewReportForm" controller="report" action="viewRenderedReport" target="_blank">
                <sbauth:isEnterpriseOrBulk>
                  <div class="pad1TopBtm">
                    <fieldset>
                      <legend>Client</legend>
                      <div class="pad1TopBtm center">
                        <g:select class="paddedSelect" onChange="javascript:choiceMade();" name="clientId" from="${clientList}" optionKey="id" optionValue="name" noSelection="['':'[-Select a Client-]']" value="${params.clientId}"/>
                      </div>
                    </fieldset>
                  </div>
                </sbauth:isEnterpriseOrBulk>
                <div id="dataSetDiv" class="pad1Btm center">
                  <g:render template="/report/dataSet"/>
                </div>
                <div class="pad1Btm">
                  <fieldset>
                    <legend>Render Options</legend>
                    <div class="pad1TopBtm center">
                      <select class="paddedSelect" name="reportType" id="reportType">
                        <option value="${ReportType.APPLY.ordinal()}">${ReportType.APPLY.displayString}</option>
                      </select>
                    </div>
                  </fieldset>
                </div>
                <div>
                  <fieldset>
                    <legend>Render As</legend>
                    <div class="pad1TopBtm center">
                      <g:select class="paddedSelect" name="renderAs" from="${ReportRenderType.values()}" optionValue="displayString"/>
                    </div>
                  </fieldset>
                </div>
                <div class="pad1Top center" style="text-align:center;">
                  <input type="submit" class="btninput" value="View" title="Click to View Report" />
                </div>
              </g:form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>
