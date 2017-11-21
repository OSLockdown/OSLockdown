<?xml version='1.0'?>
<!-- **********************************************************  -->
<!-- Copyright(c) 2007-2017 Forcepoint LLC                       --> 
                
<!-- XSL Custom Layer for PDF Creation of Documentation          -->
<!-- **********************************************************  -->

<!-- See http://docbook.sourceforge.net/release/xsl/current/doc/html/ -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                version="1.0">

<!-- Import master set of docbook xsl -->
<xsl:import href="docbook-xsl-stylesheets/fo/docbook.xsl"/>
<xsl:import href="./admin-tcs-pdf-custom-title.xsl"/>

<!-- Include TCS/Forcepoint mods to docbook stylesheets -->
<xsl:include href="FORCEPOINT_MODS/fo/ForcepointMods.xsl" />


<!-- *******************************************************
                    Generic Setttings
     ******************************************************* -->
  <xsl:param name="draft.mode">no</xsl:param> 
  <xsl:param name="fop1.extensions" select="1"></xsl:param>
  <xsl:param name="bookmarks.collapse" select="1"></xsl:param>
  <xsl:param name="alignment">left</xsl:param>
  <xsl:param name="hyphenate" select="'false'"/>
  <xsl:param name="callout.graphics.path" select="'Figures/'" />
  <xsl:param name="callout.graphics.extension">.png</xsl:param>
  <xsl:param name="generate.toc">
       appendix  toc
       book      toc,title,figure,table,example,procedure,equation
       preface   nop
       sect1     toc
       sect2     toc
       sect3     toc
       sect4     toc
       sect5     toc
       section   toc
       set       nop
   </xsl:param>
   <xsl:template match="appendix[@role = 'NotInToc']"  mode="toc" />

<!-- *******************************************************
                    Primary Document Layout
     ******************************************************* -->
  <xsl:param name="page.margin.inner" select="'0.5in'"/>
  <xsl:param name="page.margin.outer" select="'0.5in'"/>
  <xsl:param name="page.margin.top" select="'0.25in'"/>
  <xsl:param name="page.margin.bottom" select="'0.25in'"/>
  <xsl:param name="body.margin.top" select="'0.5in'"/>
  <xsl:param name="body.margin.bottom" select="'0.75in'"/>

  <xsl:param name="body.start.indent" select="'0pt'"/>
  <xsl:param name="body.font.family" select="'Times Roman'"/>
  <xsl:param name="body.font.master" select="10"/>

  <xsl:param name="generate.index" select="1"></xsl:param>
  <xsl:param name="glossary.as.blocks" select="1"></xsl:param>


  <xsl:attribute-set name="root.properties">
    <xsl:attribute name="text-align">left</xsl:attribute>
  </xsl:attribute-set>


<!-- *******************************************************
                 Chapter/Section Labeling, etc
     ******************************************************* -->
  <xsl:param name="chapter.autolabel" select="1"/>
  <xsl:param name="section.autolabel" select="1"/>
  <xsl:param name="section.label.includes.component.label" select="1"/>
  <xsl:param name="bibliography.numbered" select="1"></xsl:param>


<!-- *******************************************************
                     Cross Reference Links 
     ******************************************************* -->
  <xsl:param name="insert.xref.page.number">no</xsl:param> 
  <xsl:attribute-set name="xref.properties">
    <xsl:attribute name="color">#315581</xsl:attribute>
    <!-- If you want the link to be "underlined", uncomment the following -->
    <!-- <xsl:attribute name="border-bottom">1pt solid #315581</xsl:attribute> -->
  </xsl:attribute-set>


<!-- *******************************************************
                 Admonitions: Notes, Warnings, etc.
     ******************************************************* -->
<xsl:attribute-set name="admonition.properties">
  <xsl:attribute name="space-before">1em</xsl:attribute>
  <xsl:attribute name="space-after">1em</xsl:attribute>
  <xsl:attribute name="border">none</xsl:attribute>
  <xsl:attribute name="background-color">white</xsl:attribute>
  <xsl:attribute name="padding">0pt</xsl:attribute>
  <xsl:attribute name="font-size">10pt</xsl:attribute>
