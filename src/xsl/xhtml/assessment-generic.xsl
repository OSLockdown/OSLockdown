<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Assessment Report XML to XHTML
     =========================================================================
-->
  <xsl:param name="report.title">Assessment Report</xsl:param>
  <xsl:param name="css.file">/OSLockdown/css/assessment-report.css</xsl:param>
  <xsl:param name="modules.display.left">false</xsl:param>
    
  <xsl:include href="xhtml-report-styles.xsl"/>
  <xsl:include href="common-xhtml.xsl"/>
    
  <xsl:output method="html" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
             doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" indent="yes" encoding="utf-8" />

  <xsl:template match="/">
        
    <html xmlns="http://www.w3.org/1999/xhtml" dir="ltr">
      <xsl:call-template name="html.header"/>
            
      <body>
        <div class="reportWrapper">
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
                  <xsl:value-of select="/AssessmentReport/report/@created"/>
                </span>
              </th>
            </tr>
                        
            <tr>
              <td class="subSectionTitle" style="border-bottom: 1px dotted gray; border-right: 1px solid black; text-align: right">Hostname</td>
              <td class="infoItem" colspan="5" style="border-bottom: 1px dotted gray">
                <xsl:value-of select="/AssessmentReport/report/@hostname"/>
              </td>
            </tr>
                        
            <tr>
              <td class="subSectionTitle" style="text-align: right; border-bottom: 1px dotted gray; border-right: 1px solid black;">Operating System</td>
              <td class="infoItem" colspan="5" style="border-bottom: 1px dotted gray">
                <xsl:variable name="distVersion" select="/AssessmentReport/report/@distVersion"/>
                <xsl:variable name="dist" select="/AssessmentReport/report/@dist"/>
                <xsl:choose>
                  <xsl:when test="$distVersion = '10' and $dist = 'redhat'">
                    <xsl:text>Fedora 10</xsl:text>
                  </xsl:when>
                  <xsl:when test="$dist = 'Red Hat'">
                    <xsl:text>Red Hat Enterprise Linux </xsl:text>
                    <xsl:value-of select="/AssessmentReport/report/@distVersion"/>
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:value-of select="/AssessmentReport/report/@dist"/>
                    <xsl:text> </xsl:text>
                    <xsl:value-of select="/AssessmentReport/report/@distVersion"/>
                  </xsl:otherwise>
                </xsl:choose>
              </td>
            </tr>
                        
           <!-- Profile Information -->
            <xsl:call-template name="profile.information">
              <xsl:with-param name="reportRoot" select="/AssessmentReport"/>
            </xsl:call-template>
                        
            <tr>
              <td rowspan="5" class="subSectionTitle" width="5%" style="text-align:right;">Results</td>
              <td class="infoName" rowspan="2" style="vertical-align: bottom; border-bottom: none; border-right: 1px solid black; text-align: right">
                <a style="cursor:pointer" href="#high">High Risk</a>&#x020;
              </td>
              <th class="statsHeader" style="text-align:center; border-top: none; color: red;">Failed</th>
              <th class="statsHeader" style="text-align:center; border-top: none; color: green">Passed</th>
              <th class="statsHeader" style="text-align:center; border-top: none; color: #467fc5" title="Not scanned or applicable">Other</th>
              <th class="statsHeader" style="text-align:center; border-top: none; border-left: 1px solid black;">Total</th>
            </tr>
                        
            <tr>
              <td class="statsCell" style="border-bottom: 1px dotted black">
                <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='High' and @results='Fail'])"/>
              </td>
              <td class="statsCell" style="border-bottom: 1px dotted black; border-left: 1px dotted black">
                <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='High' and @results='Pass'])"/>
              </td>
              <td class="statsCell" style="border-bottom: 1px dotted black; border-left: 1px dotted black" >
                <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='High' and @results != 'Pass' and @results != 'Fail'])"/>
              </td>
              <td class="statsCell" style="border-left: 1px solid black">
                <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='High'])"/>
              </td>
            </tr>
            <tr>
              <td class="infoName" style="border-bottom: none; border-right: 1px solid black; text-align: right">
                <a style="cursor:pointer" href="#medium">Medium Risk&#x020;</a>
              </td>
              <td class="statsCell" style="border-bottom: 1px dotted black;">
                <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='Medium' and @results='Fail'])"/>
              </td>
              <td class="statsCell" style="border-bottom: 1px dotted black;border-left: 1px dotted black; ">
                <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='Medium' and @results='Pass'])"/>
              </td>
              <td class="statsCell" style="border-bottom: 1px dotted black;border-left: 1px dotted black" >
                <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='Medium' and @results != 'Pass' and @results != 'Fail'])"/>
              </td>
              <td class="statsCell" style="border-left: 1px solid black">
                <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='Medium'])"/>
              </td>
            </tr>
            <tr>
              <td class="infoName" style="border-right: 1px solid black; border-bottom: none; text-align: right">
                <a style="cursor:pointer" href="#low">Low Risk</a>&#x020;
              </td>
              <td class="statsCell">
                <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='Low' and @results='Fail'])"/>
              </td>
              <td class="statsCell" style="border-left: 1px dotted black" >
                <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='Low' and @results='Pass'])"/>
              </td>
              <td class="statsCell" style="border-left: 1px dotted black" >
                <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='Low' and @results != 'Pass' and @results != 'Fail'])"/>
              </td>
              <td class="statsCell" style="border-left: 1px solid black">
                <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='Low'])"/>
              </td>
            </tr>
                        
            <tr>
              <xsl:variable name="totalFail" select="count(/AssessmentReport/modules/module[@results='Fail'])"/>
              <xsl:variable name="totalPass" select="count(/AssessmentReport/modules/module[@results='Pass'])"/>
              <xsl:variable name="totalOther" select="count(/AssessmentReport/modules/module[@results !='Pass' and @results !='Fail'])"/>

              <td class="infoName" style="color: gray; border-right: 1px solid black; border-bottom: 1px solid black; text-align: right">
                <xsl:text>Totals&#x020;</xsl:text>
              </td>

              <td class="statsCell" style="border-top: 2px solid black; color: red; font-weight: bold">
                <xsl:value-of select="count(/AssessmentReport/modules/module[@results='Fail'])"/>
                <xsl:text> (</xsl:text>
                <xsl:value-of select="round(($totalFail div ($totalFail + $totalPass + $totalOther)) * 100)"/>
                <xsl:text>%)</xsl:text>
              </td>
              <td class="statsCell" style="border-left: 1px solid black; border-top: 2px solid black; color: green; font-weight: bold">
                <xsl:value-of select="count(/AssessmentReport/modules/module[@results='Pass'])"/>
                <xsl:text> (</xsl:text>
                <xsl:value-of select="round(($totalPass div ($totalFail + $totalPass + $totalOther)) * 100)"/>
                <xsl:text>%)</xsl:text>
              </td>
              <td class="statsCell" style="border-left: 1px solid black; border-top: 2px solid black; color: #467fc5">
                <xsl:value-of select="count(/AssessmentReport/modules/module[@results != 'Pass' and @results != 'Fail'])"/>
                <xsl:text> (</xsl:text>
                <xsl:value-of select="round(($totalOther div ($totalFail + $totalPass + $totalOther)) * 100)"/>
                <xsl:text>%)</xsl:text>
              </td>
              <td class="statsCell" style="border-left: 1px solid black; border-top: 2px solid black;">
                <xsl:value-of select="count(/AssessmentReport/modules/module)"/>
              </td>
            </tr>
                        
          </table>
          <div style="padding-top: 10px; color: gray; width: 100%; text-align: left;">
            <a href="#" style="cursor:pointer" onClick="return expandAll();">Show</a> /
            <a href="#" style="cursor:pointer" onClick="return collapseAll();">Hide</a> all module descriptions.
          </div>
          
          <xsl:call-template name="show_severity">
            <xsl:with-param name="sevTitle" select="'High'"/>
          </xsl:call-template>
          <xsl:call-template name="show_severity">
            <xsl:with-param name="sevTitle" select="'Medium'"/>
          </xsl:call-template>
          <xsl:call-template name="show_severity">
            <xsl:with-param name="sevTitle" select="'Low'"/>
          </xsl:call-template>
                    
                    
               <!-- Report Footer -->
          <xsl:if test="$footer.display != 'false'">
            <xsl:call-template name="footer">
              <xsl:with-param name="sbVersion" select="/AssessmentReport/@sbVersion"/>
            </xsl:call-template>
          </xsl:if>
                    
                    
        </div>
      </body>
    </html>
  </xsl:template>

  <xsl:template name="show_severity" match="/AssessmentReport/modules">
    <xsl:param name="sevTitle" />
    <xsl:param name="sevName" />
