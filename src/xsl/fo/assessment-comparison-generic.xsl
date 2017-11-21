<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Assessment Comparison Report XML to FO -> PDF
     =========================================================================
-->
  <xsl:include href="common-fo.xsl"/>

  <xsl:param name="report.title">Assessment Comparison Report</xsl:param>
  <xsl:param name="header.display">true</xsl:param>
  <xsl:param name="logo.display">true</xsl:param>
  <xsl:param name="modules.display.description">false</xsl:param>

  <xsl:output method="xml" encoding="utf-8" indent="yes"/>

  <xsl:template match="/">
    <fo:root xmlns:fo="http://www.w3.org/1999/XSL/Format"
           xmlns:fox="http://xmlgraphics.apache.org/fop/extensions">

      <fo:layout-master-set>
        <fo:simple-page-master master-name="first" xsl:use-attribute-sets="page-portrait">
          <fo:region-body margin-top="0.25in" margin-bottom="0.5in"/>
          <fo:region-before extent="0.5in"/>
          <fo:region-after extent="0.5in"/>
        </fo:simple-page-master>
      </fo:layout-master-set>
<!-- 
        =======================================================================
                         PDF Document Properities (Metadata)
        =======================================================================
-->
      <fo:declarations>
        <x:xmpmeta xmlns:x="adobe:ns:meta/">
          <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">

<!-- Dublin Core properties go here -->
            <rdf:Description xmlns:dc="http://purl.org/dc/elements/1.1/" rdf:about="">
              <dc:title>
                <xsl:copy-of select="$report.title"/>
              </dc:title>
              <dc:creator>OS Lockdown</dc:creator>
              <dc:description>Assessment Comparison Report</dc:description>
            </rdf:Description>

<!-- XMP properties go here -->
            <rdf:Description xmlns:xmp="http://ns.adobe.com/xap/1.0/" rdf:about="">
              <xmp:CreatorTool>OS Lockdown</xmp:CreatorTool>
            </rdf:Description>

<!-- PDF properties go here -->
            <rdf:Description xmlns:pdf="http://ns.adobe.com/pdf/1.3/" rdf:about="">
              <pdf:Producer>OS Lockdown and Apache FOP</pdf:Producer>
              <pdf:Keywords>Assessment</pdf:Keywords>
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
      </fo:bookmark-tree>
<!-- 
    =======================================================================
                            MAIN PAGE SEUQNECE
    =======================================================================
-->
      <fo:page-sequence master-reference="first" xsl:use-attribute-sets="master-font">

<!--
    | Footer (Static)
    +-->
        <fo:static-content flow-name="xsl-region-after">
          <fo:block margin-top="0.25in" font-size="10pt" text-align-last="justify" color="#467fc5">
             OS Lockdown v<xsl:value-of select="/AssessmentReportDelta/@sbVersion"/>
            <fo:leader leader-pattern="space" />Page
            <fo:page-number/> of
            <fo:page-number-citation ref-id="terminator"/>
          </fo:block>
        </fo:static-content>

<!-- 
     =======================================================================
                               Report Header 
     =======================================================================
