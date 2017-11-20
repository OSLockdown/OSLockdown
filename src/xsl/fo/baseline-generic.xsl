<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: baseline-generic.xsl 23917 2017-03-07 15:44:30Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Baseline Report XML to FO -> PDF
     =========================================================================
-->
 <xsl:include href="common-fo.xsl"/>
<!--
   Report Parameter Definitions:
     report.title     : Report title to be used in header 
     header.display   : if false, do not display header
     logo.display     : if false, do not display logo in header

-->
 <xsl:param name="report.title">Baseline Report</xsl:param>
 <xsl:param name="header.display">true</xsl:param>
 <xsl:param name="logo.display">true</xsl:param>
 <xsl:output method="xml" encoding="utf-8" indent="yes"/>
 <xsl:template match="/">
  <fo:root xmlns:fo="http://www.w3.org/1999/XSL/Format" 
           xmlns:fox="http://xmlgraphics.apache.org/fop/extensions">

   <fo:layout-master-set>
    <fo:simple-page-master master-name="summary" 
                           page-width="{$page.height}" page-height="{$page.width}" 
                           margin-top="0.25in" margin-bottom="0.5in" 
                           margin-right="0.5in" margin-left="0.5in">
     <fo:region-body margin-top="0.25in" margin-bottom="0.25in"/>
     <fo:region-before extent="0.25in"/>
     <fo:region-after extent="0.25in"/>
    </fo:simple-page-master>

    <fo:simple-page-master master-name="pages" 
                           page-width="{$page.height}" page-height="{$page.width}" 
                           margin-top="0.25in" margin-bottom="0.5in" 
                           margin-right="0.5in" margin-left="0.5in">
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
       <dc:description><xsl:copy-of select="$report.title"/></dc:description>
      </rdf:Description>

<!-- XMP properties go here -->
      <rdf:Description xmlns:xmp="http://ns.adobe.com/xap/1.0/" rdf:about="">
       <xmp:CreatorTool>OS Lockdown v<xsl:value-of select="/BaselineReport/@sbVersion"/></xmp:CreatorTool>
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
   <fo:bookmark-tree>
    <fo:bookmark internal-destination="summaryTable">
     <fo:bookmark-title>Summary</fo:bookmark-title>
    </fo:bookmark>

    <xsl:if test="count(/BaselineReport/sections/section[@name='Auditing and Logging']/subSection) != 0">
      <fo:bookmark internal-destination="Auditing">
       <fo:bookmark-title>Auditing and Logging</fo:bookmark-title>
       <xsl:for-each select="/BaselineReport/sections/section[@name='Auditing and Logging']/subSection">
        <xsl:variable name="secname" select="@name"/>
        <fo:bookmark internal-destination="{$secname}">
         <fo:bookmark-title>
          <xsl:value-of select="@name"/>
         </fo:bookmark-title>
        </fo:bookmark>
       </xsl:for-each>
      </fo:bookmark>
     </xsl:if>

    <xsl:if test="count(/BaselineReport/sections/section[@name='Hardware']/subSection) != 0">
      <fo:bookmark internal-destination="Hardware">
       <fo:bookmark-title>Hardware</fo:bookmark-title>
       <xsl:for-each select="/BaselineReport/sections/section[@name='Hardware']/subSection">
        <xsl:variable name="secname" select="@name"/>
        <fo:bookmark internal-destination="{$secname}">
         <fo:bookmark-title>
          <xsl:value-of select="@name"/>
         </fo:bookmark-title>
        </fo:bookmark>
       </xsl:for-each>
      </fo:bookmark>
     </xsl:if>

    <xsl:if test="count(/BaselineReport/sections/section[@name='Network']/subSection) != 0">
      <fo:bookmark internal-destination="Network">
       <fo:bookmark-title>Network</fo:bookmark-title>
       <xsl:for-each select="/BaselineReport/sections/section[@name='Network']/subSection">
        <xsl:variable name="secname" select="@name"/>
        <fo:bookmark internal-destination="{$secname}">
         <fo:bookmark-title>
          <xsl:value-of select="@name"/>
         </fo:bookmark-title>
        </fo:bookmark>
       </xsl:for-each>
      </fo:bookmark>
     </xsl:if>

    <xsl:if test="count(/BaselineReport/sections/section[@name='Software']/subSection) != 0">
      <fo:bookmark internal-destination="Software">
       <fo:bookmark-title>Software</fo:bookmark-title>
      </fo:bookmark>
    </xsl:if>
   </fo:bookmark-tree>
