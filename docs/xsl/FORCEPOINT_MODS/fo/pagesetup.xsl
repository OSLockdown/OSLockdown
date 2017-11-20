<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                version="1.0">

<!-- PassiveTeX can't handle the math expression for
     title.margin.left being negative, so ignore it.
     margin-left="{$page.margin.outer} - {$title.margin.left}"
-->
<xsl:param name="margin.left.outer">
  <xsl:value-of select="$page.margin.outer"/>
</xsl:param>

<xsl:param name="margin.left.inner">
  <xsl:value-of select="$page.margin.inner"/>
</xsl:param>

<xsl:template name="header.table">
  <xsl:param name="pageclass" select="''"/>
  <xsl:param name="sequence" select="''"/>
  <xsl:param name="gentext-key" select="''"/>

  <!-- default is a single table style for all headers -->
  <!-- Customize it for different page classes or sequence location -->

  <xsl:choose>
      <xsl:when test="$pageclass = 'index'">
          <xsl:attribute name="margin-left">0pt</xsl:attribute>
      </xsl:when>
  </xsl:choose>

  <xsl:variable name="column1">
    <xsl:choose>
      <xsl:when test="$double.sided = 0">1</xsl:when>
      <xsl:when test="$sequence = 'first' or $sequence = 'odd'">1</xsl:when>
      <xsl:otherwise>3</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="column3">
    <xsl:choose>
      <xsl:when test="$double.sided = 0">3</xsl:when>
      <xsl:when test="$sequence = 'first' or $sequence = 'odd'">3</xsl:when>
      <xsl:otherwise>1</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="candidate">
    <fo:table xsl:use-attribute-sets="header.table.properties">
      <xsl:call-template name="head.sep.rule">
        <xsl:with-param name="pageclass" select="$pageclass"/>
        <xsl:with-param name="sequence" select="$sequence"/>
        <xsl:with-param name="gentext-key" select="$gentext-key"/>
      </xsl:call-template>

      <xsl:choose>
        <xsl:when test="$passivetex.extensions != 0">
          <fo:table-column column-number="1">
            <xsl:attribute name="column-width">
              <xsl:call-template name="header.footer.width">
                <xsl:with-param name="location">header</xsl:with-param>
                <xsl:with-param name="position" select="$column1"/>
              </xsl:call-template>
              <xsl:text>%</xsl:text>
            </xsl:attribute>
          </fo:table-column>
        </xsl:when>
        <xsl:otherwise>
          <fo:table-column column-number="1">
            <xsl:attribute name="column-width">
              <xsl:text>proportional-column-width(</xsl:text>
              <xsl:call-template name="header.footer.width">
                <xsl:with-param name="location">header</xsl:with-param>
                <xsl:with-param name="position" select="$column1"/>
              </xsl:call-template>
              <xsl:text>)</xsl:text>
            </xsl:attribute>
          </fo:table-column>
        </xsl:otherwise>
			</xsl:choose>
      <xsl:choose>
        <xsl:when test="$passivetex.extensions != 0">
          <fo:table-column column-number="2">
            <xsl:attribute name="column-width">
              <xsl:call-template name="header.footer.width">
                <xsl:with-param name="location">header</xsl:with-param>
                <xsl:with-param name="position" select="2"/>
              </xsl:call-template>
              <xsl:text>%</xsl:text>
            </xsl:attribute>
          </fo:table-column>
        </xsl:when>
        <xsl:otherwise>
          <fo:table-column column-number="2">
            <xsl:attribute name="column-width">
              <xsl:text>proportional-column-width(</xsl:text>
              <xsl:call-template name="header.footer.width">
                <xsl:with-param name="location">header</xsl:with-param>
                <xsl:with-param name="position" select="2"/>
              </xsl:call-template>
              <xsl:text>)</xsl:text>
            </xsl:attribute>
          </fo:table-column>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:choose>
        <xsl:when test="$passivetex.extensions != 0">
          <fo:table-column column-number="3">
            <xsl:attribute name="column-width">
              <xsl:call-template name="header.footer.width">
                <xsl:with-param name="location">header</xsl:with-param>
                <xsl:with-param name="position" select="$column3"/>
              </xsl:call-template>
              <xsl:text>%</xsl:text>
            </xsl:attribute>
          </fo:table-column>
        </xsl:when>
        <xsl:otherwise>
          <fo:table-column column-number="3">
            <xsl:attribute name="column-width">
              <xsl:text>proportional-column-width(</xsl:text>
              <xsl:call-template name="header.footer.width">
                <xsl:with-param name="location">header</xsl:with-param>
                <xsl:with-param name="position" select="$column3"/>
              </xsl:call-template>
              <xsl:text>)</xsl:text>
            </xsl:attribute>
          </fo:table-column>
        </xsl:otherwise>
      </xsl:choose>

      <fo:table-body>
        <fo:table-row>
          <xsl:attribute name="block-progression-dimension.minimum">
            <xsl:value-of select="$header.table.height"/>
          </xsl:attribute>
          <fo:table-cell text-align="left"
                         display-align="before">
            <xsl:if test="$fop.extensions = 0">
              <xsl:attribute name="relative-align">baseline</xsl:attribute>
            </xsl:if>
            <fo:block>
              <xsl:call-template name="header.content">
                <xsl:with-param name="pageclass" select="$pageclass"/>
                <xsl:with-param name="sequence" select="$sequence"/>
                <xsl:with-param name="position" select="'left'"/>
                <xsl:with-param name="gentext-key" select="$gentext-key"/>
              </xsl:call-template>
            </fo:block>
          </fo:table-cell>
          <fo:table-cell text-align="center"
                         display-align="before">
            <xsl:if test="$fop.extensions = 0">
              <xsl:attribute name="relative-align">baseline</xsl:attribute>
            </xsl:if>
            <fo:block>
              <xsl:call-template name="header.content">
                <xsl:with-param name="pageclass" select="$pageclass"/>
                <xsl:with-param name="sequence" select="$sequence"/>
                <xsl:with-param name="position" select="'center'"/>
                <xsl:with-param name="gentext-key" select="$gentext-key"/>
              </xsl:call-template>
            </fo:block>
          </fo:table-cell>
          <fo:table-cell text-align="right"
                         display-align="before">
            <xsl:if test="$fop.extensions = 0">
              <xsl:attribute name="relative-align">baseline</xsl:attribute>
            </xsl:if>
            <fo:block>
              <xsl:call-template name="header.content">
                <xsl:with-param name="pageclass" select="$pageclass"/>
                <xsl:with-param name="sequence" select="$sequence"/>
                <xsl:with-param name="position" select="'right'"/>
                <xsl:with-param name="gentext-key" select="$gentext-key"/>
              </xsl:call-template>
            </fo:block>
          </fo:table-cell>
        </fo:table-row>
      </fo:table-body>
    </fo:table>
  </xsl:variable>

  <!-- Really output a header? -->
  <xsl:choose>
    <xsl:when test="$pageclass = 'titlepage' and $gentext-key = 'book'
                    and $sequence='first'">
      <!-- no, book titlepages have no headers at all -->
    </xsl:when>
    <xsl:when test="$sequence = 'blank' and $headers.on.blank.pages = 0">
      <!-- no output -->
    </xsl:when>
    <xsl:otherwise>
      <xsl:copy-of select="$candidate"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template name="footer.table">
  <xsl:param name="pageclass" select="''"/>
  <xsl:param name="sequence" select="''"/>
  <xsl:param name="gentext-key" select="''"/>

  <!-- default is a single table style for all footers -->
  <!-- Customize it for different page classes or sequence location -->

  <xsl:choose>
      <xsl:when test="$pageclass = 'index'">
          <xsl:attribute name="margin-left">0pt</xsl:attribute>
      </xsl:when>
  </xsl:choose>

  <xsl:variable name="column1">
    <xsl:choose>
      <xsl:when test="$double.sided = 0">1</xsl:when>
      <xsl:when test="$sequence = 'first' or $sequence = 'odd'">1</xsl:when>
      <xsl:otherwise>3</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="column3">
    <xsl:choose>
      <xsl:when test="$double.sided = 0">3</xsl:when>
      <xsl:when test="$sequence = 'first' or $sequence = 'odd'">3</xsl:when>
      <xsl:otherwise>1</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="candidate">
    <fo:table xsl:use-attribute-sets="footer.table.properties">
      <xsl:call-template name="foot.sep.rule">
        <xsl:with-param name="pageclass" select="$pageclass"/>
        <xsl:with-param name="sequence" select="$sequence"/>
        <xsl:with-param name="gentext-key" select="$gentext-key"/>
      </xsl:call-template>
      <xsl:choose>
        <xsl:when test="$passivetex.extensions != 0">
          <fo:table-column column-number="1">
            <xsl:attribute name="column-width">
              <xsl:call-template name="header.footer.width">
                <xsl:with-param name="location">footer</xsl:with-param>
                <xsl:with-param name="position" select="$column1"/>
              </xsl:call-template>
              <xsl:text>%</xsl:text>
            </xsl:attribute>
          </fo:table-column>
        </xsl:when>
        <xsl:otherwise>
          <fo:table-column column-number="1">
            <xsl:attribute name="column-width">
              <xsl:text>proportional-column-width(</xsl:text>
              <xsl:call-template name="header.footer.width">
                <xsl:with-param name="location">footer</xsl:with-param>
                <xsl:with-param name="position" select="$column1"/>
              </xsl:call-template>
              <xsl:text>)</xsl:text>
            </xsl:attribute>
          </fo:table-column>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:choose>
        <xsl:when test="$passivetex.extensions != 0">
          <fo:table-column column-number="2">
            <xsl:attribute name="column-width">
              <xsl:call-template name="header.footer.width">
                <xsl:with-param name="location">footer</xsl:with-param>
                <xsl:with-param name="position" select="2"/>
              </xsl:call-template>
              <xsl:text>%</xsl:text>
            </xsl:attribute>
          </fo:table-column>
        </xsl:when>
        <xsl:otherwise>
          <fo:table-column column-number="2">
            <xsl:attribute name="column-width">
              <xsl:text>proportional-column-width(</xsl:text>
              <xsl:call-template name="header.footer.width">
                <xsl:with-param name="location">footer</xsl:with-param>
                <xsl:with-param name="position" select="2"/>
              </xsl:call-template>
              <xsl:text>)</xsl:text>
            </xsl:attribute>
          </fo:table-column>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:choose>
        <xsl:when test="$passivetex.extensions != 0">
          <fo:table-column column-number="3">
            <xsl:attribute name="column-width">
              <xsl:call-template name="header.footer.width">
                <xsl:with-param name="location">footer</xsl:with-param>
                <xsl:with-param name="position" select="$column3"/>
              </xsl:call-template>
              <xsl:text>%</xsl:text>
            </xsl:attribute>
          </fo:table-column>
        </xsl:when>
        <xsl:otherwise>
          <fo:table-column column-number="3">
            <xsl:attribute name="column-width">
              <xsl:text>proportional-column-width(</xsl:text>
              <xsl:call-template name="header.footer.width">
                <xsl:with-param name="location">footer</xsl:with-param>
                <xsl:with-param name="position" select="$column3"/>
              </xsl:call-template>
              <xsl:text>)</xsl:text>
            </xsl:attribute>
          </fo:table-column>
        </xsl:otherwise>
      </xsl:choose>

      <fo:table-body>
        <fo:table-row>
          <xsl:attribute name="block-progression-dimension.minimum">
            <xsl:value-of select="$footer.table.height"/>
          </xsl:attribute>
          <fo:table-cell text-align="left"
                         display-align="after">
            <xsl:if test="$fop.extensions = 0">
              <xsl:attribute name="relative-align">baseline</xsl:attribute>
            </xsl:if>
            <fo:block>
              <xsl:call-template name="footer.content">
                <xsl:with-param name="pageclass" select="$pageclass"/>
                <xsl:with-param name="sequence" select="$sequence"/>
                <xsl:with-param name="position" select="'left'"/>
                <xsl:with-param name="gentext-key" select="$gentext-key"/>
              </xsl:call-template>
            </fo:block>
          </fo:table-cell>
          <fo:table-cell text-align="center"
                         display-align="after">
            <xsl:if test="$fop.extensions = 0">
              <xsl:attribute name="relative-align">baseline</xsl:attribute>
            </xsl:if>
            <fo:block>
              <xsl:call-template name="footer.content">
                <xsl:with-param name="pageclass" select="$pageclass"/>
                <xsl:with-param name="sequence" select="$sequence"/>
                <xsl:with-param name="position" select="'center'"/>
                <xsl:with-param name="gentext-key" select="$gentext-key"/>
              </xsl:call-template>
            </fo:block>
          </fo:table-cell>
          <fo:table-cell text-align="right"
                         display-align="after">
            <xsl:if test="$fop.extensions = 0">
              <xsl:attribute name="relative-align">baseline</xsl:attribute>
            </xsl:if>
            <fo:block>
              <xsl:call-template name="footer.content">
                <xsl:with-param name="pageclass" select="$pageclass"/>
                <xsl:with-param name="sequence" select="$sequence"/>
                <xsl:with-param name="position" select="'right'"/>
                <xsl:with-param name="gentext-key" select="$gentext-key"/>
              </xsl:call-template>
            </fo:block>
          </fo:table-cell>
        </fo:table-row>
      </fo:table-body>
    </fo:table>
  </xsl:variable>

  <!-- Really output a footer? -->
  <xsl:choose>
    <xsl:when test="$pageclass='titlepage' and $gentext-key='book'
                    and $sequence='first'">
      <!-- no, book titlepages have no footers at all -->
    </xsl:when>
    <xsl:when test="$sequence = 'blank' and $footers.on.blank.pages = 0">
      <!-- no output -->
    </xsl:when>
    <xsl:otherwise>
      <xsl:copy-of select="$candidate"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

</xsl:stylesheet>
