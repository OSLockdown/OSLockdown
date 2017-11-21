<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Baseline Comparison Report XML to FO -> PDF
     =========================================================================
-->
  <xsl:include href="common-fo.xsl"/>
    <!--
   Report Parameter Definitions:
     report.title     : Report title to be used in header 
     header.display   : if false, do not display header
     logo.display     : if false, do not display logo in header

-->
  <xsl:param name="report.title">Baseline Comparison Report</xsl:param>
  <xsl:param name="header.display">true</xsl:param>
  <xsl:param name="logo.display">true</xsl:param>
  <xsl:output method="xml" encoding="utf-8" indent="yes"/>
  <xsl:template match="/">
    <fo:root xmlns:fo="http://www.w3.org/1999/XSL/Format"
             xmlns:fox="http://xmlgraphics.apache.org/fop/extensions">
      <fo:layout-master-set>
                <!-- Report is landscape so, switch width and height -->
        <fo:simple-page-master master-name="first" page-width="{$page.height}" page-height="{$page.width}" margin-top="0.25in" margin-bottom="0.5in" margin-right="0.5in" margin-left="0.5in">
          <fo:region-body margin-top="0.25in" margin-bottom="0.5in"/>
          <fo:region-before extent="0.5in"/>
          <fo:region-after extent="0.5in"/>
        </fo:simple-page-master>
      </fo:layout-master-set>
      <fo:declarations>
<!-- 
     =======================================================================
          PDF Document Properities (Metadata)
     =======================================================================
-->
        <x:xmpmeta xmlns:x="adobe:ns:meta/">
          <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
          <!-- Dublin Core properties go here -->
            <rdf:Description xmlns:dc="http://purl.org/dc/elements/1.1/" rdf:about="">
              <dc:title>
                <xsl:copy-of select="$report.title"/>
              </dc:title>
              <dc:creator>OS Lockdown</dc:creator>
              <dc:description>Baseline Comparison Report</dc:description>
            </rdf:Description>
          <!-- XMP properties go here -->
            <rdf:Description xmlns:xmp="http://ns.adobe.com/xap/1.0/" rdf:about="">
              <xmp:CreatorTool>OS Lockdown</xmp:CreatorTool>
            </rdf:Description>
            <!-- PDF properties go here -->
            <rdf:Description xmlns:pdf="http://ns.adobe.com/pdf/1.3/" rdf:about="">
              <pdf:Producer>OS Lockdown and Apache FOP</pdf:Producer>
              <pdf:Keywords>Baseline</pdf:Keywords>
            </rdf:Description>
          </rdf:RDF>
        </x:xmpmeta>
      </fo:declarations>
<!-- 
    =======================================================================
          PDF Bookmarks / Navigation
    =======================================================================
-->
      <fo:bookmark-tree>
        <fo:bookmark internal-destination="summaryTable">
          <fo:bookmark-title>Summary</fo:bookmark-title>
        </fo:bookmark>
        <fo:bookmark internal-destination="Software">
          <fo:bookmark-title>Software</fo:bookmark-title>
          <xsl:if test="count(/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages/changed/packageDelta) != 0">
            <fo:bookmark internal-destination="swChanges">
              <fo:bookmark-title>Changed Packages</fo:bookmark-title>
            </fo:bookmark>
          </xsl:if>
          <xsl:if test="count(/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages/added/package) != 0">
            <fo:bookmark internal-destination="swAdded">
              <fo:bookmark-title>New Packages</fo:bookmark-title>
            </fo:bookmark>
          </xsl:if>
          <xsl:if test="count(/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages/removed/package) != 0">
            <fo:bookmark internal-destination="swRemoved">
              <fo:bookmark-title>Non-existent Packages</fo:bookmark-title>
            </fo:bookmark>
          </xsl:if>
        </fo:bookmark>
        <xsl:for-each select="/BaselineReportDelta/sections/section[@name != 'Software' and @name != 'Files']">
          <xsl:variable name="secname" select="@name"/>
          <fo:bookmark internal-destination="{$secname}">
            <fo:bookmark-title>
              <xsl:value-of select="@name"/>
            </fo:bookmark-title>
          </fo:bookmark>
        </xsl:for-each>
        <fo:bookmark internal-destination="Files">
          <fo:bookmark-title>Files</fo:bookmark-title>
          <xsl:if test="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup/changed/fileDelta) != 0">
            <fo:bookmark internal-destination="changedFiles">
              <fo:bookmark-title>Changed Files</fo:bookmark-title>
            </fo:bookmark>
          </xsl:if>
          <xsl:if test="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup/added/file) != 0">
            <fo:bookmark internal-destination="addedFiles">
              <fo:bookmark-title>Added Files</fo:bookmark-title>
            </fo:bookmark>
          </xsl:if>
          <xsl:if test="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup/removed/file) != 0">
            <fo:bookmark internal-destination="filesRemoved">
              <fo:bookmark-title>Non-existent Files</fo:bookmark-title>
            </fo:bookmark>
          </xsl:if>
        </fo:bookmark>
      </fo:bookmark-tree>
<!-- 
    =======================================================================
          Report Footer (Static)
    =======================================================================
