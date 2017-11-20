<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: assessment-comparison-generic.xsl 23917 2017-03-07 15:44:30Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Assessment Comparison Report XML to CSV
     =========================================================================
-->
    <xsl:param name="report.title">Assessment Comparison Report</xsl:param>
    
    <xsl:include href="common-csv.xsl"/>
    <xsl:output method="text" encoding="UTF-8" indent="yes" />
    
    <xsl:template match="/">
        <!-- 
              ================================================================ 
               Assessment Comparison Report Summary - Provide TOC of Report                         
              ================================================================
          -->
        <xsl:text>"</xsl:text>
        <xsl:copy-of select="translate($report.title, $vLower, $vUpper)"/>
        <xsl:text>"&#x0A;</xsl:text>

        <xsl:text>"Generated","</xsl:text>
        <xsl:value-of select="/AssessmentReportDelta/@created"/>
        <xsl:text>"&#x0A;</xsl:text>

        <xsl:text>"Generator","OS Lockdown v</xsl:text>
        <xsl:value-of select="/AssessmentReportDelta/@sbVersion"/>
        <xsl:text>"&#x0A;&#x0A;</xsl:text>
        
        <xsl:text>"","Report A","Report B"&#x0A;</xsl:text>

        <!-- System Names -->
        <xsl:text>"Hostname","</xsl:text>
        <xsl:value-of select="/AssessmentReportDelta/report[1]/@hostname"/>
        <xsl:text>","</xsl:text>
        <xsl:value-of select="/AssessmentReportDelta/report[2]/@hostname"/>
        <xsl:text>"&#x0A;</xsl:text>
        
        <!-- Creation Date of sub-reports -->
        <xsl:text>"Created","</xsl:text>
        <xsl:value-of select="/AssessmentReportDelta/report[1]/@created"/>
        <xsl:text>","</xsl:text>
        <xsl:value-of select="/AssessmentReportDelta/report[2]/@created"/>
        <xsl:text>"&#x0A;</xsl:text>
        
        
        <!-- Operating systems -->
        <xsl:text>"Operating System","</xsl:text>
        <xsl:choose>
            <xsl:when test="number(/AssessmentReportDelta/report[1]/@distVersion) &gt;= 10 and @dist = 'redhat'">
                <xsl:text>Fedora </xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="/AssessmentReportDelta/report[1]/@dist"/>
                <xsl:text> </xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:value-of select="/AssessmentReportDelta/report[1]/@distVersion"/>
        
        <xsl:text> (</xsl:text>
        <xsl:value-of select="/AssessmentReportDelta/report[1]/@arch"/>
        <xsl:text>) [Kernel </xsl:text>
        <xsl:value-of select="/AssessmentReportDelta/report[1]/@kernel"/>
        <xsl:text>]</xsl:text>
        <xsl:text>","</xsl:text>
        
        <xsl:choose>
            <xsl:when test="number(/AssessmentReportDelta/report[2]/@distVersion) &gt;= 10 and @dist = 'redhat'">
                <xsl:text>Fedora </xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="/AssessmentReportDelta/report[2]/@dist"/>
                <xsl:text> </xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:value-of select="/AssessmentReportDelta/report[2]/@distVersion"/>
        
        <xsl:text> (</xsl:text>
        <xsl:value-of select="/AssessmentReportDelta/report[2]/@arch"/>
        <xsl:text>) [Kernel </xsl:text>
        <xsl:value-of select="/AssessmentReportDelta/report[2]/@kernel"/>
        <xsl:text>]</xsl:text>
        <xsl:text>"&#x0A;</xsl:text>
        
        <xsl:text>"Profile","</xsl:text>
        <xsl:value-of select="/AssessmentReportDelta/report[1]/@profile"/>
        <xsl:text>","</xsl:text>
        <xsl:value-of select="/AssessmentReportDelta/report[2]/@profile"/>
        <xsl:text>"&#x0A;&#x0A;</xsl:text>
        
        <!-- Statistics -->
        <xsl:variable name="totalMods" select="count(/AssessmentReportDelta/*/module)"/>
        <xsl:variable name="xMods" select="count(/AssessmentReportDelta/removed/module) + count(/AssessmentReportDelta/added/module)"/>
        <xsl:variable name="changedMods" select="count(/AssessmentReportDelta/changed/module)"/>
        <xsl:variable name="unchangedMods" select="count(/AssessmentReportDelta/unchanged/module)"/>

        <xsl:choose>
            <xsl:when test="$changedMods = 1 ">
                <xsl:text>"Module with differing results"</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>"Modules with differing results"</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>,"</xsl:text>
        <xsl:value-of select="$changedMods"/>
        <xsl:text>"&#x0A;</xsl:text>
        
        <xsl:choose>
            <xsl:when test="$unchangedMods = 1 ">
                <xsl:text>"Module with same result"</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>"Modules with same results"</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>,"</xsl:text>
        <xsl:value-of select="$unchangedMods"/>
        <xsl:text>"&#x0A;</xsl:text>
        
        <xsl:choose>
            <xsl:when test="$xMods = 1 ">
                <xsl:text>"Module was present in only one report"</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>"Modules were present in only one report"</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>,"</xsl:text>
        <xsl:value-of select="$xMods"/>
        <xsl:text>"&#x0A;</xsl:text>
        
        <xsl:text>"Total modules","</xsl:text>
        <xsl:value-of select="$totalMods"/>
        <xsl:text>"&#x0A;&#x0A;</xsl:text>
        
        <!-- 
              ================================================================ 
                                       Changed Modules
              ================================================================
          -->
        <xsl:variable name="modules" select="/AssessmentReportDelta/changed/module"/>
        <xsl:if test="count($modules) != 0">
            <xsl:text>"MODULES WITH DIFFERING RESULTS","Severity","Report A","Report B"&#x0A;</xsl:text>
            
            <xsl:for-each select="$modules">
                <xsl:sort select="@name"/>
                
                <xsl:text>"</xsl:text>
                <xsl:value-of select="@name"/>
                <xsl:text>","</xsl:text>
                <xsl:value-of name="results" select="@severity"/>
                <xsl:text>","</xsl:text>
                <xsl:value-of name="results" select="@resultsA"/>
                <xsl:text>","</xsl:text>
                <xsl:value-of name="results" select="@resultsB"/>
                <xsl:text>"&#x0A;</xsl:text>
                
            </xsl:for-each>
        </xsl:if>
        
        <!-- 
              ================================================================ 
                 Modules which are not present in Both Reports
              ================================================================
          -->
        <xsl:variable name="delModules" select="/AssessmentReportDelta/removed/module"/>
        <xsl:variable name="addModules" select="/AssessmentReportDelta/added/module"/>
        <xsl:if test="count($delModules) != 0 or count($addModules) != 0">
              
                <xsl:text>&#x0A;"MODULES PRESENT IN ONLY ONE REPORT","Severity","Report A", "Report B"&#x0A;</xsl:text>
                
                <!-- Removed Modules -->
                <xsl:for-each select="$delModules">
                    <xsl:sort select="@name"/>
                    <xsl:text>"</xsl:text>
                    <xsl:value-of select="@name"/>
                    <xsl:text>","</xsl:text>
                    <xsl:value-of name="results" select="@severity"/>
                    <xsl:text>","</xsl:text>
                    <xsl:value-of name="results" select="@results"/>
                    <xsl:text>","-"&#x0A;</xsl:text>
                    
                </xsl:for-each>
                
                <!-- Added Modules -->
                <xsl:for-each select="$addModules">
                    <xsl:sort select="@name"/>
                    
                    <xsl:text>"</xsl:text>
                    <xsl:value-of select="@name"/>
                    <xsl:text>","-","</xsl:text>
                    <xsl:value-of name="results" select="@severity"/>
                    <xsl:text>","</xsl:text>
                    <xsl:value-of name="results" select="@results"/>
                    <xsl:text>"&#x0A;</xsl:text>
                    
                </xsl:for-each>
                
        </xsl:if>
        
        <!-- 
              ================================================================ 
                                       Unchanged Modules
              ================================================================
          -->
        <xsl:variable name="unmodules" select="/AssessmentReportDelta/unchanged/module"/>
        <xsl:if test="count($unmodules) != 0">
            <xsl:text>&#x0A;"MODULES WITH SAME RESULTS","Severity","Result"&#x0A;</xsl:text>
            
            <xsl:for-each select="$unmodules">
                <xsl:sort select="@name"/>
                
                <xsl:text>"</xsl:text>
                <xsl:value-of select="@name"/>
                <xsl:text>","</xsl:text>
                <xsl:value-of name="results" select="@severity"/>
                <xsl:text>","</xsl:text>
                <xsl:value-of name="results" select="@results"/>
                <xsl:text>"&#x0A;</xsl:text>
                
            </xsl:for-each>
        </xsl:if>
        <xsl:text>&#x0A;</xsl:text>
        
    </xsl:template>
</xsl:stylesheet>
