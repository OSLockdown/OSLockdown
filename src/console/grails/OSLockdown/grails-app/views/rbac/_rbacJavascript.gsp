<r:require modules="application"/>
<r:script>

  var toggled=false;
  $(document).ready(function() {
    $('#showHide').click(function() {
      if(toggled==false) {
        $('#showHide').html('Display Actions Table &#x25b2;');
        toggled=true;
      }
      else {
        $('#showHide').html('Display Actions Table &#x25bc;');
        toggled=false;
      }
      $("#allowedActions").toggle();
      return false;
    });
  });

</r:script>
