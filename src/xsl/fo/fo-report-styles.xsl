<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: fo-report-styles.xsl 23917 2017-03-07 15:44:30Z rsanders $ -->
<!-- 
    *************************************************************************
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.

      OS Lockdown:  Styles for PDF Reports (XSL-FO)
    **************************************************************************
 -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:exslt="http://exslt.org/common" version="1.0">


  <xsl:attribute-set name="master-font">
    <xsl:attribute name="font-family">Helvetica</xsl:attribute>
    <xsl:attribute name="font-size">11pt</xsl:attribute>
  </xsl:attribute-set>

  <!--
      ================================================================
            Page Layouts - typically assigned to page master
      ================================================================
  -->
  <xsl:attribute-set name="page-landscape">
    <xsl:attribute name="page-height">8.5in</xsl:attribute>
    <xsl:attribute name="page-width">11in</xsl:attribute>
    <xsl:attribute name="margin-top">0.25in</xsl:attribute>
    <xsl:attribute name="margin-bottom">0.25in</xsl:attribute>
    <xsl:attribute name="margin-right">0.5in</xsl:attribute>
    <xsl:attribute name="margin-left">0.5in</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="page-portrait">
    <xsl:attribute name="page-height">11in</xsl:attribute>
    <xsl:attribute name="page-width">8.5in</xsl:attribute>
    <xsl:attribute name="margin-top">0.25in</xsl:attribute>
    <xsl:attribute name="margin-bottom">0.25in</xsl:attribute>
    <xsl:attribute name="margin-right">0.5in</xsl:attribute>
    <xsl:attribute name="margin-left">0.5in</xsl:attribute>
  </xsl:attribute-set>
      
  <!--
      ================================================================
                          Table Styles
      ================================================================
  -->
  <xsl:attribute-set name="table">
    <xsl:attribute name="table-layout">fixed</xsl:attribute>
    <xsl:attribute name="font-size">10pt</xsl:attribute>
    <xsl:attribute name="background-color">white</xsl:attribute>
    <xsl:attribute name="color">black</xsl:attribute>
    <xsl:attribute name="border-spacing">0pt</xsl:attribute>
    <xsl:attribute name="margin-bottom">2em</xsl:attribute>
    <xsl:attribute name="border">1px solid #c8c5a1</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="table-row-header">
    <xsl:attribute name="background-color">#a19670</xsl:attribute>
    <xsl:attribute name="color">black</xsl:attribute>
    <xsl:attribute name="font-size">12pt</xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="table-row-subheader">
    <xsl:attribute name="background-color">#c8c5a1</xsl:attribute>
    <xsl:attribute name="color">black</xsl:attribute>
    <xsl:attribute name="font-size">10pt</xsl:attribute>
  </xsl:attribute-set>

  <!-- Odd/Even rows for alternate colors for contrasts -->
  <xsl:attribute-set name="row-odd">
    <xsl:attribute name="background-color">white</xsl:attribute>
    <xsl:attribute name="color">black</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="row-even">
    <xsl:attribute name="background-color">#efefef</xsl:attribute>
    <xsl:attribute name="color">black</xsl:attribute>
  </xsl:attribute-set>


<!--
      ================================================================
             Module Results (typically assigned to block elements)
      ================================================================
-->
  <xsl:attribute-set name="module-fail">
    <xsl:attribute name="background-color">red</xsl:attribute>
    <xsl:attribute name="color">white</xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="module-error">
    <xsl:attribute name="background-color">orange</xsl:attribute>
    <xsl:attribute name="color">white</xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="module-pass">
    <xsl:attribute name="background-color">green</xsl:attribute>
    <xsl:attribute name="color">white</xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="module-applied">
    <xsl:attribute name="background-color">green</xsl:attribute>
    <xsl:attribute name="color">white</xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="module-undone">
    <xsl:attribute name="background-color">green</xsl:attribute>
    <xsl:attribute name="color">white</xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="module-manual">
    <xsl:attribute name="background-color">red</xsl:attribute>
    <xsl:attribute name="color">white</xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="module-na">
    <xsl:attribute name="color">#7499c6</xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="module-notreq">
    <xsl:attribute name="color">#7499c6</xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="module-unavail">
    <xsl:attribute name="color">#7499c6</xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="module-osna">
    <xsl:attribute name="color">#7499c6</xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="module-notscanned">
    <xsl:attribute name="color">silver</xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
  </xsl:attribute-set>


<!--
      ================================================================
                   Misceallaenous Report Components
      ================================================================
-->
  <xsl:attribute-set name="footer-block">
    <xsl:attribute name="margin-top">0.25in</xsl:attribute>
    <xsl:attribute name="font-size">10pt</xsl:attribute>
    <xsl:attribute name="color">#467fc5</xsl:attribute>
  </xsl:attribute-set>

 <!--
     ================================================================
        Legacy parameters - Eventually all XSL-FO files will use
        attribute sets as much as possible.
     ================================================================
 -->
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

    <!-- Report Page Sizes -->
  <xsl:param name="page.width">8.5in</xsl:param>
  <xsl:param name="page.height">11in</xsl:param>
  <xsl:param name="page.font.size">10pt</xsl:param>

    <!-- Report Header/Banner -->
  <xsl:param name="report.header.font.size">18pt</xsl:param>
  <xsl:param name="report.header.color">#a19670</xsl:param>
  <xsl:param name="report.header.bgcolor">#a19670</xsl:param>

    <!-- Image Paths -->
  <xsl:param name="image.header.logo">OSLockdown_report.png</xsl:param>

  
  <xsl:param name="entity.up.arrow" select="'&#x25B4;'"/>
  <xsl:param name="entity.down.arrow" select="'&#x25BC;'"/>

  
    
</xsl:stylesheet>

