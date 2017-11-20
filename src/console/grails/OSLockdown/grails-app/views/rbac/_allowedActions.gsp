<div id="allowedActions" style="width:60%;display:none;" class="info centerDiv">    
    <div class="info_body">
        <table border="1">
            <tr>
                <th></th>                
                <th>Administrator</th>
                <th>User</th>
                <th>Security Officer</th>
                <th>Management</th>
            </tr>
            <tr>
                <td style="text-align:left;" colspan="5">Profile</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">create</td>
                <td style="text-align:center;">Y</td>                
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">view</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;" colspan="5">Clients</td>                
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">edit</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">
                  <g:if test="${isBulk}">detach</g:if>
                  <g:else>delete</g:else>
                </td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">auto-registration</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">scan</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">apply</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">undo</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">abort</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">baseline</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">auto-update</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;" colspan="5">Groups</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">edit</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">delete</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>

            <g:if test="${isBulk}">
              <tr>
                  <td style="text-align:left;padding-left:3em;">detach clients</td>
                  <td style="text-align:center;">Y</td>
                  <td style="text-align:center;">Y</td>
                  <td style="text-align:center;">N</td>
                  <td style="text-align:center;">N</td>
              </tr>     
            </g:if>

            <tr>
                <td style="text-align:left;padding-left:3em;">scan</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">apply</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">undo</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">abort</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">baseline</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">auto-update</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;" colspan="5">Notifications</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">view</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">delete</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;" colspan="5">Reports</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">view</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
            </tr>
            <tr>
                <td style="text-align:left;" colspan="5">Logging</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">audit log</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">application log</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
            </tr>

            <g:if test="${!isBulk}">
              <tr>
                  <td style="text-align:left;" colspan="5">Scheduler</td>
              </tr>
              <tr>
                  <td style="text-align:left;padding-left:3em;">edit</td>
                  <td style="text-align:center;">Y</td>
                  <td style="text-align:center;">Y</td>
                  <td style="text-align:center;">N</td>
                  <td style="text-align:center;">N</td>
              </tr>
              <tr>
                  <td style="text-align:left;padding-left:3em;">delete</td>
                  <td style="text-align:center;">Y</td>
                  <td style="text-align:center;">Y</td>
                  <td style="text-align:center;">N</td>
                  <td style="text-align:center;">N</td>
              </tr>
            </g:if>

            <tr>
                <td style="text-align:left;" colspan="5">Administration</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">users</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>
            <tr>
                <td style="text-align:left;padding-left:3em;">migration</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>                       
            <tr>
                <td style="text-align:left;padding-left:3em;">account preferences</td>
                <td style="text-align:center;">Y</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
                <td style="text-align:center;">N</td>
            </tr>                       
        </table>
    </div>
</div>
