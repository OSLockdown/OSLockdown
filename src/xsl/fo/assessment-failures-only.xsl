<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: assessment-failures-only.xsl 23917 2017-03-07 15:44:30Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Failures Only Assessment Report XML to FO -> PDF
     =========================================================================
-->
  <xsl:include href="common-fo.xsl"/>
<!--
   Report Parameter Definitions:
     report.title     : Report title to be used in header 
     header.display   : if false, do not display header
     logo.display     : if false, do not display logo in header

     module.display.description : if false, do not show module description and compliancy
-->
  <xsl:param name="report.title">Failed Modules Report</xsl:param>
  <xsl:param name="header.display">true</xsl:param>
  <xsl:param name="logo.display">true</xsl:param>
  <xsl:param name="modules.display.description">true</xsl:param>
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
              <dc:description>Failed Modules Report</dc:description>
            </rdf:Description>
<!-- XMP properties go here -->
            <rdf:Description xmlns:xmp="http://ns.adobe.com/xap/1.0/" rdf:about="">
              <xmp:CreatorTool>OS Lockdown</xmp:CreatorTool>
            </rdf:Description>
<!-- PDF properties go here -->
            <rdf:Description xmlns:pdf="http://ns.adobe.com/pdf/1.3/" rdf:about="">
              <pdf:Producer>OS Lockdown and Apache FOP</pdf:Producer>
              <pdf:Keywords>Security</pdf:Keywords>
            </rdf:Description>
          </rdf:RDF>
        </x:xmpmeta>
      </fo:declarations>
<!-- 
    =======================================================================
          PDF Bookmarks / Navigation
    =======================================================================
-->
 <!--
      <fo:bookmark-tree>
        <fo:bookmark internal-destination="summaryTable">
          <fo:bookmark-title>Summary</fo:bookmark-title>
        </fo:bookmark>
        <xsl:if test="count(/AssessmentReport/modules/module[@severity='High']) != 0">
          <fo:bookmark internal-destination="modulesHigh">
            <fo:bookmark-title>High Risk</fo:bookmark-title>
          </fo:bookmark>
        </xsl:if>
        <xsl:if test="count(/AssessmentReport/modules/module[@severity='Medium']) != 0">
          <fo:bookmark internal-destination="modulesMedium">
            <fo:bookmark-title>Medium Risk</fo:bookmark-title>
          </fo:bookmark>
        </xsl:if>
        <xsl:if test="count(/AssessmentReport/modules/module[@severity='Low']) != 0">
          <fo:bookmark internal-destination="modulesLow">
            <fo:bookmark-title>Low Risk</fo:bookmark-title>
          </fo:bookmark>
        </xsl:if>
      </fo:bookmark-tree>
    -->
      <fo:page-sequence master-reference="first" xsl:use-attribute-sets="master-font">
<!-- 
    =======================================================================
          Report Footer (Static)
    =======================================================================
-->
<!--
    | Footer (Static)
    +-->
        <fo:static-content flow-name="xsl-region-after">
          <fo:block margin-top="0.25in" font-size="10pt" text-align-last="justify" color="#467fc5">
              <xsl:text>OS Lockdown v</xsl:text>
              <xsl:value-of select="/AssessmentReport/@sbVersion"/>
            <fo:leader leader-pattern="space" />
            <xsl:text>Page </xsl:text>
            <fo:page-number/>
            <xsl:text> of </xsl:text>
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
            <fo:table id="doctop" table-layout="fixed" xsl:use-attribute-sets="table" width="7.5in" >
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
                          <fo:external-graphic src="url({$image.header.logo})" content-width="50%" />
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
          <fo:table id="summaryTable" table-layout="fixed" width="7.5in" xsl:use-attribute-sets="table">
            <fo:table-column column-width="proportional-column-width(1)"/>
            <fo:table-column column-width="proportional-column-width(3)"/>

            <fo:table-body>
              <fo:table-row xsl:use-attribute-sets="table-row-header">
                <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
                  <fo:block font-weight="bold">Summary</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="right" display-align="center">
                  <fo:block font-weight="bold">
                    <xsl:text>Created: </xsl:text>
                    <xsl:value-of select="/AssessmentReport/report/@created"/>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

<!-- Hostname -->
              <fo:table-row color="black" border-bottom="1px solid {$table.color}" font-size="{$table.font.size}">
                <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
                  <fo:block>Hostname</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
                  <fo:block>
                    <xsl:value-of select="/AssessmentReport/report/@hostname"/>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

