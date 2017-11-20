<!-- ********************************************************** -->
<!-- ACTION BAR FOR MULTIPLE Notifications -->
<!-- ********************************************************** -->

<div id="actionbar">
    
	<!--
		For the action bar that applies to multiple notifications,
		the g:form tag is in the main page (not the template)
		since checkboxes from the list must be inside the form.
	-->            

    <shiro:hasAnyRole in="['Administrator','User']">
        <div class="actions">            
            <div class="action_title" title="Actions">Notification</div>
      		<ui>	            			            			            			            			
      			<li><g:actionSubmit class="action_bar_btn" id="deleteMulti" value="Delete" action="deleteMulti" title="Delete"/></li>
	        </ui>       		
        </div>
	</shiro:hasAnyRole>
	            	      	        	
</div><!-- end actionbar -->