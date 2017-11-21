<?xml version="1.0" encoding="UTF-8"?>
<!-- 
     *************************************************************************
        Copyright (c) 2007-2014 Forcepoint LLC.
        This file is released under the GPLv3 license.  
        See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
	or visit https://www.gnu.org/licenses/gpl.html instead.

       OS Lockdown:  Common Templates for all FO reports
     **************************************************************************
 -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:exslt="http://exslt.org/common" version="1.0">

  <xsl:include href="fo-report-styles.xsl"/>

<!--
    ***********************************************
      What compliancy metadata do you want to see?
    ***********************************************
-->
  <!-- all others are negated if this one is 0 -->
  <xsl:param name="show.compliancy" select='1'/>

  <!-- Specific metadata -->
  <xsl:param name="show.fisma-mappings" select='1'/>
  <xsl:param name="show.cag-mappings" select='1'/>
  <xsl:param name="show.cce-items" select='1'/>
  <xsl:param name="show.disa-items" select='1'/>
  <xsl:param name="show.cis-items" select='1'/>
  <xsl:param name="show.nsa-items" select='1'/>
  <xsl:param name="show.pci-dss" select='1'/>
  <xsl:param name="show.nispom-items" select='1'/>
  <xsl:param name="show.cip-items" select='1' />
  <xsl:param name="show.sans-items" select='1' />
  <xsl:param name="show.dhs-items" select='1' />
  <xsl:param name="show.dcid-items" select='1' />
  <xsl:param name="show.jafan-items" select='1' />


  <!-- ============================================================ -->
  <xsl:template name="module.result">
    <xsl:param name="results" />
    <xsl:choose>
            
      <xsl:when test="$results = 'Fail'">
        <fo:block xsl:use-attribute-sets="module-fail">
          <xsl:value-of select="$results"/>
        </fo:block>
      </xsl:when>

      <xsl:when test="$results = 'Error'">
        <fo:block xsl:use-attribute-sets="module-error">
          <xsl:value-of select="$results"/>
        </fo:block>
      </xsl:when>
            
      <xsl:when test="$results = 'Pass'">
        <fo:block xsl:use-attribute-sets="module-pass">
          <xsl:value-of select="$results"/>
        </fo:block>
      </xsl:when>

      <xsl:when test="$results = 'Applied'">
        <fo:block xsl:use-attribute-sets="module-applied">
          <xsl:value-of select="$results"/>
        </fo:block>
      </xsl:when>

      <xsl:when test="$results = 'Undone'">
        <fo:block xsl:use-attribute-sets="module-undone">
          <xsl:value-of select="$results"/>
        </fo:block>
      </xsl:when>


      <xsl:when test="$results = 'Manual Action'">
        <fo:block xsl:use-attribute-sets="module-manual">
          <xsl:value-of select="$results"/>
        </fo:block>
      </xsl:when>

      <xsl:when test="$results = 'NA'">
        <fo:block xsl:use-attribute-sets="module-na">
          <xsl:text>Not Applicable</xsl:text>
        </fo:block>
      </xsl:when>
            
      <xsl:when test="$results = 'Not Required'">
        <fo:block xsl:use-attribute-sets="module-notreq">
          <xsl:value-of select="$results"/>
        </fo:block>
      </xsl:when>

      <xsl:when test="$results = 'Module Unavailable'">
        <fo:block xsl:use-attribute-sets="module-unavail">
          <xsl:value-of select="$results"/>
        </fo:block>
      </xsl:when>
            
      <xsl:when test="$results = 'OS NA'">
        <fo:block xsl:use-attribute-sets="module-osna">
          <xsl:text>OS N/A</xsl:text>
        </fo:block>
      </xsl:when>
            
      <xsl:when test="$results = 'Not Scanned'">
        <fo:block xsl:use-attribute-sets="module-notscanned">
          <xsl:value-of select="$results"/>
        </fo:block>
      </xsl:when>
            
      <xsl:otherwise>
        <fo:block>
          <xsl:value-of select="$results"/>
        </fo:block>
      </xsl:otherwise>
            
    </xsl:choose>
        
  </xsl:template>
    
