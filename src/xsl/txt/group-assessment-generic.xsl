<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Group Assessment Report XML to TEXT
     =========================================================================
-->
  <xsl:param name="report.title">Group Assessment Report</xsl:param>
    
  <xsl:include href="common-text.xsl"/>
  <xsl:output method="text" encoding="UTF-8" indent="yes" />


  <xsl:template name="leading-zero-to-space">
    <xsl:param name="input"/>
    <xsl:choose>
      <xsl:when test="starts-with($input,'0')">
        <xsl:value-of select="' '"/>
        <xsl:call-template name="leading-zero-to-space">
          <xsl:with-param name="input" select="substring-after($input,'0')"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$input"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <xsl:template match="/">
        
    <xsl:text>&#x0A;</xsl:text>
    <xsl:value-of select="translate($report.title, $vLower, $vUpper)"/>
    <xsl:text>&#x0A;Generated </xsl:text>
    <xsl:value-of select="substring(/GroupAssessmentReport/@created,1,20)"/>
    <xsl:text> by OS Lockdown v</xsl:text>
    <xsl:value-of select="/GroupAssessmentReport/@sbVersion"/>

    <xsl:text>&#x0A;</xsl:text>
    <xsl:text>&#x0A;</xsl:text>
    <xsl:text>Summary:&#x0A;</xsl:text>
    <xsl:text>===================================================================================&#x0A;</xsl:text>
    <xsl:text>Group Name: </xsl:text>
    <xsl:value-of select="/GroupAssessmentReport/@groupName"/>
    <xsl:text>&#x0A;</xsl:text>

    <xsl:text>   Profile: </xsl:text>
    <xsl:value-of select="/GroupAssessmentReport/@profile"/>
    <xsl:text>&#x0A;</xsl:text>

   <!-- REPORTS -->
    <xsl:text>&#x0A;</xsl:text>
    <xsl:text>   Reports: </xsl:text>
    <xsl:variable name="totalReports" select="count(/GroupAssessmentReport/reports/report)"/>
    <xsl:variable name="missingReports" select="count(/GroupAssessmentReport/missing/client)"/>
    <xsl:if test="$missingReports != 0">
      <xsl:text>&#x0A;</xsl:text>
      <xsl:if test="$totalReports != 0">
        <xsl:text>Showing </xsl:text>
        <xsl:value-of select="$totalReports"/>
        <xsl:text> client reports. &#x0A;</xsl:text>
      </xsl:if>
      <xsl:text>The following client reports were not available:&#x0A;</xsl:text>
      <xsl:for-each select="/GroupAssessmentReport/missing/client">
        <xsl:sort select="@name"/>
        <xsl:text>  * </xsl:text>
        <xsl:value-of select="@hostname"/>
        <xsl:text> (</xsl:text>
        <xsl:value-of select="@reason"/>
        <xsl:text>)</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
      </xsl:for-each>
    </xsl:if>


    <!-- 
             Clients with Failures or Errors
    -->
    <xsl:if test="count(/GroupAssessmentReport/modules/module/clients/client[@results='Fail' or @results='Error']) != 0">
      <xsl:text>&#x0A;&#x0A;Systems with Failures or Errors&#x0A;</xsl:text>
      <xsl:text>===================================================================================&#x0A;</xsl:text>
      <xsl:variable name="dots">.............................</xsl:variable>
      <xsl:variable name="spaces">
        <xsl:text>                                  </xsl:text>
      </xsl:variable>

      <!-- Create a header -->
      <xsl:value-of select="substring(concat('Hostname', $spaces, $spaces), 1, 50)"/>
      <xsl:text> |------ Security Modules ------|&#x0A;</xsl:text>
      <xsl:value-of select="substring(concat('Hostname', $spaces, $spaces), 1, 50)"/>
      <xsl:text> Failed   Errored  %Passed/Other&#x0A;</xsl:text>

      <xsl:for-each select="/GroupAssessmentReport/reports/report">
        <xsl:sort select="@hostname"/>
        <xsl:text>&#x0A; &#x0A; &#x0A;</xsl:text>
        <xsl:value-of select="substring(concat(@hostname, $dots, $dots), 1, 50)"/>

        <xsl:variable name="host_name" select="@hostname"/>
        <xsl:variable name="fail_count" select="count(/GroupAssessmentReport/modules/module/clients/client[@hostname = $host_name and @results='Fail'])"/>
        <xsl:variable name="error_count" select="count(/GroupAssessmentReport/modules/module/clients/client[@hostname = $host_name and @results='Error'])"/>
        <xsl:variable name="total_count" select="count(/GroupAssessmentReport/modules/module/clients/client[@hostname = $host_name])"/>

        <xsl:call-template name="leading-zero-to-space">
          <xsl:with-param name="input" select="format-number($fail_count, '000000')" />
        </xsl:call-template>

        <xsl:choose>
          <xsl:when test="$error_count &gt; 0">
            <xsl:call-template name="leading-zero-to-space">
              <xsl:with-param name="input" select="format-number($error_count, '0000000000')" />
            </xsl:call-template>
          </xsl:when>
          <xsl:otherwise>
            <xsl:text>         0</xsl:text>
          </xsl:otherwise>
        </xsl:choose>
        
        <xsl:call-template name="leading-zero-to-space">
          <xsl:with-param name="input" select="format-number(ceiling( (($total_count - ($fail_count + $error_count)) div $total_count)*100), '00000000000')" />
        </xsl:call-template>
        <xsl:text> %</xsl:text>

        <!-- give host details and module failed module info -->
        <xsl:text>&#x0A;    - OS: </xsl:text>
        <xsl:value-of select="@dist"/>
        <xsl:text> </xsl:text>
        <xsl:value-of select="@distVersion"/>
        <xsl:text> (</xsl:text>
        <xsl:value-of select="@arch"/>
        <xsl:text>)</xsl:text>

        <xsl:text>&#x0A;    - Kernel: </xsl:text>
        <xsl:value-of select="@kernel"/>
        <xsl:if test="count(/GroupAssessmentReport/modules/module/clients/client[@hostname = $host_name and (@results='Fail' or @results='Error')]) != 0">
          <xsl:text>&#x0A;&#x0A;  Failed and Errored Modules:</xsl:text>
          <xsl:for-each select="/GroupAssessmentReport/modules/module/clients/client[@hostname = $host_name and (@results='Fail' or @results='Error')]">
            <xsl:sort select="@results"/>
            <xsl:text>&#x0A;      - </xsl:text>
            <xsl:value-of select="@results"/>
            <xsl:text>ed - </xsl:text>
            <xsl:value-of select="../../@name"/>
          </xsl:for-each>
          <xsl:text>&#x0A;&#x0A;</xsl:text>
        </xsl:if>
        
      </xsl:for-each>
      <xsl:text>&#x0A;</xsl:text>
    </xsl:if>

