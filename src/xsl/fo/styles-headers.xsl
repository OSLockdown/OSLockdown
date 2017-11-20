<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:exslt="http://exslt.org/common"
 version="1.0">
 <!--
  *************************************************************************
  Copyright (c) 2007-2014 Forcepoint LLC.
  This file is released under the GPLv3 license.  
  See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
  or visit https://www.gnu.org/licenses/gpl.html instead.
  
  OS Lockdown: Styles for Section Titles (h1, h2, h3, etc) 
  
  NOTE: All of these attributes sets will be applied to a fo:block
  so be sure to only inlcude appicable attributes.
  *************************************************************************
 -->

 <!-- Header 1 (h1) -->
 <xsl:attribute-set name="h1">
  <xsl:attribute name="font-size">Helvetica</xsl:attribute>
  <xsl:attribute name="font-size">18pt</xsl:attribute>
  <xsl:attribute name="font-weight">bold</xsl:attribute>
  <xsl:attribute name="space-before">0.5in</xsl:attribute>
  <xsl:attribute name="space-after">0.25in</xsl:attribute>
 </xsl:attribute-set>

 <!-- Header 2 (h2) -->
 <xsl:attribute-set name="h2">
  <xsl:attribute name="font-size">Helvetica</xsl:attribute>
  <xsl:attribute name="font-size">14pt</xsl:attribute>
  <xsl:attribute name="font-weight">bold</xsl:attribute>
  <xsl:attribute name="space-before">0.25in</xsl:attribute>
  <xsl:attribute name="space-after">0.1in</xsl:attribute>
 </xsl:attribute-set>

 <!-- Header 3 (h3) -->
 <xsl:attribute-set name="h3">
  <xsl:attribute name="font-size">Helvetica</xsl:attribute>
  <xsl:attribute name="font-size">12pt</xsl:attribute>
  <xsl:attribute name="font-weight">bold</xsl:attribute>
  <xsl:attribute name="space-before">0.25in</xsl:attribute>
  <xsl:attribute name="space-after">0.1in</xsl:attribute>
  <xsl:attribute name="text-decoration">underline</xsl:attribute>
 </xsl:attribute-set>


 <!--
  ================================================= 
  Table of Contents
  =================================================
 -->
 <xsl:attribute-set name="toc1">
  <xsl:attribute name="font-size">Helvetica</xsl:attribute>
  <xsl:attribute name="font-size">12pt</xsl:attribute>
  <xsl:attribute name="space-before">0.2in</xsl:attribute>
  <xsl:attribute name="space-after">2px</xsl:attribute>
  <xsl:attribute name="start-indent">0in</xsl:attribute>
 </xsl:attribute-set>

 <xsl:attribute-set name="toc2">
  <xsl:attribute name="font-size">Helvetica</xsl:attribute>
  <xsl:attribute name="font-size">12pt</xsl:attribute>
  <xsl:attribute name="space-before">2px</xsl:attribute>
  <xsl:attribute name="space-after">2px</xsl:attribute>
  <xsl:attribute name="start-indent">0.25in</xsl:attribute>
 </xsl:attribute-set>

 <xsl:attribute-set name="toc3">
  <xsl:attribute name="font-size">Helvetica</xsl:attribute>
  <xsl:attribute name="font-size">12pt</xsl:attribute>
  <xsl:attribute name="space-before">2px</xsl:attribute>
  <xsl:attribute name="space-after">2px</xsl:attribute>
  <xsl:attribute name="start-indent">0.5in</xsl:attribute>
 </xsl:attribute-set>

</xsl:stylesheet>