-->
      <fo:page-sequence master-reference="first" font-family="Helvetica" font-size="{$page.font.size}">
        <fo:static-content flow-name="xsl-region-after">
          <fo:block margin-top="0.25in" font-size="10pt" text-align="end" color="#467fc5">
            <fo:table table-layout="fixed" background-color="{$table.bgcolor}" width="10in">
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-body>
                <fo:table-row>
                  <fo:table-cell text-align="left">
                    <fo:block>
                         OS Lockdown v<xsl:value-of select="/BaselineReportDelta/@sbVersion"/>
                    </fo:block>
                  </fo:table-cell>
                  <fo:table-cell text-align="center">
                    <fo:block>
                      <xsl:text> </xsl:text>
                    </fo:block>
                  </fo:table-cell>
                  <fo:table-cell text-align="right">
                    <fo:block>Page <fo:page-number/> of
                      <fo:page-number-citation ref-id="terminator"/>
                    </fo:block>
                  </fo:table-cell>
                </fo:table-row>
              </fo:table-body>
            </fo:table>
          </fo:block>
        </fo:static-content>
        <fo:flow flow-name="xsl-region-body">
<!-- 
   =======================================================================
          Report Header 
   =======================================================================
-->
          <xsl:if test="$header.display = 'true'">
<!--
            <fo:table id="doctop" table-layout="fixed" background-color="{$report.header.bgcolor}" width="10in" border-spacing="0pt" margin-bottom="1em">
-->
            <fo:table id="doctop" table-layout="fixed" xsl:use-attribute-sets="table" >
              <fo:table-column column-width="proportional-column-width(2.5)"/>
              <fo:table-column column-width="proportional-column-width(1.5)"/>
              <fo:table-body>
                <fo:table-row>
                  <fo:table-cell border-width="0pt" display-align="center">
                    <fo:block text-align="center" font-weight="bold" color="black" font-size="18pt">
                      <xsl:copy-of select="$report.title"/>
                    </fo:block>
                  </fo:table-cell>
                  <fo:table-cell>
                    <fo:block text-align="center" padding="5pt">
                      <xsl:choose>
                        <xsl:when test="$logo.display = 'true'">
                          <fo:external-graphic src="url({$image.header.logo})" content-width="50%"/>
                        </xsl:when>
                        <xsl:otherwise>
                          <xsl:text> </xsl:text>
                        </xsl:otherwise>
                      </xsl:choose>
                    </fo:block>
                  </fo:table-cell>
                </fo:table-row>
              </fo:table-body>
            </fo:table>
          </xsl:if>
<!-- 
    =======================================================================
          Summary Table
    =======================================================================
