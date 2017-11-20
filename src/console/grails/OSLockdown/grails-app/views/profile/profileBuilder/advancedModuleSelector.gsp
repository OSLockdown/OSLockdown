
<%@ page import="com.trustedcs.sb.metadata.SecurityModule" %>
<g:set var="isNew" value="${ profile?.id ? false : true }"/>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="searching-for-modules" />
    <title>
      <g:if test="${isNew}" >
            Create Profile > ${ profile.name ? profile.name : "Unspecified" } > Add/Remove Modules > Search For Modules
    </g:if>
    <g:else>
      Edit Profile > ${ profile.name ? profile.name : "Unspecified" } > Add/Remove Modules > Search for Modules
    </g:else>
  </title>  
  <r:require modules="application,tcs_sbmodules"/>
  <r:script>		
    function addFilter(type) {
      //Create AjaxRequest object
      var ajaxRequest = new AjaxRequest('addSearchFilter');
      ajaxRequest.addNameValuePair('type',type);
      ajaxRequest.addFormElementsById('filterCount');
      ajaxRequest.addFormElementsById(type+'Count');
      //Send the request
      ajaxRequest.sendRequest();
    }
			
    function removeFilter(type,id) {
      //Create AjaxRequest object
      var ajaxRequest = new AjaxRequest('removeSearchFilter');
      ajaxRequest.addNameValuePair('filterId',id);
      ajaxRequest.addFormElementsById(type+'Count');
      ajaxRequest.addNameValuePair('type',type);
      //Send the request
      ajaxRequest.sendRequest();
    }

    $(document).ready(function() {
      $("#selectionCheckbox").click(function() {
        if ( $('#selectionCheckbox').attr('checked') ) {
         checkAllBoxes("updateProfileForm");
        }
        else {
         uncheckAllBoxes("updateProfileForm");
        }
      })
    });

    function checkModuleSelectionCount() {
      if ( $(":checkbox:checked").length == 0 ) {
        return !(confirm('No modules were selected to be added do you wish to return to search page?'));
      }
    }
						
  </r:script>