</xsl:attribute-set>
  <xsl:attribute-set name="admonition.title.properties">
    <xsl:attribute name="font-size">12pt</xsl:attribute>
    <xsl:attribute name="font-weight">bold</xsl:attribute>
    <xsl:attribute name="hyphenate">false</xsl:attribute>
    <xsl:attribute name="keep-with-next.within-column">always</xsl:attribute>
  </xsl:attribute-set>
  
  <xsl:attribute-set name="sidebar.properties" 
    use-attribute-sets="formal.object.properties">
    <xsl:attribute name="border-style">solid</xsl:attribute>
    <xsl:attribute name="border-width">1pt</xsl:attribute>
    <xsl:attribute name="border-color">black</xsl:attribute>
    <xsl:attribute name="background-color">#DDDDDD</xsl:attribute>
    <xsl:attribute name="padding-left">12pt</xsl:attribute>
    <xsl:attribute name="padding-right">12pt</xsl:attribute>
    <xsl:attribute name="padding-top">0pt</xsl:attribute>
    <xsl:attribute name="padding-bottom">8pt</xsl:attribute>
    <xsl:attribute name="margin-left">0pt</xsl:attribute>
    <xsl:attribute name="margin-right">0pt</xsl:attribute> 
    
      <xsl:attribute name="margin-top">6pt</xsl:attribute>
      <xsl:attribute name="margin-bottom">6pt</xsl:attribute> 
   
  </xsl:attribute-set>
  
  

<!-- *******************************************************
                           Lists
     ******************************************************* -->
<xsl:attribute-set name="list.block.properties">
  <xsl:attribute name="font-size">10pt</xsl:attribute>
</xsl:attribute-set>

<xsl:attribute-set name="list.item.spacing">
  <xsl:attribute name="space-before.optimum">0.2em</xsl:attribute>
  <xsl:attribute name="space-before.minimum">0.1em</xsl:attribute>
  <xsl:attribute name="space-before.maximum">1.0em</xsl:attribute>
</xsl:attribute-set>
  
  
  

<!-- *******************************************************
       Programlistings, screens, and literlayouts
     ******************************************************* -->
<xsl:param name="shade.verbatim" select="1"/>
<xsl:attribute-set name="shade.verbatim.style">
  <xsl:attribute name="background-color">#EEF1F8</xsl:attribute>
  <xsl:attribute name="border-width">0.5pt</xsl:attribute>
  <xsl:attribute name="border-style">solid</xsl:attribute>
  <xsl:attribute name="border-color">#C3D2E7</xsl:attribute>
  <xsl:attribute name="padding">8pt</xsl:attribute>
  <xsl:attribute name="margin">2pt</xsl:attribute>
</xsl:attribute-set>

  <xsl:attribute-set name="verbatim.properties">
    <xsl:attribute name="space-before.minimum">0.0em</xsl:attribute>
    <xsl:attribute name="space-before.optimum">0.1em</xsl:attribute>
    <xsl:attribute name="space-before.maximum">0.1em</xsl:attribute>
    <xsl:attribute name="space-after.minimum">0.1em</xsl:attribute>
    <xsl:attribute name="space-after.optimum">0.1em</xsl:attribute>
    <xsl:attribute name="space-after.maximum">0.1em</xsl:attribute>
    
    <xsl:attribute name="line-height">135%</xsl:attribute>
  </xsl:attribute-set>
<!-- *******************************************************
          Component Level Titles: Chapter, Appendix
     ******************************************************* -->
<xsl:attribute-set name="component.title.properties">
  <xsl:attribute name="font-size">18pt</xsl:attribute>
  <xsl:attribute name="font-family">Helvetica</xsl:attribute>
  <xsl:attribute name="space-before">2em</xsl:attribute>
</xsl:attribute-set>

<!-- *******************************************************
                Section Title Headers 
     ******************************************************* -->
    <xsl:attribute-set name="section.title.level1.properties">
      <xsl:attribute name="font-size">16pt</xsl:attribute>
      <xsl:attribute name="font-family">Helvetica</xsl:attribute>
      <xsl:attribute name="font-weight">bold</xsl:attribute>
      <xsl:attribute name="space-before">1em</xsl:attribute>
      <xsl:attribute name="space-after">0.5em</xsl:attribute>
<!--
      <xsl:attribute name="padding">2pt</xsl:attribute>
      <xsl:attribute name="border-bottom">3pt solid #C8C5A1</xsl:attribute>