-->
          <fo:table id="summaryTable" table-layout="fixed" width="10in" background-color="{$table.bgcolor}" border-spacing="0pt" border="1px solid {$table.color}" margin-top="2em" margin-bottom="1em" font-size="{$table.font.size}">
            <fo:table-column column-width="proportional-column-width(1)"/>
            <fo:table-column column-width="proportional-column-width(2)"/>
            <fo:table-column column-width="proportional-column-width(2)"/>
            <fo:table-header>
              <fo:table-row color="{$table.font.color}">
                <fo:table-cell background-color="{$report.header.bgcolor}" padding="2px 5px 2px 5px" text-align="left" display-align="center" number-columns-spanned="2">
                  <fo:block font-weight="bold">Summary</fo:block>
                </fo:table-cell>
                <fo:table-cell background-color="{$report.header.bgcolor}" padding="2px 5px 2px 5px" text-align="right" display-align="center">
                  <fo:block font-weight="bold">Generated:
                    <xsl:value-of select="substring(/BaselineReportDelta/@created,1,20)"/>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>
            </fo:table-header>
            <fo:table-body>
              <xsl:variable name="report1" select="/BaselineReportDelta/report[1]"/>
              <xsl:variable name="report2" select="/BaselineReportDelta/report[2]"/>
              <fo:table-row color="{$table.font.color}">
                <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center" number-columns-spanned="1">
                  <fo:block font-weight="bold">
                    <xsl:text> </xsl:text>
                  </fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center" background-color="{$table.color}">
                  <fo:block>Report A</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center" background-color="{$table.color}">
                  <fo:block>Report B</fo:block>
                </fo:table-cell>
              </fo:table-row>
           <!-- Hostnames of Report A and B -->
              <fo:table-row color="{$table.font.color}" font-size="{$table.font.size}">
                <xsl:variable name="fontColor">
                  <xsl:choose>
                    <xsl:when test="$report1/@hostname != $report2/@hostname">red</xsl:when>
                    <xsl:otherwise>black</xsl:otherwise>
                  </xsl:choose>
                </xsl:variable>
                <fo:table-cell color="{$fontColor}" padding="2px 5px 2px 5px" text-align="right" display-align="center">
                  <fo:block>System</fo:block>
                </fo:table-cell>
                <fo:table-cell color="{$fontColor}" border-bottom="1px solid {$table.color}" padding="2px 5px 2px 5px" border-left="1px solid {$table.color}" text-align="left" display-align="center">
                  <fo:block>
                    <xsl:value-of select="$report1/@hostname"/>
                  </fo:block>
                </fo:table-cell>
                <fo:table-cell color="{$fontColor}" border-bottom="1px solid {$table.color}" padding="2px 5px 2px 5px" border-left="1px solid {$table.color}" text-align="left" display-align="center">
                  <fo:block>
                    <xsl:value-of select="$report2/@hostname"/>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

            <!-- Report Creation Dates -->
              <fo:table-row color="{$table.font.color}" font-size="{$table.font.size}">
                <fo:table-cell padding="2px 5px 2px 5px" text-align="right" display-align="center">
                  <fo:block>Created</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px" border-bottom="1px solid {$table.color}" border-left="1px solid {$table.color}" text-align="left" display-align="center">
                  <fo:block>
                    <xsl:value-of select="$report1/@created"/>
                  </fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px" border-bottom="1px solid {$table.color}" border-left="1px solid {$table.color}" text-align="left" display-align="center">
                  <fo:block>
                    <xsl:value-of select="$report2/@created"/>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

            <!-- Operating Systems -->
              <fo:table-row color="{$table.font.color}" font-size="{$table.font.size}">
                <xsl:variable name="fontColor">
                  <xsl:choose>
                    <xsl:when test="$report1/@distVersion != $report2/@distVersion or $report1/@dist != $report2/@dist or $report1/@arch != $report2/@arch or $report1/@kernel != $report2/@kernel">#467fc5</xsl:when>
                    <xsl:otherwise>black</xsl:otherwise>
                  </xsl:choose>
                </xsl:variable>
                <fo:table-cell padding="2px 5px 2px 5px" text-align="right" display-align="center">
                  <fo:block>Operating System</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px" border-bottom="1px solid {$table.color}" color="{$fontColor}" border-left="1px solid {$table.color}" text-align="left" display-align="center">
                  <fo:block>
                    <xsl:choose>
                      <xsl:when test="number($report1/@distVersion) &gt;= 10 and $report1/@dist = 'redhat'">
                        <xsl:text>Fedora </xsl:text>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:value-of select="$report1/@dist"/>
                        <xsl:text> </xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                    <xsl:value-of select="$report1/@distVersion"/>
                    <xsl:text> (</xsl:text>
                    <xsl:value-of select="$report1/@arch"/>
                    <xsl:text>) [Kernel </xsl:text>
                    <xsl:value-of select="$report1/@kernel"/>
                    <xsl:text>]</xsl:text>
                  </fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px" color="{$fontColor}" border-bottom="1px solid {$table.color}" border-left="1px solid {$table.color}" text-align="left" display-align="center">
                  <fo:block>
                    <xsl:choose>
                      <xsl:when test="number($report2/@distVersion) &gt;= 10 and $report2/@dist = 'redhat'">
                        <xsl:text>Fedora </xsl:text>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:value-of select="$report2/@dist"/>
                        <xsl:text> </xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                    <xsl:value-of select="$report2/@distVersion"/>
                    <xsl:text> (</xsl:text>
                    <xsl:value-of select="$report2/@arch"/>
                    <xsl:text>) [Kernel </xsl:text>
                    <xsl:value-of select="$report2/@kernel"/>
                    <xsl:text>]</xsl:text>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

          <!-- Memory Information -->
              <fo:table-row color="{$table.font.color}" font-size="{$table.font.size}">
                <xsl:variable name="fontColor">
                  <xsl:choose>
                    <xsl:when test="$report1/@totalMemory != $report2/@totalMemory">#467fc5</xsl:when>
                    <xsl:otherwise>black</xsl:otherwise>
                  </xsl:choose>
                </xsl:variable>
                <fo:table-cell padding="2px 5px 2px 5px" text-align="right" display-align="center">
                  <fo:block>Total Memory</fo:block>
                </fo:table-cell>
                <fo:table-cell color="{$fontColor}" border-bottom="1px solid {$table.color}" padding="2px 5px 2px 5px" border-left="1px solid {$table.color}" text-align="left" display-align="center">
                  <fo:block>
                    <xsl:value-of select="$report1/@totalMemory"/>
                  </fo:block>
                </fo:table-cell>
                <fo:table-cell color="{$fontColor}" padding="2px 5px 2px 5px" border-bottom="1px solid {$table.color}" border-left="1px solid {$table.color}" text-align="left" display-align="center">
                  <fo:block>
                    <xsl:value-of select="$report2/@totalMemory"/>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

           <!-- Cpu Information -->
              <fo:table-row color="{$table.font.color}" border-bottom="1px solid {$table.color}" font-size="{$table.font.size}">
                <xsl:variable name="fontColor">
                  <xsl:choose>
                    <xsl:when test="$report1/@cpuInfo != $report2/@cpuInfo">#467fc5</xsl:when>
                    <xsl:otherwise>black</xsl:otherwise>
                  </xsl:choose>
                </xsl:variable>
                <fo:table-cell padding="2px 5px 2px 5px" border-bottom="1px solid {$table.color}" text-align="right" display-align="center">
                  <fo:block>Processors</fo:block>
                </fo:table-cell>
                <fo:table-cell color="{$fontColor}" padding="2px 5px 2px 5px" border-left="1px solid {$table.color}" text-align="left" display-align="center">
                  <fo:block>
                    <xsl:value-of select="$report1/@cpuInfo"/>
                  </fo:block>
                </fo:table-cell>
                <fo:table-cell color="{$fontColor}" border-bottom="1px solid {$table.color}" padding="2px 5px 2px 5px" border-left="1px solid {$table.color}" text-align="left" display-align="center">
                  <fo:block>
                    <xsl:value-of select="$report2/@cpuInfo"/>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

           <!-- Software Information -->
              <fo:table-row color="{$table.font.color}" font-size="{$table.font.size}">
                <fo:table-cell padding="2px 5px 2px 5px" text-align="right" display-align="center">
                  <fo:block>Software</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px" border-left="1px solid {$table.color}" text-align="left" display-align="center" number-columns-spanned="2">
                  <fo:block>
                    <xsl:choose>
                      <xsl:when test="./packages[@hasChanged] != 'true'">
                        <xsl:text>No changes detected</xsl:text>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text>In Report B: </xsl:text>
                    <!-- Changed Software -->
                        <xsl:variable name="swDelta" select="count(/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages/changed/packageDelta)"/>
                        <xsl:variable name="fontColor1">
                          <xsl:choose>
                            <xsl:when test="$swDelta != 0">#467fc5</xsl:when>
                            <xsl:otherwise>black</xsl:otherwise>
                          </xsl:choose>
                        </xsl:variable>
                        <fo:inline color="{$fontColor1}">
                          <xsl:copy-of select="$swDelta"/>
                          <xsl:text> packages changed, </xsl:text>
                        </fo:inline>
                    <!-- Added Software -->
                        <xsl:variable name="swAdded" select="count(/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages/added/package)"/>
                        <xsl:variable name="fontColor2">
                          <xsl:choose>
                            <xsl:when test="$swAdded != 0">#467fc5</xsl:when>
                            <xsl:otherwise>black</xsl:otherwise>
                          </xsl:choose>
                        </xsl:variable>
                        <fo:inline color="{$fontColor2}">
                          <xsl:copy-of select="$swAdded"/>
                          <xsl:text> are new</xsl:text>
                        </fo:inline>
                        <xsl:text>, and </xsl:text>
                    <!-- Removed  Software -->
                        <xsl:variable name="swRemoved" select="count(/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages/removed/package)"/>
                        <xsl:variable name="fontColor3">
                          <xsl:choose>
                            <xsl:when test="$swRemoved != 0">#467fc5</xsl:when>
                            <xsl:otherwise>black</xsl:otherwise>
                          </xsl:choose>
                        </xsl:variable>
                        <fo:inline color="{$fontColor3}">
                          <xsl:copy-of select="$swRemoved"/>
                          <xsl:text> are non-existent.</xsl:text>
                        </fo:inline>
                      </xsl:otherwise>
                    </xsl:choose>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

          <!-- General Sections -->
              <xsl:for-each select="/BaselineReportDelta/sections/section[@name != 'Software' and @name != 'Files']">
                <fo:table-row color="{$table.font.color}" font-size="{$table.font.size}">
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="right" display-align="center">
                    <fo:block>
                      <xsl:value-of select="@name"/>
                    </fo:block>
                  </fo:table-cell>
                  <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="left" display-align="center" number-columns-spanned="2">
                    <xsl:variable name="changeCount" select="count(./subSection/content[@hasChanged = 'true'])"/>
                    <xsl:variable name="fontColor">
                      <xsl:choose>
                        <xsl:when test="number($changeCount) != 0">#467fc5</xsl:when>
                        <xsl:otherwise>black</xsl:otherwise>
                      </xsl:choose>
                    </xsl:variable>
                    <fo:block color="{$fontColor}">
                      <xsl:copy-of select="format-number($changeCount, '###,###')"/>
                      <xsl:text> change</xsl:text>
                      <xsl:if test="$changeCount != 1">
                        <xsl:text>s</xsl:text>
                      </xsl:if>
                    </fo:block>
                  </fo:table-cell>
                </fo:table-row>
              </xsl:for-each>
              
           <!-- Files Information -->
              <fo:table-row color="{$table.font.color}" font-size="{$table.font.size}">
                <fo:table-cell padding="2px 5px 2px 5px" text-align="right" display-align="center">
                  <fo:block>Files</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px" border-left="1px solid {$table.color}" text-align="left" display-align="center" number-columns-spanned="2">
                  <fo:block>
                    <xsl:text>In Report B: </xsl:text>
                    <xsl:variable name="filesChanged" select="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup/changed/fileDelta)"/>
                    <xsl:variable name="fontColor4">
                      <xsl:choose>
                        <xsl:when test="number($filesChanged) != 0">#467fc5</xsl:when>
                        <xsl:otherwise>black</xsl:otherwise>
                      </xsl:choose>
                    </xsl:variable>
                    <fo:inline color="{$fontColor4}">
                      <xsl:value-of select="format-number($filesChanged, '###,###')"/>
                      <xsl:text> files changed, </xsl:text>
                    </fo:inline>
                    <xsl:variable name="filesAdded" select="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup/added/file)"/>
                    <xsl:variable name="fontColor5">
                      <xsl:choose>
                        <xsl:when test="number($filesAdded) != 0">#467fc5</xsl:when>
                        <xsl:otherwise>black</xsl:otherwise>
                      </xsl:choose>
                    </xsl:variable>
                    <fo:inline color="{$fontColor5}">
                      <xsl:value-of select="format-number($filesAdded, '###,###')"/>
                      <xsl:text> are new, </xsl:text>
                    </fo:inline>
                    <xsl:text>and </xsl:text>
                    <xsl:variable name="filesRemoved" select="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup/removed/file)"/>
                    <xsl:variable name="fontColor6">
                      <xsl:choose>
                        <xsl:when test="number($filesAdded) != 0">#467fc5</xsl:when>
                        <xsl:otherwise>black</xsl:otherwise>
                      </xsl:choose>
                    </xsl:variable>
                    <fo:inline color="{$fontColor6}">
                      <xsl:value-of select="format-number($filesRemoved, '###,###')"/>
                      <xsl:text> are non-existent.</xsl:text>
                    </fo:inline>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>
            </fo:table-body>
          </fo:table>
