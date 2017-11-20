<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Assessment Comparison Report XML to TEXT
     =========================================================================
-->
    <xsl:param name="report.title">Assessment Comparison Report</xsl:param>
    
    <xsl:include href="common-text.xsl"/>
    <xsl:output method="text" encoding="UTF-8" indent="yes"/>
    
    <xsl:template match="/">
        <!-- 
              ================================================================ 
               Assessment Comparison Report Summary - Provide TOC of Report                         
              ================================================================
          -->
        <xsl:variable name="leaders">.............................</xsl:variable>

        <xsl:text>&#x0A;</xsl:text>
        <xsl:copy-of select="translate($report.title, $vLower, $vUpper)"/>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>Generated </xsl:text>
        <xsl:value-of select="substring(/AssessmentReportDelta/@created,1,20)"/>
        <xsl:text> by OS Lockdown v</xsl:text>
        <xsl:value-of select="/AssessmentReportDelta/@sbVersion"/>
        <xsl:text>&#x0A;&#x0A;</xsl:text>
        
        <xsl:text>Summary</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:call-template name="pad.line">
           <xsl:with-param name="count" select="50"/>
        </xsl:call-template>
        <xsl:text>&#x0A;</xsl:text>

        <!-- System Names -->
        <xsl:value-of select="substring(concat('    System A / B', $leaders, $leaders), 1, 25)"/>
        <xsl:value-of select="/AssessmentReportDelta/report[1]/@hostname"/>
        <xsl:text> / </xsl:text>
        <xsl:value-of select="/AssessmentReportDelta/report[2]/@hostname"/>
        <xsl:text>&#x0A;</xsl:text>
        
        <!-- Creation Date of sub-reports -->
        <xsl:value-of select="substring(concat('   Created A / B', $leaders, $leaders), 1, 25)"/>
        <xsl:value-of select="/AssessmentReportDelta/report[1]/@created"/>
        <xsl:text> / </xsl:text>
        <xsl:value-of select="/AssessmentReportDelta/report[2]/@created"/>
        <xsl:text>&#x0A;</xsl:text>
        
        
        <!-- Operating systems -->
        <xsl:value-of select="substring(concat('Operating System A', $leaders, $leaders), 1, 25)"/>
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
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:value-of select="substring(concat('                 B', $leaders, $leaders), 1, 25)"/>
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
        <xsl:text>&#x0A;&#x0A;</xsl:text>
        
        <xsl:value-of select="substring(concat('Profile A / B', $leaders, $leaders), 1, 25)"/>
        <xsl:value-of select="/AssessmentReportDelta/report[1]/@profile"/>
        <xsl:text> / </xsl:text>
        <xsl:value-of select="/AssessmentReportDelta/report[2]/@profile"/>
        <xsl:text>&#x0A;</xsl:text>
        
        <!-- Statistics -->
        <xsl:variable name="totalMods" select="count(/AssessmentReportDelta/*/module)"/>
        <xsl:variable name="xMods" select="count(/AssessmentReportDelta/removed/module) + count(/AssessmentReportDelta/added/module)"/>
        <xsl:variable name="changedMods" select="count(/AssessmentReportDelta/changed/module)"/>
        <xsl:variable name="unchangedMods" select="count(/AssessmentReportDelta/unchanged/module)"/>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:value-of select="substring(concat('Results', $leaders, $leaders, $leaders), 1, 25)"/>
        
        <xsl:call-template name="pad.spaces">
            <xsl:with-param name="count" select="4 - string-length($changedMods)"/>
        </xsl:call-template>
        <xsl:value-of select="$changedMods"/>
        <xsl:choose>
            <xsl:when test="$changedMods = 1 ">
                <xsl:text> module with differing results</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text> modules with differing results</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:call-template name="pad.spaces">
            <xsl:with-param name="count" select="25 + (4 - string-length($unchangedMods))"/>
        </xsl:call-template>
        
        <xsl:value-of select="$unchangedMods"/>
        <xsl:choose>
            <xsl:when test="$unchangedMods = 1 ">
                <xsl:text> module with same result</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text> modules with same result</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:call-template name="pad.spaces">
            <xsl:with-param name="count" select="25 + (4 - string-length($xMods))"/>
        </xsl:call-template>
        
        <xsl:value-of select="$xMods"/>
        <xsl:choose>
            <xsl:when test="$xMods = 1 ">
                <xsl:text> module was present in only one report</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text> modules were present in only one report</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:call-template name="pad.spaces">
            <xsl:with-param name="count" select="25"/>
        </xsl:call-template>
        <!-- <xsl:text>&#x2500;&#x2500;&#x2500;&#x2500;&#x2500;&#x0A;</xsl:text> -->
        <xsl:text>-----&#x0A;</xsl:text>
        
        <xsl:call-template name="pad.spaces">
            <xsl:with-param name="count" select="25 + (4 - string-length($totalMods))"/>
        </xsl:call-template>
        <xsl:value-of select="$totalMods"/>
        <xsl:text> total modules &#x0A;</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        
        <!-- 
              ================================================================ 
                                       Changed Modules
              ================================================================
          -->
        <xsl:variable name="modules" select="/AssessmentReportDelta/changed/module"/>
        <xsl:if test="count($modules) != 0">
            <xsl:text>&#x0A;&#x0A;DIFFERENCES OF MODULES PRESENT IN BOTH REPORTS (A/B)&#x0A;</xsl:text>
            <xsl:call-template name="pad.line">
                <xsl:with-param name="count" select="52"/>
            </xsl:call-template>
            <xsl:text>&#x0A;</xsl:text>
            
            <xsl:for-each select="$modules">
                <xsl:sort select="@name"/>
                
                <xsl:text>&#x0A;* </xsl:text>
                <xsl:value-of select="substring(concat(@name, $leaders, $leaders, $leaders), 1, 80)"/>
                <xsl:value-of name="results" select="@resultsA"/>
                <xsl:text> / </xsl:text> 
                <xsl:value-of name="results" select="@resultsB"/>
                
                <xsl:if test="@severity">
                  <xsl:text>&#x0A;    </xsl:text>
                  <xsl:text>Severity: </xsl:text><xsl:value-of select="@severity"/>
                </xsl:if>
                <xsl:text>&#x0A;    </xsl:text>
                <xsl:call-template name="textwrap">
                    <xsl:with-param name="original" select="./description"/>
                    <xsl:with-param name="maxLength" select="70"/>
                    <xsl:with-param name="separator" select="'&#x0A;    '"/>
                    <xsl:with-param name="wordWrap" select="'true'"/>
                </xsl:call-template>
                <xsl:text>&#x0A;</xsl:text>
                
                <xsl:call-template name="module.compliancy.list" >
                    <xsl:with-param name="compliancy" select="./compliancy"/>
                </xsl:call-template>
                <xsl:text>&#x0A;&#x0A;</xsl:text>
                
                
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
                <xsl:text>STATUS OF MODULES NOT PRESENT IN BOTH REPORTS&#x0A;</xsl:text>
                <xsl:call-template name="pad.line">
                    <xsl:with-param name="count" select="45"/>
                </xsl:call-template>
                <xsl:text>&#x0A;</xsl:text>
                
                <!-- Removed Modules -->
                <xsl:for-each select="$delModules">
                    <xsl:sort select="@name"/>
                    <xsl:text>&#x0A;* </xsl:text>
                    <xsl:value-of select="substring(concat(@name, $leaders, $leaders, $leaders), 1, 80)"/>
                    <xsl:value-of name="results" select="@results"/>
                    <xsl:text> /  -  &#x0A;</xsl:text>
                    
                    <xsl:if test="@severity">
                      <xsl:text>&#x0A;    </xsl:text>
                      <xsl:text>Severity: </xsl:text><xsl:value-of select="@severity"/>
                    </xsl:if>
                    <xsl:text>&#x0A;    </xsl:text>
                    <xsl:call-template name="textwrap">
                        <xsl:with-param name="original" select="./description"/>
                        <xsl:with-param name="maxLength" select="70"/>
                        <xsl:with-param name="separator" select="'&#x0A;    '"/>
                        <xsl:with-param name="wordWrap" select="'true'"/>
                    </xsl:call-template>
                    <xsl:text>&#x0A;</xsl:text>
                    
                    <xsl:call-template name="module.compliancy.list" >
                        <xsl:with-param name="compliancy" select="./compliancy"/>
                    </xsl:call-template>
                </xsl:for-each>
                
                <!-- Added Modules -->
                <xsl:for-each select="$addModules">
                    <xsl:sort select="@name"/>
                    
                    <xsl:text>&#x0A;* </xsl:text>
                    <xsl:value-of select="substring(concat(@name, $leaders, $leaders, $leaders), 1, 80)"/>
                    <xsl:text>  -  / </xsl:text>
                    <xsl:value-of name="results" select="@results"/>
                    <xsl:text>&#x0A;</xsl:text>
                    
                    <xsl:if test="@severity">
                      <xsl:text>&#x0A;    </xsl:text>
                      <xsl:text>Severity: </xsl:text><xsl:value-of select="@severity"/>
                    </xsl:if>
                    <xsl:text>&#x0A;    </xsl:text>
                    <xsl:call-template name="textwrap">
                        <xsl:with-param name="original" select="./description"/>
                        <xsl:with-param name="maxLength" select="70"/>
                        <xsl:with-param name="separator" select="'&#x0A;    '"/>
                        <xsl:with-param name="wordWrap" select="'true'"/>
                    </xsl:call-template>
                    
                    <xsl:text>&#x0A;</xsl:text>
                    <xsl:call-template name="module.compliancy.list" >
                        <xsl:with-param name="compliancy" select="./compliancy"/>
                    </xsl:call-template>
                </xsl:for-each>
                
        </xsl:if>
        
        <!-- 
              ================================================================ 
                                       Unchanged Modules
              ================================================================
          -->
        <xsl:variable name="unmodules" select="/AssessmentReportDelta/unchanged/module"/>
        <xsl:if test="count($unmodules) != 0">
            <xsl:text>&#x0A;MODULES WITH SAME RESULTS&#x0A;</xsl:text>
            <xsl:call-template name="pad.line">
                <xsl:with-param name="count" select="46"/>
            </xsl:call-template>
            <xsl:text>&#x0A;</xsl:text>
            
            <xsl:for-each select="$unmodules">
                <xsl:sort select="@name"/>
                
                <xsl:text>&#x0A;* </xsl:text>
                <xsl:value-of select="substring(concat(@name, $leaders, $leaders, $leaders), 1, 80)"/>
                <xsl:value-of name="results" select="@results"/>
                
                <xsl:if test="@severity">
                  <xsl:text>&#x0A;    </xsl:text>
                  <xsl:text>Severity: </xsl:text><xsl:value-of select="@severity"/>
                </xsl:if>
                <xsl:text>&#x0A;    </xsl:text>
                <xsl:call-template name="textwrap">
                    <xsl:with-param name="original" select="./description"/>
                    <xsl:with-param name="maxLength" select="70"/>
                    <xsl:with-param name="separator" select="'&#x0A;    '"/>
                    <xsl:with-param name="wordWrap" select="'true'"/>
                </xsl:call-template>
                <xsl:text>&#x0A;</xsl:text>
                
                <xsl:call-template name="module.compliancy.list" >
                    <xsl:with-param name="compliancy" select="./compliancy"/>
                </xsl:call-template>
            </xsl:for-each>
        </xsl:if>
        <xsl:text>&#x0A;</xsl:text>
        
    </xsl:template>
</xsl:stylesheet>
