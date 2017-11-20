<tr class="row_odd">    
    <td class="propName" ><label for="Profile Name">Profile Name</label>:</td>
    <td>${dataMap["profileName"]}</td>
</tr>
<tr class="row_even">    
    <td class="propName" ><label for="">Number of Modules</label>:</td>
    <td>${dataMap["totalModules"]}</td>
</tr>
<tr class="row_odd">    
    <td class="propName" ><label for="Total Time">Time it took to run the undo</label>:</td>
    <td><dateFormat:printTime millis='${dataMap["totalTime"]}'/></td>
</tr>
<tr class="row_even">    
    <td class="propName" ><label for="Total Undone">Modules that were undone</label>:</td> 
    <td>${dataMap["totalUndone"]}</td>
</tr>
<tr class="row_odd">    
    <td class="propName" ><label for="Total Not Required">Modules that were not required</label>:</td>
    <td>${dataMap["totalNotReqd"]}</td>
</tr>
<tr class="row_even">    
    <td class="propName" ><label for="Total Failed">Modules that failed</label>:</td>
    <td>${dataMap["totalFail"]}</td>
</tr>
<tr class="row_odd">    
    <td class="propName" ><label for="Total Not Applicable">Modules that were not applicable</label>:</td>
    <td>${dataMap["totalNA"]}</td>
</tr>
<tr class="row_even">    
    <td class="propName" ><label for="Total Errors">Number of errors that occurred</label>:</td>
    <td>${dataMap["totalError"]}</td>
</tr>
<tr class="row_odd">    
    <td class="propName" ><label for="Total Manual">Modules that Require Manual Action</label>:</td>
    <td>${dataMap["totalManual"]}</td>
</tr>
<tr class="row_even">    
    <td class="propName" ><label for="Total Other">Modules returning something else</label>:</td>
    <td>${dataMap["totalOther"]}</td>
</tr>
<tr class="row_even">    
    <td class="propName" ><label for="Filename">Assessment report file name</label>:</td>
    <td>${dataMap["fileName"]}</td>
</tr>