<!-- ====================================================================== -->
<!--
    | BEGIN PAGE SUQUENCE 
    +-->
   <fo:page-sequence master-reference="summary" font-family="Helvetica" font-size="{$page.font.size}">
    <fo:flow flow-name="xsl-region-body">
    <fo:block id="top"/>

<!-- 
    =======================================================================
                          Report Header (First Page)
    =======================================================================
    +-->
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
     <fo:table id="summaryTable" table-layout="fixed" width="10in" xsl:use-attribute-sets="table">
      <fo:table-column column-width="proportional-column-width(1)"/>
      <fo:table-column column-width="proportional-column-width(6)"/>
      <fo:table-body>
       <fo:table-row xsl:use-attribute-sets="table-row-header">
        <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
         <fo:block font-weight="bold">Summary</fo:block>
        </fo:table-cell>
        <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="right" display-align="center">
         <fo:block font-weight="bold">
          <xsl:text>Created: </xsl:text>
          <xsl:value-of select="/BaselineReport/report/@created"/>
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
          <xsl:value-of select="/BaselineReport/report/@hostname"/>
         </fo:block>
        </fo:table-cell>
       </fo:table-row>

<!-- Operating System -->
       <fo:table-row color="{$table.font.color}" border-bottom="1px solid {$table.color}">
        <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
         <fo:block>Operating System</fo:block>
        </fo:table-cell>
        <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
         <fo:block>
          <xsl:variable name="distVersion" select="/BaselineReport/report/@distVersion"/>
          <xsl:variable name="dist" select="/BaselineReport/report/@dist"/>
          <xsl:choose>
           <xsl:when test="$distVersion = '10' and $dist = 'redhat'">
            <xsl:text>Fedora 10</xsl:text>
           </xsl:when>
           <xsl:when test="$distVersion = '11' and $dist = 'redhat'">
            <xsl:text>Fedora 11</xsl:text>
           </xsl:when>
           <xsl:when test="$distVersion = '12' and $dist = 'redhat'">
            <xsl:text>Fedora 12</xsl:text>
           </xsl:when>
           <xsl:otherwise>
            <xsl:value-of select="/BaselineReport/report/@dist"/>
            <xsl:text></xsl:text>
            <xsl:value-of select="/BaselineReport/report/@distVersion"/>
           </xsl:otherwise>
          </xsl:choose>
          <xsl:text> (</xsl:text>
          <xsl:value-of select="/BaselineReport/report/@arch"/>
          <xsl:text>) [Kernel </xsl:text>
          <xsl:value-of select="/BaselineReport/report/@kernel"/>
          <xsl:text>]</xsl:text>
         </fo:block>
        </fo:table-cell>
       </fo:table-row>

<!-- Total Memory -->
       <fo:table-row color="{$table.font.color}" border-bottom="1px solid {$table.color}">
        <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
         <fo:block>Total Memory</fo:block>
        </fo:table-cell>
        <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
         <fo:block>
          <xsl:value-of select="/BaselineReport/report/@totalMemory"/>
         </fo:block>
        </fo:table-cell>
       </fo:table-row>

<!-- CPU Information -->
       <fo:table-row color="{$table.font.color}" border-bottom="1px solid {$table.color}">
        <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
         <fo:block>Processors</fo:block>
        </fo:table-cell>
        <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
         <fo:block>
          <xsl:value-of select="/BaselineReport/report/@cpuInfo"/>
         </fo:block>
        </fo:table-cell>
       </fo:table-row>

<!-- Profile Information -->
       <fo:table-row color="{$table.font.color}" border-bottom="1px solid {$table.color}">
        <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
         <fo:block>Profile</fo:block>
        </fo:table-cell>
        <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
         <fo:block>
          <xsl:value-of select="/BaselineReport/report/@profile"/>
         </fo:block>
        </fo:table-cell>
       </fo:table-row>

