<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: group-asset-generic.xsl 23917 2017-03-07 15:44:30Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Group Asset Report XML to CSV
     =========================================================================
-->
    <xsl:param name="report.title">Group Asset Report</xsl:param>
    
    <xsl:include href="common-csv.xsl"/>
    <xsl:output method="text" encoding="UTF-8" indent="yes" />
    
    <xsl:template match="/">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:value-of select="translate($report.title, $vLower, $vUpper)"/>
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:text>"Group Name","</xsl:text><xsl:value-of select="/AssetReport/@name"/>
        <xsl:text>"&#x0A;</xsl:text>
        
        <xsl:text>"Clients","</xsl:text><xsl:value-of select="count(/AssetReport/client)"/>
        <xsl:text>"&#x0A;</xsl:text>
        
        <xsl:text>"Description","</xsl:text>
        <xsl:value-of select="/AssetReport/description"/>
        <xsl:text>"&#x0A;</xsl:text>
        
        <xsl:text>"Created","</xsl:text><xsl:value-of select="/AssetReport/@created"/>
        <xsl:text>"&#x0A;</xsl:text>
        
        <xsl:text>"Generator","OS Lockdown v</xsl:text>
        <xsl:value-of select="/AssetReport/@sbVersion"/>
        <xsl:text>"&#x0A;</xsl:text>
        
<!-- 
      =================================================================
              List all clients in Group
                - Client names are 50 characters max
      =================================================================
-->
        <xsl:text>&#x0A;"Client Name","OS","Kernel","Host Address","Port","Architecture","Total Memory","Dispatcher Version","Location","Contact","Error Message"&#x0A;</xsl:text>
        <xsl:for-each select="/AssetReport/client">
            <xsl:sort select="@name"/>
            
            <xsl:text>"</xsl:text>
            <xsl:value-of select="@name"/>
            <xsl:text>","</xsl:text>
            <xsl:value-of select="@distribution"/>
            <xsl:text>","</xsl:text> 
            <xsl:choose>
                <xsl:when test="@distribution = 'Solaris'">
                    <xsl:value-of select="substring-after(@kernel,'_')"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:choose>
                        <xsl:when test="contains(@kernel, 'Linux')">
                            <xsl:value-of select="substring-after(substring-before(@kernel,'-'),'Linux')"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="substring-before(@kernel,'-')"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:otherwise>
            </xsl:choose>
            <xsl:text>","</xsl:text>
            <xsl:value-of select="@hostAddress"/>
            <xsl:text>","</xsl:text>
            <xsl:value-of select="@port"/>
            <xsl:text>","</xsl:text>
            <xsl:choose>
                <xsl:when test="contains(@architecture, 'SUNW,')">
                    <xsl:value-of select="substring-after(@architecture,'SUNW,')"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="@architecture"/>
                </xsl:otherwise>
            </xsl:choose>
            <xsl:text>","</xsl:text>
            
            <xsl:value-of select="substring-before(substring-after(@memory, '/'), ' total')"/>
            <xsl:text>","</xsl:text>
            
            <xsl:value-of select="substring-after(@clientVersion, 'OS Lockdown ')"/>
            <xsl:text>","</xsl:text>
            
            <xsl:value-of select="@location"/>
            <xsl:text>","</xsl:text>
            
            <xsl:value-of select="@contact"/>
            <xsl:text>","</xsl:text>
            
            <xsl:value-of select="@errorMsg"/>
            <xsl:text>"&#x0A;</xsl:text>
            
        </xsl:for-each>
        
        <xsl:text>&#x0A;</xsl:text>
        
    </xsl:template>
</xsl:stylesheet>
