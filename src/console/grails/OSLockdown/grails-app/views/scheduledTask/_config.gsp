
<%@ page import="com.trustedcs.sb.util.LoggingLevel" %>
<%@ page import="com.trustedcs.sb.util.SbDateUtil" %>

<div style="padding-top:0.5em;">
  <table>
    <tr>
      <td class="tdName" title="Group">
        <label for="Group">Group:</label>
      </td>
      <td>
          <g:select class="paddedSelect" title="Select Group Name" name="groupId" from="${groupList}" optionKey="id" optionValue="name"
                    value="${task?.group?.id}" noSelection="['':'[-Select a Group-]']"/>
      </td>
    </tr>
    <tr>
      <td class="tdName" title="Logging Level">
        <label for="Logging Level">Logging Level:</label>
      </td>
      <td title="Select Logging Level Name">
        <g:select style="width:9em;" name="loggingLevel" from="${LoggingLevel.displayMap().entrySet()}"
                  optionKey="key" optionValue="value" value="${task ? task.loggingLevel : 5}" />
      </td>
    </tr>
    <tr>
      <td class="tdName" title="Generate Comparison with previous report (Scan/Baseline Only)">
        <label for="Generate Comparison with previous report(Scan/Baseline Only)">Generate Comparison with previous report (Scan/Baseline Only):</label>
      </td>
      <td title="Select Logging Level Name">
        <g:checkBox name="genDelta" value="${task ? task.genDelta : false}" />
      </td>
    </tr>
    <tr>
      <td colspan="2" style="text-align:left;padding-left:6em;padding-right:6em;">
        <fieldset>
          <legend>Period</legend>
          <!-- daily -->
          <div style="padding-left:6em;" id="daily">
            <g:radio name="periodType" value="0" onclick="return togglePeriod('daily');" checked="${ task?.isDaily() || !(task?.id) }" />
            <label for="Daily">Daily</label>
          </div>
          <!-- weekly -->
          <div style="padding-left:6em;padding-top:0.5em;" id="weekly">
            <g:radio name="periodType" value="1" onclick="return togglePeriod('weekly');" checked="${ task?.isWeekly() }" />
            <label for="Weekly">Weekly on : </label>
            <g:if test="${task?.isWeekly()}">
              <g:select id="dayOfWeek" style="width:9em;" name="periodIncrement" from="${SbDateUtil.daysOfTheWeekMap}" optionKey="key" optionValue="value" value="${task?.periodIncrement}"  title="Select Day of the Week"/>
            </g:if>
            <g:else>
              <g:select id="dayOfWeek" style="width:9em;" name="periodIncrement" from="${SbDateUtil.daysOfTheWeekMap}" disabled="true" optionKey="key" optionValue="value" value="0"  title="Select Day of the Week"/>
            </g:else>
          </div>
          <!-- monthly -->
          <div style="padding-left:6em;padding-top:0.5em;" id="monthly">
            <g:radio name="periodType" value="2" onclick="return togglePeriod('monthly');" checked="${ task?.isMonthly() }" />
            <label for="Monthly">Monthly on day :</label>
            <g:if test="${task?.isMonthly()}">
              <g:select id="dayOfMonth" style="width:4em;" name="periodIncrement" from="${SbDateUtil.daysOfTheMonthRange}" value="${task?.periodIncrement}" title="Select Day of the Month" />
            </g:if>
            <g:else>
              <g:select id="dayOfMonth" style="width:4em;" name="periodIncrement" from="${SbDateUtil.daysOfTheMonthRange}" disabled="true" value="1" title="Select Day of the Month" />
            </g:else>
          </div>
        </fieldset>
      </td>
    </tr>
    <tr>
      <td colspan="2" style="text-align:center;padding-left:6em;padding-right:6em;">
        <fieldset>
          <legend>Time of Day</legend>
          <div>
            <g:select style="width:4em;" name="hour" from="${hoursRange}" value="${task?.hoursAmPm}" title="Select Hour" />
            <span class="bold">:</span>
            <g:select style="width:4em;" name="minute" from="${SbDateUtil.minutesMap}" optionKey="key" optionValue="value" value="${task?.minute}" title="Select Minute" />
            <g:select style="width:4em;" name="hoursOffset" from="${[0:'am',12:'pm']}" optionKey="key" optionValue="value" value="${task?.hoursOffset}" title="Select AM or PM" />
          </div>
        </fieldset>
      </td>
    </tr>
    <tr>
    <g:set var="currentActionCount" value="${0}" />
    <td colspan="2" style="text-align:left;padding-left:6em;padding-right:6em;">
      <fieldset id="actionContainer">
        <legend style="cursor:pointer;" onClick="javascript:addAction();" title="Click to add an action">+&nbsp;Actions</legend>
        <g:if test="${task}">
          <g:each var="a" in="${task?.actions}">
            <g:set var="currentActionCount" value="${currentActionCount + 1}" />
            <div class="pad3top" style="padding-left:1em;" id="div.action.${currentActionCount}" filter="tag">
              <a class="btn" title="Click to remove action." href="javascript:removeAction('${currentActionCount}');">-</a>
              <g:select style="width:9em;clear: right;" name="taskAction" from="${taskActions.entrySet()}" optionKey="key" optionValue="value" value="${a}"/>
            </div>
          </g:each>
        </g:if>
        <g:else>
          <g:set var="currentActionCount" value="${currentActionCount + 1}" />
          <div class="pad3top" style="padding-left:1em;" id="div.action.${currentActionCount}" filter="tag">
            <a class="btn" title="Click to remove action." href="javascript:removeAction('${currentActionCount}');">-</a>
            <g:select style="clear: right;width:9em;" name="taskAction" from="${taskActions.entrySet()}" optionKey="key" optionValue="value" value="${a}"/>
          </div>
        </g:else>
      </fieldset>
    </td>
    <g:hiddenField id="actionCount" name="actionCount" value="${currentActionCount}" />
    </tr>
  </table>
</div>
