<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0">
<!-- Copyright (c) 2013 Forcepoint LLC.                                            -->
<!-- This file is released under the GPLv3 license.                                -->
<!-- See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license, -->
<!-- or visit https://www.gnu.org/licenses/gpl.html instead.                       -->

 <!-- Sort configuration file's compliancy lists -->

  <xsl:output method="xml" indent="yes" />
  <xsl:strip-space elements="*"/>

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

  <xsl:template match="platforms">
      <xsl:copy >
      <xsl:choose>
      <xsl:when test="count(./cpe-item/services) = 0 and count(./cpe-item/packages) =0 ">
        <xsl:apply-templates select="cpe-item">
        <xsl:sort data-type="text" select="@name" />
        </xsl:apply-templates>
       </xsl:when>
       <xsl:otherwise> 
        <xsl:apply-templates select="cpe-item"/>
       </xsl:otherwise> 
      </xsl:choose>
      </xsl:copy>
  </xsl:template>

  <xsl:template match="module_group" >
      <xsl:copy>
          <xsl:apply-templates select="@*" />
          <xsl:for-each select="./security_module">
<!--   COMMENT OUT ONE OR THE OTHER OF THE SELECT STATEMENTS BELOW
       TO TOGGLE BETWEEN SORTING ON LIBRARYNAME OR MODULE NAME
-->

              <xsl:sort select="./library"/>
<!--
              <xsl:sort select="@name"/>
-->
              <xsl:apply-templates select="."/>
        </xsl:for-each>
      </xsl:copy>
  </xsl:template>

  <xsl:template match="security_modules" >
      <xsl:copy>
          <xsl:for-each select="./module_group">
              <xsl:sort select="@name"/>
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




