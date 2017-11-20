
<%@ page import="com.trustedcs.sb.util.LoggingLevel" %>
<%@ page import="com.trustedcs.sb.util.SbDateUtil" %>
<%@ page import="com.trustedcs.sb.scheduler.ScheduledTask" %>
<%@ page import="com.trustedcs.sb.scheduler.ScheduledTaskStatus" %>

<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="scheduling" />
    <title>Scheduler</title>
    <r:require modules="application"/>
    <r:script >

      $(document).ready(function() {

        $("#selectionCheckbox").click(function() {
          if ( $('#selectionCheckbox').attr('checked') ) {
            checkAllBoxes("taskform");
          }
          else{
            uncheckAllBoxes("taskform");
          }
        })

        $("#deleteMulti").click(function() {
          if ( checkForNoneSelected('No tasks were selected for deletion.') ) {
             return confirm('Are you sure you want to delete the selected task(s)?');
          }
          return false;
        })

        $("#verifyMulti").click(function() {
          if ( checkForNoneSelected('No tasks were selected for verification.') ) {
             return confirm('Are you sure you want to synchronize the selected task(s)?');
          }
          return false;
        })

        $('.action_title').corners("5px top-left top-right");
        $('.actions').corners("5px");
      });

    </r:script>
  </head>
  <body id="scheduler">
    <div id="per_page_container">
      <g:form name="taskform">
        <div class="container" id="per_page_header" title="listTasks">
          <div class="headerLeft">
            <h1>Scheduler</h1>
          </div>
        </div>

        <div id="actionbar_outer" class="yui-b">
          <g:render template="/scheduledTask/actionbar_multi" />
        </div>

        <div id="yui-main">
          <div class="yui-b">
            <div id="main_content" class="subpage">
              <div id="table_border">
                <table>
                  <tr>
                    <th class="selectAll"><input id="selectionCheckbox" type="checkbox" title="Click here to select all" /></th>
                    <th title="Group">Group</th>                                        
                    <th title="Actions">Actions</th>
                    <th title="Logging Level">Logging Level</th>
                  </tr>
                  <g:if test="${taskList}">
                    <g:each var="task" status="i" in="${taskList}">
                      <tr class="${(i % 2) == 0 ? 'row_even' : 'row_odd'}">
                        <td title="Click to Select"><g:checkBox name="taskList" value="${task.id}" checked="${false}"/></td>
                        <td title="Scheduled Task"><g:link controller="scheduledTask" action="edit" id="${task.id}" >${task.group.name}</g:link></td>
                        <td title="Actions">${task.verboseDescription}</td>
                        <td title="Logging Level">${LoggingLevel.createEnum(task.loggingLevel).displayString}</td>                        
                      </tr>
                    </g:each>
                  </g:if>
                  <g:else>
                    <tr class="row_even">
                      <td style="text-align:center;" colspan="5">No scheduled tasks currently exist.</td>
                    </tr>
                  </g:else>
                </table>
              </div>
              <div class="paginateButtons" style="margin: 1%;">
                <g:paginate prev="&laquo; previous" next="next &raquo;" total="${taskInstanceTotal}" />
              </div>
            </div>
          </div>
        </div>
      </g:form>
    </div>

  </body>
</html>
