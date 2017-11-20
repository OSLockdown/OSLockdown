<div>
  <table>
    <tbody>
      <tr>
        <td class="tdName" title="Name"><label for="Username">Username:</label></td>
        <td title="User's Name">
    <g:if test="${userRoleRel?.id}">
      <g:fieldValue bean="${userRoleRel?.user}" field="username"/>
    </g:if>
    <g:else>
      <g:textField name="name" value="${params.name ? params.name : userRoleRel?.user?.username}"/>
    </g:else>
    </td>
    </tr>
    <tr>
      <td class="tdName" title="Role"><label for="Role">Role:</label></td>
      <td title="Click to Select Role">
        <g:select style="width:13em;" name="role" from="${roles}" value="${params.role ? params.role : userRoleRel?.role?.id}" optionKey="id" optionValue="name" />
      </td>
    </tr>
    <tr>
      <td class="tdName" title="lastChange"><label for=lastChange">Last Password Change:</label></td>
      <td title="Enter Password"><g:formatDate format="E MMM-dd-yyyy HH:mm:ss" date="${lastChange}"/></td>
    </tr>
    <tr>
      <td class="tdName" title="lastLogin"><label for="lastLogin">Last Login:</label></td>
      <td title="Enter Password"><g:formatDate format="E MMM-dd-yyyy HH:mm:ss" date="${lastLogin}"/></td>
    </tr>
    <tr>
      <td class="tdName" title="Password"><label for="Password">Password:</label></td>
      <td title="Enter Password"><input type="password" name="password"/></td>
    </tr>
    <tr>
      <td class="tdName" title="Re-enter Password"><label for="Re-enter Password">Re-enter Password:</label></td>
      <td title="Re-enter Password"><input type="password" name="reenteredPassword"/></td>
    </tr>
    </tbody>
  </table>
</div>

