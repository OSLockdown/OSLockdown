<%@ page import="com.trustedcs.sb.util.ClientType" %>
<!--This template contains the configuration information for editing a Processor. -->

<table class="margin5topbtm">
    <tbody>
     <tr class="prop">
            <td valign="top" class="propName" title="Processor Name">
                <label for="name">Name*:</label>
            </td>
            <td valign="top" class="propName">

                <input type="text" size="50" maxlength="50" id="name" name="name" value="${fieldValue(bean:processorInstance,field:'name')}" title="Enter Processor Name" />                  

            </td>
        </tr> 
    
        <tr class="prop">
          <td valign="top" class="propName" title="Processor Type">
             <label for="Type">Type:</label>
          </td>                                 
          <td valign="top" class="propValue" title="Associated Type">
            <g:if test="${editable}">
              <g:select style="width:100%;" name="clientTypeId" from="${ClientType.userAllowed()}" optionKey="name" value="${fieldValue(bean:processorInstance, field:'clientType.name')}" optionValue="name" noSelection="['':'-Select Processor Type-']"/>
            </g:if>
            <g:else>
              ${fieldValue(bean:processorInstance, field:'clientType.name')}
            </g:else>
          </td>                                   
        </tr>

        <tr class="prop">
            <td class="propName" title="Description">
                <label for="Description">Description:</label>
            </td>

            <td valign="top" class="propValue${hasErrors(bean:processorInstance,field:'description','errors')}">
                                              <!-- Note: maxlength="200" does not work for textarea. Could enforce max legnth with JavaScript function -->
              <g:textArea rows="4" cols="48" id="description" name="description" title="Enter Description" value="${fieldValue(bean:processorInstance,field:'description')}" />
            </td>
        </tr>
    
    
    </tbody>
</table>
