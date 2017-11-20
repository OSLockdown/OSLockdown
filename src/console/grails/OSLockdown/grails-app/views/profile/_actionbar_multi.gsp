

<!-- ********************************************************** -->
<!-- ACTION BAR FOR PROFILE -->
<!-- ********************************************************** -->

<div id="actionbar">

  <!--
          For the action bar that applies to multiple Tasks,
          the g:form tag is in the main page (not the template)
          since checkboxes from the list must be inside the form.
  -->

  <shiro:hasAnyRole in="['Administrator','User']">
    <div class="actions">
      <div class="action_title" title="Profile Actions">Profile</div>
      <ui>
              <li><g:link class="action_bar_btn" controller="profile" action="profileBuilder" event="newProfile" title="Click to Create a New Profile">New</g:link></li>
              <li><a class="action_bar_btn" href="javascript:showHideElement('upload');" style="#margin: 0.5em .17em .5em 0.12em;" title="Click to Import Profiles">Import</a></li>
              <li><g:actionSubmit action="deleteMulti" class="action_bar_btninput" id="deleteMulti" title="Click to Delete selected Profiles" value="Delete" /></li>
              <li><g:actionSubmit action="copyProfile" class="action_bar_btninput" id="copyProfile" title="Click to Copy Profiles" name="copyProfile" value="Copy" /></li>
              <li><g:actionSubmit action="exportProfile" class="action_bar_btninput" id="exportProfile" title="Click to Export Profiles" name="exportProfile" value="Export" /></li>
      </ui>
    </div>
  </shiro:hasAnyRole>

</div><!-- end actionbar -->