<!-- Operating System-->
              <fo:table-row color="{$table.font.color}" border-bottom="1px solid {$table.color}">
                <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
                  <fo:block>Operating System</fo:block>
                </fo:table-cell>

                <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
                  <xsl:variable name="distVersion" select="/AssessmentReport/report/@distVersion"/>
                  <xsl:variable name="dist" select="/AssessmentReport/report/@dist"/>
                  <fo:block>
                    <xsl:choose>
                      <xsl:when test="$distVersion &gt;= 10 and $dist = 'redhat'">
                        <xsl:text>Fedora </xsl:text>
                      </xsl:when>
                      <xsl:when test="number($distVersion) &lt;= 10 and $dist = 'redhat'">
                        <xsl:text>Red Hat Enterprise Linux</xsl:text>
                      </xsl:when>
                      <xsl:when test="$dist = 'Red Hat'">
                        <xsl:text>Red Hat Enterprise Linux</xsl:text>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:value-of select="$dist"/>
                        <xsl:text></xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                    <xsl:text> </xsl:text>
                    <xsl:value-of select="$distVersion"/>
                  </fo:block>
                </fo:table-cell>
                
              </fo:table-row>

<!-- Profile Information -->
              <fo:table-row color="black" border-bottom="1px solid {$table.color}">
                <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right">
                  <fo:block>Profile</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
                  <fo:block>
                    <xsl:value-of select="/AssessmentReport/report/@profile"/>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

<!-- Report Results -->
              <fo:table-row color="black" border-bottom="1px solid {$table.color}">
                <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right">
                  <fo:block>Results</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
                  <fo:block>
                    <fo:table table-layout="fixed" width="100%">
                      <fo:table-column column-width="proportional-column-width(1)"/>
                      <fo:table-column column-width="proportional-column-width(1)"/>
                      <fo:table-column column-width="proportional-column-width(1)"/>
                      <fo:table-column column-width="proportional-column-width(1)"/>
                      <fo:table-column column-width="proportional-column-width(1)"/>
                      <fo:table-body>
                        <fo:table-row border-bottom="1px solid {$table.color}">
                          <fo:table-cell text-align="center">
                            <fo:block>
                              <xsl:text> </xsl:text>
                            </fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block>Failed</fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block>Passed</fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block>N/A</fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block>Total</fo:block>
                          </fo:table-cell>
                        </fo:table-row>

<!-- High Risk -->
                        <fo:table-row>
                          <fo:table-cell text-align="right">
                            <fo:block>High Risk</fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block>
                              <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='High' and @results='Fail'])"/>
                            </fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block>
                              <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='High' and @results='Pass'])"/>
                            </fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block>
                              <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='High' and @results != 'Pass' and @results != 'Fail'])"/>
                            </fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block>
                              <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='High'])"/>
                            </fo:block>
                          </fo:table-cell>
                        </fo:table-row>

<!-- Medium Risk -->
                        <fo:table-row>
                          <fo:table-cell text-align="right">
                            <fo:block>Medium Risk</fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block>
                              <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='Medium' and @results='Fail'])"/>
                            </fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block>
                              <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='Medium' and @results='Pass'])"/>
                            </fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block>
                              <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='Medium' and @results != 'Pass' and @results != 'Fail'])"/>
                            </fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block>
                              <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='Medium'])"/>
                            </fo:block>
                          </fo:table-cell>
                        </fo:table-row>

<!-- Low Risk -->
                        <fo:table-row border-bottom="1px solid {$table.color}">
                          <fo:table-cell text-align="right">
                            <fo:block>Low Risk</fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block>
                              <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='Low' and @results='Fail'])"/>
                            </fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block>
                              <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='Low' and @results='Pass'])"/>
                            </fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block>
                              <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='Low' and @results != 'Pass' and @results != 'Fail'])"/>
                            </fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block>
                              <xsl:value-of select="count(/AssessmentReport/modules/module[@severity='Low'])"/>
                            </fo:block>
                          </fo:table-cell>
                        </fo:table-row>

