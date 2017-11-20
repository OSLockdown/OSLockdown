<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- 
 =========================================================================
   Copyright (c) 2007-2014 Forcepoint LLC.
   This file is released under the GPLv3 license.  
   See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
   or visit https://www.gnu.org/licenses/gpl.html instead.
   
   Purpose: Any Report XML to TEXT
            Intended to be used with command line only.

  $Id$
 =========================================================================
   Parameters:
     show.module.details - Show module descriptions and 
                           messages (1=enable/0=disable)

     show.module.compliancy - Show module list of compliancy line 
                              items (1=enable/0=disable)

     show.module.compliancy.source - Only show compliancy line items
                              from 'string' (e.g., DISA, CIS, NSA)
                              Default is 'DISA'


 =========================================================================
-->
  <xsl:param name="show.module.details" select="1"/>
  <xsl:param name="show.module.compliancy" select="1"/>
  <xsl:param name="show.module.compliancy.source">DISA</xsl:param>

  <xsl:output method="text" encoding="UTF-8" indent="yes" />
  <xsl:variable name="vLower" select="'abcdefghijklmnopqrstuvwxyz'"/>
  <xsl:variable name="vUpper" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>


  <xsl:template name="module.compliancy.list">
    <xsl:param name="compliancy"/>
    <xsl:text>&#x0A; &#x0A;</xsl:text>
    <xsl:text>    Compliancy:&#x0A;</xsl:text>
      <xsl:choose>
        <xsl:when test="count(./compliancy/line-item) = 0"><xsl:text>        None</xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:for-each select="compliancy/line-item[	not(./@version=preceding-sibling::line-item/@version) or not(./@source=preceding-sibling::line-item/@source) or not(./@name=preceding-sibling::line-item/@name) ]">
              <xsl:variable name="source" select="@source"/>
              <xsl:variable name="name" select="@name"/>
              <xsl:variable name="version" select="@version"/>
              <xsl:text>&#x0A;        </xsl:text>
              <xsl:value-of select="$source"/>
              <xsl:text> </xsl:text>
              <xsl:value-of select="$name"/>
              <xsl:text> </xsl:text>
              <xsl:value-of select="$version"/> 
              <xsl:text> : </xsl:text>
              <xsl:text>&#x0A;            </xsl:text>
              <xsl:variable name="CompItems">
              	<xsl:for-each select="../line-item[@source=$source and @name=$name and @version=$version]">
        	    <xsl:value-of select="@item" />
        	    <xsl:if test="position() != last()">
        	      <xsl:text>, </xsl:text>
        	    </xsl:if>
              	</xsl:for-each>
              </xsl:variable>
    	      <xsl:call-template name="textwrap">
    	        <xsl:with-param name="original" select="normalize-space($CompItems)"/>
    	        <xsl:with-param name="maxLength" select="70"/>
    	        <xsl:with-param name="separator" select="'&#x0A;            '"/>
    	        <xsl:with-param name="wordWrap" select="'true'"/>
    	      </xsl:call-template>
          </xsl:for-each>
        </xsl:otherwise>
      </xsl:choose>
  </xsl:template>
      
    
 <!-- ======================================================================= -->
  <xsl:template name="textwrap">
    <xsl:param name="original"/>
    <xsl:param name="maxLength"/>
    <xsl:param name="separator"/>
    <xsl:param name="wordWrap"/>
    <xsl:choose>
      <xsl:when test="string-length($original)>$maxLength">
        <xsl:variable name="length-substring">
          <xsl:choose>
            <xsl:when test="$wordWrap='true'">
              <xsl:call-template name="lastCharPosition">
                <xsl:with-param name="original" select="substring($original,1,$maxLength)"/>
                <xsl:with-param name="character" select="' '"/>
              </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="$maxLength"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:variable>
        <xsl:value-of select="concat(substring($original,1,$length-substring),$separator)"/>
        <xsl:call-template name="textwrap">
          <xsl:with-param name="original"  select="substring($original,$length-substring+1,string-length($original))"/>
          <xsl:with-param name="maxLength" select="$maxLength"/>
          <xsl:with-param name="separator" select="$separator"/>
          <xsl:with-param name="wordWrap"  select="'true'"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$original"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
    
<!-- This template returns the position of the last given character in the string that
     can be found. When the character is not available in the string, the position of the last
     character is returned.
     
	   Input parameters:
		   original (mandatory): original string in which the character must be searched
		   character(mandatory): character for which the last position must be returned
-->
  <xsl:template name="lastCharPosition">
    <xsl:param name="original"/>
    <xsl:param name="character"/>
    <xsl:param name="string_length"/>
    <xsl:variable name="len">
      <xsl:choose>
        <xsl:when test="$string_length">
          <xsl:value-of select="$string_length"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="'0'"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="char_len">
      <xsl:value-of select="string-length($character)"/>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="contains($original,$character)">
        <xsl:choose>
          <xsl:when test="contains(substring-after($original,$character),$character)">
            <xsl:call-template name="lastCharPosition">
              <xsl:with-param name="original" select="substring-after($original,$character)"/>
              <xsl:with-param name="character" select="$character"/>
              <xsl:with-param name="string_length"
                                 select="string-length(concat(substring-before($original,$character),' '))+$len"/>
            </xsl:call-template>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="string-length(substring-before($original,$character))+$char_len+$len"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="string-length($original)"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
    
<!-- 
  =========================================================================
                           ASSESSMENT REPORT 
  =========================================================================
