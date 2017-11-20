            <!-- ********************************************************** -->
            <!-- ACTION BAR -->
            <!-- ********************************************************** -->
            
            <div id="actionbar">
            
            	<!--
            		For the action bar that applies to only a single Client,
            		the g:form tag is in the template and does not need
            		to surround any input types outside the template.  The
            		Client id is passed in as part of the model by the
            		controller.
            		
            		TODO: how to handle both a client and group?
            	-->
                <g:form>
                <input type="hidden" name="id" value="${clientInstance?.id}" />
                <!--input type="hidden" name="group_id" value="${groupInstance?.id}" /-->                                           
            	<!-- How to handle both Clients and Groups with this template? -->
            
				<div class="actions">            
            		<div class="action_title">Configuration</div>
            		<ui>
            			<li><g:link class="action_bar_btn" action="list">List</g:link></ul>            			            		
            			<li><g:link class="action_bar_btn" action="create">New</g:link></ul>
            			<li><g:actionSubmit class="action_bar_btninput" value="Edit" action="edit" /></ul>            			
            			<li><g:actionSubmit class="action_bar_btninput" onclick="return confirm('Are you sure you want to delete this?');" value="Delete" action="delete"/></ul>
            		</ui>       		
            	</div>            
            

				<div class="actions">            
            		<div class="action_title">Actions</div>
            		<ui>
            			<li><g:actionSubmit class="action_bar_btninput" onclick="return confirm('Are you sure?');" value="Status" action="status"/></ul>
            			<li><g:actionSubmit class="action_bar_btninput" onclick="return confirm('Are you sure?');" value="Apply" action="apply"/></ul>
            			<li><g:actionSubmit class="action_bar_btninput" onclick="return confirm('Are you sure?');" value="Scan" action="scan"/></ul>
            			<li><g:actionSubmit class="action_bar_btninput" onclick="return confirm('Are you sure?');" value="Undo" action="undo"/></ul>
            			<li><g:actionSubmit class="action_bar_btninput" onclick="return confirm('Are you sure?');" value="Baseline" action="baseline"/></ul>           			            			            			
            		</ui>           		            		
            	</div>  

				<div class="actions">            
            		<div class="action_title">Reports</div>
            		<ui>
            			<li><span class="action_bar_btn">Assessment</span></ul>
            			<li><span class="action_bar_btn">Baseline</span></ul>            			            			            			
            		</ui>         		            		
            	</div>        
            	
            	</g:form>
            	      	        	
            </div><!-- navbar -->