<!-- 
    ================================================================ 
                         Changed Software
    ================================================================
-->
          <fo:block id="Software"/>
          <xsl:variable name="packages" select="/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages"/>
          <xsl:if test="count($packages/changed/packageDelta) != 0">
            <fo:table id="swChanges" table-layout="fixed" width="10in" background-color="{$table.bgcolor}" border-spacing="0pt" border="1px solid {$table.color}" margin-top="2em" margin-bottom="1em" font-size="{$table.font.size}">
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(2)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1.5)"/>
              <fo:table-column column-width="proportional-column-width(1.5)"/>
              <fo:table-header>
                <fo:table-row color="{$table.font.color}">
                  <fo:table-cell background-color="{$report.header.bgcolor}" padding="2px 5px 2px 5px" text-align="left" display-align="center" number-columns-spanned="6">
                    <fo:block font-weight="bold">Changed Software Packages: Software found in both reports but versions are different</fo:block>
                  </fo:table-cell>
                </fo:table-row>
                <fo:table-row color="{$table.font.color}">
                  <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="left" display-align="center" number-rows-spanned="2">
                    <fo:block>Package Name</fo:block>
                  </fo:table-cell>
                  <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="left" display-align="center" number-rows-spanned="2">
                    <fo:block>Description</fo:block>
                  </fo:table-cell>
                  <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center" number-columns-spanned="2">
                    <fo:block>Version</fo:block>
                  </fo:table-cell>
                  <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center" number-columns-spanned="2">
                    <fo:block>Installation Date</fo:block>
                  </fo:table-cell>
                </fo:table-row>
                <fo:table-row color="{$table.font.color}">
                  <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>Report A</fo:block>
                  </fo:table-cell>
                  <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>Report B</fo:block>
                  </fo:table-cell>
                  <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>Report A</fo:block>
                  </fo:table-cell>
                  <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>Report B</fo:block>
                  </fo:table-cell>
                </fo:table-row>
              </fo:table-header>
              <fo:table-body>
                <xsl:for-each select="$packages/changed/packageDelta">
                  <xsl:sort select="./package[1]/@name"/>
                  <xsl:variable name="rowColor">
                    <xsl:choose>
                      <xsl:when test="position() mod 2 = 0">
                        <xsl:copy-of select="$table.row.alt.bgcolor"/>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:copy-of select="$table.bgcolor"/>
                      </xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>
                  <xsl:variable name="package1" select="./package[1]"/>
                  <xsl:variable name="package2" select="./package[2]"/>
                  <fo:table-row background-color="{$rowColor}">
                    <fo:table-cell padding="2px 5px 2px 5px" text-align="right" display-align="center">
                      <fo:block>
                        <xsl:value-of select="$package1/@name"/>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="left" display-align="center">
                      <fo:block>
                        <xsl:value-of select="$package1/@summary"/>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <fo:block>
                        <xsl:value-of select="$package1/@version"/>
                        <xsl:text>-</xsl:text>
                        <xsl:value-of select="$package1/@release"/>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <fo:block>
                        <xsl:value-of select="$package2/@version"/>
                        <xsl:text>-</xsl:text>
                        <xsl:value-of select="$package2/@release"/>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <fo:block>
                        <xsl:call-template name="date.reformat" >
                          <xsl:with-param name="iDate" select="$package1/@install_localtime"/>
                        </xsl:call-template>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <fo:block>
                        <xsl:call-template name="date.reformat" >
                          <xsl:with-param name="iDate" select="$package2/@install_localtime"/>
                        </xsl:call-template>
                      </fo:block>
                    </fo:table-cell>
                  </fo:table-row>
                </xsl:for-each>
              </fo:table-body>
            </fo:table>
          </xsl:if>