-->
    
  <xsl:template match="/AssessmentReport">
    <xsl:text>&#x0A;ASSESSMENT REPORT</xsl:text>
    <xsl:text>&#x0A;Created </xsl:text>
    <xsl:value-of select="/AssessmentReport/report/@created"/>
    <xsl:text> by OS Lockdown v</xsl:text>
    <xsl:value-of select="/AssessmentReport/@sbVersion"/>

    <xsl:text>&#x0A;&#x0A;</xsl:text>
    <xsl:text>Summary:&#x0A;</xsl:text>
    <xsl:text>--------------------------------------------------------------------</xsl:text>
    <xsl:text>&#x0A;</xsl:text>
        
    <xsl:text>         Created: </xsl:text>
    <xsl:value-of select="/AssessmentReport/report/@created"/>
    <xsl:text>&#x0A;</xsl:text>
    <xsl:text>        Hostname: </xsl:text>
    <xsl:value-of select="/AssessmentReport/report/@hostname"/>
    <xsl:text>&#x0A;</xsl:text>

    <xsl:text>Operating System: </xsl:text>
    <xsl:variable name="distVersion" select="/AssessmentReport/report/@distVersion"/>
    <xsl:variable name="dist" select="/AssessmentReport/report/@dist"/>
    <xsl:choose>
      <xsl:when test="$distVersion = '10' and $dist = 'redhat'">
        <xsl:text>Fedora 10</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="/AssessmentReport/report/@dist"/>
        <xsl:text> </xsl:text>
        <xsl:value-of select="/AssessmentReport/report/@distVersion"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:text> (</xsl:text>
    <xsl:value-of select="/AssessmentReport/report/@arch"/>
    <xsl:text>) [Kernel </xsl:text>
    <xsl:value-of select="/AssessmentReport/report/@kernel"/>
    <xsl:text>]&#x0A;</xsl:text>

        
    <xsl:text>         Profile: </xsl:text>
    <xsl:value-of select="/AssessmentReport/report/@profile"/>
    <xsl:text>&#x0A;</xsl:text>

    <xsl:variable name="modFail" select="count(/AssessmentReport/modules/module[@results='Fail'])"/>
    <xsl:variable name="modPass" select="count(/AssessmentReport/modules/module[@results='Pass'])"/>
    <xsl:variable name="modOther" select="count(/AssessmentReport/modules/module[@results !='Pass' and @results !='Fail'])"/>
        
    <xsl:text>&#x0A;</xsl:text>
    <xsl:text>  Modules Failed: </xsl:text>
    <xsl:value-of select="$modFail"/>
    <xsl:text> (</xsl:text>
    <xsl:value-of select="round(($modFail div ($modFail + $modPass)) * 100)"/>
    <xsl:text>%) &#x0A;</xsl:text>
        
    <xsl:text>          Passed: </xsl:text>
    <xsl:value-of select="$modPass"/>
    <xsl:text>&#x0A;</xsl:text>
    <xsl:text>           Other: </xsl:text>
    <xsl:value-of select="$modOther"/>
    <xsl:text>&#x0A;</xsl:text>
        
    <xsl:text>&#x0A;</xsl:text>

    <xsl:if test="count(/AssessmentReport/modules/module[@severity='High']) != 0">
      <xsl:text>&#x0A;High Risk:&#x0A;</xsl:text>
      <xsl:text>--------------------------------------------------------------------&#x0A;</xsl:text>
      <xsl:for-each select="/AssessmentReport/modules/module[@severity='High']">
        <xsl:sort select="@results"/>
        <xsl:sort select="@name"/>
        <xsl:text>   </xsl:text>
        <xsl:variable name="spaces">.............................</xsl:variable>
        <xsl:value-of select="substring(concat(@name, $spaces, $spaces), 1, 60)"/>
        <xsl:value-of select="@results"/>
        <xsl:text>&#x0A;</xsl:text>

        <!-- Show Module Details -->
        <xsl:if test="$show.module.details = '1'">
          <xsl:text>&#x0A;     </xsl:text>
          <xsl:call-template name="textwrap">
            <xsl:with-param name="original" select="normalize-space(./description)"/>
            <xsl:with-param name="maxLength" select="60"/>
            <xsl:with-param name="separator" select="'&#x0A;     '"/>
            <xsl:with-param name="wordWrap" select="'true'"/>
          </xsl:call-template>
          <xsl:text>&#x0A; &#x0A;</xsl:text>
          <xsl:if test="./details/statusMessage/text() != '' and ./details/statusMessage/text() != 'None'" >
            <xsl:text>     - </xsl:text>
            <xsl:call-template name="textwrap">
              <xsl:with-param name="original" select="normalize-space(./details/statusMessage)"/>
              <xsl:with-param name="maxLength" select="55"/>
              <xsl:with-param name="separator" select="'&#x0A;       '"/>
              <xsl:with-param name="wordWrap" select="'true'"/>
            </xsl:call-template>
            <xsl:text>&#x0A;</xsl:text>
          </xsl:if>
          <xsl:if test="count(./details/messages/message) != 0">
            <xsl:for-each select="./details/messages/message">
              <xsl:text>&#x0A;       * </xsl:text>
              <xsl:call-template name="textwrap">
                <xsl:with-param name="original" select="normalize-space(.)"/>
                <xsl:with-param name="maxLength" select="55"/>
                <xsl:with-param name="separator" select="'&#x0A;         '"/>
                <xsl:with-param name="wordWrap" select="'true'"/>
              </xsl:call-template>
            </xsl:for-each>
          </xsl:if>
        </xsl:if>

        <!-- Show module compliancy -->
        <xsl:if test="$show.module.compliancy = '1'">
          <xsl:call-template name="module.compliancy.list">
            <xsl:with-param name="compliancy" select="./compliancy"/>
          </xsl:call-template>
        </xsl:if>

        <xsl:text>&#x0A; &#x0A; &#x0A;</xsl:text>

      </xsl:for-each>
    </xsl:if>
        
    <xsl:if test="count(/AssessmentReport/modules/module[@severity='Medium']) != 0">
      <xsl:text>&#x0A;Medium Risk:&#x0A;</xsl:text>
      <xsl:text>--------------------------------------------------------------------&#x0A;</xsl:text>
      <xsl:for-each select="/AssessmentReport/modules/module[@severity='Medium']">
        <xsl:sort select="@results"/>
        <xsl:sort select="@name"/>
        <xsl:text>   </xsl:text>
        <xsl:variable name="spaces">.............................</xsl:variable>
        <xsl:value-of select="substring(concat(@name, $spaces, $spaces), 1, 60)"/>
        <xsl:value-of select="@results"/>
        <xsl:text>&#x0A;</xsl:text>

        <!-- Show Module Details -->
        <xsl:if test="$show.module.details = '1'">
          <xsl:text>&#x0A;     </xsl:text>
          <xsl:call-template name="textwrap">
            <xsl:with-param name="original" select="normalize-space(./description)"/>
            <xsl:with-param name="maxLength" select="60"/>
            <xsl:with-param name="separator" select="'&#x0A;     '"/>
            <xsl:with-param name="wordWrap" select="'true'"/>
          </xsl:call-template>
          <xsl:text>&#x0A; &#x0A;</xsl:text>
          <xsl:if test="./details/statusMessage/text() != '' and ./details/statusMessage/text() != 'None'" >
            <xsl:text>     - </xsl:text>
            <xsl:call-template name="textwrap">
              <xsl:with-param name="original" select="normalize-space(./details/statusMessage)"/>
              <xsl:with-param name="maxLength" select="55"/>
              <xsl:with-param name="separator" select="'&#x0A;       '"/>
              <xsl:with-param name="wordWrap" select="'true'"/>
            </xsl:call-template>
            <xsl:text>&#x0A;</xsl:text>
          </xsl:if>
          <xsl:if test="count(./details/messages/message) != 0">
            <xsl:for-each select="./details/messages/message">
              <xsl:text>&#x0A;       * </xsl:text>
              <xsl:call-template name="textwrap">
                <xsl:with-param name="original" select="normalize-space(.)"/>
                <xsl:with-param name="maxLength" select="55"/>
                <xsl:with-param name="separator" select="'&#x0A;         '"/>
                <xsl:with-param name="wordWrap" select="'true'"/>
              </xsl:call-template>
            </xsl:for-each>
          </xsl:if>
        </xsl:if>

       <!-- Show module compliancy -->
        <xsl:if test="$show.module.compliancy = '1'">
          <xsl:call-template name="module.compliancy.list">
            <xsl:with-param name="compliancy" select="./compliancy"/>
          </xsl:call-template>
        </xsl:if>

        <xsl:text>&#x0A; &#x0A; &#x0A;</xsl:text>

      </xsl:for-each>
    </xsl:if>
        
    <xsl:if test="count(/AssessmentReport/modules/module[@results='Fail' and @severity='Low']) != 0">
      <xsl:text>&#x0A;Low Risk:&#x0A;</xsl:text>
      <xsl:text>--------------------------------------------------------------------&#x0A;</xsl:text>
      <xsl:for-each select="/AssessmentReport/modules/module[@severity='Low']">
        <xsl:sort select="@results"/>
        <xsl:sort select="@name"/>
        <xsl:text>   </xsl:text>
        <xsl:variable name="spaces">.............................</xsl:variable>
        <xsl:value-of select="substring(concat(@name, $spaces, $spaces), 1, 60)"/>
        <xsl:value-of select="@results"/>
        <xsl:text>&#x0A;</xsl:text>

        <!-- Show Module Details -->
        <xsl:if test="$show.module.details = '1'">
          <xsl:text>&#x0A;     </xsl:text>
          <xsl:call-template name="textwrap">
            <xsl:with-param name="original" select="normalize-space(./description)"/>
            <xsl:with-param name="maxLength" select="60"/>
            <xsl:with-param name="separator" select="'&#x0A;     '"/>
            <xsl:with-param name="wordWrap" select="'true'"/>
          </xsl:call-template>
          <xsl:text>&#x0A; &#x0A;</xsl:text>
          <xsl:if test="./details/statusMessage/text() != '' and ./details/statusMessage/text() != 'None'" >
            <xsl:text>     - </xsl:text>
            <xsl:call-template name="textwrap">
              <xsl:with-param name="original" select="normalize-space(./details/statusMessage)"/>
              <xsl:with-param name="maxLength" select="55"/>
              <xsl:with-param name="separator" select="'&#x0A;       '"/>
              <xsl:with-param name="wordWrap" select="'true'"/>
            </xsl:call-template>
            <xsl:text>&#x0A;</xsl:text>
          </xsl:if>
          <xsl:if test="count(./details/messages/message) != 0">
            <xsl:for-each select="./details/messages/message">
              <xsl:text>&#x0A;       * </xsl:text>
              <xsl:call-template name="textwrap">
                <xsl:with-param name="original" select="normalize-space(.)"/>
                <xsl:with-param name="maxLength" select="55"/>
                <xsl:with-param name="separator" select="'&#x0A;         '"/>
                <xsl:with-param name="wordWrap" select="'true'"/>
              </xsl:call-template>
            </xsl:for-each>
          </xsl:if>
        </xsl:if>

        <!-- Show module compliancy -->
        <xsl:if test="$show.module.compliancy = '1'">
          <xsl:call-template name="module.compliancy.list">
            <xsl:with-param name="compliancy" select="./compliancy"/>
          </xsl:call-template>
        </xsl:if>

        <xsl:text>&#x0A; &#x0A; &#x0A;</xsl:text>
      </xsl:for-each>
    </xsl:if>
        
  </xsl:template>

