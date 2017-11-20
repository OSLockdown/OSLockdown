  <r:require modules="application"/>
  <r:script >
    function togglePeriod(type) {
      if ( type == 'daily' ) {
        document.getElementById("dayOfWeek").disabled = true;
        document.getElementById("dayOfMonth").disabled = true;
        return;
      }
      if ( type == 'weekly' ) {
        document.getElementById("dayOfWeek").disabled = false;
        document.getElementById("dayOfMonth").disabled = true;
        return;
      }
      if ( type == 'monthly' ) {
        document.getElementById("dayOfWeek").disabled = true;
        document.getElementById("dayOfMonth").disabled = false;
        return;
      }
      return;
    }

    function addAction() {
      //Create AjaxRequest object
      var ajaxRequest = new AjaxRequest("${resource(dir:'')}/scheduledTask/addTaskAction");
      ajaxRequest.addFormElementsById('actionCount');
      //Send the request
      ajaxRequest.sendRequest();
    }

    function removeAction(id) {
      //Create AjaxRequest object
      var ajaxRequest = new AjaxRequest("${resource(dir:'')}/scheduledTask/removeTaskAction");
      ajaxRequest.addNameValuePair('actionId',id);
      //Send the request
      ajaxRequest.sendRequest();
    }
  </r:script>
