<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: xhtml-report-styles.xsl 23917 2017-03-07 15:44:30Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"  
                xmlns:fo="http://www.w3.org/1999/XSL/Format"  
                xmlns:exslt="http://exslt.org/common" version="1.0">
    
    <!-- *************************************************************************
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.

     OS Lockdown:  Styles for XHTML Reports 
    -->
    
    <!-- Report Header/Banner -->
    <xsl:param name="report.header.font.size">18pt</xsl:param>
    <xsl:param name="report.header.font.color">black</xsl:param>
    <xsl:param name="report.header.font.weight">bold</xsl:param>
    <xsl:param name="report.header.color">#a19670</xsl:param>
    <xsl:param name="report.header.bgcolor">#ffffff</xsl:param>
    
    <!-- Image Paths -->
    <xsl:param name="image.header.logo">/OSLockdown/images/OSLockdown_report.png</xsl:param>
    
    <!-- Table Style  -->
    <xsl:param name="table.color">#c8c5a1</xsl:param>
    <xsl:param name="table.bgcolor">white</xsl:param>
    <xsl:param name="table.font.size">10pt</xsl:param>
    <xsl:param name="table.font.color">black</xsl:param>
    <xsl:param name="table.header.font.size">11pt</xsl:param>

    <!-- For example, the baseline compare's file groupings (i.e., /bin) -->
    <xsl:param name="table.subrow.bgcolor">#7499c6</xsl:param>
    
    <!-- Alternate row color -->
    <xsl:param name="table.row.alt.bgcolor">#efefef</xsl:param>
    <xsl:param name="table.row.alt.color">black</xsl:param>
    
</xsl:stylesheet>

