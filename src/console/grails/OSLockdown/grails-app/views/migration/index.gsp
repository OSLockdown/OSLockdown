<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Manage Database</title>
    <meta name="layout" content="main" />
    <meta name="contextSensitiveHelp" content="enterprise-mig" />  
</head>
<body id="administration">
  <div id="per_page_container">
    <div id="per_page_header" title="Migration">
      <h1>Manage Database</h1>
    </div>
    <div id="yui-main">
      <div id="main_content" class="subpage">
        <div class="info half centerDiv">

          <div class="pad1TopBtm">
            <fieldset>
              <legend>Export database to XML snapshot</legend>
              <div class="pad1TopBtm" style="text-align:center;">
                <g:form controller="migration" action="exportDB">
                  <g:submitButton name="exportButton" value="Export Database Snapshot" class="btninput" title="Click to export the database"/>
                </g:form>
              </div>
            </fieldset>
          </div>

          <div class="pad1Btm">
            <fieldset>
              <legend>Import local XML snapshot into database</legend>
              <div class="pad1TopBtm">
                <g:form controller="migration" action="importDBLocal">
                  <table>
                    <tr>
                      <td style="width:70%;">
                        <g:select style="width:100%;" name="snapshot" from="${snapshots.descendingMap().entrySet()}" optionKey="key" optionValue="value" noSelection="['':'[-Select a snapshot-]']"/>
                      </td>
                      <td style="text-align:center;">
                        <input type="submit" class="btninput" value="Import Snapshot"/>
                      </td>
                    </tr>
                  </table>
                </g:form>
              </div>
            </fieldset>
          </div>

          <div class="pad1Btm">
            <fieldset>
              <legend>Upload XML snapshot into database</legend>
              <div id="upload" class="pad1TopBtm">
                <g:uploadForm controller="migration" action="importDB">
                <div class="fileinputs">
                  <input type="file" name="dbFile" size="23" class="input file1" />
                  <div class="fake_file">
                  </div>
                  <input type="submit" class="btninput" value="Upload Snapshot"/><input type="reset" class="btninput" value="Clear" />
                </div>
                </g:uploadForm>
              </div>
            </fieldset>
          </div>
        </div>
      </div> <!-- End of main_content -->
    </div> <!-- End of yui-main -->
  </div> <!-- End of per_page_container -->
</body>
</html>