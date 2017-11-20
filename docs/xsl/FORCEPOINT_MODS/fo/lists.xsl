<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                version='1.0'>

<xsl:template match="orderedlist/listitem">
  <xsl:variable name="id"><xsl:call-template name="object.id"/></xsl:variable>

  <xsl:variable name="item.contents">
    <fo:list-item-label end-indent="label-end()" xsl:use-attribute-sets="orderedlist.label.properties">
      <fo:block>
        <xsl:apply-templates select="." mode="item-number"/>
      </fo:block>
    </fo:list-item-label>
    <fo:list-item-body start-indent="body-start()">
      <xsl:choose>
        <!-- * work around broken passivetex list-item-body rendering -->
        <xsl:when test="$passivetex.extensions = '1'">
          <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
          <fo:block>
            <xsl:apply-templates/>
          </fo:block>
        </xsl:otherwise>
      </xsl:choose>
    </fo:list-item-body>
  </xsl:variable>

  <xsl:choose>
    <xsl:when test="parent::*/@spacing = 'compact'">
      <fo:list-item id="{$id}" xsl:use-attribute-sets="compact.list.item.spacing">
        <xsl:copy-of select="$item.contents"/>
      </fo:list-item>
    </xsl:when>
    <xsl:otherwise>
      <fo:list-item id="{$id}" xsl:use-attribute-sets="list.item.spacing">
        <xsl:copy-of select="$item.contents"/>
      </fo:list-item>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<xsl:template match="variablelist" mode="vl.as.list">
  <xsl:variable name="id">
    <xsl:call-template name="object.id"/>
  </xsl:variable>

  <xsl:variable name="term-width">
    <xsl:call-template name="pi.dbfo_term-width"/>
  </xsl:variable>

  <xsl:variable name="termlength">
    <xsl:choose>
      <xsl:when test="$term-width != ''">
        <xsl:value-of select="$term-width"/>
      </xsl:when>
      <xsl:when test="@termlength">
        <xsl:variable name="termlength.is.number">
          <xsl:value-of select="@termlength"/>
        </xsl:variable>
        <xsl:choose>
          <xsl:when test="string($termlength.is.number) = 'NaN'">
            <!-- if the term length isn't just a number, assume it's a measurement -->
            <xsl:value-of select="@termlength"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="@termlength"/>
            <xsl:text>em</xsl:text>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="longest.term">
          <xsl:with-param name="terms" select="varlistentry/term"/>
          <xsl:with-param name="maxlength" select="$variablelist.max.termlength"/>
        </xsl:call-template>
        <xsl:text>em</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

<!--
  <xsl:message>
    <xsl:text>term width: </xsl:text>
    <xsl:value-of select="$termlength"/>
  </xsl:message>
