<?xml version="1.0"?>
<!DOCTYPE xsl:stylesheet [
<!ENTITY % common.entities SYSTEM "../../docbook-xsl-stylesheets/common/entities.ent">
%common.entities;
]>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:rx="http://www.renderx.com/XSL/Extensions"
                xmlns:axf="http://www.antennahouse.com/names/XSL/Extensions"
                xmlns:exslt="http://exslt.org/common"
                extension-element-prefixes="exslt"
                exclude-result-prefixes="exslt"
                version="1.0">

<xsl:template match="indexterm" mode="reference">
  <xsl:param name="scope" select="."/>
  <xsl:param name="role" select="''"/>
  <xsl:param name="type" select="''"/>
  <xsl:param name="position" select="0"/>
  <xsl:param name="separator" select="''"/>

  <xsl:variable name="term.separator">
    <xsl:call-template name="index.separator">
      <xsl:with-param name="key" select="'index.term.separator'"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:variable name="range.separator">
    <xsl:call-template name="index.separator">
      <xsl:with-param name="key" select="'index.range.separator'"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:variable name="number.separator">
    <xsl:call-template name="index.separator">
      <xsl:with-param name="key" select="'index.number.separator'"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:choose>
    <xsl:when test="$separator != ''">
      <xsl:value-of select="$separator"/>
    </xsl:when>
    <xsl:when test="$position = 1">
      <xsl:value-of select="$term.separator"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="$number.separator"/>
    </xsl:otherwise>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="@zone and string(@zone)">
      <xsl:call-template name="reference">
        <xsl:with-param name="zones" select="normalize-space(@zone)"/>
        <xsl:with-param name="scope" select="$scope"/>
        <xsl:with-param name="role" select="$role"/>
        <xsl:with-param name="type" select="$type"/>
      </xsl:call-template>
    </xsl:when>
    <xsl:when test="ancestor::*[contains(local-name(),'info') and not(starts-with(local-name(),'info'))]">
      <xsl:call-template name="info.reference">
        <xsl:with-param name="scope" select="$scope"/>
        <xsl:with-param name="role" select="$role"/>
        <xsl:with-param name="type" select="$type"/>
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
      <xsl:variable name="id">
        <xsl:call-template name="object.id"/>
      </xsl:variable>

     <xsl:if test="$id != ''">
       <fo:basic-link internal-destination="{$id}"
                     xsl:use-attribute-sets="index.page.number.properties">
         <fo:page-number-citation ref-id="{$id}"/>
       </fo:basic-link>
     </xsl:if>

      <xsl:if test="key('endofrange', $id)[&scope;]">
        <xsl:apply-templates select="key('endofrange', $id)[&scope;][last()]"
                             mode="reference">
          <xsl:with-param name="scope" select="$scope"/>
          <xsl:with-param name="role" select="$role"/>
          <xsl:with-param name="type" select="$type"/>
          <xsl:with-param name="separator" select="$range.separator"/>
        </xsl:apply-templates>
      </xsl:if>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template name="reference">
  <xsl:param name="scope" select="."/>
  <xsl:param name="role" select="''"/>
  <xsl:param name="type" select="''"/>
  <xsl:param name="zones"/>

  <xsl:variable name="number.separator">
    <xsl:call-template name="index.separator">
      <xsl:with-param name="key" select="'index.number.separator'"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:choose>
    <xsl:when test="contains($zones, ' ')">
      <xsl:variable name="zone" select="substring-before($zones, ' ')"/>
      <xsl:variable name="target" select="key('id', $zone)"/>

      <xsl:variable name="id">
        <xsl:call-template name="object.id">
           <xsl:with-param name="object" select="$target[1]"/>
        </xsl:call-template>
      </xsl:variable>

     <xsl:if test="$id != ''">
      <fo:basic-link internal-destination="{$id}"
                     xsl:use-attribute-sets="index.page.number.properties">
        <fo:page-number-citation ref-id="{$id}"/>
      </fo:basic-link>
     </xsl:if>

      <xsl:if test="$passivetex.extensions = '0'">
        <xsl:copy-of select="$number.separator"/>
      </xsl:if>
      <xsl:call-template name="reference">
        <xsl:with-param name="zones" select="substring-after($zones, ' ')"/>
        <xsl:with-param name="scope" select="$scope"/>
        <xsl:with-param name="role" select="$role"/>
        <xsl:with-param name="type" select="$type"/>
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
      <xsl:variable name="zone" select="$zones"/>
      <xsl:variable name="target" select="key('id', $zone)"/>

      <xsl:variable name="id">
        <xsl:call-template name="object.id">
          <xsl:with-param name="object" select="$target[1]"/>
        </xsl:call-template>
      </xsl:variable>

     <xsl:if test="$id != ''">
      <fo:basic-link internal-destination="{$id}"
                     xsl:use-attribute-sets="index.page.number.properties">
        <fo:page-number-citation ref-id="{$id}"/>
      </fo:basic-link>
     </xsl:if>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template name="info.reference">
  <!-- This is not perfect. It doesn't treat indexterm inside info element as a range covering whole parent of info.
       It also not work when there is no ID generated for parent element. But it works in the most common cases. -->
  <xsl:param name="scope" select="."/>
  <xsl:param name="role" select="''"/>
  <xsl:param name="type" select="''"/>

  <xsl:variable name="target" select="(ancestor::appendix|ancestor::article|ancestor::bibliography|ancestor::book|
                                       ancestor::chapter|ancestor::glossary|ancestor::part|ancestor::preface|
                                       ancestor::refentry|ancestor::reference|ancestor::refsect1|ancestor::refsect2|
                                       ancestor::refsect3|ancestor::refsection|ancestor::refsynopsisdiv|
                                       ancestor::sect1|ancestor::sect2|ancestor::sect3|ancestor::sect4|ancestor::sect5|
                                       ancestor::section|ancestor::setindex|ancestor::set|ancestor::sidebar)[&scope;]"/>
  
  <xsl:variable name="id">
    <xsl:call-template name="object.id">
      <xsl:with-param name="object" select="$target[1]"/>
    </xsl:call-template>
  </xsl:variable>
  
  <xsl:if test="$id != ''">
  <fo:basic-link internal-destination="{$id}"
                 xsl:use-attribute-sets="index.page.number.properties">
    <fo:page-number-citation ref-id="{$id}"/>
  </fo:basic-link>
  </xsl:if>

</xsl:template>

</xsl:stylesheet>
