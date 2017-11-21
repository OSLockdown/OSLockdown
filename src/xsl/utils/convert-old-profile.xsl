<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- 
     =========================================================================
         Copyright (c) 2007-2014 Forcepoint LLC.
         This file is released under the GPLv3 license.  
         See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
	 or visit https://www.gnu.org/licenses/gpl.html instead.
         
         Purpose: Convert old profiles (with module_group) to v4.0.3+
     =========================================================================
    -->
 <xsl:output method="xml" encoding="UTF-8" indent="no" />
 <xsl:template match="/">
  <xsl:comment> Profile converted from 3.x to 4.x structure </xsl:comment>
  <xsl:element name="profile">
   <xsl:attribute name="name">
    <xsl:value-of select="/profile/@name"/>
   </xsl:attribute>

   <xsl:if test="/profile/@sysProfile = 'true' ">
    <xsl:attribute name="sysProfile">
     <xsl:value-of select="/profile/@sysProfile"/>
    </xsl:attribute>
   </xsl:if>

   <xsl:text>&#x0A;  </xsl:text>
   <xsl:element name="info">
    <xsl:text>&#x0A;    </xsl:text>
    <xsl:element name="description">
     <xsl:text>&#x0A;      </xsl:text>
     <xsl:element name="summary">
      <xsl:value-of select="/profile/info/description/summary"/>
     </xsl:element>
     <xsl:text>&#x0A;      </xsl:text>
     <xsl:element name="verbose">
      <xsl:value-of select="/profile/info/description/verbose"/>
     </xsl:element>
     <xsl:text>&#x0A;      </xsl:text>
     <xsl:element name="comments">
      <xsl:value-of select="/profile/info/description/comments"/>
     </xsl:element>
     <xsl:text>&#x0A;    </xsl:text>
    </xsl:element>
    <xsl:text>&#x0A;  </xsl:text>
   </xsl:element>

   <xsl:for-each select="//security_module">
    <xsl:sort select="@name"/>
    <xsl:variable name="optValue" select="./option"/>
    <xsl:text>&#x0A;  </xsl:text>
    <xsl:element name="security_module">
     <xsl:attribute name="name">
      <xsl:value-of select="@name"/>
     </xsl:attribute>
     <xsl:if test="$optValue != '' and $optValue != 'None'">
      <xsl:text>&#x0A;      </xsl:text>
      <xsl:element name="option">
       <xsl:value-of select="$optValue"/>
      </xsl:element>
      <xsl:text>&#x0A;  </xsl:text>
     </xsl:if>
    </xsl:element>
   </xsl:for-each>

   <xsl:text>&#x0A;</xsl:text>
  </xsl:element>
 </xsl:template>
</xsl:stylesheet>
