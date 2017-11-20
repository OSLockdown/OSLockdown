<?xml version="1.0"?>
<!-- Copyright(c) 2007-2017 Forcepoint LLC -->
<!-- See http://docbook.sourceforge.net/release/xsl/current/doc/html/ -->
<!-- $Id: tcs-javahelp.xsl 23875 2017-01-24 19:48:53Z acochrane $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
                xmlns:fo="http://www.w3.org/1999/XSL/Format" 
                xmlns:saxon="http://icl.com/saxon" 
                version="1.0">
    <xsl:import href="docbook-xsl-stylesheets/javahelp/javahelp.xsl"/>
    <xsl:include href="FORCEPOINT_MODS/javahelp/ForcepointMods.xsl" />
    <xsl:output method="html" 
              encoding="UTF-8"
              indent="yes" 
              saxon:character-representation="native;decimal"/>

    <!-- Just leave this blank. The top level makes/ant builds will
         set this. -->
    <xsl:param name="tcs.doc.rev" select="''"/>
    <!-- 
         Customizations Begin here 
    -->
    <xsl:param name="draft.mode" select="'no'"/> <!-- Will be overwritten from parents -->
    <xsl:param name="default.encoding">UTF-8</xsl:param>
    <xsl:param name="javahelp.encoding">utf-8</xsl:param>
    <xsl:param name="spacing.paras" select="0"/>
    <xsl:param name="css.decoration" select="0"/>
    <xsl:param name="generate.toc">
       appendix  toc,title,table
       book      toc,title,figure,table,example,procedure,equation
       chapter   toc,title
       part      title
       preface   title
       qandadiv  title
       qandaset  title
       reference title
       refentry  nop
       refentrytitle  nop
       sect1     toc
       sect2     toc
       sect3     toc
       sect4     toc
       sect5     toc
       section   title
       set       toc,title
    </xsl:param>
    <xsl:param name="suppress.navigation" select="'0'"/>
    <xsl:param name="suppress.header.navigation" select="'0'"/>
    <xsl:param name="suppress.footer.navigation" select="'0'"/>
    <xsl:param name="header.rule" select="'0'"/>
    <xsl:param name="footer.rule" select="'0'"/>
    <xsl:template match="appendix[@role = 'NotInToc']" mode="toc"/>
    <xsl:param name="xref.with.number.and.title" select="'1'"/>

    <!-- 
       NOTE: FOR PDF Documents, set these to 'yes' 
             See http://www.sagehill.net/docbookxsl/CustomXrefs.html 
    -->
    <xsl:param name="insert.xref.page.number" select="'no'"/>
    <xsl:param name="insert.link.page.number" select="'no'"/>

    <xsl:param name="chapter.autolabel" select="'1'"/>
    <xsl:param name="section.autolabel" select="'1'"/>
    <xsl:param name="section.label.includes.component.label" select="'1'"/>
    <xsl:param name="use.id.as.filename" select="'1'"/>
    <xsl:param name="chunk.section.depth" select="1"/>

   <!-- Callouts -->
    <xsl:param name="callout.graphics.path" select="'Figures/'" />
    <xsl:param name="callout.graphics.limit" select="15" />

   <!-- Admonitions -->
    <xsl:param name="admon.graphics" select="0" />
    <xsl:param name="admon.graphics.path" select="'Figures/'" />

    <xsl:param name="generate.index" select="1"/>
    <xsl:param name="html.cleanup" select="1"/>
    <xsl:param name="html.extra.head.links" select="0"/>
    <xsl:param name="chunker.output.indent">yes</xsl:param>
    <xsl:param name="html.stylesheet" select="'docbook.css'"/>
    <xsl:param name="html.cellspacing" select="0"/>
    <xsl:param name="html.cellpadding" select="1"/>
    <xsl:param name="table.cell.border.thickness">0.5pt</xsl:param>
    <xsl:param name="table.frame.border.thickness">0.5pt</xsl:param>
    <xsl:param name="tablecolumns.extension" select="1"/>
    <xsl:param name="bibliography.numbered" select="1"/>

    <!-- Hide remarks/comments used during draft mode -->
    <xsl:param name="show.comments" select="0"/>

</xsl:stylesheet>
