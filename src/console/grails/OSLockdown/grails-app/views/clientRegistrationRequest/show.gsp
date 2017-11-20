<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="show-autoregrequest" />  
    <r:require modules="application"/>
    <title>Auto-Registration Request</title>
  </head>
  <body id="group">
    <div id="per_page_container">
      <div class="container" id="per_page_header" title="Client Auto Registration">
        <div class="headerLeft">
          <h1>Auto-Registration Request</h1>
        </div>
        <div class="headerRight">
          <g:link class="btn btn_blue" controller="clientRegistrationRequest" action="list" title="Click to go Back">&laquo; Back</g:link>          
        </div>
      </div>
      <div id="yui-main">
        <div id="main_content" class="subpage">
          <div class="info half centerDiv">
            <div class="info_body">
              <g:form method="post" >
                <g:hiddenField name="id" value="${requestInstance?.id}"/>
                <table class="margin5topbtm">
                  <tbody>
                    <tr>
                      <td style="width:40%;" valign="top" title="Client Name">
                        <label for="name">Name:</label>
                      </td>
                      <td valign="top">
                  <g:fieldValue bean="${requestInstance}" field="name"/>
                  </td>
                  </tr>
                  <tr>
                    <td style="width:40%;" valign="top" title="Client Type">
                      <label for="Client Type">Client Type:</label>
                    </td>
                    <td valign="top">
                      <g:fieldValue bean="${requestInstance}" field="displayText"/>
                    </td>
                  </tr>
                  <tr>
                    <td style="width:40%;" valign="top" title="Host Address">
                      <label for="Host Address">Host Address:</label>
                    </td>
                    <td valign="top">
                  <g:fieldValue bean="${requestInstance}" field="hostAddress"/>
                  </td>
                  </tr>
                  <tr>
                    <td valign="top"  title="Location">
                      <label for="Location">Location:</label>
                    </td>
                    <td valign="top" class="propValue">
                      <g:fieldValue bean="${requestInstance}" field="location"/>
                    </td>
                  </tr>
                  <tr>
                    <td valign="top"  title="Contact">
                      <label for="contact">Contact:</label>
                    </td>
                    <td valign="top" class="propValue">
                      <g:fieldValue bean="${requestInstance}" field="contact"/>
                    </td>
                  </tr>
                  <tr>
                    <td valign="top"  title="Port">
                      <label for="Port">Port:</label>
                    </td>
                    <td valign="top" class="propValue">
                      ${requestInstance?.port}
                    </td>
                  </tr>
                  <tr>
                    <td valign="top"  title="Group">
                      <label for="Group">Group:</label>
                    </td>
                    <td valign="top" class="propValue">
                  <g:select class="paddedSelect" name="groupId" from="${groupList}" optionKey="id" optionValue="name" noSelection="['':'[-Optional Group Selection-]']"/>
                  </td>
                  </tr>
                  </tbody>
                </table>
                <div style="text-align:center;padding-top:0.5em;padding-bottom:0.5em;">                  
                  <g:actionSubmit class="btn"  action="allow" value="Allow" onclick="return confirm('Are you sure you want to allow this client request?');" id="${requestInstance?.id}" title="Click to Allow the Request"/>
                  <g:actionSubmit class="btn"  action="deny"  value="Deny" onclick="return confirm('Are you sure you want to deny this client request?');"   title="Click to Deny the Request"/>
                </div>
              </g:form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>
