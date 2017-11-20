<%@ page import="com.trustedcs.sb.web.pojo.Processor" %>
<%@ page import="com.trustedcs.sb.util.ClientType" %>

<!--This reusable template contains the configuration information for a Processor.
It is used for the create, edit, and show details page.-->
<table class="margin5topbtm">
    <tbody>
     <tr class="prop">
            <td valign="top" title="Processor Name">
                <label for="name">Name:</label>
            </td>
            <td valign="top">
                <g:fieldValue bean="${processorInstance}" field="name" />
            </td>
        </tr> 

        <tr class="prop">
          <td valign="top" class="propName" title="Processor Type">
             <label for="Type">Type:</label>
          </td>                                 
          <td valign="top" class="propValue" title="Associated Type">
            <g:if test="${processorInstance.clientType}"><g:fieldValue bean="${processorInstance}" field="clientType.name" /></g:if>
            <g:else>None</g:else>
          </td>                                   
        </tr>
    
        <tr class="prop">
            <td valign="top" title="Description">
                <label for="Description">Description:</label>
            </td>
            <td valign="top">
                <g:fieldValue bean="${processorInstance}" field="description" />
            </td>
        </tr> 

<!--
        <tr class="prop">
            <td valign="top" title="DateAdded">
                <label for="DateAdded">Date added:</label>
            </td>
            <td valign="top">
                <g:formatDate format="MMM-dd-yyyy" date="${processorInstance.dateAdded}" />
            </td>
        </tr> 
-->          

    </tbody>
</table>