<!-- ======================================================================= -->
  <xsl:template name="module.result.symbol">
    <xsl:param name="results" />
    <xsl:choose>
            
      <xsl:when test="$results = 'Fail'">
        <fo:inline font-family="ZapfDingbats" color="red">&#x2717;</fo:inline>
      </xsl:when>
            
      <xsl:when test="$results = 'Pass'">
        <fo:inline font-family="ZapfDingbats" color="gray">&#x2713;</fo:inline>
      </xsl:when>
            
      <xsl:when test="$results = 'Not Applicable'">
        <fo:inline font-family="ZapfDingbats" color="white">&#x25CF;</fo:inline>
      </xsl:when>
            
      <xsl:when test="$results = 'OS NA'">
        <fo:inline font-family="ZapfDingbats" color="white">&#x25CF;</fo:inline>
      </xsl:when>
            
      <xsl:when test="$results = 'Not Scanned'">
        <fo:inline font-family="ZapfDingbats" color="white">&#x25CF;</fo:inline>
      </xsl:when>
            
      <xsl:otherwise>
        <fo:inline font-family="ZapfDingbats" color="white">&#x25CF;</fo:inline>
      </xsl:otherwise>
            
    </xsl:choose>
  </xsl:template>

  <!-- ======================================================================= -->
  <xsl:template name="module.compliancy.list2">
    <xsl:param name="compliancy"/>
    <xsl:if test="$show.compliancy = 1">
      <fo:list-block margin-left="0.6em" margin-bottom="1em" font-size="8pt"
               provisional-distance-between-starts="10pt"
               provisional-label-separation="3pt">

        <xsl:choose>
	  <xsl:when test="count(./compliancy/line-item) = 0">
            <fo:list-item>
              <fo:list-item-label end-indent="label-end()">
          	<fo:block>&#x2022;</fo:block>
              </fo:list-item-label>
              <fo:list-item-body start-indent="body-start()">
          	<fo:block>
          	None
          	</fo:block>
              </fo:list-item-body>
            </fo:list-item>
          </xsl:when>
	  <xsl:otherwise>

  	    <xsl:for-each select="compliancy/line-item[not(./@source=preceding-sibling::line-item/@source) or not(./@name=preceding-sibling::line-item/@name) or not(./@version=preceding-sibling::line-item/@version)]">
            	<xsl:variable name="source" select="@source"/>
	    	<xsl:variable name="name" select="@name"/>
	    	<xsl:variable name="version" select="@version"/>
                <fo:list-item>
            	  <fo:list-item-label end-indent="label-end()">
            	    <fo:block>&#x2022;</fo:block>
            	  </fo:list-item-label>
            	  <fo:list-item-body start-indent="body-start()">
            	    <fo:block>
   	    	       <xsl:value-of select="$source"/>
		       <xsl:text> </xsl:text>
		       <xsl:value-of select="$name"/>
		       <xsl:text> </xsl:text>
		       <xsl:value-of select="$version"/> 
		       <xsl:text> : </xsl:text>
	    	       <xsl:for-each select="../line-item[@source=$source and @name=$name and @version=$version]">
	    	  	   <xsl:value-of select="@item" />
            	  	   <xsl:if test="position() != last()">
            	  	     <xsl:text>, </xsl:text>
            	  	   </xsl:if>
	    	       </xsl:for-each>
                    </fo:block>
                  </fo:list-item-body>
                </fo:list-item>

  	    </xsl:for-each>
	  </xsl:otherwise>
	</xsl:choose>
      </fo:list-block>
    </xsl:if>
  </xsl:template>

    
