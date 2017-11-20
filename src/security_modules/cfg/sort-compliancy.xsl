<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0">
<!-- Copyright (c) 2011 Forcepoint LLC.                                            -->
<!-- This file is released under the GPLv3 license.                                -->
<!-- See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license, -->
<!-- or visit https://www.gnu.org/licenses/gpl.html instead.                       -->

 <!-- Sort configuration file's compliancy lists -->

  <xsl:output method="xml" indent="yes" />

  <xsl:template match="compliancy">
      <xsl:copy >
      <xsl:apply-templates select="*">
        <xsl:sort data-type="text" select="@source" />
        <xsl:sort data-type="text" select="@name" />
        <xsl:sort data-type="text" select="@version" />
        <xsl:sort data-type="text" select="@item" />
      </xsl:apply-templates>
      </xsl:copy>
  </xsl:template>

<xsl:template match="@* | node()">
      <xsl:copy>
      <xsl:apply-templates select="@* | node()"/>
      </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
