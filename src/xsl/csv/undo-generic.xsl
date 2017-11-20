<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: undo-generic.xsl 23917 2017-03-07 15:44:30Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Undo Report XML to CSV
     =========================================================================
-->
    <xsl:param name="report.title">Undo Report</xsl:param>
    
    <xsl:include href="common-csv.xsl"/>
    <xsl:output method="text" encoding="UTF-8" indent="yes" />
    
    <xsl:template match="/">
        <xsl:text>&#x0A;"</xsl:text>
        <xsl:value-of select="$report.title"/>
        <xsl:text> Summary","",""&#x0A;</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:text>"Created","</xsl:text><xsl:value-of select="/UndoReport/report/@created"/>
        <xsl:text> by OS Lockdown v</xsl:text>
        <xsl:value-of select="/UndoReport/@sbVersion"/>
        <xsl:text>",""&#x0A;</xsl:text>
        <xsl:text>"Hostname","</xsl:text><xsl:value-of select="/UndoReport/report/@hostname"/>
        <xsl:text>",""&#x0A;</xsl:text>

        <xsl:text>"Operating System","</xsl:text>
        <xsl:variable name="distVersion" select="/UndoReport/report/@distVersion"/>
        <xsl:variable name="dist" select="/UndoReport/report/@dist"/>
        <xsl:choose>
            <xsl:when test="$distVersion = '10' and $dist = 'redhat'">
                <xsl:text>Fedora 10</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="/UndoReport/report/@dist"/>
                <xsl:text> </xsl:text>
                <xsl:value-of select="/UndoReport/report/@distVersion"/>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text> (</xsl:text>
        <xsl:value-of select="/UndoReport/report/@arch"/>
        <xsl:text>) [Kernel </xsl:text>
        <xsl:value-of select="/UndoReport/report/@kernel"/>
        <xsl:text>]",""&#x0A;</xsl:text>
        
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>"Profile","</xsl:text><xsl:value-of select="/UndoReport/report/@profile"/>
        <xsl:text>",""&#x0A;</xsl:text>

        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>"Module Name","Results","Severity"&#x0A;</xsl:text>
        <xsl:for-each select="/UndoReport/modules/module">
            <xsl:sort select="@name"/>
            <xsl:text>"</xsl:text><xsl:value-of select="@name"/>
            <xsl:text>","</xsl:text><xsl:value-of select="@results"/>
            <xsl:text>","</xsl:text><xsl:value-of select="@severity"/>
            <xsl:text>"&#x0A;</xsl:text>
        </xsl:for-each>
        
    </xsl:template>
</xsl:stylesheet>