<!-- ======================================================================= -->
  <xsl:template name="module.compliancy.list">
    <xsl:param name="compliancy"/>
        
    <fo:list-block margin-left="2em" margin-bottom="1em" font-size="10pt"
               provisional-distance-between-starts="10pt"
               provisional-label-separation="3pt">
            
      <xsl:for-each select="$compliancy/line-item">
        <xsl:sort select="@source"/>
        <xsl:sort select="@name"/>
        <xsl:sort select="@item"/>
        <fo:list-item>
          <fo:list-item-label end-indent="label-end()">
            <fo:block>&#x2022;</fo:block>
          </fo:list-item-label>
                    
          <fo:list-item-body start-indent="body-start()">
            <fo:block>
              <xsl:value-of select="@source"/>
              <xsl:text>&#x020;</xsl:text>
              <xsl:value-of select="@name"/>
              <xsl:text>&#x020; (</xsl:text>
              <xsl:value-of select="@version"/>
              <xsl:text>): </xsl:text>
              <xsl:value-of select="@item"/>
            </fo:block>
          </fo:list-item-body>
        </fo:list-item>
      </xsl:for-each>
    </fo:list-block>
        
  </xsl:template>
    
    <!-- ======================================================================= -->
    
  <xsl:template name="itemizedlist.label.markup">
    <xsl:param name="itemsymbol"/>
    <xsl:choose>
      <xsl:when test="$itemsymbol='none'"></xsl:when>
      <xsl:when test="$itemsymbol='disc'">&#x2022;</xsl:when>
      <xsl:when test="$itemsymbol='bullet'">&#x2022;</xsl:when>
      <xsl:when test="$itemsymbol='endash'">&#x2013;</xsl:when>
      <xsl:when test="$itemsymbol='emdash'">&#x2014;</xsl:when>
            
      <xsl:when test="$itemsymbol='square'">
        <fo:inline baseline-shift="25%" font-family="ZapfDingbats" font-size="40%">&#x25A0;</fo:inline>
      </xsl:when>
            
      <xsl:when test="$itemsymbol='diamond'">
        <fo:inline baseline-shift="25%" font-family="ZapfDingbats" font-size="60%">&#x2666;</fo:inline>
      </xsl:when>
            
      <xsl:otherwise>&#x2022;</xsl:otherwise>
    </xsl:choose>
  </xsl:template>
    
    <!-- ======================================================================= -->
  <xsl:template name="software.patch.list">
    <xsl:param name="patches"/>
    <xsl:param name="pkgname"/>
        
    <xsl:for-each select="$patches/patch[@pkg = $pkgname]">
      <xsl:sort select="@name"/>
      <fo:list-item>
        <fo:list-item-label end-indent="label-end()">
          <fo:block>
            <xsl:call-template name="itemizedlist.label.markup">
              <xsl:with-param name="itemsymbol" select="'disc'"/>
            </xsl:call-template>
          </fo:block>
        </fo:list-item-label>
        <fo:list-item-body start-indent="body-start()">
          <fo:block>
            <xsl:value-of select="@name"/>
          </fo:block>
        </fo:list-item-body>
      </fo:list-item>
    </xsl:for-each>
        
  </xsl:template>
    
    <!-- ======================================================================= -->
    <!-- Software install times and file modified times come in:                 -->
    <!--        "Tue Jan 26 11:28:25 EST 2010" but we need it to be more like    -->
    <!--                                            "2010-01-26 11:28:25"        -->
    <!-- ======================================================================= -->
  <xsl:template name="date.reformat">
    <xsl:param name="iDate"/>
    <xsl:variable name="iYear" select="substring($iDate, string-length($iDate)-4)"/>
    <xsl:variable name="iMonthName" select="substring($iDate, 5, 3)"/>
    <xsl:variable name="iDay" select="substring($iDate, 9, 2)"/>
    <xsl:variable name="iTime" select="substring($iDate, 12, 8)"/>
    <xsl:variable name="iTimezone" select="substring($iDate, 21, 3)"/>

    <xsl:variable name="iMonth">
      <xsl:choose>
        <xsl:when test="$iMonthName = 'Jan'">01</xsl:when>
        <xsl:when test="$iMonthName = 'Feb'">02</xsl:when>
        <xsl:when test="$iMonthName = 'Mar'">03</xsl:when>
        <xsl:when test="$iMonthName = 'Apr'">04</xsl:when>
        <xsl:when test="$iMonthName = 'May'">05</xsl:when>
        <xsl:when test="$iMonthName = 'Jun'">06</xsl:when>
        <xsl:when test="$iMonthName = 'Jul'">07</xsl:when>
        <xsl:when test="$iMonthName = 'Aug'">08</xsl:when>
        <xsl:when test="$iMonthName = 'Sep'">09</xsl:when>
        <xsl:when test="$iMonthName = 'Oct'">10</xsl:when>
        <xsl:when test="$iMonthName = 'Nov'">11</xsl:when>
        <xsl:when test="$iMonthName = 'Dec'">12</xsl:when>
      </xsl:choose>
    </xsl:variable>
    <xsl:copy-of select="$iYear"/>
    <xsl:text>-</xsl:text>
    <xsl:copy-of select="$iMonth"/>
    <xsl:text>-</xsl:text>
    <xsl:copy-of select="$iDay"/>
    <xsl:text> </xsl:text>
    <xsl:copy-of select="$iTime"/>
    <xsl:text> </xsl:text>
    <xsl:copy-of select="$iTimezone"/>
  </xsl:template>

    <!-- ======================================================================= -->
  <xsl:template name="pad.dots">
    <xsl:param name="count" select="1"/>
    <xsl:if test="$count > 0">
      <xsl:text>.</xsl:text>
      <xsl:call-template name="pad.dots">
        <xsl:with-param name="count" select="$count - 1"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>


