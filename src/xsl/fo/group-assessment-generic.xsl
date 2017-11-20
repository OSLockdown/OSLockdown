<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: group-assessment-generic.xsl 23917 2017-03-07 15:44:30Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Group Assessment Report XML to FO -> PDF
     =========================================================================
-->
  <xsl:include href="common-fo.xsl"/>
<!--
   Report Parameter Definitions:
     report.title     : Report title to be used in header 
     header.display   : if false, do not display header
     logo.display     : if false, do not display logo in header
-->
  <xsl:param name="report.title">Group Assessment Report</xsl:param>
  <xsl:param name="header.display">true</xsl:param>
  <xsl:param name="logo.display">true</xsl:param>


  <xsl:output method="xml" encoding="utf-8" indent="yes"/>

  <xsl:template match="/">
    <xsl:variable name="groupProfile">
      <xsl:choose>
        <xsl:when test="/GroupAssessmentReport/@profile">
          <xsl:value-of select="/GroupAssessmentReport/@profile" />
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="/GroupAssessmentReport/reports/report[1]/@profile" />
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    
    <fo:root xmlns:fo="http://www.w3.org/1999/XSL/Format"
           xmlns:fox="http://xmlgraphics.apache.org/fop/extensions">

      <fo:layout-master-set>
        <fo:simple-page-master master-name="first" xsl:use-attribute-sets="page-landscape">
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
              <dc:description>
                <xsl:copy-of select="$report.title"/>
              </dc:description>
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
                          MAIN PAGE SEUQNECE
    =======================================================================
-->
      <fo:page-sequence master-reference="first" xsl:use-attribute-sets="master-font">
<!--
    | Footer (Static)
    +-->
        <fo:static-content flow-name="xsl-region-after">
          <fo:block xsl:use-attribute-sets="footer-block" text-align-last="justify">
              <xsl:text>OS Lockdown v</xsl:text>
              <xsl:value-of select="/GroupAssessmentReport/@sbVersion"/>
            <fo:leader leader-pattern="space" />Page
            <fo:page-number/> of
            <fo:page-number-citation ref-id="terminator"/>
          </fo:block>
        </fo:static-content>
<!--
    | Begin non-static elements (flow)
    +-->
        <fo:flow flow-name="xsl-region-body">
<!-- 
    =======================================================================
                      Report Header Banner (First Page)
    =======================================================================