-->
    </xsl:attribute-set>

    <xsl:attribute-set name="section.title.level2.properties">
      <xsl:attribute name="font-size">14pt</xsl:attribute>
      <xsl:attribute name="font-family">Helvetica</xsl:attribute>
      <xsl:attribute name="font-weight">bold</xsl:attribute>
      <xsl:attribute name="space-before">1em</xsl:attribute>
    </xsl:attribute-set>

    <xsl:attribute-set name="section.title.level3.properties">
      <xsl:attribute name="font-size">
        <xsl:value-of select="$body.font.master * 1.2"/>
        <xsl:text>pt</xsl:text>
      </xsl:attribute>
    </xsl:attribute-set>

    <xsl:attribute-set name="section.title.level4.properties">
      <xsl:attribute name="font-size">
        <xsl:value-of select="$body.font.master"/>
        <xsl:text>pt</xsl:text>
      </xsl:attribute>
    </xsl:attribute-set>

    <xsl:attribute-set name="section.title.level5.properties">
      <xsl:attribute name="font-size">
        <xsl:value-of select="$body.font.master"/>
        <xsl:text>pt</xsl:text>
      </xsl:attribute>
    </xsl:attribute-set>

    <xsl:attribute-set name="section.title.level6.properties">
      <xsl:attribute name="font-size">
        <xsl:value-of select="$body.font.master"/>
        <xsl:text>pt</xsl:text>
      </xsl:attribute>
    </xsl:attribute-set>

  <!-- *******************************************************
              Screen Capture and Figure Ref Placement 
    ******************************************************* -->
  <xsl:attribute-set name="figure.properties">
    <xsl:attribute name="text-align">center</xsl:attribute>
    <xsl:attribute name="space-before.minimum">0.2em</xsl:attribute>
    <xsl:attribute name="space-before.optimum">0.4em</xsl:attribute>
    <xsl:attribute name="space-before.maximum">0.6em</xsl:attribute>
    <xsl:attribute name="space-after.minimum">0.2em</xsl:attribute>
    <xsl:attribute name="space-after.optimum">0.4em</xsl:attribute>
    <xsl:attribute name="space-after.maximum">0.6em</xsl:attribute>
  </xsl:attribute-set>
  
  <xsl:attribute-set name="formal.title.properties" use-attribute-sets="normal.para.spacing">
    <xsl:attribute name="font-weight">bold</xsl:attribute>
    <xsl:attribute name="font-size">
      <xsl:value-of select="$body.font.master * 1.1"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
    <xsl:attribute name="hyphenate">false</xsl:attribute>
    <xsl:attribute name="space-after.minimum">0.2em</xsl:attribute>
    <xsl:attribute name="space-after.optimum">0.4em</xsl:attribute>
    <xsl:attribute name="space-after.maximum">0.6em</xsl:attribute>
    <xsl:attribute name="space-before.minimum">0.2em</xsl:attribute>
    <xsl:attribute name="space-before.optimum">0.4em</xsl:attribute>
    <xsl:attribute name="space-before.maximum">0.6em</xsl:attribute>
   
  </xsl:attribute-set>
  
  <xsl:param name="formal.title.placement">
    figure after
    example before
    equation before
    table before
    procedure before
    task before
  </xsl:param>
  
  

<!-- ====================================================================== -->
<!-- ==                       CUSTOM TEMPLATES                           == -->
<!-- == These override the default DocBook XSL/FO Stylesheet templates   == -->
<!-- ====================================================================== -->

<!-- *******************************************************
      Table Cell template - Special behavior for headers
     ******************************************************* -->
<xsl:template name="table.cell.block.properties">
  <xsl:if test="ancestor::thead">
    <xsl:attribute name="font-weight">bold</xsl:attribute>
  </xsl:if>
</xsl:template>
  
  <!-- *******************************************************
      Table Row template - Keep row together
     ******************************************************* -->
  <xsl:template name="table.row.properties">
    <xsl:attribute name="keep-together.within-column">always</xsl:attribute>
  </xsl:template>
  