<!-- 
     List ALL MODULES with Host results
 -->
    <xsl:if test="count(/GroupAssessmentReport/modules/module/clients/client[@results='Fail' or @results='Error']) != 0">
      <xsl:text>&#x0A; &#x0A; &#x0A;</xsl:text>
      <xsl:text>===================================================================================&#x0A;</xsl:text>
      <xsl:text>OS Lockdown Modules          (F=Failed / E=Errored / P=Pass / O=Other)&#x0A;</xsl:text>
      <xsl:text>===================================================================================&#x0A;</xsl:text>
      <xsl:variable name="dots">.............................</xsl:variable>
      <xsl:variable name="spaces">
        <xsl:text>                                  </xsl:text>
      </xsl:variable>
      <xsl:value-of select="substring(concat('Module Name', $spaces, $spaces), 1, 60)"/>
      <xsl:text> F / E / P / O /   %</xsl:text>
      <xsl:for-each select="/GroupAssessmentReport/modules/module">
        <xsl:sort select="@name"/>
        <xsl:variable name="module_name" select="@name"/>
        <xsl:variable name="fail_count" select="count(./clients/client[@results='Fail'])" />
        <xsl:variable name="error_count" select="count(./clients/client[@results='Error'])"/>
        <xsl:variable name="pass_count" select="count(./clients/client[@results='Pass'])"/>
        <xsl:variable name="other_count" select="count(./clients/client[@results != 'Pass' and @results != 'Error' and @results != 'Fail'])"/>
        <xsl:variable name="total_count" select="$fail_count + $error_count + $pass_count + $other_count"/>
                
        <xsl:text>&#x0A; &#x0A;</xsl:text>
        <xsl:value-of select="substring(concat(@name, $dots, $dots), 1, 60)"/>
        <xsl:text> </xsl:text>
        <xsl:value-of select="$fail_count"/>
        <xsl:text> / </xsl:text>
        <xsl:value-of select="$error_count"/>
        <xsl:text> / </xsl:text>
        <xsl:value-of select="$pass_count"/>
        <xsl:text> / </xsl:text>
        <xsl:value-of select="$other_count" />
        <xsl:text> / </xsl:text>
        <xsl:value-of select="ceiling( (($total_count - ($fail_count + $error_count)) div $total_count)*100)"/>
        <xsl:text> % &#x0A;</xsl:text>

        <xsl:if test="count(./clients/client[@results = 'Fail' or @results='Error']) != 0">
          <xsl:text>    Clients with Failures or Errors:</xsl:text>
          <xsl:for-each select="./clients/client[@results = 'Fail' or @results='Error']">
            <xsl:sort select="@hostname"/>
            <xsl:text>&#x0A;     - </xsl:text>
            <xsl:value-of select="@results"/>
            <xsl:text>ed - </xsl:text>
            <xsl:value-of select="@hostname"/>
          </xsl:for-each>
          <xsl:text>&#x0A;</xsl:text>
        </xsl:if>

      </xsl:for-each>

    </xsl:if>

  </xsl:template>
</xsl:stylesheet>
