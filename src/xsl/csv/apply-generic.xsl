<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Apply Report XML to CSV
     =========================================================================
-->
    <xsl:param name="report.title">Apply Report</xsl:param>
    
    <xsl:include href="common-csv.xsl"/>
    <xsl:output method="text" encoding="UTF-8" indent="yes" />
    
    <xsl:template match="/">
        <xsl:text>&#x0A;"</xsl:text>
        <xsl:value-of select="$report.title"/>
        <xsl:text> Summary","",""&#x0A;</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:text>"Created","</xsl:text><xsl:value-of select="/ApplyReport/report/@created"/>
        <xsl:text> by OS Lockdown v</xsl:text>
        <xsl:value-of select="/ApplyReport/@sbVersion"/>
        <xsl:text>",""&#x0A;</xsl:text>
        <xsl:text>"Hostname","</xsl:text><xsl:value-of select="/ApplyReport/report/@hostname"/>
        <xsl:text>",""&#x0A;</xsl:text>

        <xsl:text>"Operating System","</xsl:text>
        <xsl:variable name="distVersion" select="/ApplyReport/report/@distVersion"/>
        <xsl:variable name="dist" select="/ApplyReport/report/@dist"/>
        <xsl:choose>
            <xsl:when test="$distVersion = '10' and $dist = 'redhat'">
                <xsl:text>Fedora 10</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="/ApplyReport/report/@dist"/>
                <xsl:text> </xsl:text>
                <xsl:value-of select="/ApplyReport/report/@distVersion"/>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text> (</xsl:text>
        <xsl:value-of select="/ApplyReport/report/@arch"/>
        <xsl:text>) [Kernel </xsl:text>
        <xsl:value-of select="/ApplyReport/report/@kernel"/>
        <xsl:text>]",""&#x0A;</xsl:text>
        
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>"Profile","</xsl:text><xsl:value-of select="/ApplyReport/report/@profile"/>
        <xsl:text>",""&#x0A;</xsl:text>

        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>"Module Name","Results","Severity"&#x0A;</xsl:text>
        <xsl:for-each select="/ApplyReport/modules/module">
            <xsl:sort select="@name"/>
            <xsl:text>"</xsl:text><xsl:value-of select="@name"/>
            <xsl:text>","</xsl:text><xsl:value-of select="@results"/>
            <xsl:text>","</xsl:text><xsl:value-of select="@severity"/>
            <xsl:text>"&#x0A;</xsl:text>
        </xsl:for-each>
        
    </xsl:template>
</xsl:stylesheet>