<!-- ======================================================================= -->
  <xsl:template name="module.message.details">
    <xsl:param name="details"/>

    <xsl:if test="(count($details/statusMessage) != 0 and $details/statusMessage != '' and $details/statusMessage != 'None') or count($details/messages/message) != 0">
      <fo:block margin-top="1em" margin-bottom="0.5em" text-decoration="underline">
        <xsl:text>Module Messages:</xsl:text>
      </fo:block>
    </xsl:if>
    <xsl:if test="count($details/statusMessage) != 0 and $details/statusMessage != '' and $details/statusMessage != 'None'">
      <xsl:variable name="statusColor">
        <xsl:choose>
          <xsl:when test="$details/../@results = 'Fail'">red</xsl:when>
          <xsl:when test="$details/../@results = 'Error'">red</xsl:when>
          <xsl:when test="$details/../@results = 'Manual Action'">red</xsl:when>
          <xsl:when test="$details/../@results = 'Pass'">green</xsl:when>
          <xsl:otherwise>black</xsl:otherwise>
        </xsl:choose>
      </xsl:variable>
      <fo:block margin-left="1em" color="{$statusColor}" margin-bottom="0.5em" margin-top="0.5em">
        <xsl:value-of select="$details/statusMessage"/>
      </fo:block>
    </xsl:if>

    <xsl:if test="count($details/messages/message) &gt; 0">
      <fo:list-block margin-left="1em" margin-bottom="1em"
               provisional-distance-between-starts="10pt"
               provisional-label-separation="3pt">
        <xsl:for-each select="$details/messages/message">
          <fo:list-item>
            <fo:list-item-label end-indent="label-end()">
              <fo:block>&#x2022;</fo:block>
            </fo:list-item-label>
            
            <fo:list-item-body start-indent="body-start()">
              <xsl:variable name="msgColor">
                <xsl:choose>
                  <xsl:when test="substring-before(., ':') = 'Error'">red</xsl:when>
                  <xsl:when test="substring-before(., ':') = 'Manual'">red</xsl:when>
                  <xsl:when test="substring-before(., ':') = 'Fail'">red</xsl:when>
                  <xsl:when test="substring-before(., ':') = 'Retired'">blue</xsl:when>
                  <xsl:otherwise>black</xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
              <fo:block color="{$msgColor}">
                <xsl:value-of select="."/>
              </fo:block>
            </fo:list-item-body>
          </fo:list-item>
        </xsl:for-each>
      </fo:list-block>
    </xsl:if>

  </xsl:template>

    <!-- ======================================================================= -->
</xsl:stylesheet>
