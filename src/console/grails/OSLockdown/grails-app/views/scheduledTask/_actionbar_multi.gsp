<!-- ********************************************************** -->
<!-- ACTION BAR FOR TASKS -->
<!-- ********************************************************** -->

<div id="actionbar">

  <!--
  For the action bar that applies to multiple Tasks,
  the g:form tag is in the main page (not the template)
  since checkboxes from the list must be inside the form.
  -->

  <shiro:hasAnyRole in="['Administrator','User']">
    <div class="actions">
      <div class="action_title" title="Configuration">Scheduled Task</div>
      <ui>
        <li><g:link class="action_bar_btn" action="create" title="New">New</g:link></li>
        <li><g:actionSubmit class="action_bar_btn" id="deleteMulti" value="Delete" title="Delete" action="deleteMulti"/></li>
      </ui>
    </div>
  </shiro:hasAnyRole>

  <div class="actions">
    <div class="action_title" title="Actions">Actions</div>
    <ui>
      <shiro:hasAnyRole in="['Administrator','User']">
        <li><g:actionSubmit class="action_bar_btn" id="verifyMulti" value="Synchronize" action="verifyMulti" title="Synchronize this task" /></li>
      </shiro:hasAnyRole>
    </ui>
  </div>

</div><!-- end actionbar -->