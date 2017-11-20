<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: assessment-failures-only.xsl 23917 2017-03-07 15:44:30Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Assessment (Show Only Failed Modules)  Report XML to XHTML
     =========================================================================
-->
  <xsl:param name="report.title">Failed Modules Report</xsl:param>
  <xsl:param name="css.file">/OSLockdown/css/assessment-report.css</xsl:param>

  <xsl:include href="xhtml-report-styles.xsl"/>
  <xsl:include href="common-xhtml.xsl"/>

  <xsl:output method="html" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
             doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" indent="yes" encoding="utf-8" />

<!-- ======================================================================= -->
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml" dir="ltr">
      <xsl:call-template name="html.header"/>
      <body>
        <a name="top"/>
        <xsl:if test="$header.display != 'false'">
          <xsl:call-template name="header"/>
        </xsl:if>
        <table class="sectionTable">
          <tr>
            <th style="text-align:left;" colspan="2">Summary</th>
            <th style="text-align: right;" colspan="3">Created:
              <xsl:value-of select="/AssessmentReport/report/@created"/>
            </th>
          </tr>
          <tr>
            <td class="subSectionTitle" style="border-bottom: 1px dotted gray; text-align: right">Hostname</td>
            <td class="infoItem" colspan="5" style=" border-bottom: 1px dotted gray">
              <xsl:value-of select="/AssessmentReport/report/@hostname"/>
            </td>
          </tr>
          <tr>
            <td class="subSectionTitle" style="text-align: right;  border-bottom: 1px dotted gray">Operating System</td>
            <td class="infoItem" colspan="5" style=" border-bottom: 1px dotted gray">
              <xsl:variable name="distVersion" select="/AssessmentReport/report/@distVersion"/>
              <xsl:variable name="dist" select="/AssessmentReport/report/@dist"/>
              <xsl:choose>
                <xsl:when test="$distVersion = '10' and $dist = 'redhat'">
                  <xsl:text>Fedora 10</xsl:text>
                </xsl:when>
                <xsl:when test="$dist = 'Red Hat'">
                  <xsl:text>Red Hat Enterprise Linux </xsl:text>
                  <xsl:value-of select="/AssessmentReport/report/@distVersion"/>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="/AssessmentReport/report/@dist"/>
                  <xsl:text> </xsl:text>
                  <xsl:value-of select="/AssessmentReport/report/@distVersion"/>
                </xsl:otherwise>
              </xsl:choose>
            </td>
          </tr>

      <!-- Profile Information -->
          <xsl:call-template name="profile.information">
            <xsl:with-param name="reportRoot" select="/AssessmentReport"/>
          </xsl:call-template>
        </table>
        <div style="padding-top: 10px; color: gray; width: 100%; text-align: left;">
          <a href="#" style="cursor:pointer" onClick="return expandAll();">Show</a> /
          <a href="#" style="cursor:pointer" onClick="return collapseAll();">Hide</a> all module descriptions.
        </div>
<!--
         ================================================================ 
                          Modules which have not passed
         ================================================================
-->
        <a name="failures"/>
        <table id="failedModules" class="sectionTable sortable">
          <thead>
            <tr>
              <th colspan="3" class="sectionHeader" style="background-color: red; color: white">All Failed Modules</th>
              <th class="sectionHeader" style="background-color: red; color: white; text-align: center">Severity</th>
            </tr>
          </thead>

<!-- High Severity -->
          <tbody>
            <xsl:for-each select="/AssessmentReport/modules/module[@results = 'Fail' and @severity = 'High']">
              <xsl:sort select="@name"/>
              <tr>
                <td class="moduleName" style="border-right: 1px solid black" colspan="3">
                  <span style="cursor:pointer; padding-right:.5em" onclick="toggleDisplay(this)">
                    <xsl:value-of select="@name"/>
                  </span>
                  <div class="moduleDescription" style="display: none">
                    <xsl:value-of select="description"/>
                    <xsl:call-template name="module.message.details" >
                      <xsl:with-param name="details" select="./details"/>
                    </xsl:call-template>
                    <xsl:call-template name="module.compliancy.list" >
                      <xsl:with-param name="compliancy" select="./compliancy"/>
                    </xsl:call-template>
                  </div>
                </td>

        <!-- Module Severity -->
                <xsl:call-template name="module.severity">
                  <xsl:with-param name="severity" select="@severity"/>
                </xsl:call-template>
              </tr>
            </xsl:for-each>

<!-- Medium Severity -->
            <xsl:for-each select="/AssessmentReport/modules/module[@results = 'Fail' and @severity = 'Medium']">
              <xsl:sort select="@name"/>
              <tr>
                <td class="moduleName" style="border-right: 1px solid black" colspan="3">
                  <span style="cursor:pointer; padding-right:.5em" onclick="toggleDisplay(this)">
                    <xsl:value-of select="@name"/>
                  </span>
                  <div class="moduleDescription" style="display: none">
                    <xsl:value-of select="description"/>
                    <xsl:call-template name="module.compliancy.list" >
                      <xsl:with-param name="compliancy" select="./compliancy"/>
                    </xsl:call-template>
                  </div>
                </td>

        <!-- Module Severity -->
                <xsl:call-template name="module.severity">
                  <xsl:with-param name="severity" select="@severity"/>
                </xsl:call-template>
              </tr>
            </xsl:for-each>

<!-- Low Severity -->
            <xsl:for-each select="/AssessmentReport/modules/module[@results = 'Fail' and @severity = 'Low']">
              <xsl:sort select="@name"/>
              <tr>
                <td class="moduleName" style="border-right: 1px solid black" colspan="3">
                  <span style="cursor:pointer; padding-right:.5em" onclick="toggleDisplay(this)">
                    <xsl:value-of select="@name"/>
                  </span>
                  <div class="moduleDescription" style="display: none">
                    <xsl:value-of select="description"/>
                    <xsl:call-template name="module.message.details" >
                      <xsl:with-param name="details" select="./details"/>
                    </xsl:call-template>
                    <xsl:call-template name="module.compliancy.list" >
                      <xsl:with-param name="compliancy" select="./compliancy"/>
                    </xsl:call-template>
                  </div>
                </td>

        <!-- Module Severity -->
                <xsl:call-template name="module.severity">
                  <xsl:with-param name="severity" select="@severity"/>
                </xsl:call-template>
              </tr>
            </xsl:for-each>
          </tbody>
        </table>

<!-- Report Footer -->
        <xsl:if test="$footer.display != 'false'">
          <xsl:call-template name="footer">
            <xsl:with-param name="sbVersion" select="/AssessmentReport/@sbVersion"/>
          </xsl:call-template>
        </xsl:if>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