-->
        <fo:flow flow-name="xsl-region-body">

          <xsl:if test="$header.display = 'true'">
            <fo:table id="doctop" table-layout="fixed"
                     xsl:use-attribute-sets="table" width="7.5in" >
              <fo:table-column column-width="proportional-column-width(2.5)"/>
              <fo:table-column column-width="proportional-column-width(1.5)"/>

              <fo:table-body>
                <fo:table-row xsl:use-attribute-sets="table-row-header">
                <xsl:attribute name="background-color">#ffffff</xsl:attribute>
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
                          <xsl:text></xsl:text>
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
          <fo:table id="summaryTable" table-layout="fixed" xsl:use-attribute-sets="table" width="7.5in" >
            <fo:table-column column-width="proportional-column-width(1)"/>
            <fo:table-column column-width="proportional-column-width(2)"/>
            <fo:table-column column-width="proportional-column-width(2)"/>

            <fo:table-body>

              <fo:table-row xsl:use-attribute-sets="table-row-header">
                <fo:table-cell number-columns-spanned="2"
                               padding="2px 5px 2px 5px"
                               border-width="0pt"
                               text-align="left"
                               display-align="center">
                  <fo:block>
                    <xsl:text>Summary</xsl:text>
                  </fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="right" display-align="center">
                  <fo:block>
                    <xsl:text>Generated: </xsl:text>
                    <xsl:value-of select="substring(/AssessmentReportDelta/@created,1,20)"/>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

              <xsl:variable name="report1" select="/AssessmentReportDelta/report[1]"/>
              <xsl:variable name="report2" select="/AssessmentReportDelta/report[2]"/>
              <fo:table-row color="{$table.font.color}">
                <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px"
                       border-width="0pt" text-align="left" display-align="center">
                  <fo:block>
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
                    <xsl:when test="$report1/@hostname != $report2/@hostname">#467fc5</xsl:when>
                    <xsl:otherwise>black</xsl:otherwise>
                  </xsl:choose>
                </xsl:variable>
                <fo:table-cell color="black" padding="2px 5px 2px 5px" text-align="right" display-align="center">
                  <fo:block>Hostname</fo:block>
                </fo:table-cell>
                <fo:table-cell color="{$fontColor}" border-bottom="1px solid {$table.color}"
                       padding="2px 5px 2px 5px" border-left="1px solid {$table.color}" 
                       text-align="left" display-align="center">
                  <fo:block>
                    <xsl:value-of select="$report1/@hostname"/>
                  </fo:block>
                </fo:table-cell>
                <fo:table-cell color="{$fontColor}" border-bottom="1px solid {$table.color}"
                       padding="2px 5px 2px 5px" border-left="1px solid {$table.color}" 
                       text-align="left" display-align="center">
                  <fo:block>
                    <xsl:value-of select="$report2/@hostname"/>
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
                <fo:table-cell padding="2px 5px 2px 5px" border-bottom="1px solid {$table.color}"
                       color="{$fontColor}" border-left="1px solid {$table.color}" 
                       text-align="left" display-align="center">
                  <fo:block>
                    <xsl:choose>
                      <xsl:when test="number($report1/@distVersion) &gt;= 10 and $report1/@dist = 'redhat'">
                        <xsl:text>Fedora </xsl:text>
                      </xsl:when>
                      <xsl:when test="number($report1/@distVersion) &lt;= 10 and $report1/@dist = 'redhat'">
                        <xsl:text>Red Hat Enterprise Linux</xsl:text>
                      </xsl:when>
                      <xsl:when test="$report1/@dist = 'Red Hat'">
                        <xsl:text>Red Hat Enterprise Linux</xsl:text>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:value-of select="$report1/@dist"/>
                        <xsl:text></xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                    <xsl:text> </xsl:text>
                    <xsl:value-of select="$report1/@distVersion"/>
                  </fo:block>
                </fo:table-cell>

                <fo:table-cell padding="2px 5px 2px 5px" color="{$fontColor}" border-bottom="1px solid {$table.color}" border-left="1px solid {$table.color}" text-align="left" display-align="center">
                  <fo:block>
                    <xsl:choose>
                      <xsl:when test="number($report2/@distVersion) &gt;= 10 and $report2/@dist = 'redhat'">
                        <xsl:text>Fedora </xsl:text>
                      </xsl:when>
                      <xsl:when test="number($report2/@distVersion) &lt;= 10 and $report2/@dist = 'redhat'">
                        <xsl:text>Red Hat Enterprise Linux</xsl:text>
                      </xsl:when>
                      <xsl:when test="$report2/@dist = 'Red Hat'">
                        <xsl:text>Red Hat Enterprise Linux</xsl:text>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:value-of select="$report2/@dist"/>
                        <xsl:text></xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                    <xsl:text> </xsl:text>
                    <xsl:value-of select="$report2/@distVersion"/>
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

<!-- Profile Names -->
              <fo:table-row color="{$table.font.color}" font-size="{$table.font.size}">
                <fo:table-cell padding="2px 5px 2px 5px" text-align="right" display-align="center">
                  <fo:block>
          Profile
                  </fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px" border-bottom="1px solid {$table.color}" border-left="1px solid {$table.color}" text-align="left" display-align="center">
                  <fo:block>
                    <xsl:value-of select="$report1/@profile"/>
                  </fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px" border-bottom="1px solid {$table.color}" border-left="1px solid {$table.color}" text-align="left" display-align="center">
                  <fo:block>
                    <xsl:value-of select="$report2/@profile"/>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