-->
          <xsl:if test="$header.display = 'true'">
            <fo:table id="doctop" xsl:use-attribute-sets="table" width="10in">
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
                    <fo:block text-align="right" margin-right="2em" padding="5pt">
                      <xsl:choose>
                        <xsl:when test="$logo.display = 'true'">
                          <fo:external-graphic content-width="50%" src="url({$image.header.logo})"/>
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
          <xsl:comment> Summary Table </xsl:comment>
          <fo:table id="summaryTable"  xsl:use-attribute-sets="table" width="10in">
            <fo:table-column column-width="proportional-column-width(1)"/>
            <fo:table-column column-width="proportional-column-width(5)"/>
            <fo:table-body>
              <fo:table-row xsl:use-attribute-sets="table-row-header">
                <fo:table-cell padding="2px 5px 2px 5px"
                               border-width="0pt"
                               text-align="left"
                               display-align="center">
                  <fo:block>Summary</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 2px 2px 2px"
                               border-width="0pt"
                               text-align="right"
                               display-align="center">
                  <fo:block>
                    Generated:
                    <xsl:text> </xsl:text>
                    <xsl:value-of select="substring(/GroupAssessmentReport/@created,1,20)"/>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

         <!-- Group Name -->
              <fo:table-row color="black" border-bottom="1px solid {$table.color}">
                <fo:table-cell padding="2px 2px 2px 2px" border-right="1px solid {$table.color}"
                               text-align="right" display-align="center">
                  <fo:block>Group Name</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt"
                               text-align="left" display-align="center"  border-right="1px solid {$table.color}">
                  <fo:block>
                    <xsl:value-of select="/GroupAssessmentReport/@groupName"/>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

              <xsl:variable name="totalReports" select="count(/GroupAssessmentReport/reports/report)"/>
              <xsl:variable name="badProfiles" select="count(/GroupAssessmentReport/reports/report[@profile != $groupProfile])"/>
              <xsl:variable name="missingReports" select="count(/GroupAssessmentReport/missing/client)"/>
              <xsl:variable name="totalClients" select="$totalReports + $missingReports"/>
              
         <!-- Group Size -->
              <fo:table-row border-bottom="1px solid {$table.color}">
                <fo:table-cell padding="2px 2px 2px 2px" border-right="1px solid {$table.color}"
                               text-align="right" display-align="center">
                  <fo:block>Group Size</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt"
                               text-align="left" display-align="center"  border-right="1px solid {$table.color}">
                  <fo:block>
                    <xsl:value-of select="$totalClients" />
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

           <!-- Group Profile -->
              <fo:table-row border-bottom="1px solid {$table.color}">
                <fo:table-cell padding="2px 2px 2px 2px" border-right="1px solid {$table.color}"
                               text-align="right" display-align="center">
                  <fo:block>Profile</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt"
                               text-align="left" display-align="center"  border-right="1px solid {$table.color}">
                  <fo:block>
                    <xsl:value-of select="$groupProfile" />
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

           <!-- Reports -->
              <xsl:comment> Report Inventory </xsl:comment>
              <fo:table-row border-bottom="1px solid {$table.color}">
                <fo:table-cell padding="2px 2px 2px 2px" border-right="1px solid {$table.color}"
                               text-align="right">
                  <fo:block>Reports</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt"
                               text-align="left" display-align="center"  border-right="1px solid {$table.color}">
                  <fo:block>
                    <xsl:if test="$totalReports != 0">
                      <fo:block>
                        <xsl:text>Assembled from </xsl:text>
                        <xsl:value-of select="$totalReports"/>
                        <xsl:text> of </xsl:text>
                        <xsl:value-of select="$totalClients"/>
                        <xsl:text> client reports.</xsl:text>
                      </fo:block>
                    </xsl:if>

                    <!-- Missing Reports, if any -->
                    <xsl:if test="$missingReports != 0">
                      <fo:block margin-top="1em" text-decoration="underline"
                                font-weight="bold">Unavailable Reports:
                      </fo:block>
                      <fo:list-block margin-left="0.5em"
                                   margin-bottom="0.5em"
                                   margin-top="0.5em"
                                   provisional-distance-between-starts="10pt"
                                   provisional-label-separation="3pt">
                        <xsl:for-each select="/GroupAssessmentReport/missing/client">
                          <xsl:sort select="@name"/>
                          <fo:list-item>
                            <fo:list-item-label end-indent="label-end()">
                              <fo:block>&#x2022;</fo:block>
                            </fo:list-item-label>
                            <fo:list-item-body start-indent="body-start()">
                              <fo:block>
                                <xsl:value-of select="@hostname"/>
                                <xsl:text> (</xsl:text>
                                <fo:inline font-style="italic">
                                  <xsl:value-of select="@reason"/>
                                </fo:inline>
                                <xsl:text>)</xsl:text>
                              </fo:block>
                            </fo:list-item-body>
                          </fo:list-item>
                        </xsl:for-each>
                      </fo:list-block>
                    </xsl:if>

                    <!-- Bad Profiles -->
                    <xsl:if test="$badProfiles != 0 ">
                      <fo:block text-decoration="underline" margin-top="1em"
                                font-weight="bold">Warnings:
                      </fo:block>
                      <fo:list-block margin-left="0.5em"
                                   margin-bottom="0.5em"
                                   margin-top="0.5em"
                                   provisional-distance-between-starts="10pt"
                                   provisional-label-separation="3pt">
                        <xsl:for-each select="/GroupAssessmentReport/reports/report[@profile != $groupProfile]">
                          <fo:list-item>
                            <fo:list-item-label end-indent="label-end()">
                              <fo:block>&#x2022;</fo:block>
                            </fo:list-item-label>
                            <fo:list-item-body start-indent="body-start()">
                              <fo:block>
                                <xsl:value-of select="@hostname"/>
                                <xsl:text> (</xsl:text>
                                <fo:inline font-style="italic">Different profile: "
                                  <xsl:value-of select="@profile"/>"
                                </fo:inline>
                                <xsl:text>)</xsl:text>
                              </fo:block>
                            </fo:list-item-body>
                          </fo:list-item>
                        </xsl:for-each>
                      </fo:list-block>
                    </xsl:if>

                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

            </fo:table-body>
          </fo:table>
