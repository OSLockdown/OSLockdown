
<%@ page import="com.trustedcs.sb.util.LoggingLevel" %>
<div class="info">
  <div style="padding-bottom:1em;padding-top:1.5em;" class="info_body">
    <fieldset>
      <legend>Security Policy</legend>
      <table>
        <tr>
          <td title="Security Profile"><label for="Security Profile">Security Profile</label>:</td>
          <td title="Security Profile Name"><g:select style="width:30em;text-align:center;" name="securityProfile" from="${securityProfileList}" optionKey="id" optionValue="name" value="${groupInstance?.profile?.id ? groupInstance.profile.id : '' }" noSelection="['':'[- Choose a Security Profile -]']"/></td>
        </tr>
        <tr>
          <td title="Baseline Profile"><label for="Baseline Profile">Baseline Profile</label>:</td>
          <td title="Baseline Profile Name"><g:select style="width:30em;text-align:center;" name="baselineProfile" from="${baselineProfileList}" optionKey="id" optionValue="name" value="${groupInstance?.baselineProfile?.id ? groupInstance.baselineProfile.id : '' }" noSelection="['':'[- Choose a Baseline Profile -]']"/></td>
        </tr>
      </table>
    </fieldset>
  </div>
  <div style="padding-bottom:1em;" class="info_body">
    <fieldset>
      <legend>Policy Invocation</legend>
      <table>
        <tr>
          <td title="Action"><label for="Action">Action</label>:</td>
          <td><g:select style="width:10em;text-align:center;" name="dispatcherAction" from="${actionList}" value="${params.dispatcherAction}" /></td>
        </tr>
        <tr>
          <td title="Logging Level"><label for="Logging Level">Logging Level</label>:</td>
          <td><g:select style="width:10em;text-align:center;" name="loggingLevel" from="${LoggingLevel.displayMap().entrySet()}" optionKey="key" optionValue="value" value="${loggingLevel}"/></td>
        </tr>
        <tr>
          <td title="Dispatcher Port"><label for="Dispatcher Port">Dispatcher Port</label>:</td>
          <td><g:textField name="agentPort" size="5" onKeyUp="limitText(this.form.agentPort,5);" value="${clientInstance?.port}"/></td>
        </tr>
      </table>
    </fieldset>
  </div>
  <div class="buttonsDiv">
    <input style="width:10em;" type="submit" class="btninput" value="Run" title="Click to submit action" />
  </div>
</div>
