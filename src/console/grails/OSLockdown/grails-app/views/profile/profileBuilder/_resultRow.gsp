<%@ page import="com.trustedcs.sb.validator.*" %>
<%@ page import="com.trustedcs.sb.help.OnlineHelp" %>

<!-- General Information -->
<tr class="${(i % 2) == 0 ? 'row_even' : 'row_odd'}">
    <g:if test="${profile.securityModules?.contains(module)}">
    <td id="selectAll"><img title="Module Already Exists in Profile." src="${resource(dir:'images',file:'xmodule_red.gif')}"/></td>
    </g:if>
    <g:else>
    <td id="selectAll"><input type="checkbox" id="module.selected.${module.id}" onclick="javascript:dependencyCheck('${module.id}');" name="module.selected.${module.id}" ${ enabled ? "checked='true'" : "" } title="Click here to select all" /></td>
    </g:else>
	<td style="text-align: left" title="Module Name"><a href="javascript:showHideElement('display_module_info_${module.id}');">${module.name}</a></td>
	<td style="text-align: center; width: 50%; #padding-top: 0.2em;" title="Module Settings">
		<g:if test="${module.options?.size() > 0 }">											
			<a href="javascript:toggleSelectedModuleOptions('${module.id}');" class="btn">View</a>			
		</g:if>		
	</td>	
</tr>

<!-- Help Text -->
<tr id="display_module_info_${module.id}"  class="${(i % 2) == 0 ? 'row_even' : 'row_odd'}" style="display: none;">
    <td id="selectAll">&nbsp;</td>
    <td colspan="2" class="moduleDescription">
        ${module.description}
        <a target="_blank" style="cursor:help;" title="Detailed help for ${module.name}." href="${resource(dir:'sbhelp/modules',file:OnlineHelp.moduleHtmlFile(module.library))}">[more]</a>
    </td>
</tr>

<!-- Configuration -->
<g:if test="${module.options?.size() > 0 }">
	<g:each var="option" in="${module.options}">
	    <g:hiddenField name="module.${module.id}.option.${option.id}" value="${settingsMap[module.id + '.' +option.id]}"/>
		<tr id="display_module_options_${module.id}"  class="${(i % 2) == 0 ? 'row_even' : 'row_odd'}" style="display: none;">			
                    <td id="selectAll">&nbsp;</td>
                    <td class="moduleSettingDescription">${option.description}</td>
			    <g:set var="optionType" value="${ProfileOptionsValidator.getInstance().optionTypes[option.type]}"/>

                    <td class="moduleSettingValue">
			    <!-- Enumerated Types -->
			    <g:if test="${optionType.validValues.size() > 0 }">
                     <g:select disabled="true" name="module.${module.id}.option.${option.id}" from="${optionType.validValues}" optionKey="value" optionValue="displayString" 
                                value="${settingsMap[module.id + '.' +option.id]}" />
                     &nbsp;${option.unit}
			    </g:if>                 	
			    <g:else>
			         <!-- String Types -->
			         <g:if test="${optionType.type == 'string'}">
			             <!-- Password String Types -->
			             <g:if test="${optionType.isPassword}">
					<g:passwordField disabled="true" name="module.${module.id}.option.${option.id}" 
                                value="${settingsMap[module.id + '.' +option.id]}" />
																		&nbsp;${option.unit}
				</g:if>                                    
						<g:elseif test="${optionType.isMultiline}">
						<!-- Multiline String Types -->
			<g:textArea  disabled="true" rows="4" cols="60" name="module.${module.id}.option.${option.id}" 
                          value="${settingsMap[module.id + '.' +option.id]}" />
						&nbsp;${option.unit}
						</g:elseif>
							<g:else>
						<!-- Basic String Types -->
							<g:textField disabled="true" name="module.${module.id}.option.${option.id}" 
                                value="${settingsMap[module.id + '.' +option.id]}" />
																		&nbsp;${option.unit}                        
													</g:else>                                 
													</g:if>			
            <!-- Number Types -->             
			         <g:if test="${optionType.type == 'number'}">
				         <g:textField disabled="true" name="module.${module.id}.option.${option.id}" 
	                               value="${settingsMap[module.id + '.' +option.id]}" />
													&nbsp;${option.unit}
												</g:if>
			    </g:else>		    
			</td>
		</tr>
	</g:each>
</g:if>
