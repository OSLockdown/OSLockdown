  <r:require modules="application" />
  <r:script type="text/javascript">
    var estimatedReportSize = ${baselineProfileInstance.estimatedReportSize};
    // Below 3 variables are used for calculation of estimatedForensicImportance and estimatedSystemLoad.
    // Comment them for now.
    //var estimatedForensicImportance = ${baselineProfileInstance.estimatedForensicImportance};
    //var estimatedSystemLoad = ${baselineProfileInstance.estimatedSystemLoad};
    //var moduleCount = ${ baselineProfileInstance.baselineModules ? baselineProfileInstance.baselineModules.size() : 0};

    function updateReportSize(state,reportSize,forensicImportance,systemLoad) {
      if (state == 'true') {
        //moduleCount += 1;
        estimatedReportSize += reportSize;
        //estimatedForensicImportance += forensicImportance;
        //estimatedSystemLoad += systemLoad;
      }
      else {
        //moduleCount -= 1;
        estimatedReportSize -= reportSize;
        //estimatedForensicImportance -= forensicImportance;
        //estimatedSystemLoad -= systemLoad;
      }
      $('#estimatedReportSize').text(estimatedReportSize);

      // TODO: ajax call to update forensic importance and system load
      //Create AjaxRequest object
      //var ajaxRequest = new AjaxRequest("${resource(dir:'')}/baselineProfile/ajaxUpdateLevels");
      // add data to the request
      //ajaxRequest.addNameValuePair('estimatedForensicImportance',estimatedForensicImportance);
      //ajaxRequest.addNameValuePair('estimatedSystemLoad',estimatedSystemLoad);
      //ajaxRequest.addNameValuePair('moduleCount',moduleCount);
      //Send the request
      //ajaxRequest.sendRequest();
    }


  </r:script>
