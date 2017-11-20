<div style="padding-top:0.5em;">
  <table>
    <tr>
      <td class="propName" title="Name"><label for="Name">Name*</label>:</td>
      <td class="profileName" style="text-align: left">
        <g:textField class="input" name="name" onKeyUp="limitText(this.form.name,35);" value="${baselineProfileInstance?.name}" size="30" title="Enter Profile Name" disabled="true"/>
    </td>
    <td><a class="btn" href="javascript:showHideElement('div_extraInfo');" title="Click for Details">Details</a></td>
    </tr>
    <tr>
      <td class="propName" title="Estimated Size"><label for="Estimated Size">Estimated Total Report Size</label>:</td>
      <td style="text-align: left">~<span id="estimatedReportSize">${baselineProfileInstance?.estimatedReportSize}</span> Kb</td>
    </tr>
  </table>
  <div id="div_extraInfo" style="display:none;">
    <table class="enterprise pad5all">
      <tr>
        <td style="vertical-align:top;" class="profileName" title="Summary"><label for="Summary">Summary</label>:</td>
        <td><g:textField class="input" name="summary" value="${baselineProfileInstance?.summary}" size="60" onKeyUp="limitText(this.form.summary,80);" title="Enter Short Description" disabled="true"/></td>
      </tr>
      <tr>
        <td style="vertical-align:top;" class="profileName" title="Description will appear in the assessment reports generated with this profile."><label for="Description">Description</label>:</td>
        <td><g:textArea class="input" name="description" value="${baselineProfileInstance?.description}" rows="5" cols="62" wrap="soft" disabled="true"/></td>
      </tr>
      <tr>
        <td style="vertical-align:top;" class="profileName" title="Comments"><label for="Comments">Comments</label>:</td>
        <td><g:textArea class="input" name="comments" value="${baselineProfileInstance?.comments}" rows="5" cols="62" wrap="soft" disabled="true"/></td>
      </tr>
    </table>
  </div>
</div>