<!-- Totals -->
                        <xsl:variable name="totalFail" select="count(/AssessmentReport/modules/module[@results='Fail'])"/>
                        <xsl:variable name="totalPass" select="count(/AssessmentReport/modules/module[@results='Pass'])"/>
                        <xsl:variable name="totalOther" select="count(/AssessmentReport/modules/module[@results !='Pass' and @results !='Fail'])"/>
                        <fo:table-row>
                          <fo:table-cell text-align="right">
                            <fo:block>Totals</fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block color="red">
                              <xsl:value-of select="count(/AssessmentReport/modules/module[@results='Fail'])"/>
                              <xsl:text> (</xsl:text>
                              <xsl:value-of select="round(($totalFail div ($totalFail + $totalPass + $totalOther)) * 100)"/>
                              <xsl:text>%)</xsl:text>
                            </fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block color="green">
                              <xsl:value-of select="count(/AssessmentReport/modules/module[@results='Pass'])"/>
                              <xsl:text> (</xsl:text>
                              <xsl:value-of select="round(($totalPass div ($totalFail + $totalPass + $totalOther)) * 100)"/>
                              <xsl:text>%)</xsl:text>
                            </fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block color="#467fc5">
                              <xsl:value-of select="count(/AssessmentReport/modules/module[@results != 'Pass' and @results != 'Fail'])"/>
                              <xsl:text> (</xsl:text>
                              <xsl:value-of select="round(($totalOther div ($totalFail + $totalPass + $totalOther)) * 100)"/>
                              <xsl:text>%)</xsl:text>
                            </fo:block>
                          </fo:table-cell>
                          <fo:table-cell text-align="center">
                            <fo:block color="black">
                              <xsl:value-of select="count(/AssessmentReport/modules/module)"/>
                            </fo:block>
                          </fo:table-cell>
                        </fo:table-row>
                      </fo:table-body>
                    </fo:table>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>
            </fo:table-body>
          </fo:table>
<!-- 
     =======================================================================
          Results of High Risk Modules (Table)
     =======================================================================
-->
          <xsl:if test="count(/AssessmentReport/modules/module[@severity='High' and @results = 'Fail']) != 0">
            <fo:table id="modulesHigh" table-layout="fixed" width="7.5in" xsl:use-attribute-sets="table">
              <fo:table-column column-width="proportional-column-width(5)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-header>
                <fo:table-row xsl:use-attribute-sets="table-row-header">
                  <fo:table-cell number-columns-spanned="2"
                                 padding="2px 5px 2px 5px"
                                 border-width="0pt"
                                 text-align="left"
                                 display-align="center">
                    <fo:block>High Risk</fo:block>
                  </fo:table-cell>
                </fo:table-row>
              </fo:table-header>

              <fo:table-body>
                <xsl:for-each select="/AssessmentReport/modules/module[@results = 'Fail' and @severity='High']">
                  <xsl:sort select="@name"/>
                  <fo:table-row background-color="{$table.bgcolor}" color="black" border-bottom="1px solid {$table.color}">
                    <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
                      <fo:block font-weight="bold">
                        <xsl:value-of select="@name"/>
                      </fo:block>

                      <xsl:if test="$modules.display.description != 'false'">
                        <fo:block margin-top="0.5em" margin-left="2em" margin-bottom="1em" font-size="9pt">
                          <fo:block font-style="italic" margin-bottom="1em">
                            <xsl:value-of select="./description"/>
                          </fo:block>

                          <xsl:call-template name="module.message.details" >
                            <xsl:with-param name="details" select="./details"/>
                          </xsl:call-template>

                          <fo:block margin-top="1em" margin-bottom="0.5em"
                                  text-decoration="underline">Compliancy:
                          </fo:block>
                          <xsl:call-template name="module.compliancy.list2">
                            <xsl:with-param name="compliancy" select="./compliancy"/>
                          </xsl:call-template>

                        </fo:block>
                      </xsl:if>
                    </fo:table-cell>

                    <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="center">
                      <xsl:call-template name="module.result">
                        <xsl:with-param name="results" select="@results"/>
                      </xsl:call-template>
                    </fo:table-cell>
                  </fo:table-row>
                </xsl:for-each>
              </fo:table-body>
            </fo:table>
          </xsl:if>
<!-- 
    =======================================================================
          Results of Medium Risk Modules (Table)
    =======================================================================