</head>
<body id="profiles">
  <div id="per_page_container">
    <g:form name="filterForm" action="profileBuilder">
      <div class="container" id="per_page_header" title="Adding Modules">
        <div class="headerLeft">
          <h1>
            <g:if test="${isNew}" >
              Create Profile > ${profile?.name} > Add/Remove Modules > Search For Modules
          </g:if>
          <g:else>
              Edit Profile > ${profile?.name} > Add/Remove Modules > Search for Modules
          </g:else>
        </h1>
      </div>
      <div class="headerRight">
        <g:link class="btn btn_blue" controller="profile" action="profileBuilder" event="back" title="Click to go Back">&laquo; Back</g:link>
        <g:link class="btn btn_blue" controller="profile" action="profileBuilder" event="cancel" title="Click to Cancel">Cancel</g:link>
      </div>
    </div>
    <div id="yui-main">
      <div id="main_content" class="subpage">
        <div class="moduleFilterList" class="margin1mbtm">
          <table>
            <tr>
              <td width="50%" valign="top">
                <div id="div_criteria">
                  <div class="info">
                    <div class="info_header" title="Search Criteria">
                      <table>
                        <tr>
                          <td style="text-align:left;">Search Criteria</td>
                          <td style="text-align:right;"><a class="btn" style="font-weight:normal;" href="javascript:removeFilter('all','all');" title="Remove All">Remove All</a></td>
                        </tr>
                      </table>
                    </div>
                    <div id="div_criteria_selection">
                      <g:set var="currentFilterCount" value="${0}" />
                      <g:set var="clearTextFilterCount" value="${0}" />
                      <g:set var="tagFilterCount" value="${0}" />
                      <g:set var="cpeFilterCount" value="${0}" />
                      <g:set var="compliancyFilterCount" value="${0}" />
                      <div id="filterContainer">
                        <fieldset id="clearTextFilterContainer">
                          <legend style="cursor:pointer;" onClick="javascript:addFilter('clearText');" title="Click to add a criteria that will search by keyword.">+&nbsp;Word Search</legend>
                          <g:if test="${clearTexts}">
                            <g:each in="${clearTexts}">
                              <g:set var="currentFilterCount" value="${currentFilterCount + 1}" />
                              <g:set var="clearTextFilterCount" value="${clearTextFilterCount + 1}" />
                              <div class="pad3top" id="div.filter.${currentFilterCount}" filter="clearText">
                                <a class="btn" title="Click to remove keyword search criteria." href="javascript:removeFilter('clearText','${currentFilterCount}');">-</a>
                                <g:textField name="module.clearText.id" value="${it}" size="40" style="clear: right;" />
                              </div>
                            </g:each>
                          </g:if>
                        </fieldset>
                        <fieldset id="tagFilterContainer">
                          <legend style="cursor:pointer;" onClick="javascript:addFilter('tag');" title="Click to add a criteria that will search by category.">+&nbsp;Category</legend>
                          <g:if test="${tags}">
                            <g:each in="${tags}">
                              <g:set var="currentFilterCount" value="${currentFilterCount + 1}" />
                              <g:set var="tagFilterCount" value="${tagFilterCount + 1}" />
                              <div class="pad3top" id="div.filter.${currentFilterCount}" filter="tag">
                                <a class="btn" title="Click to remove category search criteria." href="javascript:removeFilter('tag','${currentFilterCount}');">-</a>
                                <g:select name="module.tag.id" from="${tagList}" optionKey="id" value="${it}" style="clear: right;" />
                              </div>
                            </g:each>
                          </g:if>
                        </fieldset>
                        <fieldset id="cpeFilterContainer">
                          <legend style="cursor:pointer;" onClick="javascript:addFilter('cpe');" title="Click to add a criteria that will search by platform.">+&nbsp;Platform</legend>
                          <g:if test="${cpes}">
                            <g:each in="${cpes}">
                              <g:set var="currentFilterCount" value="${currentFilterCount + 1}" />
                              <g:set var="cpeFilterCount" value="${cpeFilterCount + 1}" />
                              <div class="pad3top" id="div.filter.${currentFilterCount}" filter="cpe">
                                <a class="btn" title="Click to remove platform search criteria." href="javascript:removeFilter('cpe','${currentFilterCount}');">-</a>
                                <g:select name="module.cpe.id" from="${cpeList}" optionKey="id" value="${it}" style="clear: right;" />
                              </div>
                            </g:each>
                          </g:if>
                        </fieldset>
                        <fieldset id="compliancyFilterContainer">
                          <legend style="cursor:pointer;" onClick="javascript:addFilter('compliancy');" title="Click to add a criteria that will search by compliancy line item.">+&nbsp;Compliancy</legend>
                          <g:if test="${compliancies}">
                            <g:each in="${compliancies}">
                              <g:set var="currentFilterCount" value="${currentFilterCount + 1}" />
                              <g:set var="compliancyFilterCount" value="${compliancyFilterCount + 1}" />
                              <div class="pad3top" id="div.filter.${currentFilterCount}" filter="compliancy">
                                <a class="btn" title="Click to remove compliancy search criteria." href="javascript:removeFilter('compliancy','${currentFilterCount}');">-</a>
                                <g:select name="module.compliancy.id" from="${compliancyList}" optionKey="id" value="${it}" style="clear: right;" />
                              </div>
                            </g:each>
                          </g:if>
                        </fieldset>
                      </div>
                    </div>
                  </div>
                  <g:hiddenField id="filterCount" name="filterCount" value="${currentFilterCount}" />
                  <g:hiddenField id="clearTextCount" name="clearTextCount" value="${clearTextFilterCount}" />
                  <g:hiddenField id="tagCount" name="tagCount" value="${tagFilterCount}" />
                  <g:hiddenField id="cpeCount" name="cpeCount" value="${cpeFilterCount}" />
                  <g:hiddenField id="compliancyCount" name="compliancyCount" value="${compliancyFilterCount}" />
                </div>
              </td>
              <td width="50%" valign="top">
                <div id="div_sources">
                  <div class="info">
                    <div class="info_header" title="Module Pool">Module Pool</div>
                    <div class="info_body">
                      <table>
                        <tr>
                          <td style="text-align:left"><g:radio name="moduleSource" value="all" checked="${!moduleSource || moduleSource == 'all' ? true : false}" class="margin4rt" title="All Modules" />All Modules<span  class="margin3mrt">&nbsp;</span></td>
                        </tr>
                        <tr>
                          <td style="text-align:left"><g:radio name="moduleSource" value="useSystemProfile" checked="${moduleSource == 'useSystemProfile' }" class="margin4rt" title="From Industry Profile"/>From Industry Profile&nbsp;<g:select name="loadSystemProfile" from="${systemProfileList}" optionKey="id" value="${useSystemProfile}" /><span class="margin3mrt">&nbsp;</span></td>
                        </tr>
                        <tr>
                          <td style="text-align:left"><g:radio name="moduleSource" value="useUserProfile" checked="${moduleSource == 'useUserProfile' }" class="margin4rt" title="From Custom Profile" />From Custom Profile&nbsp;<g:select name="loadUserProfile" from="${userProfileList}" optionKey="id" value="${useUserProfile}" /></td>
                        </tr>
                      </table>
                    </div>
                  </div>
                </div>
              </td>
            </tr>
          </table>
        </div>
        <div style="text-align:center;padding:0.5em 0em 0.5em 0em;font-weight: bold;">
          <g:submitButton class="btninput" name="search" value="Perform Search" title="Perform Search" />
        </div>
        </g:form>

        <!-- Shows the list of returned Modules -->
        <div id="moduleListDisplay">

          <div class="info">
            <div class="info_header" title="Modules that match criteria from the pool.">Modules that match criteria from the pool.</div>
            <g:form name="updateProfileForm" action="profileBuilder">
              <g:if test="${moduleList?.size() > 0 }">
                <div class="actionInner">
                  <g:submitButton onClick="return checkModuleSelectionCount()" name="addModules" value="Add Selected Modules to Profile" title="Add Selected Modules to Profile" class="btninput"/>
                </div>
                <table>
                  <tr>
                    <th class="selectAll"><input id="selectionCheckbox" type="checkbox" title="Click here to select all" /></th>
                    <th style="text-align: left;"><a href="javascript:toggleModuleDescriptions();" title="Click to view all descriptions.">Security Modules</a></th>
                    <th style="text-align: center; width: 50%;"><a href="javascript:toggleModuleOptions();" title="Click to view all settings.">Settings</a></th>
                  </tr>
                  <g:each var="module" status="i" in="${moduleList}">
                    <g:render template="/profile/profileBuilder/resultRow" model="['profile':profile,'module':module,'i':i,'enabled':false]" />
                  </g:each>
                </table>
              </g:if>
              <g:else>
                <div class="info_body" style="text-align:center;" title="No Security Modules meet the current search criteria.">No Security Modules meet the current search criteria.</div>
              </g:else>
            </g:form>
          </div>
        </div>
      </div>
    </div>
</div>
</body>
</html>
