<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: baseline-generic.xsl 23917 2017-03-07 15:44:30Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Baseline Report XML to XHTML
     =========================================================================
-->
  <xsl:param name="report.title">Baseline Report</xsl:param>
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
                 Baseline Report Summary - Provide TOC of Report                         
       ================================================================
    -->
        <table class="sectionTable">
          <tr>
            <th style="text-align:left;" colspan="2">Summary</th>
            <th colspan="2" style="text-align: right;">
              <span style="font-size: 8pt">
                <xsl:text>Created: </xsl:text>
                <xsl:value-of select="/BaselineReport/report/@created"/>
              </span>
            </th>
          </tr>
                        
          <tr>
            <td class="subSectionTitle" rowspan="4">System</td>
            <td class="infoName" style="width: 110px; border-right: 1px solid black; border-bottom: none; text-align: right; background-color:white">Hostname</td>
            <td class="infoItem" colspan="2" style="border-bottom: none">
              <xsl:value-of select="/BaselineReport/report/@hostname"/>
            </td>
          </tr>
                        
          <tr>
            <td class="infoName" style="white-space: nowrap; border-right: 1px solid black; text-align: right; border-bottom: none;background-color:white">Operating System</td>
            <td class="infoItem" colspan="2" style="border-bottom: none;">
              <xsl:variable name="distVersion" select="/BaselineReport/report/@distVersion"/>
              <xsl:variable name="dist" select="/BaselineReport/report/@dist"/>
              <xsl:choose>
                <xsl:when test="$distVersion = '10' and $dist = 'redhat'">
                  <xsl:text>Fedora 10</xsl:text>
                </xsl:when>
                  <xsl:when test="@dist = 'Red Hat'">
                    <xsl:text>Red Hat Enterprise Linux </xsl:text>
                  </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="/BaselineReport/report/@dist"/>
                  <xsl:text> </xsl:text>
                  <xsl:value-of select="/BaselineReport/report/@distVersion"/>
                </xsl:otherwise>
              </xsl:choose>
              <xsl:text> (</xsl:text>
              <xsl:value-of select="/BaselineReport/report/@arch"/>
              <xsl:text>) [Kernel </xsl:text>
              <xsl:value-of select="/BaselineReport/report/@kernel"/>
              <xsl:text>]</xsl:text>
            </td>
          </tr>
                        
          <tr>
            <td class="infoName" style="white-space: nowrap; border-right: 1px solid black; text-align: right; border-bottom: none; background-color:white;">Total Memory</td>
            <td class="infoItem" colspan="2" style="border-bottom: none">
              <xsl:value-of select="/BaselineReport/report/@totalMemory"/>
            </td>
          </tr>
                        
          <tr>
            <td class="infoName" style="text-align: right; border-right: 1px solid black; background-color:white">Processors</td>
            <td class="infoItem" colspan="2" >
              <xsl:value-of select="/BaselineReport/report/@cpuInfo"/>
            </td>
          </tr>

          <tr>
            <td class="subSectionTitle" width="25%">Profile</td>
            <td class="infoItem" colspan="3" >
              <xsl:value-of select="/BaselineReport/report/@profile"/>
            </td>
          </tr>
                        
          <tr>
            <td class="subSectionTitle" width="25%">Hardware</td>
            <td colspan="3" class="infoItem">
              <ul>
                <xsl:for-each select="/BaselineReport/sections/section[@name='Hardware']/subSection">
                  <xsl:variable name="secname" select="@name"/>
                  <li>
                    <a href="#{$secname}">
                      <xsl:value-of select="@name"/>
                    </a>
                  </li>
                </xsl:for-each>
              </ul>
            </td>
          </tr>
                        
          <tr>
            <td class="subSectionTitle" width="25%">Network</td>
            <td colspan="3" class="infoItem">
              <ul>
                <xsl:for-each select="/BaselineReport/sections/section[@name='Network']/subSection">
                  <xsl:variable name="secname" select="@name"/>
                  <li>
                    <a href="#{$secname}">
                      <xsl:value-of select="@name"/>
                    </a>
                  </li>
                </xsl:for-each>
              </ul>
            </td>
          </tr>
                        
          <tr>
            <td class="subSectionTitle" width="25%">Files</td>
            <td colspan="3" class="infoItem">
              <ul>
                <xsl:for-each select="/BaselineReport/sections/section[@name='Files']/subSection[@name != 'Device Files']">
                  <xsl:variable name="secname" select="@name"/>
                  <li>
                    <xsl:value-of select="@name"/>
                    <xsl:text> (</xsl:text>
                    <xsl:value-of select="format-number(count(./files/file), '###,###')"/>
                    <xsl:text>)</xsl:text>
                  </li>
                </xsl:for-each>
              </ul>
            </td>
          </tr>
          <tr>
            <td class="subSectionTitle" width="25%">Software</td>
            <td colspan="3" class="infoItem">
              <ul>
                <li>
                  <a href="#software">
                    <xsl:value-of
                 select="format-number(count(/BaselineReport/sections/section[@name='Software']/subSection/packages/package), '###,###')"/>
                                             packages installed
                  </a>
                </li>
              </ul>
            </td>
          </tr>
        </table>
                    <!-- 
              ================================================================ 
                                         Hardware Section
              ================================================================
          -->
        <table class="sectionTable">
          <tr>
            <th colspan="3" class="sectionHeader">Hardware</th>
            <th class="navigTop">
              <a href="#top">
                                    top
                <xsl:value-of select="$entity.up.arrow"/>
              </a>
            </th>
          </tr>
          <xsl:for-each select="/BaselineReport/sections/section[@name='Hardware']/subSection">
            <xsl:variable name="secname" select="@name"/>
            <tr>
              <td class="subSectionTitle">
                <a name="{$secname}"/>
                <xsl:value-of select="@name"/>
                <div class="subSectionInfoBox">
                  <xsl:value-of select="@fullname"/>
                  <div class="navigTop">
                    <a href="#top">
                                                top
                      <xsl:value-of select="$entity.up.arrow"/>
                    </a>
                  </div>
                </div>
              </td>
              <td colspan="3" style="color:black; background:white; vertical-align: text-top; text-align: left">
                <pre style="font-size:90%">
                  <xsl:value-of select="self::*"/>
                </pre>
              </td>
            </tr>
          </xsl:for-each>
        </table>
                    
                    <!-- 
              ================================================================ 
                                        Network Section
              ================================================================
          -->
        <table class="sectionTable">
          <tr>
            <th colspan="3" class="sectionHeader">Network</th>
            <th class="navigTop">
              <a href="#top">
                                    top
                <xsl:value-of select="$entity.up.arrow"/>
              </a>
            </th>
          </tr>
          <xsl:for-each select="/BaselineReport/sections/section[@name='Network']/subSection">
            <xsl:variable name="secname" select="@name"/>
            <tr>
              <td class="subSectionTitle">
                <a name="{$secname}"/>
                <xsl:value-of select="@name"/>
                <div class="subSectionInfoBox">
                  <xsl:value-of select="@fullname"/>
                  <div class="navigTop">
                    <a href="#top">
                                                top
                      <xsl:value-of select="$entity.up.arrow"/>
                    </a>
                  </div>
                </div>
              </td>
              <td colspan="3" style="color:black; background:white;">
                <div class="cmdOutput">
                  <pre>
                    <xsl:value-of select="./content"/>
                  </pre>
                </div>
              </td>
            </tr>
          </xsl:for-each>
        </table>
                    
          <!-- 
              ================================================================ 
                                       Software Section
              ================================================================
          -->
        <table id="installedSoftware" class="sectionTable sortable">
          <thead>
            <tr>
              <th colspan="3" class="sectionHeader">
                <a name="software"/>Software
              </th>
              <th class="navigTop"><a href="#top">top<xsl:value-of select="$entity.up.arrow"/></a></th>
            </tr>
            <tr>
              <td class="sectionSubHeader" width="25%">Package</td>
              <td class="sectionSubHeader">Description</td>
              <td class="sectionSubHeader">
                <xsl:text>Version </xsl:text>
                <xsl:if test="count(/BaselineReport/sections/section[@name='Software']/subSection[@name='Patches']/patches/patch) !=0">
                  <a href="#software" title="Show all patches" style="cursor:pointer" onClick="return expandAll();">
                    <xsl:text>[ Show / </xsl:text>
                  </a>
                  <a href="#software" title="Hide all patches" style="cursor:pointer" onClick="return collapseAll();">
                    <xsl:text>Hide patches ]</xsl:text>
                  </a>
                </xsl:if>
              </td>
              <td class="sectionSubHeader unsortable">Installed</td>
            </tr>
          </thead>
          <tbody>
            <xsl:for-each select="/BaselineReport/sections/section[@name='Software']/subSection[@name='Packages']/packages/package">
              <xsl:sort select="@name"/>
                <xsl:variable name="rowClass">
                  <xsl:choose>
                    <xsl:when test="position() mod 2 = 0">even</xsl:when>
                    <xsl:otherwise>odd</xsl:otherwise>
                  </xsl:choose>
                </xsl:variable>

              <tr class="{$rowClass}" >

                <td style="padding-top: 5px; vertical-align: top;">
                  <xsl:value-of select="@name"/>
                </td>
                <td style="padding-top: 5px; vertical-align: top;">
                  <xsl:value-of select="@summary"/>
                </td>
                <td style="padding-top: 5px; vertical-align: top;">
                  <xsl:variable name="xname" select="@name"/>
                  <xsl:variable name="cursor">
                    <xsl:choose>
                      <xsl:when test="count(../../../subSection[@name='Patches']/patches/patch[@pkg = $xname]) != 0">cursor:pointer;</xsl:when>
                      <xsl:otherwise>cursor:default;</xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>
                  <span style="{$cursor}; padding-right:.5em" onclick="toggleDisplay(this)">
                    <xsl:value-of select="@version"/>
                    <xsl:text> </xsl:text>
                    <xsl:value-of select="@release"/>
                  </span>
                  <div class="patchList" style="display: none">
                    <xsl:variable name="pkgname" select="@name"/>
                    <xsl:if test="count(../../../subSection[@name='Patches']/patches/patch[@pkg = $pkgname]) != 0">
                      <ul>
                        <xsl:text>Patches:</xsl:text>
                        <ul class="patchList">
                          <xsl:for-each select="../../../subSection[@name='Patches']/patches/patch[@pkg = $pkgname]">
                            <xsl:sort select="@name"/>
                            <li>
                              <xsl:value-of select="@name"/>
                            </li>
                          </xsl:for-each>
                        </ul>
                                                 
                      </ul>
                    </xsl:if>
                  </div>
                </td>
                <td style="padding-top: 5px; vertical-align: top; white-space: pre; ">
                  <xsl:choose>
                    <xsl:when test="@install_localtime != ''">
                      <xsl:value-of select="@install_localtime"/>
                    </xsl:when>
                    <xsl:otherwise>
                      <xsl:value-of select="@installtime"/>
                    </xsl:otherwise>
                  </xsl:choose>
                </td>
              </tr>
            </xsl:for-each>
          </tbody>
        </table>
                    
                    <!-- Report Footer -->
        <xsl:if test="$footer.display != 'false'">
          <xsl:call-template name="footer">
            <xsl:with-param name="sbVersion" select="/BaselineReport/@sbVersion"/>
          </xsl:call-template>
        </xsl:if>


      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
