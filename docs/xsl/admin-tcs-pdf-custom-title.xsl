<?xml version="1.0" ?> 
<!--  $Id 
--> 
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" version="1.0">
  <xsl:template name="book.titlepage">
   
    <!--  Title and Subtitle (Version) 
    --> 
    <fo:block-container absolute-position="absolute" left="0.2in" top="4.95in" width="7in" text-align="right">
      <fo:block font-family="Helvetica" font-size="20pt" font-weight="bold" color="#43B02A">
        <xsl:value-of select="/book/bookinfo/title" /> 
      </fo:block>
      <fo:block font-family="Helvetica" font-size="16pt" font-weight="bold">
        <xsl:value-of select="/book/bookinfo/subtitle" /> 
      </fo:block>
    </fo:block-container>
    <!--  Publish Date and Preparer Information 
    --> 
    <fo:block-container absolute-position="absolute" left="0.2in" top="6.2in" width="7in" text-align="right" font-family="Helvetica" font-size="14pt">
      <fo:block font-size="14pt" font-weight="bold" space-after="1.5em">
       November, 2017
        <xsl:value-of select="info/pubdate" /> 
      </fo:block>
      
    </fo:block-container>
   
    
    
   
   
    
    <xsl:call-template name="book.titlepage.before.verso" /> 
    <xsl:call-template name="book.titlepage.verso" /> 
    <xsl:call-template name="book.titlepage.separator" /> 
  </xsl:template>
</xsl:stylesheet>
