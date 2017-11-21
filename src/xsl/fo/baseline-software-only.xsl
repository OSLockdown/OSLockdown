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
      
      Purpose: Baseline Report - Software Only (XML to FO -> PDF)
     =========================================================================
-->
 <xsl:include href="common-fo.xsl"/>

<!--
   Report Parameter Definitions:
     report.title     : Report title to be used in header 
     header.display   : if false, do not display header
     logo.display     : if false, do not display logo in header

-->
 <xsl:param name="report.title">Baseline Report - Installed Software</xsl:param>
 <xsl:param name="header.display">true</xsl:param>
 <xsl:param name="logo.display">true</xsl:param>
 <xsl:output method="xml" encoding="utf-8" indent="yes"/>
 <xsl:template match="/">
  <fo:root xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:fox="http://xmlgraphics.apache.org/fop/extensions">

   <fo:layout-master-set>
    <fo:simple-page-master master-name="first" 
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
       <dc:description>Baseline Report</dc:description>
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
   <fo:bookmark-tree>
    <fo:bookmark internal-destination="summaryTable">
     <fo:bookmark-title>Summary</fo:bookmark-title>
    </fo:bookmark>
    <fo:bookmark internal-destination="Software">
     <fo:bookmark-title>Software</fo:bookmark-title>
    </fo:bookmark>
   </fo:bookmark-tree>
   <fo:page-sequence master-reference="first" font-family="Helvetica" font-size="{$page.font.size}">
<!-- 
    =======================================================================
                           Report Footer (Static)
    =======================================================================
-->

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
                               Report Header 
    =======================================================================
-->
     <xsl:if test="$header.display = 'true'">
      <fo:table id="doctop" table-layout="fixed" background-color="{$report.header.bgcolor}" width="10in" border-spacing="0pt" margin-bottom="1em">
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
     <xsl:variable name="todaysEpoch" select="java:java.lang.System.currentTimeMillis()"/>
     <xsl:variable name="todaysDate"  select="java:format(java:java.text.SimpleDateFormat.new ('yyyy-MM-dd'), java:java.util.Date.new())"/>
     <xsl:variable name="leaders">.............................</xsl:variable>

     <fo:table id="summaryTable" table-layout="fixed" width="10in" background-color="{$table.bgcolor}" border-spacing="0pt" border="1px solid {$table.color}" margin-top="2em" margin-bottom="1em" font-size="{$table.font.size}">
      <fo:table-column column-width="proportional-column-width(1)"/>
      <fo:table-column column-width="proportional-column-width(6)"/>
      <fo:table-body>
       <fo:table-row background-color="{$table.color}" color="{$table.font.color}" font-size="{$table.header.font.size}">
        <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
         <fo:block font-weight="bold">Summary</fo:block>
        </fo:table-cell>
        <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="right" display-align="center">
         <fo:block font-weight="bold"><xsl:text>Created: </xsl:text><xsl:value-of select="/BaselineReport/report/@created"/></fo:block>
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

    <!-- Software Section -->
       <fo:table-row color="{$table.font.color}" border-bottom="1px solid {$table.color}">
        <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
         <fo:block>Activity</fo:block>
        </fo:table-cell>
        <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center">
         <fo:block padding-bottom="5px">Software installations or updates since <xsl:copy-of select="$todaysDate"/>:</fo:block>

         <fo:block-container margin-left="0.25in" width="4in" >
           <fo:block text-align-last="justify">
             <xsl:text>Within the last 30 days</xsl:text>
             <fo:leader leader-pattern="dots" />
             <xsl:value-of select="format-number(count(/BaselineReport/sections/section[@name='Software']/subSection/packages/package[@installtime &gt; (($todaysEpoch div 1000) - (86400 * 30))]), '###,###')"/>
            </fo:block>

           <!-- 30 to 90 days -->
           <fo:block text-align-last="justify">
               <xsl:text>Between the last 30 and 90 days</xsl:text>
               <fo:leader leader-pattern="dots" />
               <xsl:value-of select="format-number(count(/BaselineReport/sections/section[@name='Software']/subSection/packages/package[@installtime &gt; (($todaysEpoch div 1000) - (86400 * 90)) and @installtime &lt; (($todaysEpoch div 1000) - (86400 * 30))]), '###,###')"/> 
           </fo:block>

           <!-- 90 days or more -->
           <fo:block text-align-last="justify">
               <xsl:text>More than 90 days ago</xsl:text>
               <fo:leader leader-pattern="dots" />
              <xsl:value-of select="format-number(count(/BaselineReport/sections/section[@name='Software']/subSection/packages/package[@installtime &lt; (($todaysEpoch div 1000) - (86400 * 90))]), '###,###')"/>
            </fo:block>

          <!-- Total Packages -->
           <fo:block text-align-last="justify" space-before="5px" padding-bottom="5px">
            <xsl:text>Total Packages</xsl:text>
            <fo:leader leader-pattern="dots" />
            <xsl:value-of select="format-number(count(/BaselineReport/sections/section[@name='Software']/subSection/packages/package), '###,###')"/> 
           </fo:block>
         </fo:block-container>

        </fo:table-cell>
       </fo:table-row>

      </fo:table-body>
     </fo:table>
