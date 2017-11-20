<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: common-text.xsl 23917 2017-03-07 15:44:30Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
                xmlns:exslt="http://exslt.org/common" version="1.0">
<!-- 
    *************************************************************************
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
       OS Lockdown:  Common Templates for all TEXT reports
    *************************************************************************
-->
    <xsl:variable name="vLower" select="'abcdefghijklmnopqrstuvwxyz'"/>
    <xsl:variable name="vUpper" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>
    <xsl:variable name="break-at" select="'60'"/>
    
    <!-- ======================================================================= -->
    <xsl:template name="footer">
            <xsl:text>Forcepoint LLC.&#x0A;</xsl:text>
            <xsl:text>12950 Worldgate Drive, Suite 600&#x0A;</xsl:text>
            <xsl:text>Herndon, VA 20170&#x0A;</xsl:text>
    </xsl:template>
    
    <!-- ======================================================================= -->
    <xsl:template name="module.compliancy.list">
        <xsl:param name="compliancy"/>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>    Compliancy:&#x0A;</xsl:text>
        <xsl:for-each select="$compliancy/line-item">
            <xsl:sort select="@source"/>
            <xsl:sort select="@name"/>
            <xsl:sort select="@item"/>
            <xsl:text>     - </xsl:text>
            <xsl:value-of select="@source"/>
            <xsl:text> </xsl:text>
            <xsl:value-of select="@name"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="@version"/>
            <xsl:text>): </xsl:text>
            <xsl:value-of select="@item"/>
            <xsl:text>&#x0A;</xsl:text>
        </xsl:for-each>
    </xsl:template>
    
    <!-- ======================================================================= -->
    <xsl:template name="software.patch.list">
        <xsl:param name="patches"/>
        
        <xsl:text>Patches:</xsl:text>
        <ul class="patchList">
            <xsl:for-each select="$patches">
                <xsl:sort select="@name"/>
                <li>
                    <xsl:value-of select="@name"/>
                </li>
            </xsl:for-each>
        </ul>
        
    </xsl:template>
    
    
    <!-- ======================================================================= -->
    
    <xsl:template name="textwrap">
        <xsl:param name="original"/>
        <xsl:param name="maxLength"/>
        <xsl:param name="separator"/>
        <xsl:param name="wordWrap"/>
        <xsl:choose>
            <xsl:when test="string-length($original)>$maxLength">
                <xsl:variable name="length-substring">
                    <xsl:choose>
                        <xsl:when test="$wordWrap='true'">
                            <xsl:call-template name="lastCharPosition">
                                <xsl:with-param name="original" select="substring($original,1,$maxLength)"/>
                                <xsl:with-param name="character" select="' '"/>
                            </xsl:call-template>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="$maxLength"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:variable>
                <xsl:value-of select="concat(substring($original,1,$length-substring),$separator)"/>
                <xsl:call-template name="textwrap">
                    <xsl:with-param name="original"  select="substring($original,$length-substring+1,string-length($original))"/>
                    <xsl:with-param name="maxLength" select="$maxLength"/>
                    <xsl:with-param name="separator" select="$separator"/>
                    <xsl:with-param name="wordWrap"  select="'true'"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$original"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
<!--     This template returns the position of the last
	 given character in the string that can be found. When
	 the character is not available in the string, the 
	 position of the last character is returned.
	 Input parameters:
		original (mandatory): original string in which the character must be searched
		character(mandatory): character for which the last position must be returned	 	 
-->
    <xsl:template name="lastCharPosition">
        <xsl:param name="original"/>
        <xsl:param name="character"/>
        <xsl:param name="string_length"/>
        <xsl:variable name="len">
            <xsl:choose>
                <xsl:when test="$string_length">
                    <xsl:value-of select="$string_length"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="'0'"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:variable name="char_len">
            <xsl:value-of select="string-length($character)"/>
        </xsl:variable>
        <xsl:choose>
            <xsl:when test="contains($original,$character)">
                <xsl:choose>
                    <xsl:when test="contains(substring-after($original,$character),$character)">
                        <xsl:call-template name="lastCharPosition">
                            <xsl:with-param name="original" select="substring-after($original,$character)"/>
                            <xsl:with-param name="character" select="$character"/>
                            <xsl:with-param name="string_length" 
                                 select="string-length(concat(substring-before($original,$character),' '))+$len"/>
                        </xsl:call-template>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="string-length(substring-before($original,$character))+$char_len+$len"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="string-length($original)"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <!-- ======================================================================= -->
    
    <xsl:template name="pad.spaces">
        <xsl:param name="count" select="1"/>
        <xsl:if test="$count > 0">
            <xsl:text> </xsl:text>
            <xsl:call-template name="pad.spaces">
                <xsl:with-param name="count" select="$count - 1"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>
    
    <xsl:template name="pad.dots">
        <xsl:param name="count" select="1"/>
        <xsl:if test="$count > 0">
            <xsl:text>.</xsl:text>
            <xsl:call-template name="pad.dots">
                <xsl:with-param name="count" select="$count - 1"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>
    
    <xsl:template name="pad.bar">
        <xsl:param name="count" select="1"/>
        <xsl:if test="$count > 0">
            <xsl:text>=</xsl:text>
            <xsl:call-template name="pad.bar">
                <xsl:with-param name="count" select="$count - 1"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>
    
    <xsl:template name="pad.line">
        <xsl:param name="count" select="1"/>
        <xsl:if test="$count > 0">
            <xsl:text>-</xsl:text>
            <xsl:call-template name="pad.line">
                <xsl:with-param name="count" select="$count - 1"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>
    
</xsl:stylesheet>
