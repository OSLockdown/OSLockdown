<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- 
     =========================================================================
         Copyright (c) 2007-2014 Forcepoint LLC.
         This file is released under the GPLv3 license.  
         See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
	 or visit https://www.gnu.org/licenses/gpl.html instead.
         
         Purpose: Apply Report XML to TEXT
     =========================================================================
    -->
    <xsl:param name="report.lang">en</xsl:param>
    <xsl:param name="report.title">Apply Report</xsl:param>
    
    <xsl:include href="common-text.xsl"/>
    <xsl:output method="text" encoding="UTF-8" indent="yes" />
    
    <xsl:template match="/">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:value-of select="translate($report.title, $vLower, $vUpper)"/>
        <xsl:text>&#x0A;Created </xsl:text>
        <xsl:value-of select="/ApplyReport/report/@created"/>
        <xsl:text> by OS Lockdown v</xsl:text>
        <xsl:value-of select="/ApplyReport/@sbVersion"/>

        <xsl:text>&#x0A;&#x0A;</xsl:text>
        <xsl:text>Summary:&#x0A;</xsl:text>
        <xsl:text>--------------------------------------------------------------------</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:text>         Created: </xsl:text><xsl:value-of select="/ApplyReport/report/@created"/>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>        Hostname: </xsl:text><xsl:value-of select="/ApplyReport/report/@hostname"/>
        <xsl:text>&#x0A;</xsl:text>

        <xsl:text>Operating System: </xsl:text>
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
        <xsl:text>]&#x0A;</xsl:text>

        
        <xsl:text>         Profile: </xsl:text><xsl:value-of select="/ApplyReport/report/@profile"/>
        <xsl:text>&#x0A;</xsl:text>

        <xsl:variable name="modError" select="count(/ApplyReport/modules/module[@results='Error'])"/>
        <xsl:variable name="modApplied" select="count(/ApplyReport/modules/module[@results='Applied'])"/>
        <xsl:variable name="modOther" select="count(/ApplyReport/modules/module[@results !='Applied' and @results !='Error'])"/>
        
        <xsl:text>&#x0A;</xsl:text> 
        <xsl:text> Modules Applied: </xsl:text><xsl:value-of select="$modApplied"/>
        <xsl:text> (</xsl:text>
        <xsl:value-of select="round(($modError div ($modError + $modApplied)) * 100)"/>
        <xsl:text>%) &#x0A;</xsl:text>
        
        <xsl:text>          Errors: </xsl:text><xsl:value-of select="$modError"/>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>           Other: </xsl:text><xsl:value-of select="$modOther"/>
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:text>&#x0A;</xsl:text>

        <xsl:if test="count(/ApplyReport/modules/module[@results='Applied']) != 0">
            <xsl:text>&#x0A;Applied:&#x0A;</xsl:text>
            <xsl:text>--------------------------------------------------------------------&#x0A;</xsl:text>
            <xsl:for-each select="/ApplyReport/modules/module[@results='Applied']">
                <xsl:sort select="@name"/>
                <xsl:variable name="spaces">.............................</xsl:variable>
                <xsl:text>   </xsl:text>
                <xsl:value-of select="substring(concat(@name, $spaces, $spaces), 1, 60)"/>
                <xsl:value-of select="@results"/>
                <xsl:text>&#x0A;</xsl:text>
            </xsl:for-each>
        </xsl:if>
        
        <xsl:if test="count(/ApplyReport/modules/module[@results='Error']) != 0">
            <xsl:text>&#x0A;Errors:&#x0A;</xsl:text>
            <xsl:text>--------------------------------------------------------------------&#x0A;</xsl:text>
            <xsl:for-each select="/ApplyReport/modules/module[@results='Error']">
                <xsl:sort select="@name"/>
                <xsl:variable name="spaces">.............................</xsl:variable>
                <xsl:text>   </xsl:text>
                <xsl:value-of select="substring(concat(@name, $spaces, $spaces), 1, 60)"/>
                <xsl:value-of select="@results"/>
                <xsl:text>&#x0A;</xsl:text>
            </xsl:for-each>
        </xsl:if>
        
        <xsl:if test="count(/ApplyReport/modules/module[@results != 'Applied' or @results != 'Error']) != 0">
            <xsl:text>&#x0A;Not required or not applicable:&#x0A;</xsl:text>
            <xsl:text>--------------------------------------------------------------------&#x0A;</xsl:text>
            <xsl:for-each select="/ApplyReport/modules/module[@results != 'Applied' and @results != 'Error']">
                <xsl:sort select="@name"/>
                <xsl:variable name="spaces">.............................</xsl:variable>
                <xsl:text>   </xsl:text>
                <xsl:value-of select="substring(concat(@name, $spaces, $spaces), 1, 60)"/>
                <xsl:value-of select="@results"/>
                <xsl:text>&#x0A;</xsl:text>
            </xsl:for-each>
        </xsl:if>
        
    </xsl:template>
</xsl:stylesheet>