<!-- 
        =======================================================================
          Software (Table)
        =======================================================================
-->
     <fo:table id="Software" table-layout="fixed" width="10in" background-color="{$table.bgcolor}" border-spacing="0pt" border="1px solid {$table.color}" margin-top="2em" margin-bottom="1em">
      <fo:table-column column-width="proportional-column-width(1.5)"/>
      <fo:table-column column-width="proportional-column-width(3)"/>
      <fo:table-column column-width="proportional-column-width(1.5)"/>
      <fo:table-column column-width="proportional-column-width(0.5)"/>

    <!-- Table Header -->
      <fo:table-header>
       <fo:table-row background-color="{$table.color}" color="{$table.font.color}">
        <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center" number-columns-spanned="1">
         <fo:block font-weight="bold">Package</fo:block>
        </fo:table-cell>
        <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center" number-columns-spanned="1">
         <fo:block font-weight="bold">Description</fo:block>
        </fo:table-cell>
        <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="left" display-align="center" number-columns-spanned="1">
         <fo:block font-weight="bold">Version</fo:block>
        </fo:table-cell>
        <fo:table-cell padding="2px 5px 2px 5px" border-width="0pt" text-align="right" display-align="center" number-columns-spanned="1">
         <fo:block font-weight="bold">Installed</fo:block>
         <fo:block font-size="8pt" font-style="italic">(Days since <xsl:copy-of select="$todaysDate"/>)</fo:block>
        </fo:table-cell>
       </fo:table-row>
      </fo:table-header>

    <!-- Table Body -->
      <fo:table-body>
       <xsl:for-each select="/BaselineReport/sections/section[@name='Software']/subSection[@name='Packages']/packages/package">
        <xsl:sort select="@installtime" order="descending" data-type="number"/>
        <xsl:sort select="@name"/>

        <!-- Determine number of days since the package was installed -->
        <xsl:variable name="installEpoch" select="format-number((($todaysEpoch div 1000) - @installtime) div 86400, '#')"/> 

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

       <!-- Package name -->
         <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
          <fo:block>
           <xsl:value-of select="@name"/>
          </fo:block>
         </fo:table-cell>

       <!-- Package Description/Summary -->
         <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="left" display-align="center">
          <fo:block>
           <xsl:value-of select="@summary"/>
          </fo:block>
         </fo:table-cell>

       <!-- Version and Release of Package -->
         <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="left" display-align="center">
          <fo:block>
           <xsl:value-of select="@version"/>
           <xsl:if test="@release != '' and @release != '-' ">
            <xsl:text>-</xsl:text>
            <xsl:value-of select="@release"/>
           </xsl:if>
          </fo:block>

         <!-- Associaed Patches if they exist (Solaris) -->
          <xsl:variable name="pkgname" select="@name"/>
          <xsl:if test="count(../../../subSection[@name='Patches']/patches/patch[@pkg = $pkgname]) != 0">
           <fo:block margin-top="0.5em">Patches:</fo:block>
           <fo:list-block margin-left="1em" margin-bottom="1em" font-size="10pt" 
                          provisional-distance-between-starts="10pt" 
                          provisional-label-separation="3pt">
            <xsl:call-template name="software.patch.list">
             <xsl:with-param name="patches" select="../../../subSection[@name='Patches']/patches"/>
             <xsl:with-param name="pkgname" select="$pkgname"/>
            </xsl:call-template>
           </fo:list-block>
          </xsl:if>

         </fo:table-cell>

       <!-- Number days since installed -->
         <fo:table-cell padding="2px 5px 2px 5px" border-right="1px solid {$table.color}" text-align="right" display-align="center">
          <fo:block>
           <xsl:copy-of select="$installEpoch"/>
          </fo:block>
         </fo:table-cell>

        </fo:table-row>
       </xsl:for-each>

      </fo:table-body>
     </fo:table>

<!-- ==============================================================
               Footer with Page number -->
     <fo:block id="terminator"/>
    </fo:flow>
   </fo:page-sequence>
  </fo:root>
 </xsl:template>
</xsl:stylesheet>
