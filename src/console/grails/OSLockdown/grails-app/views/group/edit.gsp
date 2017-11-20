<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="layout" content="main" />
    
    <sbauth:isEnterprise>
      <meta name="contextSensitiveHelp" content="edit-group"/>
    </sbauth:isEnterprise>
    <sbauth:isBulk>
      <meta name="contextSensitiveHelp" content="edit-group-su"/>
    </sbauth:isBulk>

    <r:require modules="MyPick"/>

  <title>Edit Group</title>
</head>
<body id="group">
  <div id="per_page_container">
    <g:form name="editGroup" action="update">
      <div class="container" id="per_page_header" title="Edit Group">
        <div class="headerLeft">
          <h1>Edit Group > ${groupInstance.name}</h1>
      </div>
      <div class="headerRight">        
          <g:link class="btn btn_blue" controller="group" action="show" id="${groupInstance.id}" event="back" title="Click to go Back">&laquo; Back</g:link>
      </div>
    </div>
    <div id="yui-main">
      <div id="main_content" class="subpage">
        <g:hiddenField name="id" value="${fieldValue(bean:groupInstance,field:'id')}" />
        <div class="info half centerDiv">
          <div class="info_body">
            <fieldset>
              <legend>Details</legend>
              <div>
                <table>
                  <tr>
                    <td class="clientName" style="height: 40px; vertical-alignment: bottom;" title="Name"><label for="Name">Name:</label></td>
                    <td><g:textField name="name" maxlength="20" value="${fieldValue(bean:groupInstance,field:'name')}" title="Enter Name" /></td>
                  </tr>
                  <tr>
                    <td class="clientName" title="Description"><label for="Description">Description:</label></td>
                                                        <!-- Note: maxlength="200" does not work for textarea. Could enforce max legnth with JavaScript function -->
                    <td><g:textArea  name="description" value="${fieldValue(bean:groupInstance,field:'description')}" rows="5" cols="36" title="Enter Description" /></td>
                  </tr>
                  <tr style="height: 32px;">
                    <td class="clientName" title="Security Profile"><label for="Security Profile">Security Profile:</label></td>
                    <td><g:select style="width:100%;" name="profileId" from="${securityProfileList}" optionKey="id" optionValue="name" value="${groupInstance?.profile?.id}" noSelection="['':'[-No Security Profile-]']" title="Select a Security Profile" /> </td>
                  </tr>
                  <tr style="height: 32px;">
                    <td class="clientName" title="Baseline Profile"><label for="Baseline Profile">Baseline Profile:</label></td>
                    <td><g:select style="width:100%;" name="baselineProfileId" from="${baselineProfileList}" optionKey="id" optionValue="name" value="${groupInstance?.baselineProfile?.id}" noSelection="['':'[-No Baseline Profile-]']" title="Select a Baseline Profile" /> </td>
                  </tr>
                  <tr style="height: 40px; #height: 55px">
                    <td class="clientName" title="Clients"><label for="Clients">Clients:</label></td>
                    <td title="Number of Clients">${groupInstance?.clients ? groupInstance?.clients.size() : 'None'}</td>
                  </tr>
                </table>
              </div>
            </fieldset>

            <fieldset>
              <legend>Clients</legend>
              <div class="info_body">
                <table class="pad5all">
                  <tr>
                    <td style="text-align: center;width: 45%;" title="Clients that do not currently have a group.">
	                          Unassociated Clients<sbauth:isBulk> (Attached)</sbauth:isBulk>
                  <g:select multiple="true" size="12" name="unselectedList" style="width: 90%;"
                            onDblClick="MyPickcopySelected(document.editGroup.unselectedList,document.editGroup.selectedList)"
                            from="${missingClients}" optionKey="id" optionValue="name" />
                  </td>
                  <td style="text-align: center; margin-right: 2em;">
                    <input type="button" onClick="MyPickcopySelected(this.form.unselectedList,this.form.selectedList)" value=" >> " id="button2" name="button2" class="btninput" title="Click to add the selected client" />
                    <input type="button" onClick="MyPickcopySelected(this.form.selectedList,this.form.unselectedList)" value=" << " id="button1" name="button1" class="btninput" title="Click to remove the selected client" />
                  </td>
                  <td style="text-align:center;width: 45%;" title="Clients associated with this Group">
	                          Associated Clients<sbauth:isBulk> (Attached)</sbauth:isBulk>
                  <g:select multiple="true" size="12" name="selectedList" style="width: 90%;"
                            onDblClick="MyPickcopySelected(document.editGroup.selectedList,document.editGroup.unselectedList)"
                            from="${groupClients}" optionKey="id" optionValue="name" />
                  </td>
                  </tr>
                </table>
              </div>
            </fieldset>

          </div>
          <div class="buttonsDiv">
            <input type="submit" name="submitButton" value="Update Group" onClick="MyPickselectAll(document.editGroup.selectedList);" class="btninput" title="Click to update this group" />
          </div>
        </div>
        </g:form>
      </div>
    </div>
</div>
</body>
</html>
