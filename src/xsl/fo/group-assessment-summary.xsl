<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Group Assessment Summary Report XML to FO -> PDF
     =========================================================================
-->
 <!-- <xsl:include href="fo-report-styles.xsl"/> -->
 <xsl:include href="styles-executive.xsl"/>
 <xsl:include href="common-fo.xsl"/>
<!--
   Report Parameter Definitions:
     report.title     : Report title to be used in header 
     header.display   : if false, do not display header
     logo.display     : if false, do not display logo in header

     module.display.description : if false, do not show module description and compliancy
-->
 <xsl:param name="report.title">Group Assessment Summary Report</xsl:param>
 <xsl:param name="header.display">true</xsl:param>
 <xsl:param name="logo.display">true</xsl:param>
 <xsl:param name="modules.display.description">false</xsl:param>

 <xsl:output method="xml" encoding="utf-8" indent="yes"/>

 <xsl:template match="/">
  <fo:root xmlns:fo="http://www.w3.org/1999/XSL/Format" 
           xmlns:fox="http://xmlgraphics.apache.org/fop/extensions">

    <!-- Landscape - So we switch height/width -->
   <fo:layout-master-set>
    <fo:simple-page-master master-name="first" 
                           page-width="{$page.height}" page-height="{$page.width}" 
                           margin-top="0.25in" margin-bottom="0.5in" 
                           margin-right="0.5in" margin-left="0.5in">
     <fo:region-body margin-top="0.25in" margin-bottom="0.25in"/>
     <fo:region-before extent="0.5in"/>
     <fo:region-after extent="0.25in"/>
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
   <fo:page-sequence master-reference="first" xsl:use-attribute-sets="default-font" >

<!--
    | Footer (Static)
    +-->
    <fo:static-content flow-name="xsl-region-after">
     <fo:block font-style="italic" margin-top="5px" font-size="10pt" text-align="right" color="#467fc5">
      OS Lockdown
     </fo:block>
    </fo:static-content>

