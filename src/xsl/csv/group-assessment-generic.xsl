<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: group-assessment-generic.xsl 23802 2017-01-09 22:08:40Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- =========================================================================
     Copyright (c) 2007-2014 Forcepoint LLC.
     This file is released under the GPLv3 license.  
     See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
     or visit https://www.gnu.org/licenses/gpl.html instead.
     
      Purpose: Group Assessment Report XML to CSV
     =========================================================================
-->
    <xsl:param name="report.title">Group Assessment Report</xsl:param>
    
    <xsl:include href="common-csv.xsl"/>
    <xsl:output method="text" encoding="UTF-8" indent="yes" />
    
    <xsl:template match="/">
        
        <xsl:text>&#x0A;"</xsl:text>
        <xsl:value-of select="$report.title"/>
        <xsl:text> Summary","",""&#x0A;</xsl:text>
        <xsl:text>"Created","</xsl:text><xsl:value-of select="/GroupAssessmentReport/@created"/>
        <xsl:text>"&#x0A;</xsl:text>
        <xsl:text>"Group Name","</xsl:text><xsl:value-of select="/GroupAssessmentReport/@groupName"/>
        <xsl:text>"&#x0A;</xsl:text>
        <xsl:text>"Profile","</xsl:text>
        <xsl:value-of select="/GroupAssessmentReport/reports/report[1]/@profile"/>
        <xsl:text>"&#x0A;</xsl:text>
        
        <!-- Module Results -->
        <xsl:if test="count(/GroupAssessmentReport/reports/report) != 0"> 
            
            <xsl:text>&#x0A;"Security Risk","Module Name","Client","Results"&#x0A;</xsl:text>
            <xsl:for-each select="/GroupAssessmentReport/modules/module">
                <xsl:sort select="@name"/>
                <xsl:variable name="modName" select="@name"/>
                <xsl:variable name="modSeverity" select="@severity"/>
                
                <xsl:for-each select="./clients/client">
                    <xsl:sort select="@name"/>
                    <xsl:text>"</xsl:text><xsl:value-of select="$modSeverity"/>
                    <xsl:text>",</xsl:text>
                    <xsl:text>"</xsl:text><xsl:value-of select="$modName"/>
                    <xsl:text>",</xsl:text>
                    <xsl:text>"</xsl:text><xsl:value-of select="@name"/>
                    <xsl:text>",</xsl:text>
                    <xsl:text>"</xsl:text><xsl:value-of select="@results"/>
                    <xsl:text>"&#x0A;</xsl:text>
                </xsl:for-each>
                
            </xsl:for-each>
            <xsl:text>&#x0A;</xsl:text>
            
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
