<html>
  <head>
    <title>TITLE</title>
    <meta name="layout" content="main" />  
    <r:require modules="application"/>
    <r:script>
      var timeout    = 500;
      var closetimer = 0;
      var ddmenuitem = 0;

      function jsddm_open() {
        jsddm_canceltimer();
        jsddm_close();
        ddmenuitem = $(this).find('ul').css('visibility', 'visible');
      }

      function jsddm_close() {
        if(ddmenuitem) {
          ddmenuitem.css('visibility', 'hidden');
        }
      }

      function jsddm_timer() {
        closetimer = window.setTimeout(jsddm_close, timeout);
      }

      function jsddm_canceltimer() {
        if(closetimer) {
          window.clearTimeout(closetimer);
          closetimer = null;
        }
      }

      $(document).ready(function() {
        $('#jsddm > li').bind('mouseover', jsddm_open)
        $('#jsddm > li').bind('mouseout',  jsddm_timer)
      });

      document.onclick = jsddm_close;
    </r:script>
  </head>
  <body id="test">
    <div id="per_page_container">
      <div class="container" id="per_page_header" title="Title">
        <div class="headerLeft">
          <h1>Title</h1>
        </div>
        <div class="headerRight">
        </div>
      </div>
      <div id="yui-main">
        <div id="main_content" class="subpage">
          <div class="info">
            <div class="info_header" title="Things and Stuff">
              <h2>Things and Stuff</h2>
            </div>
            <div class="info_body" title=" Hooray for Examples">
              Hooray for Examples
              <g:donuts params="['foo':'bar','legion':'honor']"/>
              <g:donuts params="${donutMap}"/>
            </div>
          </div>
        </div> <!-- End of main_content -->
      </div> <!-- End of yui-main -->
    </div> <!-- End of per_page_container -->
  </body>
</html>