<!-- Statistics -->
              <xsl:variable name="totalMods" select="count(/AssessmentReportDelta/*/module)"/>
              <xsl:variable name="xMods" select="count(/AssessmentReportDelta/removed/module) + count(/AssessmentReportDelta/added/module)"/>
              <xsl:variable name="changedMods" select="count(/AssessmentReportDelta/changed/module)"/>
              <xsl:variable name="unchangedMods" select="count(/AssessmentReportDelta/unchanged/module)"/>

              <fo:table-row color="{$table.font.color}" font-size="{$table.font.size}">
                <fo:table-cell padding="2px 5px 2px 5px" text-align="right" display-align="center">
                  <fo:block>Results</fo:block>
                </fo:table-cell>

                <fo:table-cell padding="2px 5px 2px 5px" border-bottom="1px solid {$table.color}" border-left="1px solid {$table.color}" text-align="left" display-align="center" number-columns-spanned="2">
                  <fo:block>
                    <xsl:value-of select="$totalMods"/>
                    <xsl:text> total modules (</xsl:text>
                    <xsl:value-of select="$changedMods"/>
                    <xsl:choose>
                      <xsl:when test="$changedMods = 1 ">
                        <xsl:text> module with differing results</xsl:text>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text> modules with differing results</xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                    <xsl:text>, </xsl:text>
                    <xsl:value-of select="$unchangedMods"/>
                    <xsl:choose>
                      <xsl:when test="$unchangedMods = 1 ">
                        <xsl:text> module with same result</xsl:text>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text> modules with same result</xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                    <xsl:text>, </xsl:text>
                    <xsl:value-of select="$xMods"/>
                    <xsl:choose>
                      <xsl:when test="$xMods = 1 ">
                        <xsl:text> module present in only one report</xsl:text>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text> modules present in only one report</xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                    <xsl:text>)</xsl:text>
                  </fo:block>
                </fo:table-cell>

              </fo:table-row>
            </fo:table-body>
          </fo:table>
<!-- 
     ================================================================ 
                            Changed Modules
     ================================================================
-->
          <xsl:if test="count(/AssessmentReportDelta/changed/module) != 0">
            <fo:table id="changedModules" table-layout="fixed" width="7.5in" xsl:use-attribute-sets="table">
              <fo:table-column column-width="proportional-column-width(4)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>

              <fo:table-header>
                <fo:table-row xsl:use-attribute-sets="table-row-header">
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="left" number-columns-spanned="4" display-align="center">
                    <fo:block font-weight="bold">
                      <xsl:text>Modules with differing results</xsl:text>
                    </fo:block>
                  </fo:table-cell>
                </fo:table-row>
                <fo:table-row xsl:use-attribute-sets="table-row-subheader">
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
                    <fo:block>
                      <xsl:text>Module Name</xsl:text>
                    </fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>
                      <xsl:text>Severity</xsl:text>
                    </fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>
                      <xsl:text>Result A</xsl:text>
                    </fo:block>
                  </fo:table-cell>
                  <fo:table-cell  padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>
                      <xsl:text>Result B</xsl:text>
                    </fo:block>
                  </fo:table-cell>
                </fo:table-row>
              </fo:table-header>

              <fo:table-body>
                <xsl:for-each select="/AssessmentReportDelta/changed/module">
                  <xsl:sort select="@name"/>
                  <fo:table-row border-bottom="1px solid {$table.color}">
                    <fo:table-cell padding="2px 5px 2px 5px" text-align="left">
                      <fo:block>
                        <xsl:value-of select="@name"/>
                      </fo:block>
                      <xsl:if test="$modules.display.description != 'false'">
                        <fo:block font-size="10pt" font-style="italic" margin-left="2em" margin-bottom="1em">
                          <xsl:value-of select="./description"/>
                        </fo:block>
                        <xsl:call-template name="module.compliancy.list">
                          <xsl:with-param name="compliancy" select="./compliancy"/>
                        </xsl:call-template>
                      </xsl:if>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <fo:block>
                        <xsl:value-of select="@severity"/>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <xsl:call-template name="module.result">
                        <xsl:with-param name="results" select="@resultsA"/>
                      </xsl:call-template>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <xsl:call-template name="module.result">
                        <xsl:with-param name="results" select="@resultsB"/>
                      </xsl:call-template>
                    </fo:table-cell>
                  </fo:table-row>
                </xsl:for-each>
              </fo:table-body>
            </fo:table>
          </xsl:if>