<!-- 
     =======================================================================
          List all clients which have a failure or error
     =======================================================================
-->
          <xsl:if test="count(/GroupAssessmentReport/modules/module/clients/client[@results='Fail' or @results='Error']) != 0">
            <xsl:comment> Table of Clients </xsl:comment>
            <fo:table id="listFailedClients" xsl:use-attribute-sets="table" width="10in" >
              <fo:table-column column-width="proportional-column-width(4)"/>
              <fo:table-column column-width="proportional-column-width(3)"/>
              <fo:table-column column-width="proportional-column-width(1.5)"/>
              <fo:table-column column-width="proportional-column-width(0.7)"/>
              <fo:table-column column-width="proportional-column-width(0.7)"/>
              <fo:table-column column-width="proportional-column-width(1.2)"/>

             <!-- Table Header -->
              <fo:table-header>
                <fo:table-row xsl:use-attribute-sets="table-row-header">
                  <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="left" display-align="center" number-columns-spanned="3">
                    <fo:block font-weight="bold">Systems with Failures or Errors</fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="center" display-align="center" number-columns-spanned="3">
                    <fo:block font-weight="bold">Security Modules</fo:block>
                  </fo:table-cell>
                </fo:table-row>

                <!-- Sub-header row -->
                <fo:table-row xsl:use-attribute-sets="table-row-subheader">
                  <fo:table-cell padding="2px 2px 2px 2px" border-width="1pt" text-align="left" display-align="center">
                    <fo:block color="black">
                      <xsl:text>Hostname</xsl:text>
                    </fo:block>
                  </fo:table-cell>

                  <fo:table-cell padding="2px 2px 2px 2px" border-width="1pt" text-align="left" display-align="center">
                    <fo:block color="black">
                      <xsl:text>Client Name</xsl:text>
                    </fo:block>
                  </fo:table-cell>

                  <fo:table-cell padding="2px 2px 2px 2px" border-width="1pt" text-align="left" display-align="center">
                    <fo:block color="black">
                      <xsl:text>Assessment Date</xsl:text>
                    </fo:block>
                  </fo:table-cell>

                  <fo:table-cell padding="2px 2px 2px 2px" border-width="1pt" text-align="center" display-align="center">
                    <fo:block color="black">
                      <xsl:text>Failed</xsl:text>
                    </fo:block>
                  </fo:table-cell>

                  <fo:table-cell padding="2px 2px 2px 2px" border-width="1pt" text-align="center" display-align="center" >
                    <fo:block color="black">
                      <xsl:text>Errors</xsl:text>
                    </fo:block>
                  </fo:table-cell>

                  <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="center" display-align="center">
                    <fo:block color="black">
                      <xsl:text>% Passed/Other</xsl:text>
                    </fo:block>
                  </fo:table-cell>

                </fo:table-row>
              </fo:table-header>


           <!-- body of table - List all of the clients -->
              <fo:table-body>
                <xsl:for-each select="/GroupAssessmentReport/reports/report">
                  <xsl:sort select="@hostname"/>
                  <fo:table-row background-color="{$table.bgcolor}" color="black" border-top="1px solid {$table.color}" font-size="9pt">

                    <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="left" border-right="1px solid {$table.color}">
                      <fo:block id="{@hostname}" font-weight="bold">
                        <xsl:value-of select="@hostname"/>
                      </fo:block>

                 <!-- Client Details and cross-reference to modules -->
                      <fo:block margin-left="3em" font-size="8pt">
                        <xsl:variable name="host_name" select="@hostname"/>
                        <fo:list-block margin-left="0.5em"
                                   margin-bottom="0.5em"
                                   margin-top="0.5em"
                                   provisional-distance-between-starts="10pt"
                                   provisional-label-separation="3pt">

                          <!-- Operating System Details -->
                          <fo:list-item>
                            <fo:list-item-label end-indent="label-end()">
                              <fo:block>&#x2022;</fo:block>
                            </fo:list-item-label>
                            <fo:list-item-body start-indent="body-start()">
                              <fo:block>
                                <fo:inline font-weight="bold">OS: </fo:inline>
                                <xsl:value-of select="@dist"/>
                                <xsl:text> </xsl:text>
                                <xsl:value-of select="@distVersion"/>
                                <xsl:text> (</xsl:text>
                                <xsl:value-of select="@arch"/>
                                <xsl:text>)</xsl:text>
                              </fo:block>
                            </fo:list-item-body>
                          </fo:list-item>

                        <!-- Kernel -->
                          <fo:list-item>
                            <fo:list-item-label end-indent="label-end()">
                              <fo:block>&#x2022;</fo:block>
                            </fo:list-item-label>
                            <fo:list-item-body start-indent="body-start()">
                              <fo:block>
                                <fo:inline font-weight="bold">Kernel: </fo:inline>
                                <xsl:value-of select="@kernel"/>
                              </fo:block>
                            </fo:list-item-body>
                          </fo:list-item>
                        </fo:list-block>

                        <!-- List of Failed/Errored Modules for this client -->
                        <xsl:if test="count(/GroupAssessmentReport/modules/module/clients/client[@hostname = $host_name and (@results='Fail' or @results='Error')]) != 0">
                          <fo:block text-decoration="underline">Failed and Errored Modules:</fo:block>
                          <fo:list-block margin-left="0.5em"
                                   margin-bottom="0.5em"
                                   margin-top="0.5em"
                                   provisional-distance-between-starts="10pt"
                                   provisional-label-separation="3pt">

                            <xsl:for-each select="/GroupAssessmentReport/modules/module/clients/client[@hostname = $host_name and (@results='Fail' or @results='Error')]">
                              <xsl:sort select="@results"/>
                              <fo:list-item>
                                <fo:list-item-label end-indent="label-end()">
                                  <fo:block>&#x2022;</fo:block>
                                </fo:list-item-label>
                                <fo:list-item-body start-indent="body-start()">
                                  <fo:block>
                                    <fo:basic-link color="#467fc5" internal-destination="{generate-id(../../@name)}">
                                      <xsl:value-of select="@results"/>
                                      <xsl:text>ed - </xsl:text>
                                      <xsl:value-of select="../../@name"/>
                                    </fo:basic-link>
                                  </fo:block>
                                </fo:list-item-body>
                              </fo:list-item>
                            </xsl:for-each>
                          </fo:list-block>
                        </xsl:if>
                        
                      </fo:block>
                    </fo:table-cell>

                  <!-- Client Name -->
                    <xsl:variable name="host_name" select="@hostname"/>
                    <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="left" border-right="1px solid {$table.color}" >
                      <fo:block>
                        <xsl:for-each select="/GroupAssessmentReport/modules/module/clients/client[@results='Fail' and @hostname = $host_name]">
                          <xsl:if test="position() = 1">
                            <xsl:value-of select="@name"/>
                          </xsl:if>
                        </xsl:for-each>
                      </fo:block>
                    </fo:table-cell>

                    <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="left"  border-right="1px solid {$table.color}">
                      <fo:block>
                        <xsl:value-of select="@created"/>
                      </fo:block>
                    </fo:table-cell>

                  <!-- Module counts -->
                    <xsl:variable name="fail_count" select="count(/GroupAssessmentReport/modules/module/clients/client[@hostname = $host_name and @results='Fail'])"/>
                    <xsl:variable name="error_count" select="count(/GroupAssessmentReport/modules/module/clients/client[@hostname = $host_name and @results='Error'])"/>
                    <xsl:variable name="total_count" select="count(/GroupAssessmentReport/modules/module/clients/client[@hostname = $host_name])"/>

                    <fo:table-cell padding="2px 2px 2px 2px" text-align="center" border-right="1px solid {$table.color}">
                      <fo:block xsl:use-attribute-sets="module-fail">
                        <xsl:copy-of select="$fail_count"/>
                      </fo:block>
                    </fo:table-cell>

                    <fo:table-cell padding="2px 2px 2px 2px" text-align="center" border-right="1px solid {$table.color}">
                      <fo:block>
                        <xsl:copy-of select="$error_count"/>
                      </fo:block>
                    </fo:table-cell>

                    <fo:table-cell padding="2px 2px 2px 2px" text-align="center">
                      <fo:block>
                        <xsl:value-of select="ceiling( (($total_count - ($fail_count + $error_count)) div $total_count)*100)"/>
                        <xsl:text>%</xsl:text>
                      </fo:block>
                    </fo:table-cell>

                  </fo:table-row>
                </xsl:for-each>
              </fo:table-body>
            </fo:table>
          </xsl:if>