-->
          <xsl:if test="count(/AssessmentReport/modules/module[@severity='Medium' and @results = 'Fail']) != 0">
            <fo:table id="modulesMedium" table-layout="fixed" width="7.5in" xsl:use-attribute-sets="table">
              <fo:table-column column-width="proportional-column-width(5)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              
              <fo:table-header>
                <fo:table-row xsl:use-attribute-sets="table-row-header">
                  <fo:table-cell padding="2px 5px 2px 5px" 
                                 number-columns-spanned="2"
                                 border-width="0pt"
                                 text-align="left"
                                 display-align="center">
                    <fo:block>Medium Risk</fo:block>
                  </fo:table-cell>
                </fo:table-row>
              </fo:table-header>

              <fo:table-body>
                <xsl:for-each select="/AssessmentReport/modules/module[@results = 'Fail' and @severity='Medium']">
                  <xsl:sort select="@name"/>
                  <fo:table-row background-color="{$table.bgcolor}" color="black" border-bottom="1px solid {$table.color}">
                    <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
                      <fo:block font-weight="bold">
                        <xsl:value-of select="@name"/>
                      </fo:block>
                      <xsl:if test="$modules.display.description != 'false'">
                        <fo:block margin-top="0.5em" margin-left="2em" margin-bottom="1em" font-size="9pt">
                          <fo:block font-style="italic" margin-bottom="1em">
                            <xsl:value-of select="./description"/>
                          </fo:block>

                          <xsl:call-template name="module.message.details" >
                            <xsl:with-param name="details" select="./details"/>
                          </xsl:call-template>

                          <fo:block margin-top="1em" margin-bottom="0.5em"
                                  text-decoration="underline">Compliancy:
                          </fo:block>
                          <xsl:call-template name="module.compliancy.list2">
                            <xsl:with-param name="compliancy" select="./compliancy"/>
                          </xsl:call-template>

                        </fo:block>
                      </xsl:if>
                    </fo:table-cell>
                    <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="center">
                      <xsl:call-template name="module.result">
                        <xsl:with-param name="results" select="@results"/>
                      </xsl:call-template>
                    </fo:table-cell>
                  </fo:table-row>
                </xsl:for-each>
              </fo:table-body>
            </fo:table>
          </xsl:if>
<!-- 
    =======================================================================
                     Results of Low Risk Modules (Table)
    =======================================================================
-->
          <xsl:if test="count(/AssessmentReport/modules/module[@severity='Low' and @results = 'Fail']) != 0">
            <fo:table id="modulesLow" table-layout="fixed" width="7.5in" xsl:use-attribute-sets="table">
              <fo:table-column column-width="proportional-column-width(5)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>

              <fo:table-header>
                <fo:table-row xsl:use-attribute-sets="table-row-header">
                  <fo:table-cell padding="2px 5px 2px 5px" 
                                 number-columns-spanned="2"
                                 border-width="0pt"
                                 text-align="left"
                                 display-align="center">
                    <fo:block>Low Risk</fo:block>
                  </fo:table-cell>
                </fo:table-row>
              </fo:table-header>

              <fo:table-body>
                <xsl:for-each select="/AssessmentReport/modules/module[@severity='Low' and @results = 'Fail']">
                  <xsl:sort select="@name"/>
                  <fo:table-row background-color="{$table.bgcolor}" color="{$table.font.color}" border-bottom="1px solid {$table.color}">
                    <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
                      <fo:block font-weight="bold">
                        <xsl:value-of select="@name"/>
                      </fo:block>
                      
                      <xsl:if test="$modules.display.description != 'false'">
                        <fo:block margin-top="0.5em" margin-left="2em" margin-bottom="1em" font-size="9pt">
                          <fo:block font-style="italic" margin-bottom="1em">
                            <xsl:value-of select="./description"/>
                          </fo:block>

                          <xsl:call-template name="module.message.details" >
                            <xsl:with-param name="details" select="./details"/>
                          </xsl:call-template>

                          <fo:block margin-top="1em" margin-bottom="0.5em"
                                  text-decoration="underline">Compliancy:
                          </fo:block>
                          <xsl:call-template name="module.compliancy.list2">
                            <xsl:with-param name="compliancy" select="./compliancy"/>
                          </xsl:call-template>

                        </fo:block>
                      </xsl:if>
                    </fo:table-cell>
                    <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="center">
                      <xsl:call-template name="module.result">
                        <xsl:with-param name="results" select="@results"/>
                      </xsl:call-template>
                    </fo:table-cell>
                  </fo:table-row>
                </xsl:for-each>
              </fo:table-body>

            </fo:table>
          </xsl:if>
<!-- ===============================================================
               Footer with Page number -->
          <fo:block id="terminator"/>
        </fo:flow>
      </fo:page-sequence>
    </fo:root>
  </xsl:template>
</xsl:stylesheet>
