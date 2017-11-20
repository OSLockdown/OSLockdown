<!--This template contains the configuration information for editing a Client. -->

<g:set var="detachedClient" value="${clientInstance.dateDetached}" />

<g:set var="nameLabel" value="Name:" />
<g:if test="${!detachedClient}"><g:set var="nameLabel" value="Name*:" /></g:if>

<g:set var="hostAddressLabel" value="Host Address:" />
<g:if test="${!detachedClient}"><g:set var="hostAddressLabel" value="Host Address*:" /></g:if>

<g:set var="portLabel" value="Port:" />
<g:if test="${!detachedClient}"><g:set var="portLabel" value="Port*:" /></g:if>

<table class="margin5topbtm">
    <tbody>
     <tr class="prop">
            <td valign="top" class="propName" title="Client Name">
                <label for="name">${nameLabel}</label>
            </td>
            <td valign="top" class="propValue${hasErrors(bean:clientInstance,field:'name','errors')}">

                <g:if test="${detachedClient}">
                  <!-- for a detached client make field readonly -->
                  ${fieldValue(bean:clientInstance,field:'name')}
                </g:if>
                <g:else>
                  <input type="text" size="50" maxlength="50" id="name" name="name" value="${fieldValue(bean:clientInstance,field:'name')}" title="Enter Client Name" />                  
                </g:else>

            </td>
        </tr> 
     <tr class="prop">
            <td valign="top" class="propName" title="Client Type">
                <label for="name">Client Type</label>
            </td>
            <td valign="top" class="propValue${hasErrors(bean:clientInstance,field:'name','errors')}">

                  ${fieldValue(bean:clientInstance,field:'clientType.name')}

            </td>
        </tr> 
    
        <tr class="prop">
            <td valign="top" class="propName" title="Host Address">
                <label for="Host Address">${hostAddressLabel}</label>
            </td>
            <td valign="top" class="propValue${hasErrors(bean:clientInstance,field:'hostAddress','errors')}">

                <g:if test="${detachedClient}">
                  <!-- for a detached client make field readonly -->
                  ${fieldValue(bean:clientInstance,field:'hostAddress')}
                </g:if>
                <g:else>
                  <input type="text" size="50" maxlength="30" id="hostAddress" name="hostAddress" value="${fieldValue(bean:clientInstance,field:'hostAddress')}" title="Enter Host Address" />
                </g:else>
            </td>
        </tr>

        <!--
        The Profile field should be displayed in the Show Details and Edit
        pages, but not the New Client page.  The boolean flag is set by the
        controller.
        -->
        <!-- show Group, Security and Baseline profiles for attached clients only (as for detached they are all Unassociated) -->
        <g:if test="${!detachedClient}">
            <tr class="prop">
              <td valign="top" class="propName" title="Group Name">
                 <label for="Group">Group:</label>
              </td>                                 
              <td valign="top" class="propValue" title="Associated Group">
                <g:if test="${clientInstance.group}">
                    <g:link title="Client's associated group." controller="group" action="edit" id="${clientInstance.group.id}">${clientInstance.group.name}</g:link>
                </g:if>
                <g:else>
                    Unassociated
                </g:else>                
              </td>                                   
            </tr>
            <tr class="prop">
              <td valign="top" class="propName" title="Security Profile Name">
                 <label for="Security Profile">Security Prof:</label>
              </td>                                 
              <td valign="top" class="propValue" title="Associated Security Profile">
                <g:if test="${clientInstance.group?.profile}">
                    <g:link title="Client's associated Security profile via its group." controller="profile" action="profileBuilder" event="start" class="profiles" id="${clientInstance.group.profile.id}">${clientInstance.group.profile.name}</g:link>
                </g:if>
                <g:else>
                    Unassociated
                </g:else>
              </td>                                   
            </tr>
            <tr class="prop">
              <td valign="top" class="propName" title="Baseline Profile Name">
                 <label for="Baseline Profile">Baseline Prof:</label>
              </td>
              <td valign="top" class="propValue" title="Associated Baseline Profile">
                <g:if test="${clientInstance.group?.baselineProfile}">
                    <g:link title="Client's associated Baseline profile via its group." controller="baselineProfile" action="show" class="profiles" id="${clientInstance.group.baselineProfile.id}">${clientInstance.group.baselineProfile.name}</g:link>
                </g:if>
                <g:else>
                    Unassociated
                </g:else>
              </td>
            </tr>                    
        </g:if>               

        <tr class="prop">
            <td class="propName" title="Description">
                <label for="Description">Description:</label>
            </td>

            <td valign="top" class="propValue${hasErrors(bean:clientInstance,field:'description','errors')}">
                                              <!-- Note: maxlength="200" does not work for textarea. Could enforce max legnth with JavaScript function -->
              <g:textArea rows="4" cols="48" id="description" name="description" title="Enter Description" value="${fieldValue(bean:clientInstance,field:'description')}" />
            </td>
        </tr>
    
        <tr class="prop">
            <td class="propName" title="Location">
                <label for="Location">Location:</label>
            </td>
            <td valign="top" class="propValue${hasErrors(bean:clientInstance,field:'location','errors')}">
                <textarea rows="4" cols="48" id="location" name="location" title="Enter Location" />${fieldValue(bean:clientInstance,field:'location')}</textarea>			             </td>
        </tr> 
    
        <tr class="prop">
            <td class="propName" title="Contact">
                <label for="contact">Contact:</label>
            </td>
            <td valign="top" class="propValue${hasErrors(bean:clientInstance,field:'contact','errors')}">
                <textarea rows="4" cols="48" id="contact" name="contact" title="Enter Contact" />${fieldValue(bean:clientInstance,field:'contact')}</textarea>			              </td>
        </tr> 
    
        <tr class="prop">
            <td valign="top" class="propName" title="Port">
                <label for="Port">${portLabel}</label>
            </td>
            <td valign="top" class="propValue${hasErrors(bean:clientInstance,field:'port','errors')}">

                <g:if test="${detachedClient}">
                  ${clientInstance.port}
                </g:if>
                <g:else>
                  <input type="text" size="5" id="port" name="port" value="${clientInstance?.port}" onKeyUp="limitText(this.form.port,5);" title="Enter Port number" />
                </g:else>
            </td>
        </tr> 
    
    </tbody>
</table>