<!-- Expand this template to add properties to any fo:table-cell -->
<xsl:template name="table.cell.properties">
  <xsl:param name="bgcolor.pi" select="''"/>
  <xsl:param name="rowsep.inherit" select="1"/>
  <xsl:param name="colsep.inherit" select="1"/>
  <xsl:param name="col" select="1"/>
  <xsl:param name="valign.inherit" select="''"/>
  <xsl:param name="align.inherit" select="''"/>
  <xsl:param name="char.inherit" select="''"/>

  <xsl:choose>
    <xsl:when test="ancestor::tgroup">

      <xsl:if test="$bgcolor.pi != ''">
        <xsl:attribute name="background-color">
          <xsl:value-of select="$bgcolor.pi"/>
        </xsl:attribute>
      </xsl:if>

      <!-- ********************************** -->
      <!-- TCS CUSTOM COLORS FOR TABLE HEADER -->
      <!-- ********************************** -->
      <xsl:if test="ancestor::thead">
        <xsl:attribute name="background-color">#EEF1F8</xsl:attribute>
        <xsl:attribute name="color">black</xsl:attribute>
      </xsl:if>

      <xsl:if test="$rowsep.inherit &gt; 0">
        <xsl:call-template name="border">
          <xsl:with-param name="side" select="'bottom'"/>
        </xsl:call-template>
      </xsl:if>

      <xsl:if test="$colsep.inherit &gt; 0 and 
                      $col &lt; (ancestor::tgroup/@cols|ancestor::entrytbl/@cols)[last()]">
        <xsl:call-template name="border">
          <xsl:with-param name="side" select="'right'"/>
        </xsl:call-template>
      </xsl:if>

      <xsl:if test="$valign.inherit != ''">
        <xsl:attribute name="display-align">
          <xsl:choose>
            <xsl:when test="$valign.inherit='top'">before</xsl:when>
            <xsl:when test="$valign.inherit='middle'">center</xsl:when>
            <xsl:when test="$valign.inherit='bottom'">after</xsl:when>
            <xsl:otherwise>
              <xsl:message>
                <xsl:text>Unexpected valign value: </xsl:text>
                <xsl:value-of select="$valign.inherit"/>
                <xsl:text>, center used.</xsl:text>
              </xsl:message>
              <xsl:text>center</xsl:text>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:attribute>
      </xsl:if>

      <xsl:choose>
        <xsl:when test="$align.inherit = 'char' and $char.inherit != ''">
          <xsl:attribute name="text-align">
            <xsl:value-of select="$char.inherit"/>
          </xsl:attribute>
        </xsl:when>
        <xsl:when test="$align.inherit != ''">
          <xsl:attribute name="text-align">
            <xsl:value-of select="$align.inherit"/>
          </xsl:attribute>
        </xsl:when>
      </xsl:choose>

    </xsl:when>

    <xsl:otherwise>
      <!-- HTML table -->
      <xsl:variable name="border" 
                    select="(ancestor::table |
                             ancestor::informaltable)[last()]/@border"/>
      <xsl:if test="$border != '' and $border != 0">
        <xsl:attribute name="border">
          <xsl:value-of select="$table.cell.border.thickness"/>
          <xsl:text> </xsl:text>
          <xsl:value-of select="$table.cell.border.style"/>
          <xsl:text> </xsl:text>
          <xsl:value-of select="$table.cell.border.color"/>
        </xsl:attribute>
      </xsl:if>
    </xsl:otherwise>
  </xsl:choose>

</xsl:template>

<!-- ******************************************************************** -->
<!--                        Custom Footers                                -->
<!-- ******************************************************************** -->
<xsl:template name="footer.content">
  <xsl:param name="pageclass" select="''"/>
  <xsl:param name="sequence" select="''"/>
  <xsl:param name="position" select="''"/>
  <xsl:param name="gentext-key" select="''"/>
  
  
  
  <fo:block>
    <!-- pageclass can be front, body, back -->
    <!-- sequence can be odd, even, first, blank -->
    <!-- position can be left, center, right -->
    <xsl:choose>
      <xsl:when test="$pageclass = 'titlepage'">
        <!-- nop; no footer on title pages -->
      </xsl:when>

      <!-- FOR DOUBLE SIDED PRINT -->
      <xsl:when test="$double.sided != 0 and $sequence = 'even' and $position='left'">
        <fo:page-number/>
      </xsl:when>

      <xsl:when test="$double.sided != 0 and ($sequence = 'odd' or $sequence = 'first') and $position='right'">
        <fo:page-number/>
      </xsl:when>

      <!-- FOR SINGLE SIDED PRINT -->
      <xsl:when test="$double.sided = 0 and $position='left'">
        <xsl:value-of select="/book/bookinfo/title"/>
      </xsl:when>
      <xsl:when test="$double.sided = 0 and $position='left'">
        <!-- nop; nothing for center field -->
      </xsl:when>
      <xsl:when test="$double.sided = 0 and $position='right'">
        <fo:page-number/>
      </xsl:when>


      <xsl:when test="$sequence='blank'">
        <xsl:choose>
          <xsl:when test="$double.sided != 0 and $position = 'left'">
            <fo:page-number/>
          </xsl:when>
          <xsl:when test="$double.sided = 0 and $position = 'center'">
            <fo:page-number/>
          </xsl:when>
          <xsl:otherwise>
            <!-- nop -->
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>


      <xsl:otherwise>
        <!-- nop -->
      </xsl:otherwise>
    </xsl:choose>
  </fo:block>
</xsl:template>



 

<!-- *******************************************************
        Custom 'literallayout' template
                I want all other "verbatim" elements to
                be shaded except this one. 
                ******************************************************* -->
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
      <fo:block id="{$id}" xsl:use-attribute-sets="monospace.verbatim.properties">
         <xsl:copy-of select="$content"/>
      </fo:block>
    </xsl:when>
    <xsl:otherwise>
          <fo:block id="{$id}" xsl:use-attribute-sets="verbatim.properties">
            <xsl:copy-of select="$content"/>
          </fo:block>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>
  

</xsl:stylesheet>
