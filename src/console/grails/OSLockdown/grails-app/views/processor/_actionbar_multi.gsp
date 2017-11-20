
<!-- ********************************************************** -->
<!-- ACTION BAR FOR MULTIPLE SELECTED PROCESSORS -->
<!-- ********************************************************** -->

<div id="actionbar">


  <shiro:hasAnyRole in="['Administrator','User']">

   <div class="actions">

     <div class="action_title">Processor</div>
     <ui>
       <li><g:link class="action_bar_btninput" title="Click for New Processor"  action="create">New</g:link></li>
       <li><g:actionSubmit class="action_bar_btninput" id="deleteMulti" title="Delete "  value="Delete" action="deleteMulti"/></li>
     </ui>
   </div>
    
  </shiro:hasAnyRole>


</div><!-- end actionbar -->
