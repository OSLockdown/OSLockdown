<%@ page import="com.trustedcs.sb.license.SbLicense" %>
<div class="info">
    <div class="info_header">
        <h2>General Information</h2>
    </div>
    <table class="zebra">        
        <tbody>                                        
	        <tr class="stripe">
	            <td style="width:50%">User:</td>
	            <td><shiro:principal/></td>
	        </tr>	                      
	        <tr class="stripe">
	            <td>Console Type:</td>
	            <td><sbauth:product /></td>
	        </tr>	       
	        <tr class="stripe">
	            <td>Version:</td>
	            <td><g:meta name="app.version"/></td>
	        </tr>             
	        <tr class="stripe">
	            <td>Last Login:</td>
	            <td><dateFormat:printDate date="${session.lastLogin}"/></td>
	        </tr>
        </tbody>                                                                                                                                                    
    </table>
</div>
