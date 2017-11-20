
<%@ page import="com.trustedcs.sb.util.LoggingLevel" %>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="client-app-logs" />
    <title>Client Application Log</title>
    <r:require modules="application"/>
    <r:script>
      function submitForm(submitType) {
        $('#submitType').val(submitType);
        $('form').submit();
      }

      function addFilter(filterType) {
        //Create AjaxRequest object
        var ajaxRequest = new AjaxRequest('addFilter');
        ajaxRequest.addNameValuePair('filterType',filterType);
        ajaxRequest.addFormElementsById('filterCount');
        //Send the request
        ajaxRequest.sendRequest();
      }

      function removeFilter(filterType,filterId) {
        //Create AjaxRequest object
        var ajaxRequest = new AjaxRequest('removeFilter');
        ajaxRequest.addNameValuePair('filterId',filterId);
        ajaxRequest.addNameValuePair('filterType',filterType);
        ajaxRequest.addFormElementsById('filterCount');
        //Send the request
        ajaxRequest.sendRequest();
      }

      var toggled=true;
      $(document).ready(function() {
        $('#flipper').click(function() {
           if(toggled==false) {
               $('#flipper').html('Filters &#x25bc;');
               toggled=true;
           }
           else {
               $('#flipper').html('Filters &#x25b2;');
               toggled=false;
           }
           $("#searchDetails").toggle();
           return false;
        });
      });
    </r:script>
  </head>
  <body>
    <div id="per_page_container">
      <div class="container" id="per_page_header" title="Logging">
        <div>
          <h1>Client Application Log > ${clientName}</h1>
        </div>
      </div>
      <div id="yui-main">
        <div id="main_content" class="subpage">
          <g:form name="searchAuditLog" controller="logging" action="viewSbLog">
            <g:hiddenField name="submitType" value="" />
            <div class="info">
              <div id="searchOptions" style="cursor:pointer;" class="info_header" title="Display Options">
                <g:set var="currentFilterCount" value="${0}" />
                <sbauth:isStandalone>
                  <span id="flipper">Filters &#x25bc;</span>
                </sbauth:isStandalone>
                <sbauth:isEnterpriseOrBulk>
                  <table style="padding:0 0 0 0;">
                    <tr style="padding:0 0 0 0;">
                      <td style="text-align:left;padding:0 0 0 0;">
                        <span id="flipper">Filters &#x25bc;</span>
                      </td>
                      <td style="text-align:right;padding:0 0 0 0;">
                    <g:select class="paddedSelect" name="clientId" onChange="javascript:submitForm('client');" from="${clientList}" optionKey="${{it?.id?.toString()}}"  optionValue="name" noSelection="['':'[-Select A Client-]']" value="${params.clientId}" />
                    </td>
                    </tr>
                  </table>
                </sbauth:isEnterpriseOrBulk>
              </div>
              <table id="searchDetails" class="info_body" style="display:none;">
                <tr>
                  <td style="width:50%;vertical-align:top;text-align:left;">
                    <fieldset>
                      <legend style="cursor:pointer;" onClick="javascript:addFilter('module');" title="">+&nbsp;Module</legend>
                      <div id="moduleFilters">
                        <g:if test="${params.module}">
                          <g:each in="${request.getParameterValues('module')}">
                            <g:set var="currentFilterCount" value="${currentFilterCount + 1}" />
                            <div class="pad3top" id="div.filter.${filterCount}" filter="word">
                              <a class="btn" href="javascript:removeFilter('module','${filterCount}');">-</a>
                              <g:select class="paddedSelect" name="module" from="${modules}" optionKey="library" optionValue="name" value="${it}"/>
                            </div>
                          </g:each>
                        </g:if>
                      </div>
                    </fieldset>
                  </td>
                  <td style="width:50%;vertical-align:top;">
                    <fieldset>
                      <legend style="cursor:pointer;" onClick="javascript:addFilter('word');" title="">+&nbsp;Word</legend>
                      <div id="wordFilters">
                        <div id="wordFilters">
                          <g:if test="${params.word}">
                            <g:each in="${request.getParameterValues('word')}">
                              <g:set var="currentFilterCount" value="${currentFilterCount + 1}" />
                              <div class="pad3top" id="div.filter.${filterCount}" filter="word">
                                <a class="btn" href="javascript:removeFilter('word','${filterCount}');">-</a>
                                <g:textField name="word" size="20" value="${it}"/>
                              </div>
                            </g:each>
                          </g:if>
                        </div>
                      </div>
                    </fieldset>
                  </td>
                </tr>
                <tr>
                  <td title="Select Logging Level"><g:select class="paddedSelect" name="level" from="${LoggingLevel.displayMap().entrySet()}" optionKey="key" optionValue="value" value="${params.level}" noSelection="['':'[-All Logging Levels-]']" /></td>
                <td title="Select Display Type"><g:select class="paddedSelect" name="highlight" from="${highlightOptions.entrySet()}" optionKey="key" optionValue="value" value="${params.highlight}"/></td>
                </tr>
                <tr>
                  <td style="text-align:right;padding-bottom:0.5em;">
                    <input type="submit" value="Search" class="btninput"  title="Click to Search" />
                  </td>
                  <td style="text-align:left;padding-bottom:0.5em;">
                    <button onClick="javascript:submitForm('refreshLog');" type="button" value="Refresh Log" class="btninput" title="Click to Refresh the Log" />Refresh Log</button>
                  </td>
                </tr>
              </table>
            </div>
            <g:hiddenField id="filterCount" name="filterCount" value="${currentFilterCount}" />
          </g:form>
          <div class="info">
            <div class="logcontent" title="Log Content Details">
            <g:each in="${logContents}">
	      <g:if test="${it.highlight}">
	        <pre><span style='background-color:yellow;'>${it.line}</span></pre>
	      </g:if>
	      <g:else>
	        <pre>${it.line}</pre>
	      </g:else>
	    </g:each>
            </div>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>
