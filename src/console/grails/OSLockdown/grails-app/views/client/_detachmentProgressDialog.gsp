<!-- Hidden div used as a template for the Detach popup asking the user if he wants to proceed with retaining the Reports files.-->
<div id="detachmentDialog" style="display:none; cursor: wait;margin-top: auto;margin-bottom: auto;">
  <img id="detachProgressIcon" style="margin-top:10px;" src="${resource(dir:'images',file:'loading.gif')}" />
  <h1 id="detachWarningMessage" style="margin:10px;text-align: left;">
Detaching clients may take a few minutes; progress is displayed below. Closing or refreshing this window will cause the
Detach operation to complete incorrectly. Accessing OS Lockdown in another window is allowed, however, only one Detach operation
can be run at any time.
  </h1>
  <button id="detachAbort" style="margin-bottom:10px;">Stop Detach</button>
  <!-- Initial text-align is center for the initial message; then it's changed to left. -->
  <div id="detachProgressMessage" style="text-align: center;vertical-align: middle;" >Starting to Detach Clients ...</div>
</div>
