<?xml version="1.0" encoding="ASCII"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:attribute-set name="abstract.title.properties">
  <xsl:attribute name="space-before.minimum"><xsl:value-of select="concat(($body.font.master * 0.8), 'pt')"/></xsl:attribute>
  <xsl:attribute name="space-before.maximum"><xsl:value-of select="concat(($body.font.master * 1.2), 'pt')"/></xsl:attribute>
</xsl:attribute-set>
<xsl:attribute-set name="component.title.properties">
  <xsl:attribute name="space-before.minimum"><xsl:value-of select="concat($body.font.master*0.8, 'pt')"/></xsl:attribute>
  <xsl:attribute name="space-before.maximum"><xsl:value-of select="concat($body.font.master*1.2, 'pt')"/></xsl:attribute>
</xsl:attribute-set>
<xsl:attribute-set name="index.div.title.properties">
  <xsl:attribute name="space-before.minimum"><xsl:value-of select="concat(($body.font.master * 0.8),'pt')"/></xsl:attribute>
  <xsl:attribute name="space-before.maximum"><xsl:value-of select="concat(($body.font.master * 1.2),'pt')"/></xsl:attribute>
</xsl:attribute-set>
<xsl:param name="weird.use.of.orgname" select="0"/>

</xsl:stylesheet>
