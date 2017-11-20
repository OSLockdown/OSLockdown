<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: profile-comparison-generic.xsl 23917 2017-03-07 15:44:30Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Profile Comparison Report XML to XHTML
 
     =========================================================================
-->
  <xsl:param name="report.title">Profile Comparison Report</xsl:param>
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
               Profile Comparison Report Summary - Provide TOC of Report
              ================================================================
          -->
        <table class="sectionTable">
          <tr>
            <th style="text-align:left; white-space:nowrap" colspan="1">
              <xsl:text>Summary</xsl:text>
            </th>
            <th style="text-align: right; white-space:nowrap" colspan="2">
              <span style="font-size: 8pt">
                <xsl:text>Generated: </xsl:text>
                <xsl:value-of select="substring(/ProfileDelta/@created,1,20)"/>
              </span>
            </th>
          </tr>
                        
                        <!-- Profile Names -->
          <tr>
            <td class="infoName" style="text-align: right; font-weight: bold; border-bottom: 1px dotted gray ">Profile A</td>
            <td class="infoItem" style="border-left: 1px solid black; border-bottom: 1px dotted gray;" colspan="2">
              <xsl:value-of select="/ProfileDelta/profile[1]/@name"/>
            </td>
          </tr>
          <tr>
            <td class="infoName" style="text-align: right; font-weight: bold; border-bottom: 1px dotted gray ">Profile B</td>
            <td class="infoItem" style="border-left: 1px solid black; border-bottom: 1px dotted gray;" colspan="2">
              <xsl:value-of select="/ProfileDelta/profile[2]/@name"/>
            </td>
          </tr>
                        
                        
                        <!-- Statistics -->
          <xsl:variable name="xMods" select="count(/ProfileDelta/removed/module)"/>
          <xsl:variable name="yMods" select="count(/ProfileDelta/added/module)"/>
          <xsl:variable name="changedMods" select="count(/ProfileDelta/changed/module)"/>
          <tr>
            <td class="infoName" style="vertical-align: top; text-align: right; font-weight: bold; border-bottom: 1px solid black">Differences</td>
            <td class="infoItem" colspan="2" style="border-left: 1px solid black; border-bottom: 1px solid black">
              <ul style="margin-top: 2px; margin-bottom: 2px; list-style-type:square">
                <li>
                  <a href="#changedModules">
                    <xsl:value-of select="$changedMods"/>
                    <xsl:choose>
                      <xsl:when test="$changedMods = 1 ">
                        <xsl:text> module has different parameter values</xsl:text>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text> modules have different parameter values</xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                  </a>
                </li>
                                     
                                    
                <li>
                  <a href="#xModules">
                    <xsl:value-of select="$xMods"/>
                    <xsl:choose>
                      <xsl:when test="$xMods = 1 ">
                        <xsl:text> module was only present in Profile A</xsl:text>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text> modules were only present in Profile A</xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                  </a>
                </li>
                                    
                <li>
                  <a href="#yModules">
                    <xsl:value-of select="$yMods"/>
                    <xsl:choose>
                      <xsl:when test="$yMods = 1 ">
                        <xsl:text> module was only present in Profile B</xsl:text>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text> modules were only present in Profile B</xsl:text>
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
        <xsl:variable name="modules" select="/ProfileDelta/changed/module"/>
        <xsl:if test="count($modules) != 0">
          <a name="changedModules"/>
          <table class="sectionTable">
            <tr>
              <th colspan="3" class="sectionHeader">Modules with different parameter values</th>
              <th class="navigTop">
                <a href="#top">
                                        top
                  <xsl:value-of select="$entity.up.arrow"/>
                </a>
              </th>
            </tr>
                            
            <tr>
              <td class="sectionSubHeader" style="text-align: left; font-weight: bold">Module Name</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold">
                <xsl:value-of select="/ProfileDelta/profile[1]/@name"/>
              </td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold">
                <xsl:value-of select="/ProfileDelta/profile[2]/@name"/>
              </td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold; border-right: none;">Units</td>
            </tr>
                            
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
                <td colspan="1" class="moduleName" style="padding-left: 5px; {$cellColor} {$bottomBorder} {$rightBorder}">
                  <span style="cursor:pointer; padding-right:.5em" onclick="toggleDisplay(this)">
                    <xsl:value-of select="@name"/>
                  </span>
                  <div class="moduleDescription" style="display: none">
                    <xsl:value-of select="./option/description"/>
                  </div>
                </td>
                                    
                <xsl:variable name="optionType">
                  <xsl:choose>
                    <xsl:when test="./option/@type">
                      <xsl:value-of select="./option/@type"/>
                    </xsl:when>
                    <xsl:otherwise>
                      <xsl:text>xx</xsl:text>
                    </xsl:otherwise>
                  </xsl:choose>
                </xsl:variable>
                                    
                <xsl:choose>
                  <xsl:when test="$optionType != 'basicMultilineString'">
                    <td style="text-align: center; {$cellColor}; border-right: 1px solid black">
                      <xsl:value-of select="./option/valueA"/>
                    </td>
                    <td style="text-align: center; {$cellColor}; border-right: 1px solid black">
                      <xsl:value-of select="./option/valueB"/>
                    </td>
                  </xsl:when>
                  <xsl:otherwise>
                    <td colspan="2" style="color: gray; text-align: center; {$cellColor}; font-style: italic; border-right: 1px solid black">
                      <xsl:text>Multi-line values are too large to show here.</xsl:text>
                    </td>
                  </xsl:otherwise>
                </xsl:choose>
                                    
                <td style="font-style: italic; text-align: center; {$cellColor}">
                  <xsl:value-of select="./option/units"/>
                </td>
                                    
              </tr>
            </xsl:for-each>
          </table>
        </xsl:if>
                    
                    <!-- 
              ================================================================ 
                 Modules which are not present in Both Reports
              ================================================================
          -->
        <xsl:variable name="delModules" select="/ProfileDelta/removed/module"/>
        <xsl:variable name="addModules" select="/ProfileDelta/added/module"/>
        <xsl:if test="count($delModules) != 0">
          <a name="xModules"/>
          <table class="sectionTable">
            <tr>
              <th class="sectionHeader">
                <xsl:text>Modules only present in &#x201C;</xsl:text>
                <xsl:value-of select="/ProfileDelta/profile[1]/@name"/>
                <xsl:text>&#x201D;</xsl:text>
              </th>
              <th class="navigTop">
                <a href="#top">
                                        top
                  <xsl:value-of select="$entity.up.arrow"/>
                </a>
              </th>
            </tr>
                            
            <tr>
              <td class="sectionSubHeader" colspan="2" style="padding-left: 5px; text-align: left; font-weight: bold">Module Name</td>
            </tr>
                            
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
                <td colspan="2" class="moduleName" style="{$cellColor} {$bottomBorder}">
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
              </tr>
            </xsl:for-each>
          </table>
        </xsl:if>
                    
                    <!-- Added Modules -->
        <xsl:if test="count($addModules) != 0">
          <a name="yModules"/>
          <table class="sectionTable">
            <tr>
              <th class="sectionHeader">
                <xsl:text>Modules only present in &#x201C;</xsl:text>
                <xsl:value-of select="/ProfileDelta/profile[2]/@name"/>
                <xsl:text>&#x201D;</xsl:text>
              </th>
              <th class="navigTop">
                <a href="#top">
                                        top
                  <xsl:value-of select="$entity.up.arrow"/>
                </a>
              </th>
            </tr>
                            
            <tr>
              <td class="sectionSubHeader" colspan="2" style="padding-left: 5px; text-align: left; font-weight: bold">Module Name</td>
            </tr>
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
                <td colspan="2" class="moduleName" style="{$cellColor} {$bottomBorder}">
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
                                    
              </tr>
            </xsl:for-each>
                            
          </table>
        </xsl:if>

                    <!-- Report Footer -->
        <xsl:if test="$footer.display != 'false'">
          <xsl:call-template name="footer">
            <xsl:with-param name="sbVersion" select="/ProfileDelta/@sbVersion"/>
          </xsl:call-template>
        </xsl:if>

                    
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