<!--
  =========================================================================
                              APPLY REPORT
  =========================================================================
-->
  <xsl:template match="/ApplyReport">
    <xsl:text>&#x0A;APPLY REPORT</xsl:text>
    <xsl:text>&#x0A;Created </xsl:text>
    <xsl:value-of select="/ApplyReport/report/@created"/>
    <xsl:text> by OS Lockdown v</xsl:text>
    <xsl:value-of select="/ApplyReport/@sbVersion"/>

    <xsl:text>&#x0A;&#x0A;</xsl:text>
    <xsl:text>Summary:&#x0A;</xsl:text>
    <xsl:text>--------------------------------------------------------------------</xsl:text>
    <xsl:text>&#x0A;</xsl:text>
        
    <xsl:text>         Created: </xsl:text>
    <xsl:value-of select="/ApplyReport/report/@created"/>
    <xsl:text>&#x0A;</xsl:text>
    <xsl:text>        Hostname: </xsl:text>
    <xsl:value-of select="/ApplyReport/report/@hostname"/>
    <xsl:text>&#x0A;</xsl:text>

    <xsl:text>Operating System: </xsl:text>
    <xsl:variable name="distVersion" select="/ApplyReport/report/@distVersion"/>
    <xsl:variable name="dist" select="/ApplyReport/report/@dist"/>
    <xsl:choose>
      <xsl:when test="$distVersion = '10' and $dist = 'redhat'">
        <xsl:text>Fedora 10</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="/ApplyReport/report/@dist"/>
        <xsl:text> </xsl:text>
        <xsl:value-of select="/ApplyReport/report/@distVersion"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:text> (</xsl:text>
    <xsl:value-of select="/ApplyReport/report/@arch"/>
    <xsl:text>) [Kernel </xsl:text>
    <xsl:value-of select="/ApplyReport/report/@kernel"/>
    <xsl:text>]&#x0A;</xsl:text>

        
    <xsl:text>         Profile: </xsl:text>
    <xsl:value-of select="/ApplyReport/report/@profile"/>
    <xsl:text>&#x0A;</xsl:text>

    <xsl:variable name="modError" select="count(/ApplyReport/modules/module[@results='Error'])"/>
    <xsl:variable name="modApplied" select="count(/ApplyReport/modules/module[@results='Applied'])"/>
    <xsl:variable name="modOther" select="count(/ApplyReport/modules/module[@results !='Applied' and @results !='Error'])"/>
        
    <xsl:text>&#x0A;</xsl:text>
    <xsl:text> Modules Applied: </xsl:text>
    <xsl:value-of select="$modApplied"/>
    <xsl:text> (</xsl:text>
    <xsl:value-of select="round(($modError div ($modError + $modApplied)) * 100)"/>
    <xsl:text>%) &#x0A;</xsl:text>
        
    <xsl:text>          Errors: </xsl:text>
    <xsl:value-of select="$modError"/>
    <xsl:text>&#x0A;</xsl:text>
    <xsl:text>           Other: </xsl:text>
    <xsl:value-of select="$modOther"/>
    <xsl:text>&#x0A;</xsl:text>
        
    <xsl:text>&#x0A;</xsl:text>

    <xsl:if test="count(/ApplyReport/modules/module[@results='Applied']) != 0">
      <xsl:text>&#x0A;Applied:&#x0A;</xsl:text>
      <xsl:text>--------------------------------------------------------------------&#x0A;</xsl:text>
      <xsl:for-each select="/ApplyReport/modules/module[@results='Applied']">
        <xsl:sort select="@name"/>
        <xsl:variable name="spaces">.............................</xsl:variable>
        <xsl:text>   </xsl:text>
        <xsl:value-of select="substring(concat(@name, $spaces, $spaces), 1, 60)"/>
        <xsl:value-of select="@results"/>
        <xsl:text>&#x0A;</xsl:text>
        
        <!-- Show Module Details -->
        <xsl:if test="$show.module.details = '1'">
          <xsl:text>&#x0A;     </xsl:text>
          <xsl:call-template name="textwrap">
            <xsl:with-param name="original" select="normalize-space(./description)"/>
            <xsl:with-param name="maxLength" select="60"/>
            <xsl:with-param name="separator" select="'&#x0A;     '"/>
            <xsl:with-param name="wordWrap" select="'true'"/>
          </xsl:call-template>
          <xsl:text>&#x0A; &#x0A;</xsl:text>
          <xsl:if test="./details/statusMessage/text() != '' and ./details/statusMessage/text() != 'None'" >
            <xsl:text>     - </xsl:text>
            <xsl:call-template name="textwrap">
              <xsl:with-param name="original" select="normalize-space(./details/statusMessage)"/>
              <xsl:with-param name="maxLength" select="55"/>
              <xsl:with-param name="separator" select="'&#x0A;       '"/>
              <xsl:with-param name="wordWrap" select="'true'"/>
            </xsl:call-template>
            <xsl:text>&#x0A;</xsl:text>
          </xsl:if>
          <xsl:if test="count(./details/messages/message) != 0">
            <xsl:for-each select="./details/messages/message">
              <xsl:text>&#x0A;       * </xsl:text>
              <xsl:call-template name="textwrap">
                <xsl:with-param name="original" select="normalize-space(.)"/>
                <xsl:with-param name="maxLength" select="55"/>
                <xsl:with-param name="separator" select="'&#x0A;         '"/>
                <xsl:with-param name="wordWrap" select="'true'"/>
              </xsl:call-template>
            </xsl:for-each>
          </xsl:if>
        </xsl:if>

        <!-- Show module compliancy -->
        <xsl:if test="$show.module.compliancy = '1'">
          <xsl:call-template name="module.compliancy.list">
            <xsl:with-param name="compliancy" select="./compliancy"/>
          </xsl:call-template>
        </xsl:if>

        <xsl:text>&#x0A; &#x0A;</xsl:text>

      </xsl:for-each>
    </xsl:if>
        
    <xsl:if test="count(/ApplyReport/modules/module[@results='Error']) != 0">
      <xsl:text>&#x0A;Errors:&#x0A;</xsl:text>
      <xsl:text>--------------------------------------------------------------------&#x0A;</xsl:text>
      <xsl:for-each select="/ApplyReport/modules/module[@results='Error']">
        <xsl:sort select="@name"/>
        <xsl:variable name="spaces">.............................</xsl:variable>
        <xsl:text>   </xsl:text>
        <xsl:value-of select="substring(concat(@name, $spaces, $spaces), 1, 60)"/>
        <xsl:value-of select="@results"/>
        <xsl:text>&#x0A;</xsl:text>

        <!-- Show Module Details -->
        <xsl:if test="$show.module.details = '1'">
          <xsl:text>&#x0A;     </xsl:text>
          <xsl:call-template name="textwrap">
            <xsl:with-param name="original" select="normalize-space(./description)"/>
            <xsl:with-param name="maxLength" select="60"/>
            <xsl:with-param name="separator" select="'&#x0A;     '"/>
            <xsl:with-param name="wordWrap" select="'true'"/>
          </xsl:call-template>
          <xsl:text>&#x0A; &#x0A;</xsl:text>
          <xsl:if test="./details/statusMessage/text() != '' and ./details/statusMessage/text() != 'None'" >
            <xsl:text>     - </xsl:text>
            <xsl:call-template name="textwrap">
              <xsl:with-param name="original" select="normalize-space(./details/statusMessage)"/>
              <xsl:with-param name="maxLength" select="55"/>
              <xsl:with-param name="separator" select="'&#x0A;       '"/>
              <xsl:with-param name="wordWrap" select="'true'"/>
            </xsl:call-template>
            <xsl:text>&#x0A;</xsl:text>
          </xsl:if>
          <xsl:if test="count(./details/messages/message) != 0">
            <xsl:for-each select="./details/messages/message">
              <xsl:text>&#x0A;       * </xsl:text>
              <xsl:call-template name="textwrap">
                <xsl:with-param name="original" select="normalize-space(.)"/>
                <xsl:with-param name="maxLength" select="55"/>
                <xsl:with-param name="separator" select="'&#x0A;         '"/>
                <xsl:with-param name="wordWrap" select="'true'"/>
              </xsl:call-template>
            </xsl:for-each>
          </xsl:if>
        </xsl:if>

        <!-- Show module compliancy -->
        <xsl:if test="$show.module.compliancy = '1'">
          <xsl:call-template name="module.compliancy.list">
            <xsl:with-param name="compliancy" select="./compliancy"/>
          </xsl:call-template>
        </xsl:if>

        <xsl:text>&#x0A; &#x0A;</xsl:text>

      </xsl:for-each>
    </xsl:if>
        
    <xsl:if test="count(/ApplyReport/modules/module[@results != 'Applied' and @results != 'Error']) != 0">
      <xsl:text>&#x0A;Not required or not applicable:&#x0A;</xsl:text>
      <xsl:text>--------------------------------------------------------------------&#x0A;</xsl:text>
      <xsl:for-each select="/ApplyReport/modules/module[@results != 'Applied' and @results != 'Error']">
        <xsl:sort select="@name"/>
        <xsl:variable name="spaces">.............................</xsl:variable>
        <xsl:text>   </xsl:text>
        <xsl:value-of select="substring(concat(@name, $spaces, $spaces), 1, 60)"/>
        <xsl:value-of select="@results"/>
        <xsl:text>&#x0A;</xsl:text>

        <!-- Show Module Details -->
        <xsl:if test="$show.module.details = '1'">
          <xsl:text>&#x0A;     </xsl:text>
          <xsl:call-template name="textwrap">
            <xsl:with-param name="original" select="normalize-space(./description)"/>
            <xsl:with-param name="maxLength" select="60"/>
            <xsl:with-param name="separator" select="'&#x0A;     '"/>
            <xsl:with-param name="wordWrap" select="'true'"/>
          </xsl:call-template>
          <xsl:text>&#x0A; &#x0A;</xsl:text>
          <xsl:if test="./details/statusMessage/text() != '' and ./details/statusMessage/text() != 'None'" >
            <xsl:text>     - </xsl:text>
            <xsl:call-template name="textwrap">
              <xsl:with-param name="original" select="normalize-space(./details/statusMessage)"/>
              <xsl:with-param name="maxLength" select="55"/>
              <xsl:with-param name="separator" select="'&#x0A;       '"/>
              <xsl:with-param name="wordWrap" select="'true'"/>
            </xsl:call-template>
            <xsl:text>&#x0A;</xsl:text>
          </xsl:if>
          <xsl:if test="count(./details/messages/message) != 0">
            <xsl:for-each select="./details/messages/message">
              <xsl:text>&#x0A;       * </xsl:text>
              <xsl:call-template name="textwrap">
                <xsl:with-param name="original" select="normalize-space(.)"/>
                <xsl:with-param name="maxLength" select="55"/>
                <xsl:with-param name="separator" select="'&#x0A;         '"/>
                <xsl:with-param name="wordWrap" select="'true'"/>
              </xsl:call-template>
            </xsl:for-each>
          </xsl:if>
        </xsl:if>

        <!-- Show module compliancy -->
        <xsl:if test="$show.module.compliancy = '1'">
          <xsl:call-template name="module.compliancy.list">
            <xsl:with-param name="compliancy" select="./compliancy"/>
          </xsl:call-template>
        </xsl:if>

        <xsl:text>&#x0A; &#x0A;</xsl:text>
        
      </xsl:for-each>
    </xsl:if>
  </xsl:template>

