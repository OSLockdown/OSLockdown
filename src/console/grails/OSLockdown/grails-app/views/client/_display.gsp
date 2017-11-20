<%@ page import="com.trustedcs.sb.web.pojo.Client" %>

<!--This reusable template contains the configuration information for a Client.
It is used for the create, edit, and show details page.-->
<table class="margin5topbtm">
    <tbody>
     <tr class="prop">
            <td valign="top" title="Client Name">
                <label for="name">Name:</label>
            </td>
            <td valign="top">
                <g:fieldValue bean="${clientInstance}" field="name" />
            </td>
        </tr> 
     <tr class="prop">
            <td valign="top" title="Client Type">
                <label for="name">Client Type:</label>
            </td>
            <td valign="top">
                <g:fieldValue bean="${clientInstance}" field="clientType.name" />
            </td>
        </tr> 
    
        <tr class="prop">
            <td valign="top" title="Host Address">
                <label for="Host Address">Host Address:</label>
            </td>
            <td valign="top" class="propValue${hasErrors(bean:clientInstance,field:'hostAddress','errors')}">
                <g:fieldValue bean="${clientInstance}" field="hostAddress" />
            </td>
        </tr>

        <!--
        The Profile field should be displayed in the Show Details and Edit
        pages, but not the New Client page.  The boolean flag is set by the
        controller.
        -->      
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
          <td valign="top" title="Security Profile Name">
             <label for="Security Profile">Security Profile:</label>
          </td>
          <td valign="top" title="Associated Security Profile">
            <g:if test="${clientInstance.group?.profile}">
                <g:link title="Client's associated security profile via its group." controller="profile" action="profileBuilder" event="start" class="profiles" id="${clientInstance.group.profile.id}">${clientInstance.group.profile.name}</g:link>
            </g:if>
            <g:else>
                Unassociated
            </g:else>
          </td>
        </tr>
        <tr class="prop">
          <td valign="top" title="Baseline Profile Name">
             <label for="Baseline Profile">Baseline Profile:</label>
          </td>
          <td valign="top" title="Associated Baseline Profile">
            <g:if test="${clientInstance.group?.baselineProfile}">
                <g:link title="Client's associated baseline profile via its group." controller="baselineProfile" action="show" id="${clientInstance.group.baselineProfile.id}">${clientInstance.group.baselineProfile.name}</g:link>
            </g:if>
            <g:else>
                Unassociated
            </g:else>
          </td>
        </tr>
        <tr class="prop">
            <td valign="top" title="Description">
                <label for="Description">Description:</label>
            </td>
            <td valign="top">
                <g:fieldValue bean="${clientInstance}" field="description" />
            </td>
        </tr> 
        <tr class="prop">
            <td valign="top" title="Location">
                <label for="Location">Location:</label>
            </td>
            <td valign="top">
                <g:fieldValue bean="${clientInstance}" field="location" />
            </td>
        </tr> 
        <tr class="prop">
            <td valign="top" title="Contact">
                <label for="contact">Contact:</label>
            </td>
            <td valign="top">
              <g:fieldValue bean="${clientInstance}" field="contact" />
            </td>
        </tr>    
        <tr class="prop">
            <td valign="top" class="propName" title="Port">
                <label for="Port">Port:</label>
            </td>
            <td valign="top">
                ${clientInstance.port}
            </td>
        </tr>
          
        <sbauth:isBulk>

          <tr class="prop">
              <td valign="top" class="propName" title="Attached On">
                  <label for="Attached On">Attached On:</label>
              </td>
              <g:if test="${clientInstance.dateCreated}">
                <td class="clientLastAddedDate" valign="top" style="cursor:pointer;" title="${clientInstance.dateCreated}">
                  <g:formatDate format="MMM-dd-yyyy" date="${clientInstance.dateCreated}"/>
                </td>
              </g:if>
              <g:else>
                <td></td>
              </g:else>

          </tr>

          <tr class="prop">
              <td valign="top" class="propName" title="Detached On">
                  <label for="Detached On">Detached On:</label>
              </td>
              <g:if test="${clientInstance.dateDetached}">
                <td valign="top" style="cursor:pointer;" title="${clientInstance.dateDetached}">
                  <g:formatDate format="MMM-dd-yyyy" date="${clientInstance.dateDetached}"/>
                </td>
              </g:if>
              <g:else>
                <td></td>
              </g:else>
          </tr>

          <!-- for a Detached client show fields from the detachDataMap if any -->
          <g:if test="${clientInstance.dateDetached && clientInstance.detachDataMap}">

            <g:if test="${clientInstance.detachDataMap[Client.DETACHMENT_MAP_GROUP_NAME_KEY]}">
              <tr class="prop">
                  <td valign="top" class="propName" title="Group at Detachment">
                      <label for="Group at Detachment">Group at Detachment:</label>
                  </td>
                  <td valign="top">
                      ${clientInstance.detachDataMap[Client.DETACHMENT_MAP_GROUP_NAME_KEY]}
                  </td>
              </tr>              
            </g:if>

            <g:if test="${clientInstance.detachDataMap[Client.DETACHMENT_MAP_SECURITY_PROFILE_NAME_KEY]}">
              <tr class="prop">
                  <td valign="top" class="propName" title="Security Profile at Detachment">
                      <label for="Security Profile at Detachment">Security Profile at Detachment:</label>
                  </td>
                  <td valign="top">
                      ${clientInstance.detachDataMap[Client.DETACHMENT_MAP_SECURITY_PROFILE_NAME_KEY]}
                  </td>
              </tr>              
            </g:if>

            <g:if test="${clientInstance.detachDataMap[Client.DETACHMENT_MAP_BASELINE_PROFILE_NAME_KEY]}">
              <tr class="prop">
                  <td valign="top" class="propName" title="Baseline Profile at Detachment">
                      <label for="Baseline Profile at Detachment">Baseline Profile at Detachment:</label>
                  </td>
                  <td valign="top">
                      ${clientInstance.detachDataMap[Client.DETACHMENT_MAP_BASELINE_PROFILE_NAME_KEY]}
                  </td>
              </tr>
            </g:if>

          </g:if>

        </sbauth:isBulk>

    </tbody>
</table>