-->

  <xsl:variable name="label-separation">1em</xsl:variable>
  <xsl:variable name="distance-between-starts">
    <xsl:value-of select="$termlength"/>
  </xsl:variable>

  <xsl:if test="title">
    <xsl:apply-templates select="title" mode="list.title.mode"/>
  </xsl:if>

  <!-- Preserve order of PIs and comments -->
  <xsl:apply-templates 
    select="*[not(self::varlistentry
              or self::title
              or self::titleabbrev)]
            |comment()[not(preceding-sibling::varlistentry)]
            |processing-instruction()[not(preceding-sibling::varlistentry)]"/>

  <xsl:variable name="content">
    <xsl:apply-templates mode="vl.as.list"
      select="varlistentry
              |comment()[preceding-sibling::varlistentry]
              |processing-instruction()[preceding-sibling::varlistentry]"/>
  </xsl:variable>

  <!-- nested lists don't add extra list-block spacing -->
  <xsl:choose>
    <xsl:when test="ancestor::listitem">
      <fo:list-block id="{$id}"
                     provisional-distance-between-starts=
                        "{$distance-between-starts}"
                     provisional-label-separation="{$label-separation}">
        <xsl:copy-of select="$content"/>
      </fo:list-block>
    </xsl:when>
    <xsl:otherwise>
      <fo:list-block id="{$id}"
                     provisional-distance-between-starts=
                        "{$distance-between-starts}"
                     provisional-label-separation="{$label-separation}"
                     xsl:use-attribute-sets="list.block.spacing">
        <xsl:copy-of select="$content"/>
      </fo:list-block>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="varlistentry" mode="vl.as.list">
  <xsl:variable name="id">
    <xsl:call-template name="object.id"/>
  </xsl:variable>
  <xsl:variable name="item.contents">
    <fo:list-item-label end-indent="label-end()" text-align="start">
      <fo:block>
        <xsl:apply-templates select="term"/>
      </fo:block>
    </fo:list-item-label>
    <fo:list-item-body start-indent="body-start()">
      <xsl:choose>
        <!-- * work around broken passivetex list-item-body rendering -->
        <xsl:when test="$passivetex.extensions = '1'">
          <xsl:apply-templates select="listitem"/>
        </xsl:when>
        <xsl:otherwise>
          <fo:block>
            <xsl:apply-templates select="listitem"/>
          </fo:block>
        </xsl:otherwise>
      </xsl:choose>
     </fo:list-item-body>
  </xsl:variable>

  <xsl:choose>
    <xsl:when test="parent::*/@spacing = 'compact'">
      <fo:list-item id="{$id}"
          xsl:use-attribute-sets="compact.list.item.spacing">
        <xsl:copy-of select="$item.contents"/>
      </fo:list-item>
    </xsl:when>
    <xsl:otherwise>
      <fo:list-item id="{$id}" xsl:use-attribute-sets="list.item.spacing">
        <xsl:copy-of select="$item.contents"/>
      </fo:list-item>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="procedure/step|substeps/step">
  <xsl:variable name="id">
    <xsl:call-template name="object.id"/>
  </xsl:variable>

  <fo:list-item xsl:use-attribute-sets="list.item.spacing">
    <fo:list-item-label end-indent="label-end()">
      <fo:block id="{$id}">
        <!-- dwc: fix for one step procedures. Use a bullet if there's no step 2 -->
        <xsl:choose>
          <xsl:when test="count(../step) = 1">
            <xsl:text>&#x2022;</xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:apply-templates select="." mode="number">
              <xsl:with-param name="recursive" select="0"/>
            </xsl:apply-templates>.
          </xsl:otherwise>
        </xsl:choose>
      </fo:block>
    </fo:list-item-label>
    <fo:list-item-body start-indent="body-start()">
      <xsl:choose>
        <!-- * work around broken passivetex list-item-body rendering -->
        <xsl:when test="$passivetex.extensions = '1'">
          <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
          <fo:block>
            <xsl:apply-templates/>
          </fo:block>
        </xsl:otherwise>
      </xsl:choose>
    </fo:list-item-body>
  </fo:list-item>
</xsl:template>

<xsl:template match="stepalternatives/step">
  <xsl:variable name="id">
    <xsl:call-template name="object.id"/>
  </xsl:variable>

  <fo:list-item xsl:use-attribute-sets="list.item.spacing">
    <fo:list-item-label end-indent="label-end()">
      <fo:block id="{$id}">
        <xsl:text>&#x2022;</xsl:text>
      </fo:block>
    </fo:list-item-label>
    <fo:list-item-body start-indent="body-start()">
      <xsl:choose>
        <!-- * work around broken passivetex list-item-body rendering -->
        <xsl:when test="$passivetex.extensions = '1'">
          <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
          <fo:block>
            <xsl:apply-templates/>
          </fo:block>
        </xsl:otherwise>
      </xsl:choose>
    </fo:list-item-body>
  </fo:list-item>
</xsl:template>

<xsl:template match="callout">
  <xsl:variable name="id"><xsl:call-template name="object.id"/></xsl:variable>
  <fo:list-item id="{$id}">
    <fo:list-item-label end-indent="label-end()">
      <fo:block>
        <xsl:call-template name="callout.arearefs">
          <xsl:with-param name="arearefs" select="@arearefs"/>
        </xsl:call-template>
      </fo:block>
    </fo:list-item-label>
    <fo:list-item-body start-indent="body-start()">
      <xsl:choose>
        <!-- * work around broken passivetex list-item-body rendering -->
        <xsl:when test="$passivetex.extensions = '1'">
          <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
          <fo:block>
            <xsl:apply-templates/>
          </fo:block>
        </xsl:otherwise>
      </xsl:choose>
    </fo:list-item-body>
  </fo:list-item>
</xsl:template>

</xsl:stylesheet>
