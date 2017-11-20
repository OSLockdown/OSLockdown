<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Baseline Report XML to TEXT
     =========================================================================
-->
    <xsl:param name="report.title">Baseline Report</xsl:param>
    
    <xsl:include href="common-text.xsl"/>
    <xsl:output method="text" encoding="UTF-8" indent="yes" />
    
    <xsl:template match="/">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:value-of select="translate($report.title, $vLower, $vUpper)"/>
        <xsl:text>&#x0A;Created </xsl:text>
        <xsl:value-of select="/BaselineReport/report/@created"/>
        <xsl:text> by OS Lockdown v</xsl:text>
        <xsl:value-of select="/BaselineReport/@sbVersion"/>

        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>Summary:&#x0A;</xsl:text>
        <xsl:text>====================================================================</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>        Hostname: </xsl:text><xsl:value-of select="/BaselineReport/report/@hostname"/>
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:text>Operating System: </xsl:text>
        <xsl:variable name="distVersion" select="/BaselineReport/report/@distVersion"/>
        <xsl:variable name="dist" select="/BaselineReport/report/@dist"/>
        <xsl:choose>
            <xsl:when test="$distVersion = '10' and $dist = 'redhat'">
                <xsl:text>Fedora 10</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="/BaselineReport/report/@dist"/>
                <xsl:text> </xsl:text>
                <xsl:value-of select="/BaselineReport/report/@distVersion"/>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text> (</xsl:text>
        <xsl:value-of select="/BaselineReport/report/@arch"/>
        <xsl:text>) [Kernel </xsl:text>
        <xsl:value-of select="/BaselineReport/report/@kernel"/>
        <xsl:text>]&#x0A;</xsl:text>
        <xsl:text>    Total Memory: </xsl:text><xsl:value-of select="/BaselineReport/report/@totalMemory"/>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>      Processors: </xsl:text><xsl:value-of select="/BaselineReport/report/@cpuInfo"/>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>====================================================================&#x0A;</xsl:text>
        <xsl:text>Files:&#x0A;</xsl:text>
        <xsl:text>====================================================================&#x0A;</xsl:text>
        <xsl:for-each select="/BaselineReport/sections/section[@name='Files']/subSection[@name != 'Device Files']">
            <xsl:variable name="secname" select="@name"/>
            <xsl:text> * </xsl:text>
            <xsl:value-of select="@name"/>
             <xsl:text> (</xsl:text>
             <xsl:value-of select="format-number(count(./files/file), '###,###')"/>
            <xsl:text>)&#x0A;</xsl:text>
        </xsl:for-each>

        <!-- Auditing and Logging Section -->
        <xsl:text>&#x0A;</xsl:text>
        <xsl:for-each select="/BaselineReport/sections/section[@name='Auditing and Logging']/subSection">
            <xsl:variable name="secname" select="@name"/>
            <xsl:text>====================================================================&#x0A;</xsl:text>
            <xsl:text>Auditing and Logging -&gt; </xsl:text><xsl:value-of select="normalize-space(@name)"/>
            <xsl:text>:&#x0A;</xsl:text>
            <xsl:text>====================================================================&#x0A;</xsl:text>
            <xsl:value-of select="self::*"/>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
        </xsl:for-each>
        
        <!-- Hardware Section -->
        <xsl:text>&#x0A;</xsl:text>
        <xsl:for-each select="/BaselineReport/sections/section[@name='Hardware']/subSection">
            <xsl:variable name="secname" select="@name"/>
            <xsl:text>====================================================================&#x0A;</xsl:text>
            <xsl:text>Hardware -&gt; </xsl:text><xsl:value-of select="normalize-space(@name)"/>
            <xsl:text>:&#x0A;</xsl:text>
            <xsl:text>====================================================================&#x0A;</xsl:text>
            <xsl:value-of select="self::*"/>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
        </xsl:for-each>
        
        <!-- Network Section -->
        <xsl:text>&#x0A;</xsl:text>
        <xsl:for-each select="/BaselineReport/sections/section[@name='Network']/subSection">
            <xsl:variable name="secname" select="@name"/>
            <xsl:text>====================================================================&#x0A;</xsl:text>
            <xsl:text>Network -&gt; </xsl:text><xsl:value-of select="normalize-space(@name)"/>
            <xsl:text>:&#x0A;</xsl:text>
            <xsl:text>====================================================================&#x0A;</xsl:text>
            <xsl:value-of select="self::*"/>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
        </xsl:for-each>
        
        <xsl:text>====================================================================&#x0A;</xsl:text>
        <xsl:text>Software -&gt; Installed Packages:&#x0A;</xsl:text>
        <xsl:text>====================================================================&#x0A;</xsl:text>
        <xsl:for-each select="/BaselineReport/sections/section[@name='Software']/subSection[@name='Packages']/packages/package">
            <xsl:sort select="@name"/>
            <!-- Package name -->
            <xsl:value-of select="@name"/>
            <xsl:text> (</xsl:text> <xsl:value-of select="@version"/>
            <xsl:if test="@release != '' and @release != '-' ">
                <xsl:text>-</xsl:text><xsl:value-of select="@release"/>
            </xsl:if>
            <xsl:text>) - </xsl:text><xsl:value-of select="@summary"/>
            <xsl:text>&#x0A;</xsl:text>
        </xsl:for-each>
        
        
    </xsl:template>
</xsl:stylesheet>