<!--
    | Begin non-static elements (flow)
    +-->
    <fo:flow flow-name="xsl-region-body">

    <fo:block font-size="24pt">
     <xsl:copy-of select="$report.title"/>
    </fo:block>

    <xsl:variable name="groupName" select="/GroupAssessmentReport/@groupName"/>
    <xsl:variable name="reportCount" select="count(/GroupAssessmentReport/reports/report)"/>
    <xsl:variable name="missingReports" select="count(/GroupAssessmentReport/missing/client)"/>


  <!-- =======================================================================
      | Overview Box
      +-->
    <fo:block-container absolute-position="fixed" top="1.3in" left="0.5in" width="5in" height="2.25in"
                     border-style="solid" border-width="1px" border-color="#A19670" line-height="18pt">

      <fo:block margin-top="1.8em" margin-left="10px" margin-right="10px" font-size="80%" text-align-last="justify">
          <xsl:text>Group name </xsl:text>
          <fo:leader leader-pattern="dots" />
          <fo:inline color="#980230">&#x201C;<xsl:value-of select="/GroupAssessmentReport/@groupName"/>&#x201D;</fo:inline>
      </fo:block>
      <fo:block margin-left="10px" margin-right="10px" font-size="80%" text-align-last="justify">
          <xsl:text>Number of clients </xsl:text>
          <fo:leader leader-pattern="dots" />
          <xsl:value-of select="$reportCount + $missingReports"/>      
      </fo:block>
      <fo:block margin-left="10px" margin-right="10px" font-size="80%" text-align-last="justify">
          <xsl:text>Missing client reports </xsl:text>
          <fo:leader leader-pattern="dots" />
          <xsl:value-of select="$missingReports"/>      
      </fo:block>
      <fo:block margin-left="10px" margin-right="10px" font-size="80%" text-align-last="justify">
          <xsl:text>Assessment date </xsl:text>
          <fo:leader leader-pattern="dots" />
          <xsl:value-of select="substring(/GroupAssessmentReport/@created,1,20)"/>
      </fo:block>
      <fo:block margin-left="10px" margin-right="10px" font-size="80%" text-align-last="justify">
          <xsl:text>Profile name </xsl:text>
          <fo:leader leader-pattern="dots" />
          <xsl:value-of select="/GroupAssessmentReport/reports/report[1]/@profile"/>
      </fo:block>
      <fo:block margin-left="10px" margin-right="10px" font-size="80%" text-align-last="justify">
          <xsl:text>Number of security modules in the profile</xsl:text>
          <fo:leader leader-pattern="dots" />
          <xsl:value-of select="count(/GroupAssessmentReport/modules/module)"/>
      </fo:block>
      <xsl:variable name="totalPass" select="count(/GroupAssessmentReport/modules/module/clients/client[@results='Pass'])"/>
      <xsl:variable name="totalFail" select="count(/GroupAssessmentReport/modules/module/clients/client[@results='Fail'])"/>
      <xsl:variable name="totalNA" select="count(/GroupAssessmentReport/modules/module/clients/client[@results != 'Fail' and @results != 'Pass'])"/>

      <fo:block margin-left="10px" margin-right="10px" font-size="80%" text-align-last="justify">
          <xsl:text>Failures </xsl:text>
          <fo:leader leader-pattern="dots" />
          <xsl:variable name="failurePerc" select="($totalFail div ($totalPass + $totalNA + $totalFail)) * 100"/>
          <fo:inline color="red">
            <xsl:choose>
              <xsl:when test="$failurePerc &lt; 1">less than 1%</xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="format-number($failurePerc,'###')"/><xsl:text>%</xsl:text></xsl:otherwise>
            </xsl:choose>
          </fo:inline>
      </fo:block>

    </fo:block-container>
   <!--
       | Box Label 
       +-->
    <fo:block-container absolute-position="fixed" top="1.2in" left="0.7in" 
                        width="1.5in" height="1.4em" background-color="#C8C5A1">
        <fo:block padding-top="2px" text-align="center" font-size="12pt">
           Overview
        </fo:block>
    </fo:block-container>

  <!-- =======================================================================
      | Compliancy Box
      +-->
    <fo:block-container absolute-position="fixed" top="3.8in" left="0.5in" width="5in" height="3.9in"
                     border-style="solid" border-width="1px" border-color="#A19670" line-height="18pt">
      <fo:block margin-top="2em" margin-left="10px" margin-right="10px" font-size="70%" line-height="12pt">
          Based on the modules included in the security profile, the group's compliancy 
          with standards set forth by security organizations are as follows:
      </fo:block>

      <fo:block margin-top="1em" margin-left="10px" margin-right="10px" font-size="80%" 
                text-align-last="justify" font-weight="bold" color="green" 
                border-bottom-style="solid" border-bottom-color="green" border-bottom-width="1px">
           <xsl:text>Organization</xsl:text>
           <fo:leader leader-pattern="space" />
           <xsl:text>Passed</xsl:text>
      </fo:block>

      <fo:block margin-left="10px" margin-right="10px" font-size="80%" text-align-last="justify">
          <xsl:variable name="totalFail" select="count(/GroupAssessmentReport/modules/module/clients/client[@results='Fail']/../../compliancy/line-item[@source='CIS'])"/>
          <xsl:variable name="totalPass" select="count(/GroupAssessmentReport/modules/module/clients/client[@results='Pass']/../../compliancy/line-item[@source='CIS'])"/>
          <xsl:variable name="totalNA" select="count(/GroupAssessmentReport/modules/module/clients/client[@results != 'Pass' and @results != 'Fail']/../../compliancy/line-item[@source='CIS'])"/>
          <xsl:variable name="passPerc" select="(($totalPass + $totalNA) div ($totalPass + $totalNA + $totalFail)) * 100"/>
          <xsl:text>Center for Internet Security Benchmarks (</xsl:text>
          <xsl:value-of select="format-number(($totalPass + $totalNA + $totalFail),'###,###')" />
          <xsl:text> checks)</xsl:text>
          <fo:leader leader-pattern="dots" />
          <xsl:choose>
            <xsl:when test="$passPerc &lt; 1">less than 1%</xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="format-number($passPerc,'###')"/><xsl:text>%</xsl:text></xsl:otherwise>
          </xsl:choose>
      </fo:block>

      <fo:block margin-left="10px" margin-right="10px" font-size="80%" text-align-last="justify">
          <xsl:variable name="totalFail" select="count(/GroupAssessmentReport/modules/module/clients/client[@results='Fail']/../../compliancy/line-item[@source='PCI'])"/>
          <xsl:variable name="totalPass" select="count(/GroupAssessmentReport/modules/module/clients/client[@results='Pass']/../../compliancy/line-item[@source='PCI'])"/>
          <xsl:variable name="totalNA" select="count(/GroupAssessmentReport/modules/module/clients/client[@results != 'Pass' and @results != 'Fail']/../../compliancy/line-item[@source='PCI'])"/>
          <xsl:variable name="passPerc" select="(($totalPass + $totalNA) div ($totalPass + $totalNA + $totalFail)) * 100"/>
          <xsl:text>PCI Data Security Standard (</xsl:text>
          <xsl:value-of select="format-number(($totalPass + $totalNA + $totalFail),'###,###')" />
          <xsl:text> checks)</xsl:text>
          <fo:leader leader-pattern="dots" />
          <xsl:choose>
            <xsl:when test="$passPerc &lt; 1">less than 1%</xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="format-number($passPerc,'###')"/><xsl:text>%</xsl:text></xsl:otherwise>
          </xsl:choose>
      </fo:block>

      <fo:block margin-left="10px" margin-right="10px" font-size="80%" text-align-last="justify">
          <xsl:variable name="totalFail" select="count(/GroupAssessmentReport/modules/module/clients/client[@results='Fail']/../../compliancy/line-item[@source='CAG'])"/>
          <xsl:variable name="totalPass" select="count(/GroupAssessmentReport/modules/module/clients/client[@results='Pass']/../../compliancy/line-item[@source='CAG'])"/>
          <xsl:variable name="totalNA" select="count(/GroupAssessmentReport/modules/module/clients/client[@results != 'Pass' and @results != 'Fail']/../../compliancy/line-item[@source='CAG'])"/>
          <xsl:variable name="passPerc" select="(($totalPass + $totalNA) div ($totalPass + $totalNA + $totalFail)) * 100"/>
          <xsl:text>Consensus Audit Guidelines (</xsl:text>
          <xsl:value-of select="format-number(($totalPass + $totalNA + $totalFail),'###,###')" />
          <xsl:text> checks)</xsl:text>
          <fo:leader leader-pattern="dots" />
          <xsl:choose>
            <xsl:when test="$passPerc &lt; 1">less than 1%</xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="format-number($passPerc,'###')"/><xsl:text>%</xsl:text></xsl:otherwise>
          </xsl:choose>
      </fo:block>

      <fo:block margin-left="10px" margin-right="10px" font-size="80%" text-align-last="justify">
          <xsl:variable name="totalFail" select="count(/GroupAssessmentReport/modules/module/clients/client[@results='Fail']/../../compliancy/line-item[@source='FERC'])"/>
          <xsl:variable name="totalPass" select="count(/GroupAssessmentReport/modules/module/clients/client[@results='Pass']/../../compliancy/line-item[@source='FERC'])"/>
          <xsl:variable name="totalNA" select="count(/GroupAssessmentReport/modules/module/clients/client[@results != 'Pass' and @results != 'Fail']/../../compliancy/line-item[@source='FERC'])"/>
          <xsl:variable name="passPerc" select="(($totalPass + $totalNA) div ($totalPass + $totalNA + $totalFail)) * 100"/>
          <xsl:text>FERC Critical Infrastructure Protection (</xsl:text>
          <xsl:value-of select="format-number(($totalPass + $totalNA + $totalFail),'###,###')" />
          <xsl:text> checks)</xsl:text>
          <fo:leader leader-pattern="dots" />
          <xsl:choose>
            <xsl:when test="$passPerc &lt; 1">less than 1%</xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="format-number($passPerc,'###')"/><xsl:text>%</xsl:text></xsl:otherwise>
          </xsl:choose>
      </fo:block>

      <fo:block margin-left="10px" margin-right="10px" font-size="80%" text-align-last="justify">
          <xsl:variable name="totalFail" select="count(/GroupAssessmentReport/modules/module/clients/client[@results='Fail']/../../compliancy/line-item[@source='DISA'])"/>
          <xsl:variable name="totalPass" select="count(/GroupAssessmentReport/modules/module/clients/client[@results='Pass']/../../compliancy/line-item[@source='DISA'])"/>
          <xsl:variable name="totalNA" select="count(/GroupAssessmentReport/modules/module/clients/client[@results != 'Pass' and @results != 'Fail']/../../compliancy/line-item[@source='DISA'])"/>
          <xsl:variable name="passPerc" select="(($totalPass + $totalNA) div ($totalPass + $totalNA + $totalFail)) * 100"/>
          <xsl:text>U.S. Defense Information Systems Agency (</xsl:text>
          <xsl:value-of select="format-number(($totalPass + $totalNA + $totalFail),'###,###')" />
          <xsl:text> checks)</xsl:text>
          <fo:leader leader-pattern="dots" />
          <xsl:choose>
            <xsl:when test="$passPerc &lt; 1">less than 1%</xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="format-number($passPerc,'###')"/><xsl:text>%</xsl:text></xsl:otherwise>
          </xsl:choose>
      </fo:block>

      <fo:block margin-left="10px" margin-right="10px" font-size="80%" text-align-last="justify">
          <xsl:variable name="totalFail" select="count(/GroupAssessmentReport/modules/module/clients/client[@results='Fail']/../../compliancy/line-item[@source='DoD'])"/>
          <xsl:variable name="totalPass" select="count(/GroupAssessmentReport/modules/module/clients/client[@results='Pass']/../../compliancy/line-item[@source='DoD'])"/>
          <xsl:variable name="totalNA" select="count(/GroupAssessmentReport/modules/module/clients/client[@results != 'Pass' and @results != 'Fail']/../../compliancy/line-item[@source='DoD'])"/>
          <xsl:variable name="passPerc" select="(($totalPass + $totalNA) div ($totalPass + $totalNA + $totalFail)) * 100"/>
          <xsl:text>U.S. Department of Defense (</xsl:text>
          <xsl:value-of select="format-number(($totalPass + $totalNA + $totalFail),'###,###')" />
          <xsl:text> checks)</xsl:text>
          <fo:leader leader-pattern="dots" />
          <xsl:choose>
            <xsl:when test="$passPerc &lt; 1">less than 1%</xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="format-number($passPerc,'###')"/><xsl:text>%</xsl:text></xsl:otherwise>
          </xsl:choose>
      </fo:block>

      <fo:block margin-left="10px" margin-right="10px" font-size="80%" text-align-last="justify">
          <xsl:variable name="totalFail" select="count(/GroupAssessmentReport/modules/module/clients/client[@results='Fail']/../../compliancy/line-item[@source='CIA'])"/>
          <xsl:variable name="totalPass" select="count(/GroupAssessmentReport/modules/module/clients/client[@results='Pass']/../../compliancy/line-item[@source='CIA'])"/>
          <xsl:variable name="totalNA" select="count(/GroupAssessmentReport/modules/module/clients/client[@results != 'Pass' and @results != 'Fail']/../../compliancy/line-item[@source='CIA'])"/>
          <xsl:variable name="passPerc" select="(($totalPass + $totalNA) div ($totalPass + $totalNA + $totalFail)) * 100"/>
          <xsl:text>U.S. Central Intelligence Agency (</xsl:text>
          <xsl:value-of select="format-number(($totalPass + $totalNA + $totalFail),'###,###')" />
          <xsl:text> checks)</xsl:text>
          <fo:leader leader-pattern="dots" />
          <xsl:choose>
            <xsl:when test="$passPerc &lt; 1">less than 1%</xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="format-number($passPerc,'###')"/><xsl:text>%</xsl:text></xsl:otherwise>
          </xsl:choose>
      </fo:block>

    </fo:block-container>
   <!--
       | Box Label 
       +-->
    <fo:block-container absolute-position="fixed" top="3.7in" left="0.7in" 
                        width="1.5in" height="1.4em" background-color="#C8C5A1">
        <fo:block padding-top="2px" text-align="center" font-size="12pt">
           Compliancy
        </fo:block>
    </fo:block-container>

  <!-- =======================================================================
      | Group Assets (Graphs)
      +-->
    <fo:block-container absolute-position="fixed" top="3.8in" left="6in" width="4.5in" height="3.9in"
                     border-style="solid" border-width="1px" border-color="#A19670" line-height="18pt">

      <fo:block-container absolute-position="fixed" top="4.2in" left="6.0in" font-size="80%" text-align="left">
         <!-- Labels -->
         <fo:block-container width="38px">
           <xsl:if test="count(/GroupAssessmentReport/reports/report[@dist='redhat' and @distVersion &lt; 10]) != 0">
            <fo:block space-before="5px" font-size="70%" text-align="right" color="#980230">
                  Red Hat
            </fo:block>
           </xsl:if>
           <xsl:if test="count(/GroupAssessmentReport/reports/report[@dist='SuSE']) != 0">
            <fo:block space-before="5px" font-size="70%" text-align="right" color="#669900">
                  SUSE Linux
            </fo:block>
           </xsl:if>
         </fo:block-container>

          <!-- 
              | Bar Graphs (Data)  Max Width is 250px ( = 100%) 
              +-->
         <xsl:variable name="totalReports" select="count(/GroupAssessmentReport/reports/report)"/>
         <fo:block-container absolute-position="fixed" top="4.2in" left="6.6in" padding-bottom="5px"
                             padding-top="5px" padding-left="0" border-left-style="solid" 
                             border-left-width="1px" border-left-color="#315581">

           <xsl:variable name="redhatCount" select="count(/GroupAssessmentReport/reports/report[@dist='redhat' and @distVersion &lt; 10])"/>
           <xsl:if test="$redhatCount != 0">
             <xsl:variable name="pixWidth" select="concat(format-number(($redhatCount div $totalReports) * 250, '###'),'px')" />
             <fo:block-container space-before="5px" margin-left="0" width="{$pixWidth}" color="white" background-color="#980230">
              <fo:block text-align="center">
                <xsl:copy-of select="$redhatCount"/>
              </fo:block>
            </fo:block-container>
           </xsl:if>

           <xsl:variable name="suseCount" select="count(/GroupAssessmentReport/reports/report[@dist='SuSE'])"/>
           <xsl:if test="$suseCount != 0">
             <xsl:variable name="pixWidth" select="concat(format-number(($suseCount div $totalReports) * 250, '###'),'px')" />
             <fo:block-container space-before="5px" margin-left="0" width="{$pixWidth}" color="black" background-color="#669900">
              <fo:block text-align="center">
                <xsl:copy-of select="$suseCount"/>
             </fo:block>
            </fo:block-container>
           </xsl:if>

         </fo:block-container>
          <!-- Bottom Legend -->
          <fo:block-container margin-left="42px" width="250px" color="black" 
                              border-top-style="solid" border-top-width="1px" border-top-color="#315581"
                              space-before="5px">
              <fo:block margin-left="-15px" text-align-last="justify" font-size="70%" color="#315581">
                <xsl:text> </xsl:text>
                <fo:leader leader-pattern="space" />
                <xsl:text>50%</xsl:text>
                <fo:leader leader-pattern="space" />
                <xsl:text>100%</xsl:text>
              </fo:block>
          </fo:block-container>


      </fo:block-container>
    </fo:block-container>

   <!--
       | Box Label 
       +-->
    <fo:block-container absolute-position="fixed" top="3.7in" left="6.2in" 
                        width="1.5in" height="1.4em" background-color="#C8C5A1">
        <fo:block padding-top="2px" text-align="center" font-size="12pt">
           Group Assets
        </fo:block>
    </fo:block-container>


    </fo:flow>
   </fo:page-sequence>
  </fo:root>
 </xsl:template>
</xsl:stylesheet>