<!--
    <xsl:message>GOT HERE - checking <xsl:value-of select='$sevTitle'/></xsl:message>
    <xsl:message>GOT HERE - found <xsl:value-of select="count(/AssessmentReport/modules/module[@severity=$sevTitle])"/></xsl:message>
    <xsl:message>GOT HERE - found <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='High'])"/></xsl:message>
-->    
    <xsl:if test="count(/AssessmentReport/modules/module[@severity=$sevTitle]) != 0">
      <a name="$sevTitle"/>
      <table id="$sevTitle" class="sectionTable sortable">
        <thead>
          <tr>
            <th colspan="3" class="sectionHeader"><xsl:value-of select='$sevTitle'/> Risk</th>
            <th style="text-align:center">Results</th>
          </tr>
        </thead>
        <tbody>
          <xsl:for-each select="/AssessmentReport/modules/module[@severity=$sevTitle]">
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
                  <xsl:call-template name="module.compliancy.list" >
                    <xsl:with-param name="compliancy" select="./compliancy"/>
                  </xsl:call-template>
                </div>
              </td>
                          
              <xsl:call-template name="module.result">
                <xsl:with-param name="results" select="@results"/>
              </xsl:call-template>
                          
            </tr>
          </xsl:for-each>
        </tbody>
      </table>
    </xsl:if>
  </xsl:template>
</xsl:stylesheet>
