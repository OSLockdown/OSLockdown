<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                xmlns:java="http://xml.apache.org/xslt/java" exclude-result-prefixes="java"
                version="1.0">
<!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Baseline Report - Software Only (XML to XHTML) 
     =========================================================================
-->
  <xsl:param name="report.title">Baseline Report - Installed Software</xsl:param>
  <xsl:param name="css.file">/OSLockdown/css/baseline-report.css</xsl:param>

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
<!-- 
      ================================================================ 
              Baseline Report Summary - Provide TOC of Report                         
      ================================================================
-->
          <xsl:variable name="todaysEpoch" select="java:java.lang.System.currentTimeMillis()"/>
          <xsl:variable name="todaysDate"  select="java:format(java:java.text.SimpleDateFormat.new ('yyyy-MM-dd'), java:java.util.Date.new())"/>

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

     <!-- Hostname  -->
            <tr>
              <td class="subsectionTitle" style="text-align: right">Hostname</td>
              <td colspan="3">
                <xsl:value-of select="/BaselineReport/report/@hostname"/>
              </td>
            </tr>

    <!-- Operating System -->
            <tr>
              <td class="subsectionTitle" style="text-align: right">Operating System</td>
              <td colspan="3">
                <xsl:variable name="distVersion" select="/BaselineReport/report/@distVersion"/>
                <xsl:variable name="dist" select="/BaselineReport/report/@dist"/>
                <xsl:choose>
                  <xsl:when test="$distVersion = '10' and $dist = 'redhat'">
                    <xsl:text>Fedora 10</xsl:text>
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

    <!-- Software Activity -->
            <tr>
              <td class="subsectionTitle" style="text-align: right" rowspan="5">Activity</td>
              <td colspan="3" style="border-bottom: none">Software installations or updates since
                <xsl:copy-of select="$todaysDate"/>:
              </td>
            </tr>

      <!-- last 30 days -->
            <tr>
              <td style="text-align: right; width:300px; border-bottom: none; font-size: 90%">
           Within the last 30 days:
              </td>
              <td style="width: 50px; text-align: right; border-bottom: none; font-size: 90%">
                <xsl:value-of select="format-number(count(/BaselineReport/sections/section[@name='Software']/subSection/packages/package[@installtime &gt; (($todaysEpoch div 1000) - (86400 * 30))]), '###,###')"/>
              </td>
              <td style="border-bottom:none">
                <xsl:text> </xsl:text>
              </td>
            </tr>

      <!-- Between 60 and 90 days -->
            <tr>
              <td style="text-align: right; width:300px; border-bottom: none; font-size: 90%">
           Between the last 30 and 90 days:
              </td>
              <td style="width: 50px; text-align: right; border-bottom: none; font-size: 90%">
                <xsl:value-of select="format-number(count(/BaselineReport/sections/section[@name='Software']/subSection/packages/package[@installtime &gt; (($todaysEpoch div 1000) - (86400 * 90)) and @installtime &lt; (($todaysEpoch div 1000) - (86400 * 30))]), '###,###')"/>
              </td>
              <td style="border-bottom:none">
                <xsl:text> </xsl:text>
              </td>
            </tr>

      <!-- More than 90 days -->
            <tr>
              <td style="text-align: right; width:300px; border-bottom: none; font-size: 90%">
           More than 90 days ago:
              </td>
              <td style="width: 50px; text-align: right; font-size: 90%">
                <xsl:value-of select="format-number(count(/BaselineReport/sections/section[@name='Software']/subSection/packages/package[@installtime &lt; (($todaysEpoch div 1000) - (86400 * 90))]), '###,###')"/>
              </td>
              <td style="border-bottom:none">
                <xsl:text> </xsl:text>
              </td>
            </tr>

            <tr>
              <td style="text-align: right; width:300px; font-size: 90%; font-weight: bold">
           Total:
              </td>
              <td style="width: 50px; text-align: right; font-size: 90%; font-weight: bold">
                <xsl:value-of select="format-number(count(/BaselineReport/sections/section[@name='Software']/subSection/packages/package), '###,###')"/>
              </td>
              <td>
                <xsl:text> </xsl:text>
              </td>
            </tr>

          </table>

<!-- 
      ================================================================ 
                               Software Section
      ================================================================
-->
          <table class="sectionTable">

    <!-- Table Header -->
            <tr>
              <th colspan="3" class="sectionHeader">
                <a name="software"/>Installed Software
              </th>
              <th class="navigTop">
                <a href="#top">top
                  <xsl:value-of select="$entity.up.arrow"/>
                </a>
              </th>
            </tr>
            <tr>
              <td class="sectionSubHeader">Package</td>
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
              <td class="sectionSubHeader">Installed
                <br/>
                <span style="font-size: 70%; font-style: italic;">(Days since
                  <xsl:copy-of select="$todaysDate"/>)
                </span>
              </td>
            </tr>

    <!-- Table Body -->
            <xsl:for-each select="/BaselineReport/sections/section[@name='Software']/subSection[@name='Packages']/packages/package">
              <xsl:sort select="@installtime" order="descending" data-type="number"/>
              <xsl:sort select="@name"/>

     <!-- Determine number of days since the package was installed -->
              <xsl:variable name="installEpoch" select="format-number((($todaysEpoch div 1000) - @installtime) div 86400, '#')"/>

              <tr>
                <xsl:variable name="cellColor">
                  <xsl:choose>
                    <xsl:when test="position() mod 2 = 0">background-color: #efefef;</xsl:when>
                    <xsl:otherwise>background-color: white;</xsl:otherwise>
                  </xsl:choose>
                </xsl:variable>

       <!-- Package Name -->
                <td style="padding-top: 5px; vertical-align: top; {$cellColor}; border-right: 1px solid black">
                  <xsl:value-of select="@name"/>
                </td>

       <!-- Description/Summary -->
                <td style="padding-top: 5px; vertical-align: top; {$cellColor}; border-right: 1px solid black">
                  <xsl:value-of select="@summary"/>
                </td>

       <!-- Version/Release -->
                <td style="padding-top: 5px; vertical-align: top; {$cellColor}; border-right: 1px solid black">
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

        <!-- Solaris Patch List -->
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

                <td style="padding-top: 5px; vertical-align: top; text-align: right;white-space: pre; {$cellColor}">
                  <xsl:copy-of select="$installEpoch"/>
                </td>

              </tr>
            </xsl:for-each>
          </table>

<!-- Report Footer -->
          <xsl:if test="$footer.display != 'false'">
            <xsl:call-template name="footer">
              <xsl:with-param name="sbVersion" select="/BaselineReport/@sbVersion"/>
            </xsl:call-template>
          </xsl:if>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