<!--
  =========================================================================
                              UNDO REPORT
  =========================================================================
-->
  <xsl:template match="/UndoReport">
    <xsl:text>&#x0A;UNDO REPORT</xsl:text>
    <xsl:text>&#x0A;Created </xsl:text>
    <xsl:value-of select="/UndoReport/report/@created"/>
    <xsl:text> by OS Lockdown v</xsl:text>
    <xsl:value-of select="/UndoReport/@sbVersion"/>

    <xsl:text>&#x0A;&#x0A;</xsl:text>
    <xsl:text>Summary:&#x0A;</xsl:text>
    <xsl:text>--------------------------------------------------------------------</xsl:text>
    <xsl:text>&#x0A;</xsl:text>
		
    <xsl:text>         Created: </xsl:text>
    <xsl:value-of select="/UndoReport/report/@created"/>
    <xsl:text>&#x0A;</xsl:text>
    <xsl:text>        Hostname: </xsl:text>
    <xsl:value-of select="/UndoReport/report/@hostname"/>
    <xsl:text>&#x0A;</xsl:text>

    <xsl:text>Operating System: </xsl:text>
    <xsl:variable name="distVersion" select="/UndoReport/report/@distVersion"/>
    <xsl:variable name="dist" select="/UndoReport/report/@dist"/>
    <xsl:choose>
      <xsl:when test="$distVersion = '10' and $dist = 'redhat'">
        <xsl:text>Fedora 10</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="/UndoReport/report/@dist"/>
        <xsl:text> </xsl:text>
        <xsl:value-of select="/UndoReport/report/@distVersion"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:text> (</xsl:text>
    <xsl:value-of select="/UndoReport/report/@arch"/>
    <xsl:text>) [Kernel </xsl:text>
    <xsl:value-of select="/UndoReport/report/@kernel"/>
    <xsl:text>]&#x0A;</xsl:text>

		
    <xsl:text>         Profile: </xsl:text>
    <xsl:value-of select="/UndoReport/report/@profile"/>
    <xsl:text>&#x0A;</xsl:text>

    <xsl:variable name="modError" select="count(/UndoReport/modules/module[@results='Error'])"/>
    <xsl:variable name="modUndone" select="count(/UndoReport/modules/module[@results='Undone'])"/>
    <xsl:variable name="modOther" select="count(/UndoReport/modules/module[@results !='Undone' and @results !='Error'])"/>
		
    <xsl:text>&#x0A;</xsl:text>
    <xsl:text>  Modules Undone: </xsl:text>
    <xsl:value-of select="$modUndone"/>
    <xsl:text> (</xsl:text>
    <xsl:value-of select="round(($modError div ($modError + $modUndone)) * 100)"/>
    <xsl:text>%) &#x0A;</xsl:text>
		
    <xsl:text>          Errors: </xsl:text>
    <xsl:value-of select="$modError"/>
    <xsl:text>&#x0A;</xsl:text>
    <xsl:text>           Other: </xsl:text>
    <xsl:value-of select="$modOther"/>
    <xsl:text>&#x0A;</xsl:text>
		
    <xsl:text>&#x0A;</xsl:text>

    <xsl:if test="count(/UndoReport/modules/module[@results='Undone']) != 0">
      <xsl:text>&#x0A;Undone:&#x0A;</xsl:text>
      <xsl:text>--------------------------------------------------------------------&#x0A;</xsl:text>
      <xsl:for-each select="/UndoReport/modules/module[@results='Undone']">
        <xsl:sort select="@name"/>
        <xsl:variable name="spaces">.............................</xsl:variable>
        <xsl:text>   </xsl:text>
        <xsl:value-of select="substring(concat(@name, $spaces, $spaces), 1, 60)"/>
        <xsl:value-of select="@results"/>
        <xsl:text>&#x0A;</xsl:text>

		<!-- Show Module Details -->
        <xsl:if test="$show.module.details = '1'">
          <xsl:text>&#x0A;     </xsl:text>
          <xsl:call-template name="textwrap">
            <xsl:with-param name="original" select="normalize-space(./description)"/>
            <xsl:with-param name="maxLength" select="60"/>
            <xsl:with-param name="separator" select="'&#x0A;     '"/>
            <xsl:with-param name="wordWrap" select="'true'"/>
          </xsl:call-template>
          <xsl:text>&#x0A; &#x0A;</xsl:text>
          <xsl:if test="./details/statusMessage/text() != '' and ./details/statusMessage/text() != 'None'" >
            <xsl:text>     - </xsl:text>
            <xsl:call-template name="textwrap">
              <xsl:with-param name="original" select="normalize-space(./details/statusMessage)"/>
              <xsl:with-param name="maxLength" select="55"/>
              <xsl:with-param name="separator" select="'&#x0A;       '"/>
              <xsl:with-param name="wordWrap" select="'true'"/>
            </xsl:call-template>
            <xsl:text>&#x0A;</xsl:text>
          </xsl:if>
          <xsl:if test="count(./details/messages/message) != 0">
            <xsl:for-each select="./details/messages/message">
              <xsl:text>&#x0A;       * </xsl:text>
              <xsl:call-template name="textwrap">
                <xsl:with-param name="original" select="normalize-space(.)"/>
                <xsl:with-param name="maxLength" select="55"/>
                <xsl:with-param name="separator" select="'&#x0A;         '"/>
                <xsl:with-param name="wordWrap" select="'true'"/>
              </xsl:call-template>
            </xsl:for-each>
          </xsl:if>
        </xsl:if>

		<!-- Show module compliancy -->
        <xsl:if test="$show.module.compliancy = '1'">
          <xsl:call-template name="module.compliancy.list">
            <xsl:with-param name="compliancy" select="./compliancy"/>
          </xsl:call-template>
        </xsl:if>

        <xsl:text>&#x0A; &#x0A; &#x0A; &#x0A;</xsl:text>

      </xsl:for-each>
    </xsl:if>
		
    <xsl:if test="count(/UndoReport/modules/module[@results='Error']) != 0">
      <xsl:text>&#x0A;Errors:&#x0A;</xsl:text>
      <xsl:text>--------------------------------------------------------------------&#x0A;</xsl:text>
      <xsl:for-each select="/UndoReport/modules/module[@results='Error']">
        <xsl:sort select="@name"/>
        <xsl:variable name="spaces">.............................</xsl:variable>
        <xsl:text>   </xsl:text>
        <xsl:value-of select="substring(concat(@name, $spaces, $spaces), 1, 60)"/>
        <xsl:value-of select="@results"/>
        <xsl:text>&#x0A;</xsl:text>

		<!-- Show Module Details -->
        <xsl:if test="$show.module.details = '1'">
          <xsl:text>&#x0A;     </xsl:text>
          <xsl:call-template name="textwrap">
            <xsl:with-param name="original" select="normalize-space(./description)"/>
            <xsl:with-param name="maxLength" select="60"/>
            <xsl:with-param name="separator" select="'&#x0A;     '"/>
            <xsl:with-param name="wordWrap" select="'true'"/>
          </xsl:call-template>
          <xsl:text>&#x0A; &#x0A;</xsl:text>
          <xsl:if test="./details/statusMessage/text() != '' and ./details/statusMessage/text() != 'None'" >
            <xsl:text>     - </xsl:text>
            <xsl:call-template name="textwrap">
              <xsl:with-param name="original" select="normalize-space(./details/statusMessage)"/>
              <xsl:with-param name="maxLength" select="55"/>
              <xsl:with-param name="separator" select="'&#x0A;       '"/>
              <xsl:with-param name="wordWrap" select="'true'"/>
            </xsl:call-template>
            <xsl:text>&#x0A;</xsl:text>
          </xsl:if>
          <xsl:if test="count(./details/messages/message) != 0">
            <xsl:for-each select="./details/messages/message">
              <xsl:text>&#x0A;       * </xsl:text>
              <xsl:call-template name="textwrap">
                <xsl:with-param name="original" select="normalize-space(.)"/>
                <xsl:with-param name="maxLength" select="55"/>
                <xsl:with-param name="separator" select="'&#x0A;         '"/>
                <xsl:with-param name="wordWrap" select="'true'"/>
              </xsl:call-template>
            </xsl:for-each>
          </xsl:if>
        </xsl:if>

		<!-- Show module compliancy -->
        <xsl:if test="$show.module.compliancy = '1'">
          <xsl:call-template name="module.compliancy.list">
            <xsl:with-param name="compliancy" select="./compliancy"/>
          </xsl:call-template>
        </xsl:if>

        <xsl:text>&#x0A; &#x0A; &#x0A; &#x0A;</xsl:text>

      </xsl:for-each>
    </xsl:if>
		
    <xsl:if test="count(/UndoReport/modules/module[@results != 'Undone' and @results != 'Error']) != 0">
      <xsl:text>&#x0A;Not required or not applicable:&#x0A;</xsl:text>
      <xsl:text>--------------------------------------------------------------------&#x0A;</xsl:text>
      <xsl:for-each select="/UndoReport/modules/module[@results != 'Undone' and @results != 'Error']">
        <xsl:sort select="@name"/>
        <xsl:variable name="spaces">.............................</xsl:variable>
        <xsl:text>   </xsl:text>
        <xsl:value-of select="substring(concat(@name, $spaces, $spaces), 1, 60)"/>
        <xsl:value-of select="@results"/>
        <xsl:text>&#x0A;</xsl:text>
        
        <!-- Show Module Details -->
        <xsl:if test="$show.module.details = '1'">
          <xsl:text>&#x0A;     </xsl:text>
          <xsl:call-template name="textwrap">
            <xsl:with-param name="original" select="normalize-space(./description)"/>
            <xsl:with-param name="maxLength" select="60"/>
            <xsl:with-param name="separator" select="'&#x0A;     '"/>
            <xsl:with-param name="wordWrap" select="'true'"/>
          </xsl:call-template>
          <xsl:text>&#x0A; &#x0A;</xsl:text>
          <xsl:if test="./details/statusMessage/text() != '' and ./details/statusMessage/text() != 'None'" >
            <xsl:text>     - </xsl:text>
            <xsl:call-template name="textwrap">
              <xsl:with-param name="original" select="normalize-space(./details/statusMessage)"/>
              <xsl:with-param name="maxLength" select="55"/>
              <xsl:with-param name="separator" select="'&#x0A;       '"/>
              <xsl:with-param name="wordWrap" select="'true'"/>
            </xsl:call-template>
            <xsl:text>&#x0A;</xsl:text>
          </xsl:if>
          <xsl:if test="count(./details/messages/message) != 0">
            <xsl:for-each select="./details/messages/message">
              <xsl:text>&#x0A;       * </xsl:text>
              <xsl:call-template name="textwrap">
                <xsl:with-param name="original" select="normalize-space(.)"/>
                <xsl:with-param name="maxLength" select="55"/>
                <xsl:with-param name="separator" select="'&#x0A;         '"/>
                <xsl:with-param name="wordWrap" select="'true'"/>
              </xsl:call-template>
            </xsl:for-each>
          </xsl:if>
        </xsl:if>
        
        <!-- Show module compliancy -->
        <xsl:if test="$show.module.compliancy = '1'">
          <xsl:call-template name="module.compliancy.list">
            <xsl:with-param name="compliancy" select="./compliancy"/>
          </xsl:call-template>
        </xsl:if>

        <xsl:text>&#x0A; &#x0A; &#x0A; &#x0A;</xsl:text>

      </xsl:for-each>
    </xsl:if>
  </xsl:template>

