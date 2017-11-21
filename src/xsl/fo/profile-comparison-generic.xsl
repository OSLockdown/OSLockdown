<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Profile Comparison Report XML to FO -> PDF
     =========================================================================
-->
 <xsl:include href="common-fo.xsl"/>
<!--
   Report Parameter Definitions:
     report.title     : Report title to be used in header 
     header.display   : if false, do not display header
     logo.display     : if false, do not display logo in header

-->
 <xsl:param name="report.title">Profile Comparison Report</xsl:param>
 <xsl:param name="header.display">true</xsl:param>
 <xsl:param name="logo.display">true</xsl:param>
 <xsl:param name="modules.display.description">true</xsl:param>
 <xsl:output method="xml" encoding="utf-8" indent="yes"/>
 <xsl:template match="/">
  <fo:root xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:fox="http://xmlgraphics.apache.org/fop/extensions">
   <fo:layout-master-set>
<!-- Report is landscape so, switch width and height -->
    <fo:simple-page-master master-name="first" page-height="{$page.width}" page-width="{$page.height}" margin-top="0.25in" margin-bottom="0.5in" margin-right="0.5in" margin-left="0.5in">
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
       <dc:description>Profile Comparison Report</dc:description>
      </rdf:Description>

<!-- XMP properties go here -->
      <rdf:Description xmlns:xmp="http://ns.adobe.com/xap/1.0/" rdf:about="">
       <xmp:CreatorTool>OS Lockdown</xmp:CreatorTool>
      </rdf:Description>

<!-- PDF properties go here -->
      <rdf:Description xmlns:pdf="http://ns.adobe.com/pdf/1.3/" rdf:about="">
       <pdf:Producer>OS Lockdown and Apache FOP</pdf:Producer>
       <pdf:Keywords>Profile</pdf:Keywords>
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
                      MAIN PAGE SEQUENCE
    =======================================================================
-->
   <fo:page-sequence master-reference="first" font-family="Helvetica" font-size="{$page.font.size}">
<!--
    | Footer (Static)
    +-->
    <fo:static-content flow-name="xsl-region-after">
     <fo:block margin-top="0.25in" font-size="10pt" text-align-last="justify" color="#467fc5">
         OS Lockdown v<xsl:value-of select="/ProfileDelta/@sbVersion"/>
      <fo:leader leader-pattern="space" />
      Page <fo:page-number/> of
      <fo:page-number-citation ref-id="terminator"/>
     </fo:block>
    </fo:static-content>
<!--
    | Begin main non-static flow
    +-->
    <fo:flow flow-name="xsl-region-body">
<!-- 
    =======================================================================
                  Report Header Banner (first page)
    =======================================================================
-->
     <xsl:if test="$header.display = 'true'">
      <fo:table id="doctop" table-layout="fixed" background-color="{$report.header.bgcolor}" width="10in" border-spacing="0pt" margin-bottom="1em">
       <fo:table-column column-width="proportional-column-width(2.5)"/>
       <fo:table-column column-width="proportional-column-width(1)"/>
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
            <xsl:otherwise><xsl:text></xsl:text>
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
      <fo:table-column column-width="proportional-column-width(3)"/>
      <fo:table-header>
       <fo:table-row background-color="{$report.header.bgcolor}">
        <fo:table-cell padding="2px 5px 2px 5px" text-align="left" >
         <fo:block font-weight="bold">
          <xsl:text>Summary</xsl:text>
         </fo:block>
        </fo:table-cell>
        <fo:table-cell padding="2px 5px 2px 5px" text-align="right">
         <fo:block font-weight="bold">
          <xsl:text>Generated: </xsl:text>
          <xsl:value-of select="substring(/ProfileDelta/@created,1,20)"/>
         </fo:block>
        </fo:table-cell>
       </fo:table-row>
      </fo:table-header>
      <fo:table-body>
       <xsl:variable name="report1" select="/ProfileDelta/report[1]"/>
       <xsl:variable name="report2" select="/ProfileDelta/report[2]"/>

<!-- Profile Names -->
       <fo:table-row color="{$table.font.color}">
        <fo:table-cell padding="2px 5px 2px 5px" text-align="right" >
         <fo:block>Profile A</fo:block>
        </fo:table-cell>
        <fo:table-cell padding="2px 5px 2px 5px" border-bottom="1px solid {$table.color}" border-left="1px solid {$table.color}" text-align="left" >
         <fo:block>
          <xsl:value-of select="/ProfileDelta/profile[1]/@name"/>
         </fo:block>
        </fo:table-cell>
       </fo:table-row>
       <fo:table-row color="{$table.font.color}">
        <fo:table-cell padding="2px 5px 2px 5px" text-align="right" display-align="center">
         <fo:block>Profile B</fo:block>
        </fo:table-cell>
        <fo:table-cell padding="2px 5px 2px 5px" border-bottom="1px solid {$table.color}" border-left="1px solid {$table.color}" text-align="left" display-align="center">
         <fo:block>
          <xsl:value-of select="/ProfileDelta/profile[2]/@name"/>
         </fo:block>
        </fo:table-cell>
       </fo:table-row>

