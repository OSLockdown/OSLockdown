<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: group-asset-generic.xsl 24016 2017-03-28 16:16:13Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Group Asset Report XML to FO -> PDF
     =========================================================================
-->
  <xsl:key name="distros" match="client" use="@distribution"/>
  <xsl:key name="archs" match="client" use="@architecture"/>
  <xsl:key name="locations" match="client" use="@location"/>
  <xsl:key name="contacts" match="client" use="@contact"/>

  <xsl:variable name="countResponding"><xsl:value-of select="count(/AssetReport/client[@errorMsg=''])"/></xsl:variable>    
  <xsl:variable name="countNotResponding"><xsl:value-of select="count(/AssetReport/client[@errorMsg!=''])"/></xsl:variable>    
  
  <xsl:include href="common-fo.xsl"/>
<!--
   Report Parameter Definitions:
     report.title     : Report title to be used in header 
     header.display   : if false, do not display header
     logo.display     : if false, do not display logo in header

-->
  <xsl:param name="report.title">Group Asset Inventory Report</xsl:param>
  <xsl:param name="header.display">true</xsl:param>
  <xsl:param name="logo.display">true</xsl:param>
  <xsl:output method="xml" encoding="utf-8" indent="yes"/>
  <xsl:template match="/">
    <fo:root xmlns:fo="http://www.w3.org/1999/XSL/Format"
             xmlns:fox="http://xmlgraphics.apache.org/fop/extensions">
      <fo:layout-master-set>
<!-- Report is landscape so, switch width and height -->
        <fo:simple-page-master master-name="first"
                               page-width="{$page.height}"
                               page-height="{$page.width}"
                               margin-top="0.25in"
                               margin-bottom="0.5in"
                               margin-right="0.5in"
                               margin-left="0.5in">
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
              <dc:description>Asset Report</dc:description>
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
                   BEGIN MAIN PAGE SEQUENCE
    =======================================================================
-->
      <fo:page-sequence master-reference="first" font-family="Helvetica" font-size="{$page.font.size}">
<!--
    | Footer (Static)
    +-->
        <fo:static-content flow-name="xsl-region-after">
          <fo:block margin-top="0.25in" font-size="10pt" text-align-last="justify" color="#467fc5">
            Generated by OS Lockdown v<xsl:value-of select="/AssetReport/@sbVersion"/>
            <fo:leader leader-pattern="space" />Page
            <fo:page-number/> of
            <fo:page-number-citation ref-id="terminator"/>
          </fo:block>
        </fo:static-content>

<!--
    | Begin non-static flow
    +-->
        <fo:flow flow-name="xsl-region-body">

<!-- 
    =======================================================================
                  Report Header Banner (first page)
    =======================================================================
