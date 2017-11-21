<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Undo Report XML to XHTML
     =========================================================================
-->
  <xsl:param name="report.title">Undo Report</xsl:param>
  <xsl:param name="css.file">/OSLockdown/css/undo-report.css</xsl:param>

  <xsl:param name="modules.display.left">false</xsl:param>
    
  <xsl:include href="common-xhtml.xsl"/>
  <xsl:include href="xhtml-report-styles.xsl"/>

  <xsl:output method="html" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
             doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" indent="yes" encoding="utf-8" />


  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml" dir="ltr">
      <xsl:call-template name="html.header"/>
            
      <body>
        <a name="top"/>
                    
        <xsl:if test="$header.display != 'false'">
          <xsl:call-template name="header"/>
        </xsl:if>
                    
        <table class="sectionTable">
          <tr>
            <th style="text-align:left;" colspan="3">Summary</th>
            <th style="text-align: right" colspan="3">
              <span style="font-size: 8pt">
                <xsl:text>Created: </xsl:text>
                <xsl:value-of select="/UndoReport/report/@created"/>
              </span>
            </th>
          </tr>
                        
          <tr>
            <td class="subSectionTitle" style="border-bottom: 1px dotted gray; border-right: 1px solid black; text-align: right">Hostname</td>
            <td class="infoItem" colspan="5" style="border-bottom: 1px dotted gray;">
              <xsl:value-of select="/UndoReport/report/@hostname"/>
            </td>
          </tr>
                        
          <tr>
            <td class="subSectionTitle" style="text-align: right; border-bottom: 1px dotted gray; border-right: 1px solid black;">Operating System</td>
            <td class="infoItem" colspan="5" style="border-bottom: 1px dotted gray;">
              <xsl:variable name="distVersion" select="/UndoReport/report/@distVersion"/>
              <xsl:variable name="dist" select="/UndoReport/report/@dist"/>
              <xsl:choose>
                <xsl:when test="$distVersion = '10' and $dist = 'redhat'">
                  <xsl:text>Fedora 10</xsl:text>
                </xsl:when>
                <xsl:when test="$dist = 'Red Hat'">
                  <xsl:text>Red Hat Enterprise Linux </xsl:text>
                  <xsl:value-of select="/UndoReport/report/@distVersion"/>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="/UndoReport/report/@dist"/>
                  <xsl:text> </xsl:text>
                  <xsl:value-of select="/UndoReport/report/@distVersion"/>
                </xsl:otherwise>
              </xsl:choose>
            </td>
          </tr>
                        
                        <!-- Profile Information -->
          <xsl:call-template name="profile.information">
            <xsl:with-param name="reportRoot" select="/UndoReport"/>
          </xsl:call-template>

                        
          <tr>
            <td rowspan="5" class="subSectionTitle" width="5%" style="text-align:right;">Results</td>
            <td class="infoName" rowspan="2" style="vertical-align: bottom; border-bottom: none; border-right: 1px solid black; text-align: right">High Risk</td>
            <th class="statsHeader" style="text-align:center; border-top: none; color: red;">Errors</th>
            <th class="statsHeader" style="text-align:center; border-top: none; color: green">Undone</th>
            <th class="statsHeader" style="text-align:center; border-top: none; color: #467fc5" title="Not scanned or applicable">Not Required or N/A</th>
            <th class="statsHeader" style="text-align:center; border-top: none; border-left: 1px solid black;">Total</th>
          </tr>
                        
          <tr>
            <td class="statsCell" style="border-bottom: 1px dotted black">
              <xsl:value-of select="count(/UndoReport/modules/module[@severity='High' and @results='Error'])"/>
            </td>
            <td class="statsCell" style="border-bottom: 1px dotted black; border-left: 1px dotted black">
              <xsl:value-of select="count(/UndoReport/modules/module[@severity='High' and @results='Undone'])"/>
            </td>
            <td class="statsCell" style="border-bottom: 1px dotted black; border-left: 1px dotted black" >
              <xsl:value-of select="count(/UndoReport/modules/module[@severity='High' and @results != 'Undone' and @results != 'Error'])"/>
            </td>
            <td class="statsCell" style="border-left: 1px solid black">
              <xsl:value-of select="count(/UndoReport/modules/module[@severity='High'])"/>
            </td>
          </tr>
          <tr>
            <td class="infoName" style="border-bottom: none; border-right: 1px solid black; text-align: right">
                                Medium Risk
            </td>
            <td class="statsCell" style="border-bottom: 1px dotted black;">
              <xsl:value-of select="count(/UndoReport/modules/module[@severity='Medium' and @results='Error'])"/>
            </td>
            <td class="statsCell" style="border-bottom: 1px dotted black;border-left: 1px dotted black; ">
              <xsl:value-of select="count(/UndoReport/modules/module[@severity='Medium' and @results='Undone'])"/>
            </td>
            <td class="statsCell" style="border-bottom: 1px dotted black;border-left: 1px dotted black" >
              <xsl:value-of select="count(/UndoReport/modules/module[@severity='Medium' and @results != 'Undone' and @results != 'Error'])"/>
            </td>
            <td class="statsCell" style="border-left: 1px solid black">
              <xsl:value-of select="count(/UndoReport/modules/module[@severity='Medium'])"/>
            </td>
          </tr>
          <tr>
            <td class="infoName" style="border-right: 1px solid black; border-bottom: none; text-align: right">
                                Low Risk
            </td>
            <td class="statsCell">
              <xsl:value-of select="count(/UndoReport/modules/module[@severity='Low' and @results='Error'])"/>
            </td>
            <td class="statsCell" style="border-left: 1px dotted black" >
              <xsl:value-of select="count(/UndoReport/modules/module[@severity='Low' and @results='Undone'])"/>
            </td>
            <td class="statsCell" style="border-left: 1px dotted black" >
              <xsl:value-of select="count(/UndoReport/modules/module[@severity='Low' and @results != 'Undone' and @results != 'Error'])"/>
            </td>
            <td class="statsCell" style="border-left: 1px solid black">
              <xsl:value-of select="count(/UndoReport/modules/module[@severity='Low'])"/>
            </td>
          </tr>
                        
          <tr>
            <xsl:variable name="totalError" select="count(/UndoReport/modules/module[@results='Error'])"/>
            <xsl:variable name="totalUndone" select="count(/UndoReport/modules/module[@results='Undone'])"/>
            <xsl:variable name="totalOther" select="count(/UndoReport/modules/module[@results !='Undone' and @results !='Error'])"/>

            <td class="infoName" style="color: gray; border-right: 1px solid black; border-bottom: 1px solid black; text-align: right">
              <xsl:text>Totals&#x020;</xsl:text>
            </td>

            <td class="statsCell" style="border-top: 2px solid black; color: red; font-weight: bold">
              <xsl:value-of select="count(/UndoReport/modules/module[@results='Error'])"/>
              <xsl:text> (</xsl:text>
              <xsl:value-of select="round(($totalError div ($totalError + $totalUndone + $totalOther)) * 100)"/>
              <xsl:text>%)</xsl:text>
            </td>
            <td class="statsCell" style="border-left: 1px solid black; border-top: 2px solid black; color: green; font-weight: bold">
              <xsl:value-of select="count(/UndoReport/modules/module[@results='Undone'])"/>
              <xsl:text> (</xsl:text>
              <xsl:value-of select="round(($totalUndone div ($totalError + $totalUndone + $totalOther)) * 100)"/>
              <xsl:text>%)</xsl:text>
            </td>
            <td class="statsCell" style="border-left: 1px solid black; border-top: 2px solid black; color: #467fc5">
              <xsl:value-of select="count(/UndoReport/modules/module[@results != 'Undone' and @results != 'Error'])"/>
              <xsl:text> (</xsl:text>
              <xsl:value-of select="round(($totalOther div ($totalError + $totalUndone + $totalOther)) * 100)"/>
              <xsl:text>%)</xsl:text>
            </td>
            <td class="statsCell" style="border-left: 1px solid black; border-top: 2px solid black;">
              <xsl:value-of select="count(/UndoReport/modules/module)"/>
            </td>
          </tr>
                        
        </table>
        <div style="padding-top: 10px; color: gray; width: 100%; text-align: left;">
          <a href="#" style="cursor:pointer" onClick="return expandAll();">Show</a> /
          <a href="#" style="cursor:pointer" onClick="return collapseAll();">Hide</a> all module descriptions.
        </div>
                    
          <!--
              ================================================================ 
                         Results of Security Modules
              ================================================================
          -->
        <xsl:if test="count(/UndoReport/modules/module) != 0">
          <a name="modules"/>
          <table id="modules" class="sectionTable sortable">
            <thead>
              <tr>
                <th colspan="3" class="sectionHeader">Security Module</th>
                <th style="text-align: center">Result</th>
              </tr>
            </thead>
            <tbody>
              <xsl:for-each select="/UndoReport/modules/module">
                <xsl:sort select="@name"/>
                <tr>
                  <td class="moduleName" style="border-right: 1px solid black" colspan="3">
                    <span style="cursor:pointer; padding-right:.5em" onclick="toggleDisplay(this)">
                      <xsl:value-of select="@name"/>
                    </span>
                    <div class="moduleDescription" style="display: none">
                      <xsl:value-of select="./description"/>
                      <xsl:call-template name="module.message.details" >
                        <xsl:with-param name="details" select="./details"/>
                      </xsl:call-template>
                    </div>
                  </td>

                                <!-- Module Results -->
                  <xsl:call-template name="module.result">
                    <xsl:with-param name="results" select="@results"/>
                  </xsl:call-template>
                                

                </tr>
              </xsl:for-each>
            </tbody>
          </table>
        </xsl:if>

              <!-- Report Footer -->
        <xsl:if test="$footer.display != 'false'">
          <xsl:call-template name="footer">
            <xsl:with-param name="sbVersion" select="/UndoReport/@sbVersion"/>
          </xsl:call-template>
        </xsl:if>
                    
                    
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
