<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"  
                xmlns:fo="http://www.w3.org/1999/XSL/Format"  
                xmlns:exslt="http://exslt.org/common" version="1.0">
<!-- 
   ***************************************************************************
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
     OS Lockdown:  Styles for System Configuration Document
   ***************************************************************************
 -->
<xsl:include href="styles-headers.xsl"/>

<!-- Document Page Colors, Borders, Sizes -->
    <xsl:param name="page.width">8.5in</xsl:param>
    <xsl:param name="page.height">11in</xsl:param>
    
<!-- Base/Generic Properties -->
    <xsl:attribute-set name="default-font">
      <xsl:attribute name="font-family">Helvetica</xsl:attribute>
      <xsl:attribute name="font-size">12pt</xsl:attribute>
      <xsl:attribute name="font-weight">normal</xsl:attribute>
    </xsl:attribute-set>

    <xsl:attribute-set name="default-block">
      <xsl:attribute name="font-family">Helvetica</xsl:attribute>
      <xsl:attribute name="font-size">10pt</xsl:attribute>
      <xsl:attribute name="font-weight">normal</xsl:attribute>
      <!-- <xsl:attribute name="margin-bottom">0.1in</xsl:attribute> -->
      <xsl:attribute name="line-height">14pt</xsl:attribute>
      <xsl:attribute name="space-before">10pt</xsl:attribute>
      <xsl:attribute name="space-after">8pt</xsl:attribute>
    </xsl:attribute-set>

<!-- Report Header/Banner -->
    <xsl:param name="report.header.font.size">18pt</xsl:param>
    <xsl:param name="report.header.color">#ff00ff</xsl:param>
    <xsl:param name="report.header.bgcolor">#ff00ff</xsl:param>
    <xsl:param name="image.header.logo">OSLockdown_report.png</xsl:param>
    
    
<!-- Table Styles  -->
    <xsl:attribute-set name="table-font">
      <xsl:attribute name="font-family">Helvetica</xsl:attribute>
      <xsl:attribute name="font-size">10pt</xsl:attribute>
      <xsl:attribute name="font-weight">normal</xsl:attribute>
    </xsl:attribute-set>

    <xsl:param name="table.width">7.5in</xsl:param>
    <xsl:param name="table.color">#c8c5a1</xsl:param>
    <xsl:param name="table.bgcolor">white</xsl:param>
    <xsl:param name="table.font.size">10pt</xsl:param>
    <xsl:param name="table.font.color">black</xsl:param>
    <xsl:param name="table.header.font.size">11pt</xsl:param>

    <xsl:param name="table.subrow.bgcolor">#7499c6</xsl:param>
    
    <!-- Alternate row color -->
    <xsl:param name="table.row.alt.bgcolor">#efefef</xsl:param>
    <xsl:param name="table.row.alt.color">black</xsl:param>
    
<!-- Misc -->
    <xsl:attribute-set name="screen-output-block">
      <xsl:attribute name="padding-bottom">10px</xsl:attribute>
      <xsl:attribute name="padding-left">10px</xsl:attribute>
      <xsl:attribute name="margin-left">5px</xsl:attribute>
      <xsl:attribute name="font-family">Courier</xsl:attribute>
      <xsl:attribute name="font-size">10pt</xsl:attribute>
      <xsl:attribute name="font-weight">normal</xsl:attribute>
      <xsl:attribute name="white-space">pre</xsl:attribute>
      <xsl:attribute name="background-color">#eef1f8</xsl:attribute>
      <xsl:attribute name="color">black</xsl:attribute>
    </xsl:attribute-set>

    <xsl:attribute-set name="screen-output-block-small">
      <xsl:attribute name="padding-bottom">5px</xsl:attribute>
      <xsl:attribute name="padding-left">5px</xsl:attribute>
      <xsl:attribute name="margin-left">2px</xsl:attribute>
      <xsl:attribute name="font-family">Courier</xsl:attribute>
      <xsl:attribute name="font-size">8pt</xsl:attribute>
      <xsl:attribute name="font-weight">normal</xsl:attribute>
      <xsl:attribute name="white-space">pre</xsl:attribute>
      <xsl:attribute name="background-color">#eef1f8</xsl:attribute>
      <xsl:attribute name="color">black</xsl:attribute>
    </xsl:attribute-set>

</xsl:stylesheet>

