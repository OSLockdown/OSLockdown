<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:sverb="http://nwalsh.com/xslt/ext/com.nwalsh.saxon.Verbatim"
                xmlns:xverb="com.nwalsh.xalan.Verbatim"
                xmlns:lxslt="http://xml.apache.org/xslt"
                xmlns:exsl="http://exslt.org/common"
                exclude-result-prefixes="sverb xverb lxslt exsl"
                version='1.0'>

<xsl:template match="literallayout">
  <xsl:param name="suppress-numbers" select="'0'"/>
  <xsl:variable name="id"><xsl:call-template name="object.id"/></xsl:variable>
  <xsl:variable name="content">
    <xsl:choose>
      <xsl:when test="$suppress-numbers = '0'
                      and @linenumbering = 'numbered'
                      and $use.extensions != '0'
                      and $linenumbering.extension != '0'">
        <xsl:call-template name="number.rtf.lines">
          <xsl:with-param name="rtf">
            <xsl:apply-templates/>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:choose>
    <xsl:when test="@class='monospaced'">
      <xsl:choose>
        <xsl:when test="$shade.verbatim != 0">
          <fo:block id="{$id}"
                    xsl:use-attribute-sets="monospace.verbatim.properties shade.verbatim.style">
            <xsl:copy-of select="$content"/>
          </fo:block>
        </xsl:when>
        <xsl:otherwise>
          <fo:block id="{$id}"
                    xsl:use-attribute-sets="monospace.verbatim.properties">
            <xsl:copy-of select="$content"/>
          </fo:block>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:when>
    <xsl:otherwise>
      <xsl:choose>
        <xsl:when test="$shade.verbatim != 0">
          <fo:block id="{$id}"
                    xsl:use-attribute-sets="verbatim.properties shade.verbatim.style">
            <xsl:copy-of select="$content"/>
          </fo:block>
        </xsl:when>
        <xsl:otherwise>
          <fo:block id="{$id}"
                    xsl:use-attribute-sets="verbatim.properties">
            <xsl:copy-of select="$content"/>
          </fo:block>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


</xsl:stylesheet>