<!-- 
    ================================================================ 
                             Added Software
    ================================================================
-->
          <xsl:if test="count(/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages/added/package) != 0">
            <xsl:variable name="newPackages" select="/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages"/>
            <fo:table id="swAdded" table-layout="fixed" width="10in" background-color="{$table.bgcolor}" border-spacing="0pt" border="1px solid {$table.color}" margin-top="2em" margin-bottom="1em" font-size="{$table.font.size}">
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(2)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-header>
                <fo:table-row background-color="{$report.header.bgcolor}">
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center" number-columns-spanned="4">
                    <fo:block font-weight="bold">New Software Packages: This software was found in Report B but not Report A</fo:block>
                  </fo:table-cell>
                </fo:table-row>
                <fo:table-row color="{$table.font.color}">
                  <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="left" display-align="center" number-rows-spanned="1">
                    <fo:block>Package Name</fo:block>
                  </fo:table-cell>
                  <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="left" display-align="center" number-rows-spanned="1">
                    <fo:block>Description</fo:block>
                  </fo:table-cell>
                  <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center" number-columns-spanned="1">
                    <fo:block>Version</fo:block>
                  </fo:table-cell>
                  <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center" number-columns-spanned="1">
                    <fo:block>Installation Date</fo:block>
                  </fo:table-cell>
                </fo:table-row>
              </fo:table-header>
              <fo:table-body>
                <xsl:for-each select="$newPackages/added/package">
                  <xsl:sort select="@name"/>
                  <xsl:variable name="rowColor">
                    <xsl:choose>
                      <xsl:when test="position() mod 2 = 0">
                        <xsl:copy-of select="$table.row.alt.bgcolor"/>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:copy-of select="$table.bgcolor"/>
                      </xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>
                  <fo:table-row background-color="{$rowColor}">
                    <fo:table-cell padding="2px 5px 2px 5px" text-align="right" display-align="center">
                      <fo:block>
                        <xsl:value-of select="@name"/>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="left" display-align="center">
                      <fo:block>
                        <xsl:value-of select="@summary"/>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell padding="2px 5px 2px 5px" border-left="1px solid {$table.color}" text-align="center" display-align="center">
                      <fo:block>
                        <xsl:value-of select="@version"/>
                        <xsl:text>-</xsl:text>
                        <xsl:value-of select="@release"/>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <fo:block>
                        <xsl:call-template name="date.reformat" >
                          <xsl:with-param name="iDate" select="@install_localtime"/>
                        </xsl:call-template>
                      </fo:block>
                    </fo:table-cell>
                  </fo:table-row>
                </xsl:for-each>
              </fo:table-body>
            </fo:table>
          </xsl:if>
<!-- 
    ================================================================ 
                             Removed Software
    ================================================================