<!-- Auditing and Logging -->
       <xsl:if test="count(/BaselineReport/sections/section[@name='Auditing and Logging']/subSection) != 0">
        <fo:table-row color="{$table.font.color}" border-bottom="1px solid {$table.color}">
         <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
          <fo:block><fo:basic-link color="#467fc5" internal-destination="Auditing">Auditing and Logging</fo:basic-link></fo:block>
         </fo:table-cell>
         <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
          <fo:list-block margin-left="0.5em" margin-top="0.5em" margin-bottom="0.5em" font-size="10pt" 
                        provisional-distance-between-starts="10pt" provisional-label-separation="3pt">
           <xsl:for-each select="/BaselineReport/sections/section[@name='Auditing and Logging']/subSection">
            <xsl:variable name="secname" select="@name"/>
            <fo:list-item>
             <fo:list-item-label end-indent="label-end()">
              <fo:block>• </fo:block>
             </fo:list-item-label>
             <fo:list-item-body start-indent="body-start()">
              <fo:block>
               <fo:basic-link color="#467fc5" internal-destination="{$secname}">
                 <xsl:value-of select="@name"/>
               </fo:basic-link>
              </fo:block>
             </fo:list-item-body>
            </fo:list-item>
           </xsl:for-each>
          </fo:list-block>
         </fo:table-cell>
        </fo:table-row>
       </xsl:if>

<!-- Hardware Section -->
       <xsl:if test="count(/BaselineReport/sections/section[@name='Hardware']/subSection) != 0">
        <fo:table-row color="{$table.font.color}" border-bottom="1px solid {$table.color}">
         <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
          <fo:block><fo:basic-link color="#467fc5" internal-destination="Hardware">Hardware</fo:basic-link></fo:block>
         </fo:table-cell>
         <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
          <fo:list-block margin-left="0.5em" margin-top="0.5em" margin-bottom="0.5em" font-size="10pt" 
                        provisional-distance-between-starts="10pt" provisional-label-separation="3pt">
           <xsl:for-each select="/BaselineReport/sections/section[@name='Hardware']/subSection">
            <xsl:variable name="secname" select="@name"/>
            <fo:list-item>
             <fo:list-item-label end-indent="label-end()">
              <fo:block>• </fo:block>
             </fo:list-item-label>
             <fo:list-item-body start-indent="body-start()">
              <fo:block>
               <fo:basic-link color="#467fc5" internal-destination="{$secname}">
                 <xsl:value-of select="@name"/>
               </fo:basic-link>
              </fo:block>
             </fo:list-item-body>
            </fo:list-item>
           </xsl:for-each>
          </fo:list-block>
         </fo:table-cell>
        </fo:table-row>
       </xsl:if>

<!-- Network Section -->
       <xsl:if test="count(/BaselineReport/sections/section[@name='Network']/subSection) != 0">
        <fo:table-row color="{$table.font.color}" border-bottom="1px solid {$table.color}">
         <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
          <fo:block><fo:basic-link color="#467fc5" internal-destination="Network">Network</fo:basic-link></fo:block>
         </fo:table-cell>
         <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
          <fo:list-block margin-left="0.5em" margin-top="0.5em" margin-bottom="0.5em" font-size="10pt" 
                        provisional-distance-between-starts="10pt" provisional-label-separation="3pt">
           <xsl:for-each select="/BaselineReport/sections/section[@name='Network']/subSection">
            <xsl:variable name="secname" select="@name"/>
            <fo:list-item>
             <fo:list-item-label end-indent="label-end()">
              <fo:block>• </fo:block>
             </fo:list-item-label>
             <fo:list-item-body start-indent="body-start()">
              <fo:block>
               <fo:basic-link color="#467fc5" internal-destination="{$secname}">
                 <xsl:value-of select="@name"/>
               </fo:basic-link>
              </fo:block>
             </fo:list-item-body>
            </fo:list-item>
           </xsl:for-each>
          </fo:list-block>
         </fo:table-cell>
        </fo:table-row>
       </xsl:if>

