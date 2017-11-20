
<%@ page import="com.trustedcs.sb.help.OnlineHelp" %>
<div class="baselineModule">
  <table>

    <tr class="${(i % 2) == 0 ? 'row_even' : 'row_odd'}" style="text-align:left;">
      <td style="text-align:left;width:80%">
        <a href="javascript:showHideElement('display_module_info_${baselineModule.id}');"><g:fieldValue bean="${baselineModule}" field="name" /></a>
      </td>
      <td style="${immutable ? 'float:right;' : 'text-align:right;'}">
    <g:set var="inProfile" value="${baselineProfileInstance?.baselineModules?.contains(baselineModule)}"/>
    <g:if test="${immutable}">
      <label:enabledDisabled value="${inProfile}"/>
    </g:if>
    <g:else>      
      <g:select class="enabledDisabledDropDown" name="baselineModule_${baselineModule.id}"
                from="${[false:'Disabled',true:'Enabled']}"
                optionKey="key" optionValue="value"
                onChange="javascript:updateReportSize(this.value,${baselineModule.avgKbPerReport},${baselineModule.systemLoadImpactInteger},${baselineModule.forensicImportanceInteger});"
                value="${inProfile}"/>
    </g:else>
    </td>
    </tr>
    <tr id="display_module_info_${baselineModule.id}" style="text-align:left;display: none;" class="baselineModuleInfo ${(i % 2) == 0 ? 'row_even' : 'row_odd'}">
      <td colspan="2">
        <table>
          <tr style="border-top:1px dotted gray;">
            <td style="text-align:left;width:50%;" class="moduleDescription">
              <p>
                <g:fieldValue bean="${baselineModule}" field="description" />
                <a target="_blank" style="cursor:help;" title="Detailed help for ${baselineModule.name}." href="${resource(dir:'sbhelp/admin',file:OnlineHelp.adminHtmlFile(baselineModule.helpId))}">[more]</a>
                </p>
            </td>
            <td style="vertical-align:top;">
              <table>
                <tr>
                  <td>
                    <label class="bold">Report Size:</label>
                  </td>
                  <td>
                    <g:fieldValue bean="${baselineModule}" field="sizeCategory" /> ( ~<g:fieldValue bean="${baselineModule}" field="avgKbPerReport" /> Kb per report )
                  </td>
                </tr>
              </table>
            </td>
          </tr>

<!-- Module Suboptions -->
<g:if test="${baselineModule.subOptions}">
  <tr style="border-top:1px dotted gray;">
    <td colspan="2" style="text-align:center;">
      <label>Optional Configuration Options</label>
    </td>
  </tr>
  <g:each in="${baselineModule.subOptions}" var="baselineSuboption">
    <tr>
      <td style="text-align:right;width:50%;font-style:italic;">
    <g:fieldValue bean="${baselineSuboption}" field="name"/>:
    </td>
    <td>
    <g:set var="optionValueKey" value="${baselineModule.id+'_'+baselineSuboption.id}"/>
    <g:if test="${immutable}">
      <label:enabledDisabled string="${baselineProfileInstance?.subOptionValues[optionValueKey]}"/>
    </g:if>
    <g:else>
      <g:select class="enabledDisabledDropDown" name="baselineSuboption_${baselineModule.id}_${baselineSuboption.id}"
                from="${['false':'Disabled','true':'Enabled']}" optionKey="key" optionValue="value"
                value="${baselineProfileInstance?.subOptionValues[optionValueKey]}" />
    </g:else>
    </td>
    </tr>
  </g:each>
</g:if>

</table>
</td>
</tr>
</table>
</div>