-->
          <xsl:variable name="delPackages" select="/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages"/>
          <xsl:if test="count($delPackages/removed/package) != 0">
            <fo:table id="swRemoved" table-layout="fixed" width="10in" background-color="{$table.bgcolor}" border-spacing="0pt" border="1px solid {$table.color}" margin-top="2em" margin-bottom="1em" font-size="{$table.font.size}">
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(2)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(2)"/>
              <fo:table-header>
                <fo:table-row background-color="{$report.header.bgcolor}">
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center" number-columns-spanned="4">
                    <fo:block font-weight="bold">Non-existent Software Packages: This software was found in Report A but not Report B</fo:block>
                  </fo:table-cell>
                </fo:table-row>
                <fo:table-row color="{$table.font.color}">
                  <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="left" display-align="center" number-rows-spanned="1">
                    <fo:block>Package Name</fo:block>
                  </fo:table-cell>
                  <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="left" display-align="center" number-rows-spanned="1">
                    <fo:block>Description</fo:block>
                  </fo:table-cell>
                  <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center" number-columns-spanned="1">
                    <fo:block>Version</fo:block>
                  </fo:table-cell>
                  <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center" number-columns-spanned="1">
                    <fo:block>Installation Date</fo:block>
                  </fo:table-cell>
                </fo:table-row>
              </fo:table-header>
              <fo:table-body>
                <xsl:for-each select="$delPackages/removed/package">
                  <xsl:sort select="@name"/>
                  <xsl:variable name="rowColor">
                    <xsl:choose>
                      <xsl:when test="position() mod 2 = 0">
                        <xsl:copy-of select="$table.row.alt.bgcolor"/>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:copy-of select="$table.bgcolor"/>
                      </xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>
                  <fo:table-row background-color="{$rowColor}">
                    <fo:table-cell padding="2px 5px 2px 5px" text-align="right" display-align="center">
                      <fo:block>
                        <xsl:value-of select="@name"/>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="left" display-align="center">
                      <fo:block>
                        <xsl:value-of select="@summary"/>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell padding="2px 5px 2px 5px" border-left="1px solid {$table.color}" text-align="center" display-align="center">
                      <fo:block>
                        <xsl:value-of select="@version"/>
                        <xsl:text>-</xsl:text>
                        <xsl:value-of select="@release"/>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <fo:block>
                        <xsl:call-template name="date.reformat" >
                          <xsl:with-param name="iDate" select="@install_localtime"/>
                        </xsl:call-template>
                      </fo:block>
                    </fo:table-cell>
                  </fo:table-row>
                </xsl:for-each>
              </fo:table-body>
            </fo:table>
          </xsl:if>
<!-- 
     ================================================================ 
                          Generic Sections
     ================================================================
-->
          <xsl:for-each select="/BaselineReportDelta/sections/section[@name != 'Software' and @name != 'Files']">
            <xsl:if test="count(./subSection) != 0" >
              <xsl:variable name="secname" select="@name"/>
              <fo:table id="{$secname}" table-layout="fixed" width="10in" background-color="{$table.bgcolor}" border-spacing="0pt" border="1px solid {$table.color}" margin-top="2em" margin-bottom="1em" font-size="{$table.font.size}">
                <fo:table-column column-width="proportional-column-width(1)"/>
                <fo:table-column column-width="proportional-column-width(4)"/>
                <fo:table-header>
                  <fo:table-row background-color="{$report.header.bgcolor}">
                    <fo:table-cell padding="2px 5px 2px 5px" text-align="left" number-columns-spanned="2" display-align="center">
                      <fo:block font-weight="bold">
                        <xsl:value-of select="@name"/>
                      </fo:block>
                    </fo:table-cell>
                  </fo:table-row>
                </fo:table-header>
                <fo:table-body>
                  <xsl:for-each select="./subSection">
                    <fo:table-row border-bottom="1px solid {$table.color}">
                      <fo:table-cell padding="2px 5px 2px 5px" text-align="right">
                        <fo:block>
                          <xsl:value-of select="@name"/>
                        </fo:block>
                      </fo:table-cell>
                      <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="left" display-align="center">
                        <fo:block>
                          <xsl:choose>
                            <xsl:when test="@hasChanged = 'true'">
                              <fo:inline color="#467fc5">Changed</fo:inline>
                            </xsl:when>
                            <xsl:otherwise>Unchanged</xsl:otherwise>
                          </xsl:choose>
                        </fo:block>
                      </fo:table-cell>
                    </fo:table-row>
                  </xsl:for-each>
                </fo:table-body>
              </fo:table>
            </xsl:if>
          </xsl:for-each>
<!-- 
    ================================================================ 
                            File Changes
    ================================================================