<!-- Files Section -->
       <xsl:if test="count(/BaselineReport/sections/section[@name='Files']/subSection) != 0">
        <fo:table-row color="{$table.font.color}" border-bottom="1px solid {$table.color}">
         <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
          <fo:block>Files</fo:block>
         </fo:table-cell>
         <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
          <fo:list-block margin-left="0.5em" margin-top="0.5em" margin-bottom="0.5em" font-size="10pt" 
                        provisional-distance-between-starts="10pt" provisional-label-separation="3pt">
           <xsl:for-each select="/BaselineReport/sections/section[@name='Files']/subSection[@name != 'Device Files']">
            <xsl:variable name="secname" select="@name"/>
            <fo:list-item>
             <fo:list-item-label end-indent="label-end()">
              <fo:block>• </fo:block>
             </fo:list-item-label>
             <fo:list-item-body start-indent="body-start()">
              <fo:block>
               <xsl:value-of select="@name"/> (<xsl:value-of select="format-number(count(./files/file), '###,###')"/>)
             </fo:block>
             </fo:list-item-body>
            </fo:list-item>
           </xsl:for-each>
          </fo:list-block>
         </fo:table-cell>
        </fo:table-row>
       </xsl:if>

<!-- Software Section -->
       <xsl:if test="count(/BaselineReport/sections/section[@name='Software']/subSection) != 0">
        <fo:table-row color="{$table.font.color}" border-bottom="1px solid {$table.color}">
         <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
          <fo:block><fo:basic-link color="#467fc5" internal-destination="Software">Software</fo:basic-link></fo:block>
         </fo:table-cell>
         <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
          <fo:block>
           <xsl:value-of select="format-number(count(/BaselineReport/sections/section[@name='Software']/subSection/packages/package), '###,###')"/>
          packages installed
         </fo:block>
         </fo:table-cell>
        </fo:table-row>
       </xsl:if>
      </fo:table-body>
     </fo:table>
    </fo:flow>
   </fo:page-sequence>

<!-- 
    | NEW PAGE SQUENCE - Report Details 
      
    | Report Header (Static)
    + -->
   <fo:page-sequence master-reference="pages" font-family="Helvetica" font-size="{$page.font.size}">
    <fo:static-content flow-name="xsl-region-before">
      <fo:block text-align-last="justify" color="#467fc5">
        <fo:inline color="#a19670">Hostname: </fo:inline>
        <fo:inline color="#980230"><xsl:value-of select="/BaselineReport/report/@hostname"/></fo:inline>
        <fo:leader leader-pattern="space" />
        <fo:retrieve-marker retrieve-class-name="sectionTitle" retrieve-position="first-including-carryover" />
      </fo:block>
    </fo:static-content>
<!--
    | Report Footer (Static)
    + -->
    <fo:static-content flow-name="xsl-region-after">
     <fo:block margin-top="0.25in" font-size="10pt" text-align-last="justify" color="#467fc5">
         OS Lockdown v<xsl:value-of select="/BaselineReport/@sbVersion"/>
      <fo:leader leader-pattern="space" />
      Page <fo:page-number/> of <fo:page-number-citation ref-id="terminator"/>
     </fo:block>
    </fo:static-content>

    <fo:flow flow-name="xsl-region-body">
<!-- 
    =======================================================================
                         Auditing and Logging (Table)
    =======================================================================
-->
     <xsl:if test="count(/BaselineReport/sections/section[@name='Auditing and Logging']/subSection) != 0">
      <fo:block break-before="page">
        <fo:marker marker-class-name="sectionTitle">Auditing and Logging</fo:marker>
      </fo:block>
      <fo:table id="Auditing" table-layout="fixed" width="10in" xsl:use-attribute-sets="table">
       <fo:table-column column-width="proportional-column-width(1)"/>
       <fo:table-column column-width="proportional-column-width(6)"/>
       <fo:table-header>
        <fo:table-row xsl:use-attribute-sets="table-row-header">
         <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center" number-columns-spanned="2">
           <fo:block text-align-last="justify">
             <fo:inline font-weight="bold">Auditing and Logging</fo:inline>
             <fo:leader leader-pattern="space" />
             <fo:basic-link internal-destination="top">
               <fo:inline font-family="ZapfDingbats">&#x25B2;</fo:inline>
             </fo:basic-link>
           </fo:block>
         </fo:table-cell>
        </fo:table-row>
       </fo:table-header>

       <fo:table-body>
        <xsl:for-each select="/BaselineReport/sections/section[@name='Auditing and Logging']/subSection">
         <xsl:variable name="secname" select="@name"/>
         <fo:table-row background-color="{$table.bgcolor}" color="{$table.font.color}" border-top="1px solid {$table.color}">
          <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
           <fo:block id="{$secname}">
            <fo:marker marker-class-name="sectionTitle">Auditing and Logging / <xsl:value-of select="@name"/></fo:marker>
            <xsl:value-of select="@name"/>
           </fo:block>
          </fo:table-cell>
          <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="left" display-align="center">
           <fo:block linefeed-treatment="preserve" white-space-collapse="false" 
                    white-space-treatment="preserve" wrap-option="wrap" font-family="Courier" font-size="10pt">
            <xsl:value-of select="self::*"/>
           </fo:block>
          </fo:table-cell>
         </fo:table-row>
        </xsl:for-each>
       </fo:table-body>
      </fo:table>
     </xsl:if>

