<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:exslt="http://exslt.org/common" version="1.0">
    <!-- *************************************************************************
     Copyright (c) 2007-2014 Forcepoint LLC.
     This file is released under the GPLv3 license.  
     See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
     or visit https://www.gnu.org/licenses/gpl.html instead.

     OS Lockdown:  Common Templates for all CSV reports
-->

    <xsl:variable name="vLower" select="'abcdefghijklmnopqrstuvwxyz'"/>
    <xsl:variable name="vUpper" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>

    <xsl:param name="entity.up.arrow" select="'&#x25B4;'"/>
    <xsl:param name="entity.down.arrow" select="'&#x25BC;'"/>
    
    
    <!-- ======================================================================= -->
    <xsl:template name="footer">
        <div style="width: 100%; white-space: pre; text-align: right; color: gray">
            <a href="https://www.github.com/OSLockdown/OSLockdown">OSLockdown</a>
        </div>
    </xsl:template>
    
    
    <!-- ======================================================================= -->
    <xsl:template name="left-trim">
        <xsl:param name="s" />
        <xsl:choose>
            <xsl:when test="substring($s, 1, 1) = ''">
                <xsl:value-of select="$s"/>
            </xsl:when>
            <xsl:when test="normalize-space(substring($s, 1, 1)) = ''">
                <xsl:call-template name="left-trim">
                    <xsl:with-param name="s" select="substring($s, 2)" />
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$s" />
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template name="right-trim">
        <xsl:param name="s" />
        <xsl:choose>
            <xsl:when test="substring($s, 1, 1) = ''">
                <xsl:value-of select="$s"/>
            </xsl:when>
            <xsl:when test="normalize-space(substring($s, string-length($s))) = ''">
                <xsl:call-template name="right-trim">
                    <xsl:with-param name="s" select="substring($s, 1, string-length($s) - 1)" />
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$s" />
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template name="trim">
        <xsl:param name="s" />
        <xsl:call-template name="right-trim">
            <xsl:with-param name="s">
                <xsl:call-template name="left-trim">
                    <xsl:with-param name="s" select="$s" />
                </xsl:call-template>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>
    
    <!-- ======================================================================= -->
</xsl:stylesheet>
