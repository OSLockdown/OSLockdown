<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0">

 <!-- Sort configuration file's compliancy lists -->
<!-- Copyright (c) 2013 Forcepoint LLC.                                            -->
<!-- This file is released under the GPLv3 license.                                -->
<!-- See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license, -->
<!-- or visit https://www.gnu.org/licenses/gpl.html instead.                       -->

  <xsl:output method="xml" indent="yes" />
  <xsl:strip-space elements="*"/>


  <xsl:template match="line-item" >
      <xsl:copy>
          <xsl:apply-templates select="@*" />
          <xsl:for-each select="./module">
              <xsl:sort data-type="text" select="translate(@libraryName, 'abcdefghijklmnopqrstuvxyz','ABCDEFGHIJKLMNOPQRSTUVXYZ')"/>
              <xsl:apply-templates select="."/>
        </xsl:for-each>
      </xsl:copy>
  </xsl:template>

  <xsl:template match="line-items" >
      <xsl:copy>
          <xsl:for-each select="./line-item">
              <xsl:sort data-type="text" select="translate(@name, 'abcdefghijklmnopqrstuvxyz','ABCDEFGHIJKLMNOPQRSTUVXYZ')"/>
              <xsl:apply-templates select="."/>
          </xsl:for-each>
      </xsl:copy>
  </xsl:template>


<xsl:template match="@* | node()">
      <xsl:copy>
      <xsl:apply-templates select="@* | node()"/>
      </xsl:copy>
  </xsl:template>

</xsl:stylesheet>