<!-- 
    =======================================================================
                               Hardware (Table)
    =======================================================================
-->
     <xsl:if test="count(/BaselineReport/sections/section[@name='Hardware']/subSection) != 0">
      <fo:block break-before="page">
        <fo:marker marker-class-name="sectionTitle">Hardware</fo:marker>
      </fo:block>
      <fo:table id="Hardware" table-layout="fixed" width="10in" xsl:use-attribute-sets="table">
       <fo:table-column column-width="proportional-column-width(1)"/>
       <fo:table-column column-width="proportional-column-width(6)"/>

       <fo:table-header>
        <fo:table-row xsl:use-attribute-sets="table-row-header">
         <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
          <fo:block font-weight="bold">Hardware</fo:block>
         </fo:table-cell>
         <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="right" display-align="center">
          <fo:block font-family="ZapfDingbats">
           <fo:basic-link internal-destination="top">&#x25B2;</fo:basic-link>
          </fo:block>
         </fo:table-cell>
        </fo:table-row>
       </fo:table-header>

       <fo:table-body>
        <xsl:for-each select="/BaselineReport/sections/section[@name='Hardware']/subSection">
         <xsl:variable name="secname" select="@name"/>
         <fo:table-row background-color="{$table.bgcolor}" color="{$table.font.color}" border-top="1px solid {$table.color}">
          <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
           <fo:block id="{$secname}">
            <fo:marker marker-class-name="sectionTitle">Hardware / <xsl:value-of select="@name"/></fo:marker>
            <xsl:value-of select="@name"/>
           </fo:block>
          </fo:table-cell>
          <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="left" display-align="center">
           <fo:block linefeed-treatment="preserve" white-space-collapse="false" 
                    white-space-treatment="preserve" wrap-option="wrap" font-family="Courier" font-size="10pt">
            <xsl:value-of select="self::*"/>
           </fo:block>
          </fo:table-cell>
         </fo:table-row>
        </xsl:for-each>
       </fo:table-body>
      </fo:table>
     </xsl:if>
<!-- 
        =======================================================================
                                    Network (Table)
        =======================================================================
-->
     <xsl:if test="count(/BaselineReport/sections/section[@name='Network']/subSection) != 0">
      <fo:block break-before="page">
        <fo:marker marker-class-name="sectionTitle">Network</fo:marker>
      </fo:block>
      <fo:table id="Network" table-layout="fixed" width="10in" xsl:use-attribute-sets="table"> 
       <fo:table-column column-width="proportional-column-width(1)"/>
       <fo:table-column column-width="proportional-column-width(6)"/>

       <fo:table-header>
        <fo:table-row xsl:use-attribute-sets="table-row-header">
         <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
          <fo:block font-weight="bold">Network</fo:block>
         </fo:table-cell>
         <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="right" display-align="center">
          <fo:block font-family="ZapfDingbats">
           <fo:basic-link internal-destination="top">&#x25B2;</fo:basic-link>
          </fo:block>
         </fo:table-cell>
        </fo:table-row>
       </fo:table-header>
       <fo:table-body>
        <xsl:for-each select="/BaselineReport/sections/section[@name='Network']/subSection">
         <xsl:variable name="secname" select="@name"/>
         <fo:table-row background-color="{$table.bgcolor}" color="{$table.font.color}" border-top="1px solid {$table.color}">
          <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
           <fo:block id="{$secname}">
            <fo:marker marker-class-name="sectionTitle">Network / <xsl:value-of select="@name"/></fo:marker>
            <xsl:value-of select="@name"/>
           </fo:block>
          </fo:table-cell>
          <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="left" display-align="center">
           <fo:block linefeed-treatment="preserve" white-space-collapse="false" 
                     white-space-treatment="preserve" wrap-option="wrap" font-family="Courier" font-size="10pt">
            <xsl:value-of select="self::*"/>
           </fo:block>
          </fo:table-cell>
         </fo:table-row>
        </xsl:for-each>
       </fo:table-body>
      </fo:table>
     </xsl:if>
