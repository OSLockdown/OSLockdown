<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Profile Comparison Report XML to TEXT
     =========================================================================
-->
    <xsl:param name="report.title">Profile Comparison Report</xsl:param>
    
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
        <xsl:value-of select="substring(/ProfileDelta/@created,1,20)"/>
        <xsl:text> by OS Lockdown v</xsl:text>
        <xsl:value-of select="/ProfileDelta/@sbVersion"/>
        <xsl:text>&#x0A;&#x0A;</xsl:text>
        
        <xsl:text>Summary</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:call-template name="pad.line">
           <xsl:with-param name="count" select="80"/>
        </xsl:call-template>
        <xsl:text>&#x0A;</xsl:text>

        <!-- Profile Names -->
        <xsl:value-of select="substring(concat('    Profile A', $leaders, $leaders), 1, 25)"/>
        <xsl:value-of select="/ProfileDelta/profile[1]/@name"/>
        <xsl:text>&#x0A;</xsl:text>

        <xsl:value-of select="substring(concat('    Profile B', $leaders, $leaders), 1, 25)"/>
        <xsl:value-of select="/ProfileDelta/profile[2]/@name"/>
        <xsl:text>&#x0A;</xsl:text>
        
        <!-- Statistics -->
        <xsl:variable name="xMods" select="count(/ProfileDelta/removed/module)"/>
        <xsl:variable name="yMods" select="count(/ProfileDelta/added/module)"/>
        <xsl:variable name="changedMods" select="count(/ProfileDelta/changed/module)"/>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:value-of select="substring(concat('Differences', $leaders, $leaders, $leaders), 1, 25)"/>
        
        <xsl:call-template name="pad.spaces">
            <xsl:with-param name="count" select="4 - string-length($changedMods)"/>
        </xsl:call-template>
        <xsl:value-of select="$changedMods"/>
        <xsl:choose>
            <xsl:when test="$changedMods = 1 ">
                <xsl:text> module has different parameter values</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text> modules have different parameter values</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:call-template name="pad.spaces">
            <xsl:with-param name="count" select="25 + (4 - string-length($xMods))"/>
        </xsl:call-template>
        
        <xsl:value-of select="$xMods"/>
        <xsl:choose>
            <xsl:when test="$xMods = 1 ">
                <xsl:text> module was only present in Profile A</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text> modules were only present in Profile A</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>&#x0A;</xsl:text>

        <xsl:call-template name="pad.spaces">
            <xsl:with-param name="count" select="25 + (4 - string-length($yMods))"/>
        </xsl:call-template>
        <xsl:value-of select="$yMods"/>
        <xsl:choose>
            <xsl:when test="$yMods = 1 ">
                <xsl:text> module was only present in Profile B</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text> modules were only present in Profile B</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>&#x0A;</xsl:text>
        
        <!-- 
              ================================================================ 
                                       Changed Modules
              ================================================================
          -->
        <xsl:variable name="modules" select="/ProfileDelta/changed/module"/>
        <xsl:if test="count($modules) != 0">
            <xsl:text>&#x0A;&#x0A;MODULES WITH DIFFERENT PARAMETER VALUES&#x0A;</xsl:text>
            <xsl:call-template name="pad.line">
                <xsl:with-param name="count" select="80"/>
            </xsl:call-template>
            <xsl:text>&#x0A;</xsl:text>
            
            <xsl:for-each select="$modules">
                <xsl:sort select="@name"/>
                
                <xsl:text>&#x0A;* </xsl:text>
                <xsl:value-of select="@name"/>
                <xsl:text>&#x0A;    </xsl:text>

                <xsl:if test="./option"> 
                    <xsl:call-template name="textwrap">
                        <xsl:with-param name="original" select="translate(./option/description, '&#x20;&#x9;&#xD;&#xA;', ' ')"/>
                        <xsl:with-param name="maxLength" select="70"/>
                        <xsl:with-param name="separator" select="'&#x0A;    '"/>
                        <xsl:with-param name="wordWrap" select="'true'"/>
                    </xsl:call-template>
                    <xsl:text>&#x0A;</xsl:text>

                    <xsl:variable name="optionType">
                        <xsl:choose>
                            <xsl:when test="./option/@type">
                                <xsl:value-of select="./option/@type"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:text>xx</xsl:text>
                            </xsl:otherwise>
                        </xsl:choose>
                     </xsl:variable>

                    <!-- Don't Display the huge option values such as banners or audit rules -->
                    <xsl:if test="$optionType != 'basicMultilineString'">
                        <xsl:text>     - Profile A: </xsl:text>
                        <xsl:value-of select="./option/valueA"/>
                        <xsl:text> </xsl:text>
                        <xsl:value-of select="./option/units"/>
                        <xsl:text>&#x0A;</xsl:text>
           
                        <xsl:text>     - Profile B: </xsl:text>
                        <xsl:value-of select="./option/valueB"/>
                        <xsl:text> </xsl:text>
                        <xsl:value-of select="./option/units"/>
                        <xsl:text>&#x0A;</xsl:text>
                    </xsl:if>

                </xsl:if>

            </xsl:for-each>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
        </xsl:if>
        
        <!-- 
              ================================================================ 
                 Modules which are not present in Both Reports
              ================================================================
          -->
        <xsl:variable name="delModules" select="/ProfileDelta/removed/module"/>
        <xsl:variable name="addModules" select="/ProfileDelta/added/module"/>
        <xsl:if test="count($delModules) != 0">
                <xsl:text>MODULES ONLY PRESENT IN "</xsl:text>
                <xsl:value-of select="/ProfileDelta/profile[1]/@name"/>
                <xsl:text>"&#x0A;</xsl:text>
                
                <xsl:call-template name="pad.line">
                    <xsl:with-param name="count" select="80"/>
                </xsl:call-template>
                <xsl:text>&#x0A;</xsl:text>
                
                <!-- Removed Modules -->
                <xsl:for-each select="$delModules">
                    <xsl:sort select="@name"/>

                    <xsl:text>&#x0A;* </xsl:text>
                    <xsl:value-of select="@name"/>
                </xsl:for-each>
                <xsl:text>&#x0A;</xsl:text>
                <xsl:text>&#x0A;</xsl:text>
        </xsl:if>

        <xsl:if test="count($addModules) != 0">
                <xsl:text>&#x0A;</xsl:text>
                <!-- Added Modules -->
                <xsl:text>MODULES ONLY PRESENT IN "</xsl:text>
                <xsl:value-of select="/ProfileDelta/profile[2]/@name"/>
                <xsl:text>"&#x0A;</xsl:text>
                
                <xsl:call-template name="pad.line">
                    <xsl:with-param name="count" select="80"/>
                </xsl:call-template>
                <xsl:text>&#x0A;</xsl:text>

                <xsl:for-each select="$addModules">
                    <xsl:sort select="@name"/>

                    <xsl:text>&#x0A;* </xsl:text>
                    <xsl:value-of select="@name"/>
                </xsl:for-each>
                <xsl:text>&#x0A;</xsl:text>
                <xsl:text>&#x0A;</xsl:text>
                
        </xsl:if>
        
    </xsl:template>
</xsl:stylesheet>
