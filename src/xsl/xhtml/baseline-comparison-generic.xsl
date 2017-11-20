<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: baseline-comparison-generic.xsl 23917 2017-03-07 15:44:30Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Baseline Comparison Report XML to XHTML
     =========================================================================
-->
  <xsl:param name="report.title">Baseline Comparison Report</xsl:param>
  <xsl:param name="css.file">/OSLockdown/css/baseline-report.css</xsl:param>
    
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
                 Baseline Comparison Report Summary - Provide TOC of Report                         
              ================================================================
          -->
        <table class="sectionTable">
          <tr>
            <th style="text-align:left;" colspan="2">Summary</th>
            <th style="text-align: right;" colspan="2">
              <span style="font-size: 8pt">
                <xsl:text>Generated: </xsl:text>
                <xsl:value-of select="substring(/BaselineReportDelta/@created, 1, 20)"/>
              </span>
            </th>
          </tr>
                        
          <tr>
            <td style="border-bottom: none">&#x020;</td>
            <td style="background-color: #eef1f8; border-left: 1px solid black; font-weight: bold">Report A</td>
            <td style="background-color: #eef1f8; border-left: 1px solid black; font-weight: bold">Report B</td>
          </tr>
                        
         <!-- System Names (hostnames) -->
          <tr>
            <td class="infoName" style="text-align: right; font-weight: bold; border-bottom: 1px dotted gray ">Hostname</td>
                            
            <xsl:variable name="report1" select="/BaselineReportDelta/report[1]"/>
            <xsl:variable name="report2" select="/BaselineReportDelta/report[2]"/>
            <xsl:variable name="fontColor">
              <xsl:choose>
                <xsl:when test="$report1/@hostname != $report2/@hostname">color: red;</xsl:when>
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
                         
                        
                        <!-- Creation Date of sub-reports -->
          <tr>
            <td class="infoName" style="text-align: right; font-weight: bold; border-bottom: 1px dotted gray ">Created</td>
            <td class="infoItem" style="border-left: 1px solid black; border-bottom: 1px dotted gray">
              <xsl:value-of select="/BaselineReportDelta/report[1]/@created"/>
            </td>
            <td class="infoItem" style="border-left: 1px solid black; border-bottom: 1px dotted gray">
              <xsl:value-of select="/BaselineReportDelta/report[2]/@created"/>
            </td>
          </tr>
                         
                        
                        <!-- Operating system -->
          <tr>
            <td class="infoName" style="text-align: right; font-weight: bold; border-bottom: 1px dotted gray ">Operating System</td>
                            
            <xsl:for-each select="/BaselineReportDelta/report">
                                
              <xsl:variable name="report1" select="/BaselineReportDelta/report[1]"/>
              <xsl:variable name="report2" select="/BaselineReportDelta/report[2]"/>
                                
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
                                    
                <xsl:text> (</xsl:text>
                <xsl:value-of select="@arch"/>
                <xsl:text>) [Kernel </xsl:text>
                <xsl:value-of select="@kernel"/>
                <xsl:text>]</xsl:text>
              </td>
            </xsl:for-each>
          </tr>
                        <!-- Memory -->
          <tr>
            <td class="infoName" style="text-align: right; font-weight: bold; border-bottom: 1px dotted gray;">Total Memory</td>
                            
            <xsl:variable name="report1" select="/BaselineReportDelta/report[1]"/>
            <xsl:variable name="report2" select="/BaselineReportDelta/report[2]"/>
            <xsl:variable name="fontColor">
              <xsl:choose>
                <xsl:when test="$report1/@totalMemory != $report2/@totalMemory">color: red;</xsl:when>
                <xsl:otherwise>color: black;</xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
                            
            <td class="infoItem" style="border-left: 1px solid black; {$fontColor}; border-bottom: 1px dotted gray;">
              <xsl:value-of select="$report1/@totalMemory"/>
            </td>
            <td class="infoItem" style="border-left: 1px solid black; {$fontColor}; border-bottom: 1px dotted gray;">
              <xsl:value-of select="$report2/@totalMemory"/>
            </td>
          </tr>
                        
          <!-- Cpu Information -->
          <tr>
            <td class="infoName" style="text-align: right; font-weight: bold;">Processors</td>
                            
            <xsl:variable name="report1" select="/BaselineReportDelta/report[1]"/>
            <xsl:variable name="report2" select="/BaselineReportDelta/report[2]"/>
            <xsl:variable name="fontColor">
              <xsl:choose>
                <xsl:when test="$report1/@cpuInfo != $report2/@cpuInfo">color: red;</xsl:when>
                <xsl:otherwise>color: black;</xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
                            
            <td class="infoItem" style="border-left: 1px solid black; {$fontColor}">
              <xsl:value-of select="$report1/@cpuInfo"/>
            </td>
            <td class="infoItem" style="border-left: 1px solid black; {$fontColor}">
              <xsl:value-of select="$report2/@cpuInfo"/>
            </td>
          </tr>
                         
                        
                        <!-- ===================================================================== -->
                        
          <tr>
            <xsl:variable name="filesRowCount" select="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection) + 1"/>
            <xsl:variable name="totalRows" select="number($filesRowCount) + 6"/>
                            
            <td style="border-bottom: 1px dotted gray; text-align: right; font-weight: bold">Software</td>
            <td colspan="2" class="infoItem" style="border-left: 1px solid black; border-bottom: 1px dotted gray">
              <xsl:choose>
                <xsl:when test="./packages[@hasChanged] != 'true'">
                  <xsl:text>No changes detected</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                                        
                  <xsl:text>In report </xsl:text>
                  <span style="font-style: italic">Report B</span>
                  <xsl:text>: </xsl:text>
                                        <!-- Changed Software -->
                  <xsl:variable name="swDelta"
             select="count(/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages/changed/packageDelta)"/>
                  <xsl:variable name="fontColor1">
                    <xsl:choose>
                      <xsl:when test="$swDelta != 0">color: #467fc5;</xsl:when>
                      <xsl:otherwise>color: black</xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>
                  <a href="#changedPackages" style="text-decoration: none; {$fontColor1}">
                    <xsl:copy-of select="$swDelta"/>
                    <xsl:text> packages changed, </xsl:text>
                  </a>
                                        
                                        <!-- Added Software -->
                  <xsl:variable name="swAdded"
             select="count(/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages/added/package)"/>
                  <xsl:variable name="fontColor2">
                    <xsl:choose>
                      <xsl:when test="$swAdded != 0">color: #467fc5;</xsl:when>
                      <xsl:otherwise>color: black</xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>
                  <a href="#addedPackages" style="text-decoration: none; {$fontColor2}">
                    <xsl:copy-of select="$swAdded"/>
                    <xsl:text> are new</xsl:text>
                  </a>
                  <xsl:text>, and </xsl:text>
                                        
                                        <!-- Removed  Software -->
                  <xsl:variable name="swRemoved"
             select="count(/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages/removed/package)"/>
                  <xsl:variable name="fontColor3">
                    <xsl:choose>
                      <xsl:when test="$swRemoved != 0">color: #467fc5;</xsl:when>
                      <xsl:otherwise>color: black</xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>
                  <a href="#removedPackages" style="text-decoration: none; {$fontColor3}">
                    <xsl:copy-of select="$swRemoved"/>
                    <xsl:text> are non-existent.</xsl:text>
                  </a>
                                        
                </xsl:otherwise>
                                    
              </xsl:choose>
                                
            </td>
          </tr>
                        
                        <!-- General Sections -->
          <xsl:for-each select="/BaselineReportDelta/sections/section[@name != 'Software' and @name != 'Files']">
            <tr>
              <td style="border-bottom: 1px dotted gray; text-align: right; font-weight: bold">
                <xsl:variable name="secname" select="@name"/>
                <a href="#{$secname}" style="color: black">
                  <xsl:value-of select="@name"/>
                </a>
              </td>
              <td colspan="2" class="infoItem" style="border-left: 1px solid black; border-bottom: 1px dotted gray">
                <xsl:variable name="changeCount" select="count(./subSection/content[@hasChanged = 'true'])"/>
                <xsl:variable name="fontColor">
                  <xsl:choose>
                    <xsl:when test="number($changeCount) != 0">color: #467fc5;</xsl:when>
                    <xsl:otherwise>color: black</xsl:otherwise>
                  </xsl:choose>
                </xsl:variable>
                <span style="{$fontColor}">
                  <xsl:copy-of select="format-number($changeCount, '###,###')"/>
                  <xsl:text> changes</xsl:text>
                </span>
              </td>
            </tr>
          </xsl:for-each>
                        
                        <!-- File Changes -->
          <tr>
            <td colspan="1" style="border-bottom: 1px solid black; vertical-align: top; text-align: right; font-weight: bold">Files</td>
            <td colspan="2" class="infoItem" style="border-left: 1px solid black;">
              <xsl:text>In report </xsl:text>
              <span style="font-style: italic">Report B</span>
              <xsl:text>: </xsl:text>
                                
              <xsl:variable name="filesChanged" select="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup/changed/fileDelta)"/>
              <xsl:variable name="fontColor4">
                <xsl:choose>
                  <xsl:when test="number($filesChanged) != 0">color: #467fc5;</xsl:when>
                  <xsl:otherwise>color: black</xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
              <a href="#changedFiles" style="text-decoration: none; {$fontColor4}">
                <xsl:value-of select="format-number($filesChanged, '###,###')"/>
                <xsl:text> files changed, </xsl:text>
              </a>
                                
              <xsl:variable name="filesAdded" select="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup/added/file)"/>
              <xsl:variable name="fontColor5">
                <xsl:choose>
                  <xsl:when test="number($filesAdded) != 0">color: #467fc5;</xsl:when>
                  <xsl:otherwise>color: black</xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
              <a href="#addedFiles" style="text-decoration: none; {$fontColor5}">
                <xsl:value-of select="format-number($filesAdded, '###,###')"/>
                <xsl:text> are new, </xsl:text>
              </a>
                                
              <xsl:text>and </xsl:text>
              <xsl:variable name="filesRemoved" select="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup/removed/file)"/>
              <xsl:variable name="fontColor6">
                <xsl:choose>
                  <xsl:when test="number($filesAdded) != 0">color: #467fc5;</xsl:when>
                  <xsl:otherwise>color: black</xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
              <a href="#removedFiles" style="text-decoration: none; {$fontColor6}">
                <xsl:value-of select="format-number($filesRemoved, '###,###')"/>
                <xsl:text> are non-existent.</xsl:text>
              </a>
            </td>
          </tr>
                        
        </table>
                    
                    <!-- 
              ================================================================ 
                                         Changed Software
              ================================================================
          -->
        <xsl:variable name="packages" select="/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages"/>
        <xsl:if test="count($packages/changed/packageDelta) != 0">
          <a name="changedPackages"/>
          <table class="sectionTable">
            <tr>
              <th colspan="5" class="sectionHeader">Changed Software Packages: Software found in both reports but versions are different</th>
              <th class="navigTop">
                <a href="#top">
                                        top
                  <xsl:value-of select="$entity.up.arrow"/>
                </a>
              </th>
            </tr>
                            
            <tr>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold" rowspan="2">Name</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold" rowspan="2">Description</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold" colspan="2">Version</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold; border-right: none; white-space: nowrap" colspan="2">Date Installed</td>
            </tr>
                            
            <tr>
              <td class="sectionSubHeader" style="text-align: center; border-right: none">Report A</td>
              <td class="sectionSubHeader" style="text-align: center; border-left: 1px dotted gray">Report B</td>
              <td class="sectionSubHeader" style="text-align: center; border-right: none">Report A</td>
              <td class="sectionSubHeader" style="text-align: center; border-left: 1px dotted gray; border-right: none">Report B</td>
            </tr>
                            
            <xsl:for-each select="$packages/changed/packageDelta">
              <xsl:sort select="./package[1]/@name"/>
                                
              <xsl:variable name="leftBorder">border-left: 1px dotted gray;</xsl:variable>
              <xsl:variable name="rightBorder">border-right: 1px solid black;</xsl:variable>
              <xsl:variable name="bottomBorder">
                <xsl:choose>
                  <xsl:when test="position() = last()">border-bottom: 1px solid black;</xsl:when>
                  <xsl:otherwise>border-bottom: 1px dotted gray;</xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
                                
              <xsl:variable name="cellColor">
                <xsl:choose>
                  <xsl:when test="position() mod 2 = 0">background-color: #efefef;</xsl:when>
                  <xsl:otherwise>background-color: white;</xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
                                
              <tr>
                <xsl:variable name="package1" select="./package[1]"/>
                <xsl:variable name="package2" select="./package[2]"/>
                <td colspan="1" style="{$cellColor} {$bottomBorder} {$rightBorder}; ">
                  <xsl:value-of select="$package1/@name"/>
                </td>
                                     
                <td colspan="1" style="{$cellColor} {$bottomBorder} {$rightBorder}">
                  <xsl:value-of select="$package1/@summary"/>
                </td>
                                     
                                    
                <td colspan="1" style="{$cellColor} {$bottomBorder}; white-space:nowrap; text-align: center; ">
                  <xsl:value-of select="$package1/@version"/>
                  <xsl:text>-</xsl:text>
                  <xsl:value-of select="$package1/@release"/>
                </td>
                                     
                <td colspan="1" style="{$cellColor} {$bottomBorder}; white-space:nowrap; text-align: center;  {$leftBorder}; border-right: 1px solid black; ">
                  <xsl:value-of select="$package2/@version"/>
                  <xsl:text>-</xsl:text>
                  <xsl:value-of select="$package2/@release"/>
                </td>
                                    
                <td colspan="1" style="{$cellColor} {$bottomBorder}; text-align: center; border-left: none; white-space:nowrap">

                  <xsl:call-template name="date.reformat" >
                    <xsl:with-param name="iDate" select="$package1/@install_localtime"/>
                  </xsl:call-template>
                </td>
                                     
                <td colspan="1" style="{$cellColor} {$bottomBorder} {$leftBorder}; text-align:center; white-space:nowrap">
                  <xsl:call-template name="date.reformat" >
                    <xsl:with-param name="iDate" select="$package2/@install_localtime"/>
                  </xsl:call-template>
                </td>
              </tr>
            </xsl:for-each>
          </table>
        </xsl:if>
                    
                    <!-- 
              ================================================================ 
                                         Added Software
              ================================================================
          -->
        <xsl:if test="count(/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages/added/package) != 0">
          <xsl:variable name="newPackages" select="/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages"/>
          <a name="addedPackages"/>
          <table class="sectionTable">
            <tr>
              <th colspan="3" class="sectionHeader">New Software Packages: This software was found in Report B but not Report A</th>
              <th class="navigTop">
                <a href="#top">
                                        top
                  <xsl:value-of select="$entity.up.arrow"/>
                </a>
              </th>
            </tr>
                            
            <tr>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold">Name</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold">Description</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold">Version</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold; border-right: none; white-space: nowrap">Date Installed</td>
            </tr>
                            
            <xsl:for-each select="$newPackages/added/package">
              <xsl:sort select="@name"/>
                                
              <xsl:variable name="leftBorder">border-left: 1px dotted gray;</xsl:variable>
              <xsl:variable name="rightBorder">border-right: 1px dotted gray;</xsl:variable>
              <xsl:variable name="bottomBorder">
                <xsl:choose>
                  <xsl:when test="position() = last()">border-bottom: 1px solid black;</xsl:when>
                  <xsl:otherwise>border-bottom: 1px dotted gray;</xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
                                
              <xsl:variable name="cellColor">
                <xsl:choose>
                  <xsl:when test="position() mod 2 = 0">background-color: #efefef;</xsl:when>
                  <xsl:otherwise>background-color: white;</xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
                                
              <tr>
                <td style="{$rightBorder} {$bottomBorder} {$cellColor}">
                  <xsl:value-of select="@name"/>
                </td>
                <td style="{$rightBorder} {$bottomBorder} {$cellColor}">
                  <xsl:value-of select="@summary"/>
                </td>
                <td style="{$rightBorder} {$bottomBorder} {$cellColor}">
                  <xsl:value-of select="@version"/>
                  <xsl:text>-</xsl:text>
                  <xsl:value-of select="@release"/>
                </td>
                <td style="{$bottomBorder} {$cellColor}; white-space: nowrap">
                  <xsl:call-template name="date.reformat" >
                    <xsl:with-param name="iDate" select="@install_localtime"/>
                  </xsl:call-template>
                </td>
              </tr>
                                
            </xsl:for-each>
          </table>
        </xsl:if>
                    
                    <!-- 
              ================================================================ 
                                         Removed Software
              ================================================================
          -->
        <xsl:variable name="delPackages" select="/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages"/>
        <xsl:if test="count($delPackages/removed/package) != 0">
          <a name="removedPackages"/>
          <table class="sectionTable">
            <tr>
              <th colspan="3" class="sectionHeader">Non-existent Software Packages: This software was found in Report A but not Report B</th>
              <th class="navigTop">
                <a href="#top">
                                        top
                  <xsl:value-of select="$entity.up.arrow"/>
                </a>
              </th>
            </tr>
                            
            <tr>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold">Name</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold">Description</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold">Version</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold; border-right: none; white-space: nowrap">Date Installed</td>
            </tr>
                            
            <xsl:for-each select="$delPackages/removed/package">
              <xsl:sort select="@name"/>
                                
              <xsl:variable name="leftBorder">border-left: 1px dotted gray;</xsl:variable>
              <xsl:variable name="rightBorder">border-right: 1px dotted gray;</xsl:variable>
              <xsl:variable name="bottomBorder">
                <xsl:choose>
                  <xsl:when test="position() = last()">border-bottom: 1px solid black;</xsl:when>
                  <xsl:otherwise>border-bottom: 1px dotted gray;</xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
                                
              <xsl:variable name="cellColor">
                <xsl:choose>
                  <xsl:when test="position() mod 2 = 0">background-color: #efefef;</xsl:when>
                  <xsl:otherwise>background-color: white;</xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
                                
              <tr>
                <td style="{$rightBorder} {$bottomBorder} {$cellColor}">
                  <xsl:value-of select="@name"/>
                </td>
                <td style="{$rightBorder} {$bottomBorder} {$cellColor}">
                  <xsl:value-of select="@summary"/>
                </td>
                <td style="{$rightBorder} {$bottomBorder} {$cellColor}">
                  <xsl:value-of select="@version"/>
                  <xsl:text>-</xsl:text>
                  <xsl:value-of select="@release"/>
                </td>
                <td style="{$bottomBorder} {$cellColor}; white-space: nowrap">
                  <xsl:call-template name="date.reformat" >
                    <xsl:with-param name="iDate" select="@install_localtime"/>
                  </xsl:call-template>
                </td>
              </tr>
                                
            </xsl:for-each>
          </table>
        </xsl:if>
                    
                    
                    <!-- 
              ================================================================ 
                                         Generic Sections
              ================================================================
          -->
        <xsl:for-each select="/BaselineReportDelta/sections/section[@name != 'Software' and @name != 'Files']">
          <xsl:if test="count(./subSection/content[hasChanged='true']) != 0">
            <xsl:variable name="secname" select="@name"/>
            <a name="{$secname}"/>
            <table class="sectionTable">
              <tr>
                <th colspan="3" class="sectionHeader">
                  <xsl:value-of select="@name"/>
                </th>
                <th class="navigTop">
                  <a href="#top">
                                            top
                    <xsl:value-of select="$entity.up.arrow"/>
                  </a>
                </th>
              </tr>
              <xsl:for-each select="./subSection">
                <tr>
                  <td class="subSectionTitle">
                    <xsl:value-of select="@name"/>
                  </td>
                  <td colspan="3">
                    <xsl:choose>
                      <xsl:when test="@hasChanged = 'true'">
                        <span style="color: red">Changed</span>
                      </xsl:when>
                      <xsl:otherwise>Unchanged</xsl:otherwise>
                    </xsl:choose>
                  </td>
                </tr>
              </xsl:for-each>
            </table>
          </xsl:if>
        </xsl:for-each>
                    
        <br/>
                    <!-- 
              ================================================================ 
                                         Files Information
              ================================================================
          -->
        <xsl:if test="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup/changed/fileDelta) != 0">
          <a name="changedFiles"/>
          <table class="sectionTable">
            <tr>
              <th colspan="5" class="sectionHeader">Changed Files: Files exist in both reports but differences exist</th>
              <th class="navigTop">
                <a href="#top">
                                        top
                  <xsl:value-of select="$entity.up.arrow"/>
                </a>
              </th>
            </tr>
                            
            <tr>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold">File Path</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold">Permissions</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold; white-space: nowrap">Owner / Group ID</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold; white-space: nowrap">SUID / SGID </td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold">Contents</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold; border-right: none">Last Modified</td>
            </tr>
                            
            <xsl:variable name="fileTypes" select="/BaselineReportDelta/sections/section[@name = 'Files']/subSection"/>
            <xsl:for-each select="$fileTypes/fileGroups/fileGroup">
                                
              <xsl:if test="count(./changed/fileDelta) != 0">
                <tr>
                  <td colspan="6" style="background-color: #7499c6;">
                    <span style="font-weight: bold">
                      <xsl:value-of select="../../@name"/>
                      <xsl:text> - </xsl:text>
                      <xsl:value-of select="@name"/>
                    </span>
                  </td>
                </tr>
                                    
                <xsl:variable name="leftBorder">border-left: 1px dotted gray;</xsl:variable>
                <xsl:variable name="rightBorder">border-right: 1px dotted gray;</xsl:variable>
                <xsl:for-each select="./changed/fileDelta">
                  <xsl:sort select="./file[1]/@path"/>
                                        
                  <xsl:variable name="bottomBorder">
                    <xsl:choose>
                      <xsl:when test="position() = last()">border-bottom: 1px solid black;</xsl:when>
                      <xsl:otherwise>border-bottom: 1px dotted gray;</xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>
                                        
                  <xsl:variable name="cellColor">
                    <xsl:choose>
                      <xsl:when test="position() mod 2 = 0">background-color: #efefef;</xsl:when>
                      <xsl:otherwise>background-color: white;</xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>
                                        
                  <tr>
                    <xsl:variable name="file1" select="./file[1]"/>
                    <xsl:variable name="file2" select="./file[2]"/>
                                            
                    <td style="{$bottomBorder}; {$cellColor}; {$rightBorder}; padding-left: 1em;">
                      <xsl:value-of select="$file1/@path"/>
                    </td>
                                            
                    <td style="{$bottomBorder};  {$cellColor}; {$rightBorder}; text-align: center; white-space: nowrap">
                      <xsl:choose>
                        <xsl:when test="$file1/@mode != $file2/@mode">
                          <span style="color: #467fc5">
                            <xsl:value-of select="$file1/@mode"/>
                            <xsl:text> &gt;&gt; </xsl:text>
                            <xsl:value-of select="$file2/@mode"/>
                          </span>
                        </xsl:when>
                        <xsl:otherwise>
                          <xsl:value-of select="$file1/@mode"/>
                        </xsl:otherwise>
                      </xsl:choose>
                    </td>
                                            
                    <td style="{$bottomBorder};  {$cellColor}; {$rightBorder}; text-align: center; white-space:nowrap">
                      <xsl:choose>
                        <xsl:when test="$file1/@uid != $file2/@uid or $file1/@gid != $file2/@gid">
                          <span style="color: #467fc5">
                            <xsl:value-of select="$file1/@uid"/>
                            <xsl:text> / </xsl:text>
                            <xsl:value-of select="$file1/@gid"/>
                            <xsl:text> &gt;&gt; </xsl:text>
                            <xsl:value-of select="$file2/@uid"/>
                            <xsl:text> / </xsl:text>
                            <xsl:value-of select="$file2/@gid"/>
                          </span>
                        </xsl:when>
                        <xsl:otherwise>
                          <xsl:value-of select="$file1/@uid"/>
                          <xsl:text> / </xsl:text>
                          <xsl:value-of select="$file1/@gid"/>
                        </xsl:otherwise>
                      </xsl:choose>
                    </td>
                                            
                    <xsl:variable name="suidColor">
                      <xsl:choose>
                        <xsl:when test="$file1/@suid='true' or $file1/@sgid='true'">font-weight: bold; color: black;</xsl:when>
                        <xsl:otherwise>color: gray</xsl:otherwise>
                      </xsl:choose>
                    </xsl:variable>
                                            
                    <td style="{$bottomBorder}; {$cellColor}; {$rightBorder}; {$suidColor}; text-align: center; white-space:nowrap">
                      <xsl:choose>
                        <xsl:when test="$file1/@suid != $file2/@suid or $file1/@sgid != $file2/@sgid">
                          <span style="color: #467fc5">
                            <xsl:value-of select="$file1/@suid"/>
                            <xsl:text> / </xsl:text>
                            <xsl:value-of select="$file1/@sgid"/>
                            <xsl:text> &gt;&gt; </xsl:text>
                            <xsl:value-of select="$file2/@suid"/>
                            <xsl:text> / </xsl:text>
                            <xsl:value-of select="$file2/@sgid"/>
                          </span>
                        </xsl:when>
                        <xsl:otherwise>
                          <xsl:value-of select="$file1/@suid"/>
                          <xsl:text> / </xsl:text>
                          <xsl:value-of select="$file1/@sgid"/>
                        </xsl:otherwise>
                      </xsl:choose>
                    </td>
                                            
                    <td style="{$bottomBorder}; {$cellColor}; text-align: center;">
                      <xsl:choose>
                        <xsl:when test="$file1/@sha1 != $file2/@sha1">
                          <span style="color: #467fc5">Changed</span>
                        </xsl:when>
                        <xsl:otherwise>
                          <span style="color: gray">unchanged</span>
                        </xsl:otherwise>
                      </xsl:choose>
                    </td>
                                            
                    <td style="{$bottomBorder}; {$cellColor}; {$leftBorder}; text-align: center; ; white-space: nowrap">
                      <xsl:choose>
                        <xsl:when test="$file1/@mtime != $file2/@mtime">
                          <span style="color: #467fc5">
                            <xsl:call-template name="date.reformat" >
                              <xsl:with-param name="iDate" select="$file2/@mtime"/>
                            </xsl:call-template>
                          </span>
                        </xsl:when>
                        <xsl:otherwise>
                          <xsl:call-template name="date.reformat" >
                            <xsl:with-param name="iDate" select="$file2/@mtime"/>
                          </xsl:call-template>
                        </xsl:otherwise>
                      </xsl:choose>
                    </td>
                                            
                  </tr>
                </xsl:for-each>
                                    
              </xsl:if>
            </xsl:for-each>
                            
          </table>
        </xsl:if>
                    
                    <!-- 
              ================================================================ 
                                       Added/New Files
              ================================================================
          -->
        <xsl:variable name="addedFiles" select="/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup"/>
        <xsl:if test="count($addedFiles/added/file) != 0">
          <a name="addedFiles"/>
          <table class="sectionTable">
            <tr>
              <th colspan="4" class="sectionHeader">New Files: These files were found in Report B but not Report A</th>
              <th class="navigTop">
                <a href="#top">
                                        top
                  <xsl:value-of select="$entity.up.arrow"/>
                </a>
              </th>
            </tr>
                            
            <tr>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold">File Path</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold">Permissions</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold; white-space: nowrap">Owner / Group ID</td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold; white-space: nowrap">SUID / SGID </td>
              <td class="sectionSubHeader" style="text-align: center; font-weight: bold; border-right: none">Last Modified</td>
            </tr>
                            
            <xsl:for-each select="$addedFiles">
              <xsl:if test="count(./added/file) != 0">
                <tr>
                  <td colspan="5" style="background-color: #7499c6;">
                    <span style="font-weight: bold">
                      <xsl:value-of select="../../@name"/>
                      <xsl:text> - </xsl:text>
                      <xsl:value-of select="@name"/>
                    </span>
                  </td>
                </tr>
                                    
                <xsl:variable name="leftBorder">border-left: 1px dotted gray;</xsl:variable>
                <xsl:variable name="rightBorder">border-right: 1px dotted gray;</xsl:variable>
                                    
                <xsl:for-each select="./added/file">
                  <xsl:sort select="@path"/>
                                        
                  <xsl:variable name="bottomBorder">
                    <xsl:choose>
                      <xsl:when test="position() = last()">border-bottom: 1px solid black;</xsl:when>
                      <xsl:otherwise>border-bottom: 1px dotted gray;</xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>
                                        
                  <xsl:variable name="cellColor">
                    <xsl:choose>
                      <xsl:when test="position() mod 2 = 0">background-color: #efefef;</xsl:when>
                      <xsl:otherwise>background-color: white;</xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>
                                        
                  <tr>
                    <td style="{$bottomBorder}; {$cellColor}; {$rightBorder}; padding-left: 1em;">
                      <xsl:value-of select="@path"/>
                    </td>
                                            
                    <td style="{$bottomBorder};  {$cellColor}; {$rightBorder}; text-align: center;">
                      <xsl:value-of select="@mode"/>
                    </td>
                                            
                    <td style="{$bottomBorder};  {$cellColor}; {$rightBorder}; text-align: center;">
                      <xsl:value-of select="@uid"/>
                      <xsl:text> / </xsl:text>
                      <xsl:value-of select="@gid"/>
                    </td>
                                            
                    <xsl:variable name="suidColor">
                      <xsl:choose>
                        <xsl:when test="@suid='true' or @sgid='true'">font-weight: bold; color: black;</xsl:when>
                        <xsl:otherwise>color: gray</xsl:otherwise>
                      </xsl:choose>
                    </xsl:variable>
                                            
                    <td style="{$bottomBorder}; {$cellColor}; {$rightBorder}; {$suidColor}; text-align: center; white-space: nowrap">
                      <xsl:value-of select="@suid"/>
                      <xsl:text> / </xsl:text>
                      <xsl:value-of select="@sgid"/>
                    </td>
                                            
                    <td style="{$bottomBorder}; {$cellColor}; {$leftBorder}; text-align: center; white-space: nowrap">
                      <xsl:call-template name="date.reformat" >
                        <xsl:with-param name="iDate" select="@mtime"/>
                      </xsl:call-template>
                    </td>
                  </tr>
                                        
                </xsl:for-each>
              </xsl:if>
            </xsl:for-each>
                            
          </table>
        </xsl:if>
                    
                    <!-- 
              ================================================================ 
                                       Removed Files
              ================================================================
          -->
        <xsl:variable name="removedFiles" select="/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup"/>
        <xsl:if test="count($removedFiles/removed/file) != 0">
          <a name="removedFiles"/>
          <table class="sectionTable">
            <tr>
              <th class="sectionHeader">Non-existent Files: These files were found in Report A but not Report B</th>
              <th class="navigTop">
                <a href="#top">
                                        top
                  <xsl:value-of select="$entity.up.arrow"/>
                </a>
              </th>
            </tr>
                            
            <xsl:for-each select="$removedFiles">
              <xsl:if test="count(./removed/file) != 0">
                <tr>
                  <td colspan="2" style="background-color: #7499c6;">
                    <span style="font-weight: bold">
                      <xsl:value-of select="../../@name"/>
                      <xsl:text> - </xsl:text>
                      <xsl:value-of select="@name"/>
                    </span>
                  </td>
                </tr>
                                    
                <xsl:variable name="leftBorder">border-left: 1px dotted gray;</xsl:variable>
                <xsl:variable name="rightBorder">border-right: 1px dotted gray;</xsl:variable>
                                    
                <xsl:for-each select="./removed/file">
                  <xsl:sort select="@path"/>
                                        
                  <xsl:variable name="bottomBorder">
                    <xsl:choose>
                      <xsl:when test="position() = last()">border-bottom: 1px solid black;</xsl:when>
                      <xsl:otherwise>border-bottom: 1px dotted gray;</xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>
                                        
                  <xsl:variable name="cellColor">
                    <xsl:choose>
                      <xsl:when test="position() mod 2 = 0">background-color: #efefef;</xsl:when>
                      <xsl:otherwise>background-color: white;</xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>
                                        
                  <tr>
                    <td colspan="2" style="{$bottomBorder}; {$cellColor}; {$rightBorder}; padding-left: 1em;">
                      <xsl:value-of select="@path"/>
                    </td>
                  </tr>
                                        
                </xsl:for-each>
              </xsl:if>
            </xsl:for-each>
                            
          </table>
        </xsl:if>
                    
                    
                    
                    
                    <!-- ======================================================================== -->
                    <!-- Report Footer -->
        <xsl:if test="$footer.display != 'false'">
          <xsl:call-template name="footer">
            <xsl:with-param name="sbVersion" select="/BaselineReportDelta/@sbVersion"/>
          </xsl:call-template>
        </xsl:if>

      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