<!-- Statistics -->
       <xsl:variable name="xMods" select="count(/ProfileDelta/removed/module)"/>
       <xsl:variable name="yMods" select="count(/ProfileDelta/added/module)"/>
       <xsl:variable name="changedMods" select="count(/ProfileDelta/changed/module)"/>
       <fo:table-row color="{$table.font.color}" font-size="{$table.font.size}">
        <fo:table-cell padding="2px 5px 2px 5px" text-align="right" >
         <fo:block>Differences</fo:block>
        </fo:table-cell>
        <fo:table-cell padding="2px 5px 2px 5px" border-bottom="1px solid {$table.color}" border-left="1px solid {$table.color}" text-align="left" display-align="center">
         <fo:block>
          <fo:list-block margin-left="5px" font-size="10pt"  
                         provisional-distance-between-starts="10pt"
                         provisional-label-separation="3pt">
           <fo:list-item>
            <fo:list-item-label end-indent="label-end()">
             <fo:block>
              &#x2022;
             </fo:block>
            </fo:list-item-label>
            <fo:list-item-body start-indent="body-start()">
             <fo:block>
              <xsl:value-of select="$changedMods"/>
              <xsl:choose>
               <xsl:when test="$changedMods = 1 "><xsl:text> module has different parameter values</xsl:text>
               </xsl:when>
               <xsl:otherwise><xsl:text> modules have different parameter values</xsl:text>
               </xsl:otherwise>
              </xsl:choose>
             </fo:block>
            </fo:list-item-body>
           </fo:list-item>
           <fo:list-item>
            <fo:list-item-label end-indent="label-end()">
             <fo:block> &#x2022; </fo:block>
            </fo:list-item-label>
            <fo:list-item-body start-indent="body-start()">
             <fo:block>
              <xsl:value-of select="$xMods"/>
              <xsl:choose>
               <xsl:when test="$xMods = 1 "><xsl:text> module was only present in Profile A</xsl:text>
               </xsl:when>
               <xsl:otherwise><xsl:text> modules were only present in Profile A</xsl:text>
               </xsl:otherwise>
              </xsl:choose>
             </fo:block>
            </fo:list-item-body>
           </fo:list-item>
           <fo:list-item>
            <fo:list-item-label end-indent="label-end()">
             <fo:block>
              &#x2022;
             </fo:block>
            </fo:list-item-label>
            <fo:list-item-body start-indent="body-start()">
             <fo:block>
              <xsl:value-of select="$yMods"/>
              <xsl:choose>
               <xsl:when test="$yMods = 1 "><xsl:text> module was only present in Profile B</xsl:text>
               </xsl:when>
               <xsl:otherwise><xsl:text> modules were only present in Profile B</xsl:text>
               </xsl:otherwise>
              </xsl:choose>
             </fo:block>
            </fo:list-item-body>
           </fo:list-item>
          </fo:list-block>
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
     <fo:table id="changedModules" table-layout="fixed" width="10in" background-color="{$table.bgcolor}" border-spacing="0pt" border="1px solid {$table.color}" margin-top="2em" margin-bottom="1em" font-size="{$table.font.size}">
      <fo:table-column column-width="proportional-column-width(3)"/>
      <fo:table-column column-width="proportional-column-width(1)"/>
      <fo:table-column column-width="proportional-column-width(1)"/>
      <fo:table-column column-width="proportional-column-width(.75)"/>
      <fo:table-header>
       <fo:table-row background-color="{$report.header.bgcolor}">
        <fo:table-cell padding="2px 5px 2px 5px" text-align="left" number-columns-spanned="4" display-align="center">
         <fo:block font-weight="bold">
          <xsl:text>Modules with different parameter values</xsl:text>
         </fo:block>
        </fo:table-cell>
       </fo:table-row>
      </fo:table-header>
      <fo:table-body>
       <fo:table-row>
        <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="left" display-align="center">
         <fo:block>
          <xsl:text>Module Name</xsl:text>
         </fo:block>
        </fo:table-cell>
        <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
         <fo:block>
          <xsl:value-of select="/ProfileDelta/profile[1]/@name"/>
         </fo:block>
        </fo:table-cell>
        <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
         <fo:block>
          <xsl:value-of select="/ProfileDelta/profile[2]/@name"/>
         </fo:block>
        </fo:table-cell>
        <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
         <fo:block>
          <xsl:text>Units</xsl:text>
         </fo:block>
        </fo:table-cell>
       </fo:table-row>
       <xsl:for-each select="/ProfileDelta/changed/module">
        <xsl:sort select="@name"/>
        <fo:table-row border-bottom="1px solid {$table.color}">
         <fo:table-cell padding="2px 5px 2px 5px" text-align="left">
          <fo:block>
           <xsl:value-of select="@name"/>
          </fo:block>
          <fo:block font-size="10pt" font-style="italic" margin-left="2em" margin-bottom="1em">
           <xsl:value-of select="./option/description"/>
          </fo:block>
         </fo:table-cell>
         <xsl:variable name="optionType">
          <xsl:choose>
           <xsl:when test="./option/@type">
            <xsl:value-of select="./option/@type"/>
           </xsl:when>
           <xsl:otherwise><xsl:text>xx</xsl:text>
           </xsl:otherwise>
          </xsl:choose>
         </xsl:variable>
         <xsl:choose>
          <xsl:when test="$optionType != 'basicMultilineString'">
           <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
            <fo:block>
             <xsl:value-of select="./option/valueA"/>
            </fo:block>
           </fo:table-cell>
           <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
            <fo:block>
             <xsl:value-of select="./option/valueB"/>
            </fo:block>
           </fo:table-cell>
          </xsl:when>
          <xsl:otherwise>
           <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center" number-columns-spanned="2">
            <fo:block font-style="italic" color="gray">
             Multi-line values are too large to show here.
            </fo:block>
           </fo:table-cell>
          </xsl:otherwise>
         </xsl:choose>
         <fo:table-cell border-left="1px solid {$table.color}" padding="2px 5px 2px 5px" text-align="center" display-align="center">
          <fo:block>
           <xsl:value-of select="./option/units"/>
          </fo:block>
         </fo:table-cell>
        </fo:table-row>
       </xsl:for-each>
      </fo:table-body>
     </fo:table>