-->
          <fo:block id="Files"/>
          <xsl:if test="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup/changed/fileDelta) != 0">
            <fo:table id="changedFiles" table-layout="fixed" width="10in" background-color="{$table.bgcolor}" border-spacing="0pt" border="1px solid {$table.color}" margin-top="2em" margin-bottom="1em" font-size="{$table.font.size}">
              <fo:table-column column-width="proportional-column-width(2.5)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1.1)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(0.8)"/>
              <fo:table-column column-width="proportional-column-width(2)"/>
              <fo:table-header>
                <fo:table-row background-color="{$report.header.bgcolor}">
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="left" number-columns-spanned="6" display-align="center">
                    <fo:block font-weight="bold">Changed Files: Files exist in both reports but differences exist</fo:block>
                  </fo:table-cell>
                </fo:table-row>
                <fo:table-row background-color="{$table.color}" color="{$table.font.color}">
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
                    <fo:block>File Path</fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>Permissions</fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>Owner / Group ID</fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>SUID / SGID</fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>Contents</fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
                    <fo:block>Last Modified</fo:block>
                  </fo:table-cell>
                </fo:table-row>
              </fo:table-header>
              <fo:table-body>
                <xsl:variable name="fileTypes" select="/BaselineReportDelta/sections/section[@name = 'Files']/subSection"/>
                <xsl:for-each select="$fileTypes/fileGroups/fileGroup">
                  <xsl:if test="count(./changed/fileDelta) != 0">
                    <fo:table-row background-color="{$table.subrow.bgcolor}" color="{$table.font.color}">
                      <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center" number-columns-spanned="6">
                        <fo:block font-weight="bold">
                          <xsl:value-of select="../../@name"/>
                          <xsl:text> - </xsl:text>
                          <xsl:value-of select="@name"/>
                        </fo:block>
                      </fo:table-cell>
                    </fo:table-row>
                    <xsl:for-each select="./changed/fileDelta">
                      <xsl:sort select="./file[1]/@path"/>
                      <xsl:variable name="file1" select="./file[1]"/>
                      <xsl:variable name="file2" select="./file[2]"/>
                      <xsl:variable name="rowColor">
                        <xsl:choose>
                          <xsl:when test="position() mod 2 = 0">
                            <xsl:copy-of select="$table.row.alt.bgcolor"/>
                          </xsl:when>
                          <xsl:otherwise>
                            <xsl:copy-of select="$table.bgcolor"/>
                          </xsl:otherwise>
                        </xsl:choose>
                      </xsl:variable>
                      <fo:table-row background-color="{$rowColor}" color="{$table.font.color}">
                        <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
                          <fo:block margin-left="1em">
                            <xsl:value-of select="$file1/@path"/>
                          </fo:block>
                        </fo:table-cell>
                        <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                          <fo:block margin-left="1em">
                            <xsl:choose>
                              <xsl:when test="$file1/@mode != $file2/@mode">
                                <fo:inline color="#467fc5">
                                  <xsl:value-of select="$file1/@mode"/>
                                  <xsl:text> &gt;&gt; </xsl:text>
                                  <xsl:value-of select="$file2/@mode"/>
                                </fo:inline>
                              </xsl:when>
                              <xsl:otherwise>
                                <xsl:value-of select="$file1/@mode"/>
                              </xsl:otherwise>
                            </xsl:choose>
                          </fo:block>
                        </fo:table-cell>
                        <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                          <fo:block>
                            <xsl:choose>
                              <xsl:when test="$file1/@uid != $file2/@uid or $file1/@gid != $file2/@gid">
                                <fo:inline color="#467fc5">
                                  <xsl:value-of select="$file1/@uid"/>
                                  <xsl:text> / </xsl:text>
                                  <xsl:value-of select="$file1/@gid"/>
                                  <xsl:text> &gt;&gt; </xsl:text>
                                  <xsl:value-of select="$file2/@uid"/>
                                  <xsl:text> / </xsl:text>
                                  <xsl:value-of select="$file2/@gid"/>
                                </fo:inline>
                              </xsl:when>
                              <xsl:otherwise>
                                <xsl:value-of select="$file1/@uid"/>
                                <xsl:text> / </xsl:text>
                                <xsl:value-of select="$file1/@gid"/>
                              </xsl:otherwise>
                            </xsl:choose>
                          </fo:block>
                        </fo:table-cell>
                        <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                          <fo:block>
                            <xsl:choose>
                              <xsl:when test="$file1/@suid != $file2/@suid or $file1/@sgid != $file2/@sgid">
                                <fo:inline color="#467fc5">
                                  <xsl:value-of select="$file1/@suid"/>
                                  <xsl:text> / </xsl:text>
                                  <xsl:value-of select="$file1/@sgid"/>
                                  <xsl:text> &gt;&gt; </xsl:text>
                                  <xsl:value-of select="$file2/@suid"/>
                                  <xsl:text> / </xsl:text>
                                  <xsl:value-of select="$file2/@sgid"/>
                                </fo:inline>
                              </xsl:when>
                              <xsl:otherwise>
                                <xsl:value-of select="$file1/@suid"/>
                                <xsl:text> / </xsl:text>
                                <xsl:value-of select="$file1/@sgid"/>
                              </xsl:otherwise>
                            </xsl:choose>
                          </fo:block>
                        </fo:table-cell>
                        <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                          <fo:block>
                            <xsl:choose>
                              <xsl:when test="$file1/@sha1 != $file2/@sha1">
                                <fo:inline color="#467fc5">Changed</fo:inline>
                              </xsl:when>
                              <xsl:otherwise>
                                <fo:inline color="gray">unchanged</fo:inline>
                              </xsl:otherwise>
                            </xsl:choose>
                          </fo:block>
                        </fo:table-cell>
                        <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
                          <fo:block>
                            <xsl:choose>
                              <xsl:when test="$file1/@mtime != $file2/@mtime">
                                <fo:inline color="#467fc5">
                                  <xsl:call-template name="date.reformat" >
                                    <xsl:with-param name="iDate" select="$file2/@mtime"/>
                                  </xsl:call-template>
                                </fo:inline>
                              </xsl:when>
                              <xsl:otherwise>
                                <xsl:call-template name="date.reformat" >
                                  <xsl:with-param name="iDate" select="$file2/@mtime2"/>
                                </xsl:call-template>
                              </xsl:otherwise>
                            </xsl:choose>
                          </fo:block>
                        </fo:table-cell>
                      </fo:table-row>
                    </xsl:for-each>
                  </xsl:if>
                </xsl:for-each>
              </fo:table-body>
            </fo:table>
          </xsl:if>
<!-- 
     ================================================================ 
                                Added/New Files
     ================================================================