<!-- ============================================================== -->
          <xsl:variable name="delModules" select="/AssessmentReportDelta/removed/module"/>
          <xsl:variable name="addModules" select="/AssessmentReportDelta/added/module"/>

          <xsl:if test="count($delModules) != 0 or count($addModules) != 0">
            <fo:table id="delModules" table-layout="fixed" width="7.5in" xsl:use-attribute-sets="table">
              <fo:table-column column-width="proportional-column-width(4)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>

              <fo:table-header>
                <fo:table-row xsl:use-attribute-sets="table-row-header">
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="left" number-columns-spanned="4" display-align="center">
                    <fo:block font-weight="bold">
                      <xsl:text>Modules present in only one report</xsl:text>
                    </fo:block>
                  </fo:table-cell>
                </fo:table-row>
                <fo:table-row xsl:use-attribute-sets="table-row-subheader">
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
                    <fo:block>
                      <xsl:text>Module Name</xsl:text>
                    </fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>
                      <xsl:text>Severity</xsl:text>
                    </fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>
                      <xsl:text>Result A</xsl:text>
                    </fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>
                      <xsl:text>Result B</xsl:text>
                    </fo:block>
                  </fo:table-cell>
                </fo:table-row>
              </fo:table-header>

              <fo:table-body>
                <xsl:for-each select="$delModules">
                  <xsl:sort select="@name"/>
                  <fo:table-row border-bottom="1px solid {$table.color}">
                    <fo:table-cell padding="2px 5px 2px 5px" text-align="left">
                      <fo:block>
                        <xsl:value-of select="@name"/>
                      </fo:block>
                      <xsl:if test="$modules.display.description != 'false'">
                        <fo:block font-size="10pt" font-style="italic" margin-left="2em" margin-bottom="1em">
                          <xsl:value-of select="./description"/>
                        </fo:block>
                        <xsl:call-template name="module.compliancy.list">
                          <xsl:with-param name="compliancy" select="./compliancy"/>
                        </xsl:call-template>
                      </xsl:if>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <fo:block>
                        <xsl:value-of select="@severity"/>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <xsl:call-template name="module.result">
                        <xsl:with-param name="results" select="@results"/>
                      </xsl:call-template>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <fo:block>-</fo:block>
                    </fo:table-cell>
                  </fo:table-row>
                </xsl:for-each>
                <xsl:for-each select="$addModules">
                  <xsl:sort select="@name"/>
                  <fo:table-row border-bottom="1px solid {$table.color}">
                    <fo:table-cell padding="2px 5px 2px 5px" text-align="left">
                      <fo:block>
                        <xsl:value-of select="@name"/>
                      </fo:block>
                      <xsl:if test="$modules.display.description != 'false'">
                        <fo:block font-size="10pt" font-style="italic" margin-left="2em" margin-bottom="1em">
                          <xsl:value-of select="./description"/>
                        </fo:block>
                        <xsl:call-template name="module.compliancy.list">
                          <xsl:with-param name="compliancy" select="./compliancy"/>
                        </xsl:call-template>
                      </xsl:if>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <fo:block>
                        <xsl:value-of select="@severity"/>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <fo:block>-</fo:block>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <xsl:call-template name="module.result">
                        <xsl:with-param name="results" select="@results"/>
                      </xsl:call-template>
                    </fo:table-cell>
                  </fo:table-row>
                </xsl:for-each>
              </fo:table-body>
            </fo:table>
          </xsl:if>

<!-- ============================================================== -->
          <xsl:variable name="unmodules" select="/AssessmentReportDelta/unchanged/module"/>
          <xsl:if test="count($unmodules) != 0">
            <fo:table id="unModules" table-layout="fixed" width="7.5in" xsl:use-attribute-sets="table">
              <fo:table-column column-width="proportional-column-width(4)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>

              <fo:table-header>
                <fo:table-row xsl:use-attribute-sets="table-row-header">
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="left" number-columns-spanned="2" display-align="center">
                    <fo:block font-weight="bold">
                      <xsl:text>Modules with same results</xsl:text>
                    </fo:block>
                  </fo:table-cell>
                </fo:table-row>
                <fo:table-row xsl:use-attribute-sets="table-row-subheader">
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
                    <fo:block>
                      <xsl:text>Module Name</xsl:text>
                    </fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>Severity</fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 5px 2px 5px" text-align="center" display-align="center">
                    <fo:block>Results</fo:block>
                  </fo:table-cell>
                </fo:table-row>
              </fo:table-header>

              <fo:table-body>

                <xsl:for-each select="$unmodules">
                  <xsl:sort select="@name"/>
                  <fo:table-row border-bottom="1px solid {$table.color}">
                    <fo:table-cell padding="2px 5px 2px 5px" text-align="left">
                      <fo:block>
                        <xsl:value-of select="@name"/>
                      </fo:block>
                      <xsl:if test="$modules.display.description != 'false'">
                        <fo:block font-size="10pt" font-style="italic" margin-left="2em" margin-bottom="1em">
                          <xsl:value-of select="./description"/>
                        </fo:block>
                        <xsl:call-template name="module.compliancy.list">
                          <xsl:with-param name="compliancy" select="./compliancy"/>
                        </xsl:call-template>
                      </xsl:if>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <fo:block>
                        <xsl:value-of select="@severity"/>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
                      <xsl:call-template name="module.result">
                        <xsl:with-param name="results" select="@results"/>
                      </xsl:call-template>
                    </fo:table-cell>
                  </fo:table-row>
                </xsl:for-each>
              </fo:table-body>
            </fo:table>
          </xsl:if>

<!-- ==============================================================
                     Footer with Page number 
     ============================================================== -->
          <fo:block id="terminator"/>
        </fo:flow>
      </fo:page-sequence>
    </fo:root>

  </xsl:template>
</xsl:stylesheet>
