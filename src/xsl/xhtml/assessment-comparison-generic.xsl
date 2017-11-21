<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Assessment Comparison Report XML to XHTML
     =========================================================================
-->
  <xsl:param name="report.title">Assessment Comparison Report</xsl:param>
  <xsl:param name="css.file">/OSLockdown/css/assessment-comparison.css</xsl:param>
    
  <xsl:include href="xhtml-report-styles.xsl"/>
  <xsl:include href="common-xhtml.xsl"/>

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
                    
          <!--
              ================================================================ 
               Assessment Comparison Report Summary - Provide TOC of Report                         
              ================================================================
          -->
        <table class="sectionTable">
          <tr>
            <th style="text-align:left; white-space:nowrap" colspan="1">Summary</th>
            <th style="text-align: right; white-space:nowrap" colspan="2">
              <xsl:text>Generated: </xsl:text>
              <xsl:value-of select="substring(/AssessmentReportDelta/@created, 1, 20)"/>
            </th>
          </tr>
                        
          <tr>
            <td style="border-bottom: none; background-color:#eef1f8; width:15%">&#x020;</td>
            <td style="background-color: #eef1f8; border-left: 1px solid black; font-weight: bold">Report A</td>
            <td style="background-color: #eef1f8; border-left: 1px solid black; font-weight: bold; border-right: none">Report B</td>
          </tr>
                        
          <!-- System Names -->
          <tr>
            <td class="infoName" style="text-align: right; font-weight: bold; border-bottom: 1px dotted gray;background-color:#eef1f8;">Hostname</td>
                            
            <xsl:variable name="report1" select="/AssessmentReportDelta/report[1]"/>
            <xsl:variable name="report2" select="/AssessmentReportDelta/report[2]"/>
            <xsl:variable name="fontColor">
              <xsl:choose>
                <xsl:when test="$report1/@hostname != $report2/@hostname">color: #467fc5;</xsl:when>
                <xsl:otherwise>color: black;</xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
                            
            <td class="infoItem" style="border-left: 1px solid black; border-bottom: 1px dotted gray; {$fontColor}">
              <xsl:value-of select="$report1/@hostname"/>
            </td>
            <td class="infoItem" style="border-left: 1px solid black; border-bottom: 1px dotted gray; {$fontColor}">
              <xsl:value-of select="$report2/@hostname"/>
            </td>
          </tr>
                         
                        
          <!-- Operating systems -->
          <tr>
            <td class="infoName" nowrap="nowrap" style="text-align: right; font-weight: bold; border-bottom: 1px dotted gray;background-color:#eef1f8">Operating System</td>
                            
            <xsl:for-each select="/AssessmentReportDelta/report">
                                
              <xsl:variable name="report1" select="/AssessmentReportDelta/report[1]"/>
              <xsl:variable name="report2" select="/AssessmentReportDelta/report[2]"/>
                                
              <xsl:variable name="fontColor">
                <xsl:choose>
                  <xsl:when test="$report1/@distVersion != $report2/@distVersion or $report1/@dist != $report2/@dist or $report1/@arch != $report2/@arch or $report1/@kernel != $report2/@kernel">color: #467fc5;</xsl:when>
                  <xsl:otherwise>color: black;</xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
                                
              <td class="infoItem" style="border-left: 1px solid black; border-bottom: 1px dotted gray; {$fontColor}">
                <xsl:choose>
                  <xsl:when test="number(@distVersion) &gt;= 10 and @dist = 'redhat'">
                    <xsl:text>Fedora </xsl:text>
                  </xsl:when>
                  <xsl:when test="@dist = 'Red Hat'">
                    <xsl:text>Red Hat Enterprise Linux </xsl:text>
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:value-of select="@dist"/>
                    <xsl:text> </xsl:text>
                  </xsl:otherwise>
                </xsl:choose>
                <xsl:value-of select="@distVersion"/>
                                    
              </td>
            </xsl:for-each>
          </tr>
                        
         <!-- Creation Date of sub-reports -->
          <tr>
            <td class="infoName" style="text-align: right; font-weight: bold; border-bottom: 1px dotted gray;background-color:#eef1f8; ">Created</td>
            <td class="infoItem" style="border-left: 1px solid black; border-bottom: 1px dotted gray">
              <xsl:value-of select="/AssessmentReportDelta/report[1]/@created"/>
            </td>
            <td class="infoItem" style="border-left: 1px solid black; border-bottom: 1px dotted gray">
              <xsl:value-of select="/AssessmentReportDelta/report[2]/@created"/>
            </td>
          </tr>
                         
                        
                        <!-- Profiles -->
          <tr>
            <td class="infoName" style="text-align: right; font-weight: bold; border-bottom: 1px solid gray;background-color:#eef1f8;">Profile</td>
            <td class="infoItem" style="border-left: 1px solid black; border-bottom: 1px solid black">
              <xsl:value-of select="/AssessmentReportDelta/report[1]/@profile"/>
            </td>
            <td class="infoItem" style="border-left: 1px solid black; border-bottom: 1px solid black">
              <xsl:value-of select="/AssessmentReportDelta/report[2]/@profile"/>
            </td>
          </tr>
		 
		
		<!-- Statistics -->
          <xsl:variable name="totalMods" select="count(/AssessmentReportDelta/*/module)"/>
          <xsl:variable name="xMods" select="count(/AssessmentReportDelta/removed/module) + count(/AssessmentReportDelta/added/module)"/>
          <xsl:variable name="changedMods" select="count(/AssessmentReportDelta/changed/module)"/>
          <xsl:variable name="unchangedMods" select="count(/AssessmentReportDelta/unchanged/module)"/>
          <tr>
            <td class="infoName" style="background-color:#eef1f8;text-align: right; font-weight: bold; border-bottom: 1px solid black; vertical-align: top">Results</td>
            <td class="infoItem" colspan="2" style="border-left: 1px solid black; border-bottom: 1px solid black">
              <xsl:value-of select="$totalMods"/>
              <xsl:text> Total modules:</xsl:text>
              <ul style="margin-top: 5px; list-style-type: square">
                <li>
                  <a href="#changedModules">
                    <xsl:value-of select="$changedMods"/>
                    <xsl:choose>
                      <xsl:when test="$changedMods = 1 ">
                        <xsl:text> module with differing results</xsl:text>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text> modules with differing results</xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                  </a>
                </li>
 
                <li>
                  <a href="#unchangedModules">
                    <xsl:value-of select="$unchangedMods"/>
                    <xsl:choose>
                      <xsl:when test="$unchangedMods = 1 ">
                        <xsl:text> module with same result</xsl:text>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text> modules with same result</xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                  </a>
                </li>
                                
                <li>
                  <a href="#xModules">
                    <xsl:value-of select="$xMods"/>
                    <xsl:choose>
                      <xsl:when test="$xMods = 1 ">
                        <xsl:text> module present in only one report</xsl:text>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text> modules present in only one report</xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                  </a>
                </li>
              </ul>
            </td>
          </tr>
                        
        </table>
                    
          <!-- 
              ================================================================ 
                                       Changed Modules
              ================================================================
          -->
        <xsl:variable name="modules" select="/AssessmentReportDelta/changed/module"/>
        <a name="changedModules"/>
        <xsl:if test="count($modules) != 0">
          <table id="changedModules" class="sectionTable sortable">
             <thead>
	      <tr>
                <th colspan="3" class="sectionHeader">Modules with differing results</th>
                <th class="navigTop">
                   <a href="#top">top <xsl:value-of select="$entity.up.arrow"/></a>
                </th>
              </tr>
                	      
              <tr>
                <td class="sectionSubHeader" style="text-align: left; font-weight: bold">Module Name</td>
                <td class="sectionSubHeader" style="text-align: center; font-weight: bold">Severity</td>
                <td class="sectionSubHeader" style="text-align: center; font-weight: bold">Result A</td>
                <td class="sectionSubHeader" style="text-align: center; font-weight: bold; border-right: none">Result B</td>
              </tr>
             </thead>               
            <xsl:for-each select="$modules">
              <xsl:sort select="@name"/>
                                
              <xsl:variable name="leftBorder">border-left: 1px solid black;</xsl:variable>
              <xsl:variable name="rightBorder">border-right: 1px solid black;</xsl:variable>
              <xsl:variable name="bottomBorder">border-bottom: 1px solid black;</xsl:variable>
                                
              <xsl:variable name="cellColor">
                <xsl:choose>
                  <xsl:when test="position() mod 2 = 0">background-color: #efefef;</xsl:when>
                  <xsl:otherwise>background-color: white;</xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
                                
              <tr>
                <td colspan="1" class="moduleName" style="{$cellColor} {$bottomBorder} {$rightBorder}; ">
                  <span style="cursor:pointer; padding-right:.5em" onclick="toggleDisplay(this)">
                    <xsl:value-of select="@name"/>
                  </span>
                  <div class="moduleDescription" style="display: none">
                    <xsl:value-of select="./description"/>
                    <xsl:call-template name="module.compliancy.list" >
                      <xsl:with-param name="compliancy" select="./compliancy"/>
                    </xsl:call-template>
                  </div>
                </td>
                                     
                <td class="moduleResults" style="{$cellColor} {$bottomBorder} {$rightBorder};">
                  <xsl:value-of select="@severity"/>
                </td>

                <xsl:call-template name="module.result">
                  <xsl:with-param name="results" select="@resultsA"/>
                </xsl:call-template>
                                    
                <xsl:call-template name="module.result">
                  <xsl:with-param name="results" select="@resultsB"/>
                </xsl:call-template>
                                    
              </tr>
            </xsl:for-each>
          </table>
        </xsl:if>
                    
         <!-- 
              ================================================================ 
                 Modules which are not present in Both Reports
              ================================================================
          -->
        <xsl:variable name="delModules" select="/AssessmentReportDelta/removed/module"/>
        <xsl:variable name="addModules" select="/AssessmentReportDelta/added/module"/>
        <a name="xModules"/>
        <xsl:if test="count($delModules) != 0 or count($addModules) != 0">
          <table id="oneOrTheOtherModules" class="sectionTable sortable">
            <thead>
	       <tr>
                <th colspan="3" class="sectionHeader">Modules present in only one report</th>
                <th class="navigTop">
                  <a href="#top">
                			  top
                    <xsl:value-of select="$entity.up.arrow"/>
                  </a>
                </th>
              </tr>
                	      
              <tr>
                <td class="sectionSubHeader" style="text-align: left; font-weight: bold">Module Name</td>
                <td class="sectionSubHeader" style="text-align: center; font-weight: bold">Severity</td>
                <td class="sectionSubHeader" style="text-align: center; font-weight: bold">Result A</td>
                <td class="sectionSubHeader" style="text-align: center; font-weight: bold; border-right: none">Result B</td>
              </tr>
            </thead>               
                            <!-- Removed Modules -->
            <xsl:for-each select="$delModules">
              <xsl:sort select="@name"/>
                                
              <xsl:variable name="leftBorder">border-left: 1px solid black;</xsl:variable>
              <xsl:variable name="rightBorder">border-right: 1px solid black;</xsl:variable>
              <xsl:variable name="bottomBorder">border-bottom: 1px solid black;</xsl:variable>
                                
              <xsl:variable name="cellColor">
                <xsl:choose>
                  <xsl:when test="position() mod 2 = 0">background-color: #efefef;</xsl:when>
                  <xsl:otherwise>background-color: white;</xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
                                
              <tr>
                <td colspan="1" class="moduleName" style="{$cellColor} {$bottomBorder} {$rightBorder}; ">
                  <span style="cursor:pointer; padding-right:.5em" onclick="toggleDisplay(this)">
                    <xsl:value-of select="@name"/>
                  </span>
                  <div class="moduleDescription" style="display: none">
                    <xsl:value-of select="./description"/>
                    <xsl:call-template name="module.compliancy.list" >
                      <xsl:with-param name="compliancy" select="./compliancy"/>
                    </xsl:call-template>
                  </div>
                </td>
                                     
                <td class="moduleResults" style="{$cellColor} {$bottomBorder} {$rightBorder};">
                  <xsl:value-of select="@severity"/>
                </td>

                                    
                <xsl:call-template name="module.result">
                  <xsl:with-param name="results" select="@results"/>
                </xsl:call-template>
                                    
                <td class="moduleResults" style="{$cellColor} {$bottomBorder}">-</td>
                                    
              </tr>
            </xsl:for-each>
                            
                            <!-- Added Modules -->
            <xsl:for-each select="$addModules">
              <xsl:sort select="@name"/>
                                
              <xsl:variable name="leftBorder">border-left: 1px solid black;</xsl:variable>
              <xsl:variable name="rightBorder">border-right: 1px solid black;</xsl:variable>
              <xsl:variable name="bottomBorder">border-bottom: 1px solid black;</xsl:variable>
                                
              <xsl:variable name="cellColor">
                <xsl:choose>
                  <xsl:when test="position() mod 2 = 0">background-color: #efefef;</xsl:when>
                  <xsl:otherwise>background-color: white;</xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
                                
              <tr>
                <td colspan="1" class="moduleName" style="{$cellColor} {$bottomBorder} {$rightBorder}; ">
                  <span style="cursor:pointer; padding-right:.5em" onclick="toggleDisplay(this)">
                    <xsl:value-of select="@name"/>
                  </span>
                  <div class="moduleDescription" style="display: none">
                    <xsl:value-of select="./description"/>
                    <xsl:call-template name="module.compliancy.list" >
                      <xsl:with-param name="compliancy" select="./compliancy"/>
                    </xsl:call-template>
                  </div>
                </td>
                                     
                                    
                <td class="moduleResults" style="{$cellColor} {$bottomBorder} {$rightBorder};">
                  <xsl:value-of select="@severity"/>
                </td>

                <td class="moduleResults" style="{$cellColor} {$bottomBorder}">-</td>

                <xsl:call-template name="module.result">
                  <xsl:with-param name="results" select="@results"/>
                </xsl:call-template>
                                    
              </tr>
            </xsl:for-each>
                            
          </table>
        </xsl:if>
                    
         <!-- 
              ================================================================ 
                                       Unchanged Modules
              ================================================================
          -->
        <xsl:variable name="unmodules" select="/AssessmentReportDelta/unchanged/module"/>
        <a name="unchangedModules"/>
        <xsl:if test="count($unmodules) != 0">
          <table id="unchangedModules" class="sectionTable sortable">
            <thead>
              <tr>
                <th colspan="2" class="sectionHeader">Modules with same results</th>
                <th class="navigTop">
                  <a href="#top">
                                        top
                    <xsl:value-of select="$entity.up.arrow"/>
                  </a>
                </th>
              </tr>
                            
              <tr>
                <td class="sectionSubHeader" style="text-align: left; font-weight: bold">Module Name</td>
                <td class="sectionSubHeader" style="text-align: center; font-weight: bold">Severity</td>
                <td class="sectionSubHeader" style="text-align: center; font-weight: bold">Result</td>
              </tr>
            </thead>
                            
            <tbody>
              <xsl:for-each select="$unmodules">
                <xsl:sort select="@name"/>
                                
                <xsl:variable name="leftBorder">border-left: 1px solid black;</xsl:variable>
                <xsl:variable name="rightBorder">border-right: 1px solid black;</xsl:variable>
                <xsl:variable name="bottomBorder">border-bottom: 1px solid black;</xsl:variable>
                                
                <xsl:variable name="cellColor">
                  <xsl:choose>
                    <xsl:when test="position() mod 2 = 0">background-color: #efefef;</xsl:when>
                    <xsl:otherwise>background-color: white;</xsl:otherwise>
                  </xsl:choose>
                </xsl:variable>
                                
                <tr>
                  <td colspan="1" class="moduleName" style="{$cellColor} {$bottomBorder} {$rightBorder}; ">
                    <span style="cursor:pointer; padding-right:.5em" onclick="toggleDisplay(this)">
                      <xsl:value-of select="@name"/>
                    </span>
                    <div class="moduleDescription" style="display: none">
                      <xsl:value-of select="./description"/>
                      <xsl:call-template name="module.compliancy.list" >
                        <xsl:with-param name="compliancy" select="./compliancy"/>
                      </xsl:call-template>
                    </div>
                  </td>
                                     
                <td class="moduleResults" style="{$cellColor} {$bottomBorder} {$rightBorder};">
                  <xsl:value-of select="@severity"/>
                </td>
                                    
                  <xsl:call-template name="module.result">
                    <xsl:with-param name="results" select="@results"/>
                  </xsl:call-template>
                                    
                </tr>
              </xsl:for-each>
            </tbody>
          </table>
        </xsl:if>
                    
                    <!-- ======================================================================== -->
                    <!-- Report Footer -->
        <xsl:if test="$footer.display != 'false'">
          <xsl:call-template name="footer">
            <xsl:with-param name="sbVersion" select="/AssessmentReportDelta/@sbVersion"/>
          </xsl:call-template>
        </xsl:if>

      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