-->
        <xsl:if test="$header.display = 'true'">
          <fo:table id="doctop" table-layout="fixed" xsl:use-attribute-sets="table">
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
          <fo:table table-layout="fixed" 
                    width="10in" 
                    background-color="{$table.bgcolor}"
                    border-spacing="0pt" 
                    border="1px solid {$table.color}" 
                    margin-top="2em" 
                    margin-bottom="1em" 
                    font-size="{$table.font.size}">
            <fo:table-column column-width="proportional-column-width(0.7)"/>
            <fo:table-column column-width="proportional-column-width(1)"/>
            <fo:table-column column-width="proportional-column-width(1)"/>
            <fo:table-column column-width="proportional-column-width(1)"/>
            <fo:table-column column-width="proportional-column-width(1)"/>
            <fo:table-body>
              <fo:table-row background-color="{$table.color}" color="black"
                            font-size="{$table.header.font.size}">
                <fo:table-cell padding="2px 5px 2px 5px"
                               border-width="0pt"
                               number-columns-spanned="3"
                               text-align="left"
                               display-align="center">
                  <fo:block font-weight="bold">
                    <xsl:text>Summary</xsl:text>
                  </fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px"
                               border-width="0pt"
                               text-align="right"
                               display-align="center"
                               number-columns-spanned="2">
                  <fo:block font-weight="bold">
                    <xsl:text>Created: </xsl:text>
                    <xsl:value-of select="substring(/AssetReport/@created,1,20)"/>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

         <!-- Group Name -->
              <fo:table-row color="{$table.font.color}"  background-color="{$table.bgcolor}">
                <fo:table-cell padding="2px 5px 2px 5px"
                               border-width="0pt"
                               text-align="right"
                               border-right="1px solid {$table.color}"
                               border-bottom="1px solid {$table.color}">
                  <fo:block>Group Name</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px"
                               border-width="0pt"
                               text-align="left"
                               number-columns-spanned="4"
                               border-bottom="1px solid {$table.color}">
                  <fo:block>
                    <xsl:value-of select="/AssetReport/@name" />
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

          <!-- Group Description -->
              <fo:table-row color="{$table.font.color}"  background-color="{$table.bgcolor}">
                <fo:table-cell padding="2px 5px 2px 5px"
                               border-width="0pt"
                               text-align="right"
                               border-right="1px solid {$table.color}"
                               border-bottom="1px solid {$table.color}">
                  <fo:block>Description</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px"
                               border-width="0pt"
                               text-align="left"
                               number-columns-spanned="4"
                               border-bottom="1px solid {$table.color}">
                  <fo:block linefeed-treatment="preserve"
                            white-space-collapse="false"
                            white-space-treatment="preserve">
                    <xsl:value-of select="/AssetReport/description" />
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

          <!-- Console Version -->
              <fo:table-row color="{$table.font.color}"  background-color="{$table.bgcolor}">
                <fo:table-cell padding="2px 5px 2px 5px"
                               border-width="0pt"
                               text-align="right"
                               border-right="1px solid {$table.color}"
                               border-bottom="1px solid {$table.color}">
                  <fo:block>Console Version</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px"
                               border-width="0pt"
                               text-align="left"
                               number-columns-spanned="4"
                               border-bottom="1px solid {$table.color}">
                  <fo:block>
                    OS Lockdown
                    <xsl:value-of select="/AssetReport/@sbVersion" />
                    <xsl:variable name="badClients" 
                                  select="count(/AssetReport/client[substring-after(@clientVersion, 'OS Lockdown ') != /AssetReport/@sbVersion])"/>
                    <xsl:if test="$badClients != 0 ">
                      <fo:block margin-left="0.25in" space-before="0.1in" margin-bottom="0.25in">
                        <fo:inline text-decoration="underline" font-weight="bold">Warning:</fo:inline>
                        <xsl:text> </xsl:text>
                        The highlighted items (in the
                        <fo:inline font-style="italic">Program Version</fo:inline>
                        column below) indicate a difference between the OS Lockdown Console version
                        and the client version. It is strongly recommended to update the client version
                        to maintain proper security posture.
                      </fo:block>
                    </xsl:if>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

          <!-- Group Size -->
              <fo:table-row color="{$table.font.color}"  background-color="{$table.bgcolor}">
                <fo:table-cell padding="2px 5px 2px 5px"
                               border-width="0pt"
                               text-align="right"
                               border-right="1px solid {$table.color}"
                               border-bottom="1px solid {$table.color}">
                  <fo:block>Group Size</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px"
                               border-width="0pt"
                               text-align="left"
                               number-columns-spanned="4"
                               border-bottom="1px solid {$table.color}">
                  <fo:block linefeed-treatment="preserve"
                            white-space-collapse="false"
                            white-space-treatment="preserve">
                    <xsl:value-of select="count(/AssetReport/client)" /> Total -- (<xsl:value-of select="$countResponding"/> responding, <xsl:value-of select="$countNotResponding"/> not responding)
        <xsl:text>&#x0A;</xsl:text>
                  </fo:block>
                </fo:table-cell>
              </fo:table-row>

          <!-- Analysis -->
              <fo:table-row color="{$table.font.color}"  background-color="{$table.bgcolor}">
                <fo:table-cell padding="2px 5px 2px 5px"
                               border-width="0pt"
                               text-align="right"
                               border-right="1px solid {$table.color}">
                  <fo:block>Analysis</fo:block>
                </fo:table-cell>
                <fo:table-cell padding="2px 5px 2px 5px"
                               border-width="0pt"
                               text-align="left"
                               number-columns-spanned="4"
                               border-bottom="1px solid {$table.color}">

                   <!-- Mini Table of statistics -->
                  <fo:table table-layout="fixed"
                            width="8.18in"
                            margin="2px 4px 2px 4px"
                            border-separation="2px"
                            border="2px solid white"
                            background-color="{$table.bgcolor}"
                            font-size="8pt">
                    <fo:table-column column-width="proportional-column-width(1)"/>
                    <fo:table-column column-width="proportional-column-width(0.6)"/>
                    <fo:table-column column-width="proportional-column-width(1)"/>
                    <fo:table-column column-width="proportional-column-width(1)"/>
                    <fo:table-body>
                      <fo:table-row>
                        <fo:table-cell>
                          <fo:block text-align-last="justify"
                                    padding="2px 5px 2px 5px"
                                    font-weight="bold"
                                    background-color="{$table.color}">
                            Operating Systems
                            <fo:leader leader-pattern="space"/>
                            Count
                          </fo:block>
                          <xsl:for-each select="/AssetReport/client[generate-id() = generate-id(key('distros',@distribution)[1])]">
                            <xsl:sort select="@distribution"/>
                            <xsl:variable name="distro" select="@distribution"/>

                            <!-- odd/even row coloring -->
                            <xsl:variable name="blockColor">
                              <xsl:choose>
                                <xsl:when test="position() mod 2 = 0">#eef1f8</xsl:when>
                                <xsl:otherwise>white</xsl:otherwise>
                              </xsl:choose>
                            </xsl:variable>

                            <fo:block text-align-last="justify"
                                      padding="2px 5px 2px 5px"
                                      background-color="{$blockColor}">
                              <xsl:value-of select="@distribution"/>
                              <fo:leader leader-pattern="space"/>
                              <xsl:value-of select="count(/AssetReport/client[@distribution = $distro ])"/>
                            </fo:block>
                          </xsl:for-each>
                        </fo:table-cell>
                        
                        <fo:table-cell>
                          <fo:block text-align-last="justify"
                                    padding="2px 5px 2px 5px"
                                    font-weight="bold"
                                    background-color="{$table.color}">
                            Architectures
                            <fo:leader leader-pattern="space"/>
                            Count
                          </fo:block>
                          <xsl:for-each select="/AssetReport/client[generate-id() = generate-id(key('archs',@architecture)[1])]">
                            <xsl:sort select="@architecture"/>
                            <xsl:variable name="arch" select="@architecture"/>

                            <!-- odd/even row coloring -->
                            <xsl:variable name="blockColor">
                              <xsl:choose>
                                <xsl:when test="position() mod 2 = 0">#eef1f8</xsl:when>
                                <xsl:otherwise>white</xsl:otherwise>
                              </xsl:choose>
                            </xsl:variable>

                            <fo:block text-align-last="justify"
                                      background-color="{$blockColor}"
                                      padding="2px 5px 2px 5px">
                              <xsl:choose>
                                <xsl:when test="contains(@architecture, 'SUNW,')">
                                  <xsl:value-of select="substring-after(@architecture,'SUNW,')"/>
                                </xsl:when>
                                <xsl:otherwise>
                                  <xsl:value-of select="@architecture"/>
                                </xsl:otherwise>
                              </xsl:choose>
                              <fo:leader leader-pattern="space"/>
                              <xsl:value-of select="count(/AssetReport/client[@architecture = $arch ])"/>
                            </fo:block>
                          </xsl:for-each>

                        </fo:table-cell>
                        <fo:table-cell>
                          <fo:block text-align-last="justify"
                                    padding="2px 5px 2px 5px"
                                    font-weight="bold"
                                    background-color="{$table.color}">
                            Locations
                            <fo:leader leader-pattern="space"/>
                            Count
                          </fo:block>
                          <xsl:for-each select="/AssetReport/client[generate-id() = generate-id(key('locations',@location)[1])]">
                            <xsl:sort select="@location"/>
                            <xsl:variable name="loc" select="@location"/>

                            <!-- odd/even row coloring -->
                            <xsl:variable name="blockColor">
                              <xsl:choose>
                                <xsl:when test="position() mod 2 = 0">#eef1f8</xsl:when>
                                <xsl:otherwise>white</xsl:otherwise>
                              </xsl:choose>
                            </xsl:variable>

                            <fo:block text-align-last="justify"
                                      background-color="{$blockColor}"
                                      padding="2px 5px 2px 5px">
                              <xsl:value-of select="@location"/>
                              <fo:leader leader-pattern="space"/>
                              <xsl:value-of select="count(/AssetReport/client[@location = $loc ])"/>
                            </fo:block>
                          </xsl:for-each>
                        </fo:table-cell>
                        <fo:table-cell>
                          <fo:block text-align-last="justify"
                                    padding="2px 5px 2px 5px"
                                    font-weight="bold"
                                    background-color="{$table.color}">
                            Contacts
                            <fo:leader leader-pattern="space"/>
                            Count
                          </fo:block>
                          <xsl:for-each select="/AssetReport/client[generate-id() = generate-id(key('contacts',@contact)[1])]">
                            <xsl:sort select="@contact"/>
                            <xsl:variable name="cont" select="@contact"/>

                            <!-- odd/even row coloring -->
                            <xsl:variable name="blockColor">
                              <xsl:choose>
                                <xsl:when test="position() mod 2 = 0">#eef1f8</xsl:when>
                                <xsl:otherwise>white</xsl:otherwise>
                              </xsl:choose>
                            </xsl:variable>

                            <fo:block text-align-last="justify"
                                      background-color="{$blockColor}"
                                      padding="2px 5px 2px 5px">
                              <xsl:value-of select="@contact"/>
                              <fo:leader leader-pattern="space"/>
                              <xsl:value-of select="count(/AssetReport/client[@contact = $cont ])"/>
                            </fo:block>
                          </xsl:for-each>
                        </fo:table-cell>
                      </fo:table-row>
                    </fo:table-body>
                  </fo:table>


                </fo:table-cell>
              </fo:table-row>

            </fo:table-body>
          </fo:table>
    <!-- 
        =======================================================================
                                  Responding Client Listing
        =======================================================================
    -->
        <xsl:if test="$countNotResponding > 0">
              <fo:table id="clientNotRespondingListing"
                        table-layout="fixed" width="10in"
                        background-color="{$table.bgcolor}"
                        border-spacing="0pt"
                        border="1px solid {$table.color}"
                        margin-top="2em"
                        margin-bottom="1em"
                        font-size="10pt">
                <fo:table-column column-width="proportional-column-width(1.25)"/>
                <fo:table-column column-width="proportional-column-width(3)"/>

                <fo:table-header>
                  <fo:table-row background-color="{$table.color}" color="black">
                    <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" 
                                   text-align="left" display-align="center">
                      <fo:block font-weight="bold">Non-Responding Client Name</fo:block>
                    </fo:table-cell>

                    <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" 
                                   text-align="left" display-align="center">
                      <fo:block font-weight="bold">Operating System</fo:block>
                    </fo:table-cell>


                  </fo:table-row>
                </fo:table-header>

                <fo:table-body>
                  <xsl:for-each select="/AssetReport/client[@errorMsg!='']">
                    <xsl:sort select="@name"/>

                    <xsl:variable name="rowColor">
                      <xsl:choose>
                        <xsl:when test="position() mod 2 = 0">#eef1f8</xsl:when>
                        <xsl:otherwise>white</xsl:otherwise>
                      </xsl:choose>
                    </xsl:variable>

                    <fo:table-row background-color="{$rowColor}" 
                                  color="{$table.font.color}" 
                                  border-bottom="1px solid {$table.color}" 
                                  font-size="10pt">
                      <fo:table-cell padding="2px 5px 2px 5px" 
                                     border-right="1px solid {$table.color}" 
                                     text-align="left" 
                                     display-align="center">
                        <fo:block>
                          <xsl:value-of select="@name"/>
                        </fo:block>

                      </fo:table-cell>

                      <fo:table-cell padding="2px 5px 2px 5px"  
                                     border-right="1px solid {$table.color}" 
                                     text-align="left" 
                                     display-align="center"
                                     background-color="yellow">
                        <fo:block>
                          <xsl:value-of select="@distribution"/>
                        </fo:block>
                      </fo:table-cell>
                    </fo:table-row>
                  </xsl:for-each>
                </fo:table-body>

              </fo:table>
          </xsl:if>
    <!-- 
        =======================================================================
                                  Responding Client Listing
        =======================================================================
    -->
        <xsl:if test="$countResponding > 0">
              <fo:table id="clientListing"
                        table-layout="fixed" width="10in"
                        background-color="{$table.bgcolor}"
                        border-spacing="0pt"
                        border="1px solid {$table.color}"
                        margin-top="2em"
                        margin-bottom="1em"
                        font-size="10pt">
                <fo:table-column column-width="proportional-column-width(1.5)"/>
                <fo:table-column column-width="proportional-column-width(1.1)"/>
                <fo:table-column column-width="proportional-column-width(0.5)"/>
                <fo:table-column column-width="proportional-column-width(1)"/>
                <fo:table-column column-width="proportional-column-width(1)"/>

                <fo:table-header>
                  <fo:table-row background-color="{$table.color}" color="black">
                    <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" 
                                   text-align="left" display-align="center">
                      <fo:block font-weight="bold">Client Name</fo:block>
                    </fo:table-cell>

                    <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" 
                                   text-align="left" display-align="center">
                      <fo:block font-weight="bold">Operating System</fo:block>
                    </fo:table-cell>

                    <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" 
                                   text-align="left" display-align="center">
                      <fo:block font-weight="bold">Program Version</fo:block>
                    </fo:table-cell>

                    <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" 
                                   text-align="left" display-align="center">
                      <fo:block font-weight="bold">Location</fo:block>
                    </fo:table-cell>

                    <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" 
                                   text-align="left" display-align="center">
                      <fo:block font-weight="bold">Contact</fo:block>
                    </fo:table-cell>

                  </fo:table-row>
                </fo:table-header>

                <fo:table-body>
                  <xsl:for-each select="/AssetReport/client[@errorMsg='']">
                    <xsl:sort select="@name"/>

                    <xsl:variable name="rowColor">
                      <xsl:choose>
                        <xsl:when test="position() mod 2 = 0">#eef1f8</xsl:when>
                        <xsl:otherwise>white</xsl:otherwise>
                      </xsl:choose>
                    </xsl:variable>

                    <fo:table-row background-color="{$rowColor}" 
                                  color="{$table.font.color}" 
                                  border-bottom="1px solid {$table.color}" 
                                  font-size="10pt">
                      <fo:table-cell padding="2px 5px 2px 5px" 
                                     border-right="1px solid {$table.color}" 
                                     text-align="left" 
                                     display-align="center">
                        <fo:block>
                          <xsl:value-of select="@name"/>
                        </fo:block>

                        <!-- Extra host information -->
                        <fo:list-block margin-left="0.5em"
                                       margin-bottom="0.5em"
                                       margin-top="1em"
                                       font-size="8pt"
                                       provisional-distance-between-starts="10pt"
                                       provisional-label-separation="3pt">

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

                          <fo:list-item>
                            <fo:list-item-label end-indent="label-end()">
                              <fo:block>&#x2022;</fo:block>
                            </fo:list-item-label>
                            <fo:list-item-body start-indent="body-start()">
                              <fo:block>
                                <fo:inline font-weight="bold">Arch: </fo:inline>
                                <xsl:value-of select="@architecture"/>
                              </fo:block>
                            </fo:list-item-body>
                          </fo:list-item>

                          <fo:list-item>
                            <fo:list-item-label end-indent="label-end()">
                              <fo:block>&#x2022;</fo:block>
                            </fo:list-item-label>
                            <fo:list-item-body start-indent="body-start()">
                              <fo:block>
                                <fo:inline font-weight="bold">Memory: </fo:inline>
                                <xsl:value-of select="substring-after(@memory, ' / ')"/>
                              </fo:block>
                            </fo:list-item-body>
                          </fo:list-item>
                        </fo:list-block>
                      </fo:table-cell>

                      <fo:table-cell padding="2px 5px 2px 5px"  
                                     border-right="1px solid {$table.color}" 
                                     text-align="left" 
                                     display-align="center">
                        <fo:block>
                          <xsl:value-of select="@distribution"/>
                        </fo:block>
                      </fo:table-cell>

                    <!-- color code client versions which don't match the console's -->
                      <xsl:variable name="cltVersion">
                        <xsl:choose>
                          <xsl:when test="contains(@clientVersion, 'OS Lockdown')">
                            <xsl:value-of select="substring-after(@clientVersion, 'OS Lockdown ')"/>
                          </xsl:when>
                          <xsl:otherwise>
                            <xsl:value-of select="@clientVersion"/>
                          </xsl:otherwise>
                        </xsl:choose>
                      </xsl:variable>
                      <xsl:variable name="cellColor">
                        <xsl:choose>
                          <xsl:when test="/AssetReport/@sbVersion != $cltVersion">yellow</xsl:when>
                          <xsl:otherwise>
                            <xsl:value-of select="$rowColor"/>
                          </xsl:otherwise>
                        </xsl:choose>
                      </xsl:variable>

                      <fo:table-cell padding="2px 5px 2px 5px"
                                     border-width="0pt" 
                                     text-align="center"
                                     display-align="center"
                                     border-right="1px solid {$table.color}"
                                     background-color="{$cellColor}">
                        <fo:block>
                          <xsl:value-of select="$cltVersion" />
                        </fo:block>
                      </fo:table-cell>

                      <fo:table-cell padding="2px 5px 2px 5px" 
                                     border-right="1px solid {$table.color}" 
                                     text-align="left" 
                                     display-align="center">
                        <fo:block>
                          <xsl:value-of select="@location"/>
                        </fo:block>
                      </fo:table-cell>
                      <fo:table-cell padding="2px 5px 2px 5px" 
                                     border-width="0pt" 
                                     text-align="left" 
                                     display-align="center">
                        <fo:block>
                          <xsl:value-of select="@contact"/>
                        </fo:block>
                      </fo:table-cell>

                    </fo:table-row>
                  </xsl:for-each>
                </fo:table-body>

              </fo:table>
          </xsl:if>

<!-- 
    | Footer with Page number 
    +-->
          <fo:block id="terminator"/>
        </fo:flow>
      </fo:page-sequence>
    </fo:root>
  </xsl:template>
</xsl:stylesheet>
