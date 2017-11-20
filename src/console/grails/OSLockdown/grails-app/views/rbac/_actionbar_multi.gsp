<div id="actionbar">          
  <shiro:hasAnyRole in="['Administrator']">
    <div class="actions">
      <div class="action_title">Users</div>
      <ui>
        <li><g:link class="action_bar_btn" action="create">New</g:link></li>
        <li><g:actionSubmit class="action_bar_btninput" id="deleteMulti" value="Delete" action="deleteMulti"/></li>
      </ui>
    </div>
  </shiro:hasAnyRole>
</div><!-- end actionbar -->