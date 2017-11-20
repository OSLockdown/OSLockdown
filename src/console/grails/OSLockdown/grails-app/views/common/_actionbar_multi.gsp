            <!-- ********************************************************** -->
            <!-- ACTION BAR FOR MULTIPLE SELECTED CLIENTS -->
            <!-- ********************************************************** -->
            
            <div id="actionbar">
            
            	<!--
            		For the action bar that applies to multiple Clients,
            		the g:form tag is in the main page (not the template)
            		since checkboxes from the list must be inside the form.
            		
            		TODO: how to handle both a client and group?
            	-->            

				<div class="actions">            
            		<div class="action_title">Configuration</div>
            		<ui>
            			<li><g:link class="action_bar_btn" action="list">List</g:link></ul>            			            		
            			<li><g:link class="action_bar_btn" action="create">New</g:link></ul>            			 
            			<li><g:actionSubmit class="action_bar_btninput" id="editMulti" value="Edit" action="editMulti" /></ul>            			            			
            			<li><g:actionSubmit class="action_bar_btninput" id="deleteMulti" onclick="return confirm('Are you sure you want to delete this?');" value="Delete" action="deleteMulti"/></ul>
            		</ui>       		
            	</div>
            	
				<div class="actions">            
            		<div class="action_title">Actions</div>
            		<ui>
            			<li><g:actionSubmit class="action_bar_btninput" id="statusMulti" onclick="return confirm('Are you sure?');" value="Status" action="statusMulti"/></ul>
            			<li><g:actionSubmit class="action_bar_btninput" id="applyMulti" onclick="return confirm('Are you sure?');" value="Apply" action="applyMulti"/></ul>
            			<li><g:actionSubmit class="action_bar_btninput" id="scanMulti" onclick="return confirm('Are you sure?');" value="Scan" action="scanMulti"/></ul>
            			<li><g:actionSubmit class="action_bar_btninput" id="undoMulti" onclick="return confirm('Are you sure?');" value="Undo" action="undoMulti"/></ul>
            			<li><g:actionSubmit class="action_bar_btninput" id="baselineMulti" onclick="return confirm('Are you sure?');" value="Baseline" action="baselineMulti"/></ul>            			            			            			
            		</ui>           		            		
            	</div>   
            	         	
				<div class="actions">            
            		<div class="action_title">Reports</div>
            		<ui>
            			<li><span class="action_bar_btn">Assessment</span></ul>
            			<li><span class="action_bar_btn">Baseline</span></ul>            			            			            			
            		</ui>         		            		
            	</div>             	            	                 	
            	      	        	
            </div><!-- end actionbar -->