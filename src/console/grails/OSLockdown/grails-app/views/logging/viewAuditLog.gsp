
<%@ page import="com.trustedcs.sb.util.LoggingLevel" %>
<html>
  <head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
  <meta name="layout" content="main" />
  <meta name="contextSensitiveHelp" content="console-audit-log" />
  <title>Console Audit Log</title>
  <r:require modules="application"/>
  <r:script >

    function submitForm(submitType) {
      $('#submitType').val(submitType);
      $('form').submit();
    }

    function toggleSearchOptions() {
      $('#searchDetails').toggle();
    }

    var toggled=true;
    $(document).ready(function() {
      $('#searchOptions').click(function() {
        if(toggled==false) {
          $('#searchOptions').html('Filters &#x25bc;');
          toggled=true;
        }
        else {
          $('#searchOptions').html('Filters &#x25b2;');
          toggled=false;
        }
        $("#searchDetails").toggle();
        return false;
      });
    });

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
	        
  </r:script>
</head>
<body>
  <div id="per_page_container">
    <div class="container" id="per_page_header" title="Logging">
      <div class="headerLeft">
        <h1>Console Audit Log</h1>
      </div>
    </div>
    <div id="yui-main">
      <div id="main_content" class="subpage">
        <g:form name="searchAuditLog" controller="logging" action="viewAuditLog">
          <g:hiddenField name="submitType" value="" />
          <div class="info">
            <g:set var="currentFilterCount" value="${0}" />
            <div id="searchOptions" style="cursor:pointer;" class="info_header" title="Display Filters">
              <h2>Filters &#x25bc;</h2>
            </div>
            <g:set var="columnWidth" value="50%" />
            <sbauth:isEnterpriseOrBulk>
              <g:set var="columnWidth" value="33%" />
            </sbauth:isEnterpriseOrBulk>
            <div id="searchDetails" style="display:none;">
              <table>
                <tr>
                  <td style="vertical-align:top;width:${columnWidth};">
                    <fieldset style="text-align:left;">
                      <legend style="cursor:pointer;" onClick="javascript:addFilter('user');" title="">+&nbsp;User</legend>
                      <div id="userFilters">
                        <g:if test="${params.user}">
                          <g:each in="${request.getParameterValues('user')}">
                            <g:set var="currentFilterCount" value="${currentFilterCount + 1}" />
                            <div class="pad3top" id="div.filter.${currentFilterCount}" filter="user">
                              <a class="btn" href="javascript:removeFilter('user','${currentFilterCount}');">-</a>
                              <g:select class="paddedSelect" name="user" from="${userList}" optionKey="username" optionValue="username" value="${it}"/>
                            </div>
                          </g:each>
                        </g:if>
                      </div>
                    </fieldset>
                  </td>
                <sbauth:isEnterpriseOrBulk>
                  <td style="vertical-align:top;width:${columnWidth};">
                    <fieldset>
                      <legend style="cursor:pointer;" onClick="javascript:addFilter('group');" title="">+&nbsp;Group</legend>
                      <div id="groupFilters">
                        <g:if test="${params.group}">
                          <g:each in="${request.getParameterValues('group')}">
                            <g:set var="currentFilterCount" value="${currentFilterCount + 1}" />
                            <div class="pad3top" id="div.filter.${filterCount}" filter="group">
                              <a class="btn" href="javascript:removeFilter('group','${filterCount}');">-</a>
                              <g:select class="paddedSelect" name="group" from="${groupList}" optionKey="name" optionValue="name" value="${it}"/>
                            </div>
                          </g:each>
                        </g:if>
                      </div>
                    </fieldset>
                  </td>
                </sbauth:isEnterpriseOrBulk>
                <td style="vertical-align:top;width:${columnWidth};">
                  <fieldset>
                    <legend style="cursor:pointer;" onClick="javascript:addFilter('profile');" title="">+&nbsp;Profile</legend>
                    <div id="profileFilters">
                      <g:if test="${params.profile}">
                        <g:each in="${request.getParameterValues('profile')}">
                          <g:set var="currentFilterCount" value="${currentFilterCount + 1}" />
                          <div class="pad3top" id="div.filter.${filterCount}" filter="profile">
                            <a class="btn" href="javascript:removeFilter('profile','${filterCount}');">-</a>
                            <g:select class="paddedSelect" name="profile" from="${profileList}" optionKey="name" optionValue="name" value="${it}"/>
                          </div>
                        </g:each>
                      </g:if>
                    </div>
                  </fieldset>
                </td>
                </tr>
                <tr>
                  <td style="vertical-align:top;width:${columnWidth};">
                    <fieldset style="text-align:left;">
                      <legend style="cursor:pointer;" onClick="javascript:addFilter('action');" title="">+&nbsp;Action</legend>
                      <div id="actionFilters">
                        <g:if test="${params.action}">
                          <g:each in="${request.getParameterValues('action')}">
                            <g:set var="currentFilterCount" value="${currentFilterCount + 1}" />
                            <div class="pad3top" id="div.filter.${filterCount}" filter="action">
                              <a class="btn" href="javascript:removeFilter('action','${filterCount}');">-</a>
                              <g:select class="paddedSelect" name="action" from="${actionList}" value="${it}"/>
                            </div>
                          </g:each>
                        </g:if>
                      </div>
                    </fieldset>
                  </td>
                <sbauth:isEnterpriseOrBulk>
                  <td style="vertical-align:top;width:${columnWidth};">
                    <fieldset>
                      <legend style="cursor:pointer;" onClick="javascript:addFilter('client');" title="">+&nbsp;Client</legend>
                      <div id="clientFilters">
                        <g:if test="${params.client}">
                          <g:each in="${request.getParameterValues('client')}">
                            <g:set var="currentFilterCount" value="${currentFilterCount + 1}" />
                            <div class="pad3top" id="div.filter.${filterCount}" filter="client">
                              <a class="btn" href="javascript:removeFilter('client','${filterCount}');">-</a>
                              <g:select class="paddedSelect" name="client" from="${clientList}" optionKey="name" optionValue="name" value="${it}"/>
                            </div>
                          </g:each>
                        </g:if>
                      </div>
                    </fieldset>
                  </td>
                </sbauth:isEnterpriseOrBulk>
                <td style="vertical-align:top;width:${columnWidth};">
                  <fieldset>
                    <legend style="cursor:pointer;" onClick="javascript:addFilter('word');" title="">+&nbsp;Word</legend>
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
                  </fieldset>
                </td>
                </tr>
              </table>
              <div style="text-align:center;" class="info_body half centerDiv">
                <div id="displayType">
                  <g:select class="paddedSelect" name="highlight" from="${highlightOptions.entrySet()}" optionKey="key" optionValue="value" value="${params.highlight}"/>
                </div>
                <div>
                  <input type="submit" value="Search" class="btninput"  title="Click to Search" />
                </div>
              </div>
            </div>
            <g:hiddenField id="filterCount" name="filterCount" value="${currentFilterCount}" />
          </div>
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
