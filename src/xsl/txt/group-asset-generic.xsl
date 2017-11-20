<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Group Asset Report XML to TEXT
     =========================================================================
-->
    <xsl:param name="report.title">Group Asset Inventory Report</xsl:param>
    
    <xsl:include href="common-text.xsl"/>
    <xsl:output method="text" encoding="UTF-8" ndent="yes" />

    <xsl:variable name="countResponding"><xsl:value-of select="count(/AssetReport/client[@errorMsg=''])"/></xsl:variable>    
    <xsl:variable name="countNotResponding"><xsl:value-of select="count(/AssetReport/client[@errorMsg!=''])"/></xsl:variable>    

    <xsl:template match="/">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:value-of select="translate($report.title, $vLower, $vUpper)"/>
        <xsl:text>&#x0A;Generated </xsl:text>
        <xsl:value-of select="substring(/AssetReport/@created,1,20)"/>
        <xsl:text> by OS Lockdown v</xsl:text>
        <xsl:value-of select="/AssetReport/@sbVersion"/>
        <xsl:text>&#x0A;</xsl:text>

        <xsl:call-template name="pad.line">
           <xsl:with-param name="count" select="80"/>
        </xsl:call-template>
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:text> Group Name: </xsl:text><xsl:value-of select="/AssetReport/@name"/>
        <xsl:text>&#x0A;</xsl:text>

        <xsl:text>    Clients: </xsl:text><xsl:value-of select="count(/AssetReport/client)"/> Total -- (<xsl:value-of select="$countResponding"/> responding, <xsl:value-of select="$countNotResponding"/> not responding)
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:text>Description: </xsl:text>
        <xsl:call-template name="textwrap">
            <xsl:with-param name="original" select="/AssetReport/description"/>
            <xsl:with-param name="maxLength" select="70"/>
            <xsl:with-param name="separator" select="'&#x0A;             '"/>
            <xsl:with-param name="wordWrap" select="'true'"/>
        </xsl:call-template>
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:variable name="leaders">.............................</xsl:variable>

        <!-- =================================================================
              List all Non-Responding clients in Group
                - Client names are 50 characters max
             =================================================================
        -->
        <xsl:if test="$countNotResponding > 0">
            <xsl:call-template name="pad.line">
               <xsl:with-param name="count" select="80"/>
            </xsl:call-template>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>Clients Not Responding</xsl:text>
            <xsl:text>&#x0A;&#x0A;</xsl:text>

            <xsl:for-each select="/AssetReport/client[@errorMsg!='']">
                <xsl:sort select="@name"/>
                <xsl:value-of select="substring(concat('Client: ', @name, $leaders, $leaders, $leaders), 1, 60)"/>
                <xsl:text>&#x0A;</xsl:text>

                <xsl:text> - Error   : </xsl:text>
                <xsl:call-template name="textwrap">
                    <xsl:with-param name="original" select="@errorMsg"/>
                    <xsl:with-param name="maxLength" select="60"/>
                    <xsl:with-param name="separator" select="'&#x0A;             '"/>
                    <xsl:with-param name="wordWrap" select="'true'"/>
                </xsl:call-template>
                <xsl:text>&#x0A;</xsl:text>

                <xsl:text>&#x0A;</xsl:text>
            </xsl:for-each>
        </xsl:if>




        
        <!-- =================================================================
              List all Responding clients in Group
                - Client names are 50 characters max
             =================================================================
        -->
        <xsl:if test="$countResponding > 0">
            <xsl:call-template name="pad.line">
               <xsl:with-param name="count" select="80"/>
            </xsl:call-template>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>Clients Responding</xsl:text>
            <xsl:text>&#x0A;&#x0A;</xsl:text>

            <xsl:for-each select="/AssetReport/client[@errorMsg='']">
                <xsl:sort select="@name"/>

                <xsl:value-of select="substring(concat('Client: ', @name, $leaders, $leaders, $leaders), 1, 60)"/>
                <xsl:value-of select="@distribution"/>
                <xsl:text> (</xsl:text> 
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
                <xsl:text>)&#x0A;</xsl:text>

                <xsl:text> - Host Address: </xsl:text>
                <xsl:value-of select="@hostAddress"/>
                <xsl:text>&#x0A;</xsl:text>

                <xsl:text> - Port: </xsl:text>
                <xsl:value-of select="@port"/>
                <xsl:text>&#x0A;</xsl:text>

                <xsl:text> - Architecture: </xsl:text>
                    <xsl:choose>
                        <xsl:when test="contains(@architecture, 'SUNW,')">
                            <xsl:value-of select="substring-after(@architecture,'SUNW,')"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="@architecture"/>
                        </xsl:otherwise>
                    </xsl:choose>
                <xsl:text>&#x0A;</xsl:text>

                <xsl:text> - Total Memory: </xsl:text>
                <xsl:value-of select="substring-before(substring-after(@memory, '/'), ' total')"/>
                <xsl:text>&#x0A;</xsl:text>

                <xsl:text> - Dispatcher: </xsl:text>
                <xsl:value-of select="substring-after(@clientVersion, 'OS Lockdown ')"/>
                <xsl:text>&#x0A;</xsl:text>

                <xsl:text> - Location: </xsl:text>
                <xsl:call-template name="textwrap">
                    <xsl:with-param name="original" select="@location"/>
                    <xsl:with-param name="maxLength" select="60"/>
                    <xsl:with-param name="separator" select="'&#x0A;             '"/>
                    <xsl:with-param name="wordWrap" select="'true'"/>
                </xsl:call-template>
                <xsl:text>&#x0A;</xsl:text>

                <xsl:text> - Contact:  </xsl:text>
                <xsl:call-template name="textwrap">
                    <xsl:with-param name="original" select="@contact"/>
                    <xsl:with-param name="maxLength" select="60"/>
                    <xsl:with-param name="separator" select="'&#x0A;             '"/>
                    <xsl:with-param name="wordWrap" select="'true'"/>
                </xsl:call-template>
                <xsl:text>&#x0A;</xsl:text>

                <xsl:text>&#x0A;</xsl:text>
            </xsl:for-each>
        </xsl:if>
        
    </xsl:template>
</xsl:stylesheet>