<!--
  =========================================================================
                              BASELINE REPORT
  =========================================================================
-->
  <xsl:template match="/BaselineReport">
    <xsl:text>&#x0A;BASELINE REPORT</xsl:text>
    <xsl:text>&#x0A; &#x0A;</xsl:text>
    <xsl:text>Summary:&#x0A;</xsl:text>
    <xsl:text>====================================================================</xsl:text>
    <xsl:text>&#x0A;</xsl:text>
        
    <xsl:text>         Created: </xsl:text>
    <xsl:value-of select="/BaselineReport/report/@created"/>
    <xsl:text>&#x0A;</xsl:text>
    <xsl:text>        Hostname: </xsl:text>
    <xsl:value-of select="/BaselineReport/report/@hostname"/>
    <xsl:text>&#x0A;</xsl:text>
        
    <xsl:text>Operating System: </xsl:text>
    <xsl:variable name="distVersion" select="/BaselineReport/report/@distVersion"/>
    <xsl:variable name="dist" select="/BaselineReport/report/@dist"/>
    <xsl:choose>
      <xsl:when test="$distVersion = '10' and $dist = 'redhat'">
        <xsl:text>Fedora 10</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="/BaselineReport/report/@dist"/>
        <xsl:text> </xsl:text>
        <xsl:value-of select="/BaselineReport/report/@distVersion"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:text> (</xsl:text>
    <xsl:value-of select="/BaselineReport/report/@arch"/>
    <xsl:text>) [Kernel </xsl:text>
    <xsl:value-of select="/BaselineReport/report/@kernel"/>
    <xsl:text>]&#x0A;</xsl:text>
    <xsl:text>    Total Memory: </xsl:text>
    <xsl:value-of select="/BaselineReport/report/@totalMemory"/>
    <xsl:text>&#x0A;</xsl:text>
    <xsl:text>      Processors: </xsl:text>
    <xsl:value-of select="/BaselineReport/report/@cpuInfo"/>
    <xsl:text>&#x0A;</xsl:text>
    <xsl:text>&#x0A;</xsl:text>
    <xsl:text>====================================================================&#x0A;</xsl:text>
    <xsl:text>Files:&#x0A;</xsl:text>
    <xsl:text>====================================================================&#x0A;</xsl:text>
    <xsl:for-each select="/BaselineReport/sections/section[@name='Files']/subSection[@name != 'Device Files']">
      <xsl:variable name="secname" select="@name"/>
      <xsl:text> * </xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text> (</xsl:text>
      <xsl:value-of select="format-number(count(./files/file), '###,###')"/>
      <xsl:text>)&#x0A;</xsl:text>
    </xsl:for-each>

    <!-- Auditing and Logging Section -->
    <xsl:text>&#x0A;</xsl:text>
    <xsl:for-each select="/BaselineReport/sections/section[@name='Auditing and Logging']/subSection">
      <xsl:variable name="secname" select="@name"/>
      <xsl:text>====================================================================&#x0A;</xsl:text>
      <xsl:text>Auditing and Logging -&gt; </xsl:text>
      <xsl:value-of select="normalize-space(@name)"/>
      <xsl:text>:&#x0A;</xsl:text>
      <xsl:text>====================================================================&#x0A;</xsl:text>
      <xsl:value-of select="self::*"/>
      <xsl:text>&#x0A;</xsl:text>
      <xsl:text>&#x0A;</xsl:text>
    </xsl:for-each>
        
    <!-- Hardware Section -->
    <xsl:text>&#x0A;</xsl:text>
    <xsl:for-each select="/BaselineReport/sections/section[@name='Hardware']/subSection">
      <xsl:variable name="secname" select="@name"/>
      <xsl:text>====================================================================&#x0A;</xsl:text>
      <xsl:text>Hardware -&gt; </xsl:text>
      <xsl:value-of select="normalize-space(@name)"/>
      <xsl:text>:&#x0A;</xsl:text>
      <xsl:text>====================================================================&#x0A;</xsl:text>
      <xsl:value-of select="self::*"/>
      <xsl:text>&#x0A;</xsl:text>
      <xsl:text>&#x0A;</xsl:text>
    </xsl:for-each>
        
    <!-- Network Section -->
    <xsl:text>&#x0A;</xsl:text>
    <xsl:for-each select="/BaselineReport/sections/section[@name='Network']/subSection">
      <xsl:variable name="secname" select="@name"/>
      <xsl:text>====================================================================&#x0A;</xsl:text>
      <xsl:text>Network -&gt; </xsl:text>
      <xsl:value-of select="normalize-space(@name)"/>
      <xsl:text>:&#x0A;</xsl:text>
      <xsl:text>====================================================================&#x0A;</xsl:text>
      <xsl:value-of select="self::*"/>
      <xsl:text>&#x0A;</xsl:text>
      <xsl:text>&#x0A;</xsl:text>
    </xsl:for-each>
        
    <xsl:text>====================================================================&#x0A;</xsl:text>
    <xsl:text>Software -&gt; Installed Packages:&#x0A;</xsl:text>
    <xsl:text>====================================================================&#x0A;</xsl:text>
    <xsl:for-each select="/BaselineReport/sections/section[@name='Software']/subSection[@name='Packages']/packages/package">
      <xsl:sort select="@name"/>
      <!-- Package name -->
      <xsl:value-of select="@name"/>
      <xsl:text> (</xsl:text>
      <xsl:value-of select="@version"/>
      <xsl:if test="@release != '' and @release != '-' ">
        <xsl:text>-</xsl:text>
        <xsl:value-of select="@release"/>
      </xsl:if>
      <xsl:text>) - </xsl:text>
      <xsl:value-of select="@summary"/>
      <xsl:text>&#x0A;</xsl:text>
    </xsl:for-each>
        
  </xsl:template>

</xsl:stylesheet>
