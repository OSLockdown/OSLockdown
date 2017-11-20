<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Report Customization Parameters

      These parameters enable/disable or show/hide various pieces of
      information within the report. Its purpose is not to define style
      characteristics such as colors and fonts but rather document structure
      characteristics.

      These parameters can be overriden within a template scope if necessary.
      For example, setting the show.disa-items parameter under the
      <xsl:template match="/"> element would override the value set in this
      file.
     =========================================================================
 -->
  <xsl:param name="report.encoding">UTF-8</xsl:param>
  <xsl:param name="report.lang">en</xsl:param>

  <!-- 
       Replace the fields in the two lines below it
       if you need your organizations name/URL to appear on the footer of 
       reports.
   -->
  <xsl:param name="report.owner.name"></xsl:param>
  <xsl:param name="report.owner.url"></xsl:param>



  <xsl:param name="header.display">true</xsl:param>
  <xsl:param name="logo.display">true</xsl:param>
  <xsl:param name="footer.display">true</xsl:param>

 <!-- 
     ***********************************************
      What compliancy metadata do you want to see? 
     ***********************************************
  -->
  <!-- all others are negated if this one is 0 -->
  <xsl:param name="show.compliancy" select='1'/>

  <!-- Specific metadata -->
  <xsl:param name="show.fisma-mappings" select='1'/>
  <xsl:param name="show.cag-mappings" select='1'/>
  <xsl:param name="show.cce-items" select='1'/>
  <xsl:param name="show.disa-items" select='1'/>
  <xsl:param name="show.cis-items" select='1'/>

</xsl:stylesheet>