-->
          <xsl:variable name="addedFiles" select="/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup"/>
          <xsl:if test="count($addedFiles/added/file) != 0">
            <fo:table id="addedFiles" table-layout="fixed" width="10in" background-color="{$table.bgcolor}" border-spacing="0pt" border="1px solid {$table.color}" margin-top="2em" margin-bottom="1em" font-size="{$table.font.size}">
              <fo:table-column column-width="proportional-column-width(3)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1.7)"/>
              <fo:table-header>
                <fo:table-row background-color="{$report.header.bgcolor}">
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="left" number-columns-spanned="5" display-align="center">
                    <fo:block font-weight="bold">New Files: These files were found in Report B but not Report A</fo:block>
                  </fo:table-cell>
                </fo:table-row>
                <fo:table-row background-color="{$table.color}" color="{$table.font.color}">
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
                    <fo:block>File Path</fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>Permissions</fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>Owner / Group ID</fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>SUID / SGID</fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
                    <fo:block>Last Modified</fo:block>
                  </fo:table-cell>
                </fo:table-row>
              </fo:table-header>
              <fo:table-body>
                <xsl:for-each select="$addedFiles">
                  <xsl:if test="count(./added/file) != 0">
                    <fo:table-row background-color="{$table.subrow.bgcolor}" color="{$table.font.color}">
                      <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center" number-columns-spanned="5">
                        <fo:block font-weight="bold">
                          <xsl:value-of select="../../@name"/>
                          <xsl:text> - </xsl:text>
                          <xsl:value-of select="@name"/>
                        </fo:block>
                      </fo:table-cell>
                    </fo:table-row>
                    <xsl:for-each select="./added/file">
                      <xsl:sort select="@path"/>
                      <xsl:variable name="rowColor">
                        <xsl:choose>
                          <xsl:when test="position() mod 2 = 0">
                            <xsl:copy-of select="$table.row.alt.bgcolor"/>
                          </xsl:when>
                          <xsl:otherwise>
                            <xsl:copy-of select="$table.bgcolor"/>
                          </xsl:otherwise>
                        </xsl:choose>
                      </xsl:variable>
                      <fo:table-row background-color="{$rowColor}" color="{$table.font.color}">
                        <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
                          <fo:block margin-left="1em">
                            <xsl:value-of select="@path"/>
                          </fo:block>
                        </fo:table-cell>
                        <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                          <fo:block>
                            <xsl:value-of select="@mode"/>
                          </fo:block>
                        </fo:table-cell>
                        <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                          <fo:block>
                            <xsl:value-of select="@uid"/>
                            <xsl:text> / </xsl:text>
                            <xsl:value-of select="@gid"/>
                          </fo:block>
                        </fo:table-cell>
                        <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                          <fo:block>
                            <xsl:value-of select="@suid"/>
                            <xsl:text> / </xsl:text>
                            <xsl:value-of select="@sgid"/>
                          </fo:block>
                        </fo:table-cell>
                        <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
                          <fo:block>
                            <xsl:call-template name="date.reformat" >
                              <xsl:with-param name="iDate" select="@mtime"/>
                            </xsl:call-template>
                          </fo:block>
                        </fo:table-cell>
                      </fo:table-row>
                    </xsl:for-each>
                  </xsl:if>
                </xsl:for-each>
              </fo:table-body>
            </fo:table>
          </xsl:if>
<!-- 
    ================================================================ 
                           Removed Files
    ================================================================
-->
          <xsl:variable name="removedFiles" select="/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup"/>
          <xsl:if test="count($removedFiles/removed/file) != 0">
            <fo:table id="filesRemoved" table-layout="fixed" width="10in" background-color="{$table.bgcolor}" border-spacing="0pt" border="1px solid {$table.color}" margin-top="2em" margin-bottom="1em" font-size="{$table.font.size}">
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-header>
                <fo:table-row background-color="{$report.header.bgcolor}">
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
                    <fo:block font-weight="bold">Non-existent Files: These files were found in Report A but not Report B</fo:block>
                  </fo:table-cell>
                </fo:table-row>
                <fo:table-row background-color="{$table.color}" color="{$table.font.color}">
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
                    <fo:block>File Path</fo:block>
                  </fo:table-cell>
                </fo:table-row>
              </fo:table-header>
              <fo:table-body>
                <xsl:for-each select="$removedFiles">
                  <xsl:if test="count(./removed/file) != 0">
                    <fo:table-row background-color="{$table.subrow.bgcolor}" color="{$table.font.color}">
                      <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
                        <fo:block font-weight="bold">
                          <xsl:value-of select="../../@name"/>
                          <xsl:text> - </xsl:text>
                          <xsl:value-of select="@name"/>
                        </fo:block>
                      </fo:table-cell>
                    </fo:table-row>
                    <xsl:for-each select="./removed/file">
                      <xsl:sort select="@path"/>
                      <xsl:variable name="rowColor">
                        <xsl:choose>
                          <xsl:when test="position() mod 2 = 0">
                            <xsl:copy-of select="$table.row.alt.bgcolor"/>
                          </xsl:when>
                          <xsl:otherwise>
                            <xsl:copy-of select="$table.bgcolor"/>
                          </xsl:otherwise>
                        </xsl:choose>
                      </xsl:variable>
                      <fo:table-row background-color="{$rowColor}" color="{$table.font.color}">
                        <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
                          <fo:block margin-left="1em">
                            <xsl:value-of select="@path"/>
                          </fo:block>
                        </fo:table-cell>
                      </fo:table-row>
                    </xsl:for-each>
                  </xsl:if>
                </xsl:for-each>
              </fo:table-body>
            </fo:table>
          </xsl:if>
<!-- ==============================================================
               Footer with Page number
-->
          <fo:block id="terminator"/>
        </fo:flow>
      </fo:page-sequence>
    </fo:root>
  </xsl:template>
</xsl:stylesheet>