<!-- 
        =======================================================================
                                  Software (Table)
        =======================================================================
-->
     <xsl:if test="count(/BaselineReport/sections/section[@name='Software']/subSection) != 0">
      <fo:block break-before="page">
        <fo:marker marker-class-name="sectionTitle">Software</fo:marker>
      </fo:block>
      <fo:table id="Software" table-layout="fixed" width="10in" xsl:use-attribute-sets="table">
       <fo:table-column column-width="proportional-column-width(1)"/>
       <fo:table-column column-width="proportional-column-width(3)"/>
       <fo:table-column column-width="proportional-column-width(1.5)"/>

       <fo:table-header>
        <fo:table-row xsl:use-attribute-sets="table-row-header" border-bottom="1px solid black">
         <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center" number-columns-spanned="2">
          <fo:block font-weight="bold">Software</fo:block>
         </fo:table-cell>
         <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="right" display-align="center">
          <fo:block font-family="ZapfDingbats">
           <fo:basic-link internal-destination="top">&#x25B2;</fo:basic-link>
          </fo:block>
         </fo:table-cell>
        </fo:table-row>

        <fo:table-row xsl:use-attribute-sets="table-row-subheader">
         <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
          <fo:block font-weight="bold">Package</fo:block>
         </fo:table-cell>
         <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
          <fo:block font-weight="bold">Description</fo:block>
         </fo:table-cell>
         <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
          <fo:block font-weight="bold">Version</fo:block>
         </fo:table-cell>
        </fo:table-row>
       </fo:table-header>

       <fo:table-body>
        <xsl:for-each select="/BaselineReport/sections/section[@name='Software']/subSection[@name='Packages']/packages/package">
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
         <fo:table-row background-color="{$rowColor}" color="{$table.font.color}" border-top="1px solid {$table.color}">
<!-- 
    | Package name 
    +-->
          <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
           <fo:block>
            <xsl:value-of select="@name"/>
           </fo:block>
          </fo:table-cell>
<!-- 
    | Package Description/Summary 
    +-->
          <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="left" display-align="center">
           <fo:block>
            <xsl:value-of select="@summary"/>
           </fo:block>
          </fo:table-cell>
<!-- 
    | Version and Release of Package 
    +-->
          <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="left" display-align="center">
           <fo:block>
            <xsl:value-of select="@version"/>
            <xsl:if test="@release != '' and @release != '-' ">
             <xsl:text>-</xsl:text>
             <xsl:value-of select="@release"/>
            </xsl:if>
           </fo:block>
<!-- 
    | Associaed Patches if they exist (Solaris) 
    +-->
           <xsl:variable name="pkgname" select="@name"/>
           <xsl:if test="count(../../../subSection[@name='Patches']/patches/patch[@pkg = $pkgname]) != 0">
            <fo:block margin-top="0.5em">Patches:</fo:block>
            <fo:list-block margin-left="1em" margin-bottom="1em" font-size="10pt" 
                          provisional-distance-between-starts="10pt" provisional-label-separation="3pt">
             <xsl:call-template name="software.patch.list">
              <xsl:with-param name="patches" select="../../../subSection[@name='Patches']/patches"/>
              <xsl:with-param name="pkgname" select="$pkgname"/>
             </xsl:call-template>
            </fo:list-block>
           </xsl:if>
          </fo:table-cell>

         </fo:table-row>
        </xsl:for-each>

       </fo:table-body>
      </fo:table>
     </xsl:if>

<!-- ============================================================== -->
<!--
    | Footer with Page number 
    +-->
     <fo:block id="terminator"/>
    </fo:flow>
   </fo:page-sequence>

  </fo:root>
 </xsl:template>
</xsl:stylesheet>