<!-- 
      ================================================================ 
                 Modules only present in Profile A (Removed)
      ================================================================
-->
     <xsl:variable name="delModules" select="/ProfileDelta/removed/module"/>
     <xsl:if test="count($delModules) != 0">
      <fo:table id="xModules" table-layout="fixed" width="10in" background-color="{$table.bgcolor}" border-spacing="0pt" border="1px solid {$table.color}" margin-top="2em" margin-bottom="1em" font-size="{$table.font.size}">
       <fo:table-column column-width="proportional-column-width(1)"/>
       <fo:table-header>
        <fo:table-row background-color="{$report.header.bgcolor}">
         <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
          <fo:block font-weight="bold">
           <xsl:text>Modules only present in &#x201C;</xsl:text>
           <xsl:value-of select="/ProfileDelta/profile[1]/@name"/>
           <xsl:text>&#x201D;</xsl:text>
          </fo:block>
         </fo:table-cell>
        </fo:table-row>
       </fo:table-header>
       <fo:table-body>
        <fo:table-row>
         <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="left" display-align="center">
          <fo:block>Module Name</fo:block>
         </fo:table-cell>
        </fo:table-row>
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
         </fo:table-row>
        </xsl:for-each>
       </fo:table-body>
      </fo:table>
     </xsl:if>
<!-- 
      ================================================================ 
              Modules only present in Profile B (Added)
      ================================================================
-->
     <xsl:variable name="addModules" select="/ProfileDelta/added/module"/>
     <xsl:if test="count($addModules) != 0">
      <fo:table id="yModules" table-layout="fixed" width="10in" background-color="{$table.bgcolor}" border-spacing="0pt" border="1px solid {$table.color}" margin-top="2em" margin-bottom="1em" font-size="{$table.font.size}">
       <fo:table-column column-width="proportional-column-width(1)"/>
       <fo:table-header>
        <fo:table-row background-color="{$report.header.bgcolor}">
         <fo:table-cell padding="2px 5px 2px 5px" text-align="left" display-align="center">
          <fo:block font-weight="bold">
           <xsl:text>Modules only present in &#x201C;</xsl:text>
           <xsl:value-of select="/ProfileDelta/profile[2]/@name"/>
           <xsl:text>&#x201D;</xsl:text>
          </fo:block>
         </fo:table-cell>
        </fo:table-row>
       </fo:table-header>
       <fo:table-body>
        <fo:table-row>
         <fo:table-cell background-color="{$table.color}" padding="2px 5px 2px 5px" text-align="left" display-align="center">
          <fo:block>Module Name</fo:block>
         </fo:table-cell>
        </fo:table-row>
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