<!-- 
     =======================================================================
          List all modules which has a client fail or error
     =======================================================================
-->
          <xsl:if test="count(/GroupAssessmentReport/modules/module/clients/client[@results='Fail' or @results='Error']) != 0">
            <xsl:comment> List of all modudules which has a client fail or error </xsl:comment>
            <fo:table id="listFailedModules" xsl:use-attribute-sets="table" width="10in">
              <fo:table-column column-width="proportional-column-width(6)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1)"/>
              <fo:table-column column-width="proportional-column-width(1.3)"/>

             <!-- Table Header -->
              <fo:table-header>
                <fo:table-row xsl:use-attribute-sets="table-row-header">
                  <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="left" display-align="center" number-columns-spanned="1">
                    <fo:block font-weight="bold">OS Lockdown Modules</fo:block>
                  </fo:table-cell>
                  <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="center" display-align="center" number-columns-spanned="5">
                    <fo:block font-weight="bold">Systems</fo:block>
                  </fo:table-cell>
                </fo:table-row>

                <fo:table-row xsl:use-attribute-sets="table-row-subheader">
                  <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="left" display-align="center">
                    <fo:block>Module Name</fo:block>
                  </fo:table-cell>

                  <fo:table-cell padding="2px 2px 2px 2px" border-width="1pt" text-align="center" display-align="center">
                    <fo:block color="black">
                      <xsl:text>Failed</xsl:text>
                    </fo:block>
                  </fo:table-cell>

                  <fo:table-cell padding="2px 2px 2px 2px" border-width="1pt" text-align="center" display-align="center">
                    <fo:block color="black">
                      <xsl:text>Errors</xsl:text>
                    </fo:block>
                  </fo:table-cell>

                  <fo:table-cell padding="2px 2px 2px 2px" border-width="1pt" text-align="center" display-align="center">
                    <fo:block color="black">
                      <xsl:text>Passed</xsl:text>
                    </fo:block>
                  </fo:table-cell>

                  <fo:table-cell padding="2px 2px 2px 2px" border-width="1pt" text-align="center" display-align="center">
                    <fo:block color="black">
                      <xsl:text>Other</xsl:text>
                    </fo:block>
                  </fo:table-cell>

                  <fo:table-cell padding="2px 2px 2px 2px" border-width="1pt" text-align="center" display-align="center">
                    <fo:block color="black">
                      <xsl:text>% Passed/Other</xsl:text>
                    </fo:block>
                  </fo:table-cell>

                </fo:table-row>
              </fo:table-header>


              <fo:table-body>
                <xsl:for-each select="/GroupAssessmentReport/modules/module">
                  <xsl:sort select="@name"/>
         
                  <xsl:variable name="fail_count" select="count(./clients/client[@results='Fail'])" />
                  <xsl:variable name="error_count" select="count(./clients/client[@results='Error'])"/>
                  <xsl:variable name="pass_count" select="count(./clients/client[@results='Pass'])"/>
                  <xsl:variable name="other_count" select="count(./clients/client[@results != 'Pass' and @results != 'Error' and @results != 'Fail'])"/>
                  <xsl:variable name="total_count" select="$fail_count + $error_count + $pass_count + $other_count"/>

                  <xsl:variable name="rowColor">
                    <xsl:choose>
                      <xsl:when test="position() mod 2 = 0">#efefef</xsl:when>
                      <xsl:otherwise>white</xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>

                  <fo:table-row  background-color="{$rowColor}" border-top="1px solid {$table.color}">
                    <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="left" border-right="1px solid {$table.color}">
                      <fo:block id="{generate-id(@name)}">
                        <xsl:value-of select="@name"/>
                      </fo:block>

                   <!-- Details about this module -->
                      <fo:block margin-left="3em" margin-top="1em" margin-bottom="0.5em" font-size="8pt">

                        <fo:block font-style="italic">
                          <xsl:value-of select="./description"/>
                        </fo:block>

                        <fo:block margin-top="1em" margin-bottom="0.5em" text-decoration="underline">Compliancy:</fo:block>
                        <xsl:call-template name="module.compliancy.list2">
                          <xsl:with-param name="compliancy" select="./compliancy"/>
                        </xsl:call-template>

                      <!-- Correlate Systems which failed or errored this module -->
                        <xsl:if test="count(./clients/client[@results = 'Fail' or @results='Error']) != 0">
                          <fo:block margin-top="1em" text-decoration="underline">Clients with Failures or Errors:</fo:block>
                          <fo:list-block margin-left="0.5em"
                                   margin-bottom="0.5em"
                                   margin-top="0.5em"
                                   provisional-distance-between-starts="10pt"
                                   provisional-label-separation="3pt">
                            <xsl:for-each select="./clients/client[@results = 'Fail' or @results='Error']">
                              <xsl:sort select="@hostname"/>
                              <fo:list-item>
                                <fo:list-item-label end-indent="label-end()">
                                  <fo:block>&#x2022;</fo:block>
                                </fo:list-item-label>
                                <fo:list-item-body start-indent="body-start()">
                                  <fo:block>
                                    <fo:basic-link internal-destination="{@hostname}" color="#467fc5">
                                      <xsl:value-of select="@results"/>
                                      <xsl:text>ed - </xsl:text>
                                      <xsl:value-of select="@hostname"/>
                                    </fo:basic-link>
                                  </fo:block>
                                </fo:list-item-body>
                              </fo:list-item>
                            </xsl:for-each>
                          </fo:list-block>
                        </xsl:if>

                      </fo:block>

                    </fo:table-cell>

                  <!-- Failed Count -->
                    <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="center">
                      <xsl:choose>
                        <xsl:when test="$fail_count &gt; 0">
                          <fo:block xsl:use-attribute-sets="module-fail">
                            <xsl:copy-of select="$fail_count"/>
                          </fo:block>
                        </xsl:when>
                        <xsl:otherwise>
                          <fo:block>
                            <xsl:copy-of select="$fail_count"/>
                          </fo:block>
                        </xsl:otherwise>

                      </xsl:choose>
                    </fo:table-cell>

                   <!-- Errored Count -->
                    <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="center" border-right="1px dotted {$table.color}">
                      <fo:block>
                        <xsl:copy-of select="$error_count"/>
                      </fo:block>
                    </fo:table-cell>

                    <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="center">
                      <fo:block>
                        <xsl:copy-of select="$pass_count"/>
                      </fo:block>
                    </fo:table-cell>

                    <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="center" border-right="1px solid {$table.color}">
                      <fo:block>
                        <xsl:copy-of select="$other_count"/>
                      </fo:block>
                    </fo:table-cell>

                    <fo:table-cell padding="2px 2px 2px 2px" border-width="0pt" text-align="center">
                      <xsl:variable name="good_count" select="ceiling( (($total_count - ($fail_count + $error_count)) div $total_count)*100)"/>
                      <xsl:choose>
                        <xsl:when test="$good_count = 100">
                          <fo:block xsl:use-attribute-sets="module-pass">
                            <xsl:value-of select="$good_count"/>
                            <xsl:text>%</xsl:text>
                          </fo:block>
                        </xsl:when>
                        <xsl:otherwise>
                          <fo:block>
                            <xsl:value-of select="$good_count"/>
                            <xsl:text>%</xsl:text>
                          </fo:block>
                        </xsl:otherwise>
                      </xsl:choose>
                    </fo:table-cell>

                  </fo:table-row>
                </xsl:for-each>

              </fo:table-body>
            </fo:table>



          </xsl:if>

     <!-- To extract page numbers for footer -->
          <fo:block id="terminator"/>

        </fo:flow>
      </fo:page-sequence>
    </fo:root>
  </xsl:template>
</xsl:stylesheet>
