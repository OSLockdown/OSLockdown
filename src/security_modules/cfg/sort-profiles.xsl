<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- Copyright (c) 2013 Forcepoint LLC.                                            -->
<!-- This file is released under the GPLv3 license.                                -->
<!-- See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license, -->
<!-- or visit https://www.gnu.org/licenses/gpl.html instead.                       -->

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>


  <xsl:template match="profile" >
      <xsl:copy>
          <xsl:apply-templates select="info"/>
          <xsl:apply-templates select="@*" />
          <xsl:for-each select="./security_module">
              <xsl:sort select="@name"/>
              <xsl:copy-of select="."/>
        </xsl:for-each>
      </xsl:copy>
  </xsl:template>


  <xsl:template match="@*|node()|text()">
      <xsl:copy>
          <xsl:apply-templates select="@*" />
          <xsl:apply-templates />
      </xsl:copy>
  </xsl:template>


</xsl:stylesheet>
