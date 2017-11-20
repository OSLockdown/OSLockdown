<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: group-assessment-generic.xsl 23917 2017-03-07 15:44:30Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Group Assessment Report XML to XHTML
 
     =========================================================================
-->
  <xsl:param name="report.title">Group Assessment Report</xsl:param>
  <xsl:param name="css.file">/OSLockdown/css/group-assessment-report.css</xsl:param>
  <xsl:include href="xhtml-report-styles.xsl"/>
  <xsl:include href="common-xhtml.xsl"/>

  <xsl:output method="html" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
             doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" indent="yes" encoding="utf-8" />
 <!--
  <xsl:output method="html" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
             doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN" indent="yes" encoding="utf-8" />
 -->

  <xsl:template match="/">
    <xsl:variable name="groupProfile">
      <xsl:choose>
        <xsl:when test="/GroupAssessmentReport/@profile">
          <xsl:value-of select="/GroupAssessmentReport/@profile" />
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="/GroupAssessmentReport/reports/report[1]/@profile" />
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
        
    <html xmlns="http://www.w3.org/1999/xhtml" lang="{$report.lang}" xml:lang="{$report.lang}">
      <xsl:call-template name="html.header"/>
            
      <body>
        <a name="top"/>
                    
        <xsl:if test="$header.display != 'false'">
          <xsl:call-template name="header"/>
        </xsl:if>
                    
        <table class="summaryTable">
          
          <thead>
            <tr class="firstRow">
              <th style="text-align:left;" colspan="2">Summary</th>
              <th style="text-align: right;" colspan="2">
                <xsl:text>Generated: </xsl:text>
                <xsl:value-of select="substring(/GroupAssessmentReport/@created, 1, 20)"/>
              </th>
            </tr>
          </thead>
 
          <tbody>
            <tr>
              <td class="firstCol">Group Name</td>
              <td colspan="3">
                <xsl:value-of select="/GroupAssessmentReport/@groupName"/>
              </td>
            </tr>

            <xsl:variable name="totalReports" select="count(/GroupAssessmentReport/reports/report)"/>
            <xsl:variable name="badProfiles" select="count(/GroupAssessmentReport/reports/report[@profile != $groupProfile])"/>
            <xsl:variable name="missingReports" select="count(/GroupAssessmentReport/missing/client)"/>
            <xsl:variable name="totalClients" select="$totalReports + $missingReports"/>
            <tr>
              <td class="firstCol">Group Size</td>
              <td colspan="3">
                <xsl:value-of select="$totalClients" />
              </td>
            </tr>
                        
            <tr>
              <td class="firstCol">Profile</td>
              <td colspan="3">
                <xsl:value-of select="$groupProfile" />
              </td>
            </tr>

            <tr>
              <td class="firstCol">Reports</td>
              <td colspan="3">
                <xsl:if test="$totalReports != 0">
                  <p>
                    <xsl:text>Assembled from </xsl:text>
                    <xsl:value-of select="$totalReports"/>
                    <xsl:text> of </xsl:text>
                    <xsl:value-of select="$totalClients"/>
                    <xsl:text> client reports.</xsl:text>
                  </p>
                </xsl:if>

                <xsl:if test="$missingReports != 0">
                  <p style="text-decoration:underline">Unavailable Reports:</p>
                  <ul style="list-style-type:square">
                    <xsl:for-each select="/GroupAssessmentReport/missing/client">
                      <xsl:sort select="@name"/>
                      <li>
                        <xsl:value-of select="@hostname"/>
                        <xsl:text> (</xsl:text>
                        <i>
                          <xsl:value-of select="@reason"/>
                        </i>
                        <xsl:text>)</xsl:text>
                      </li>
                    </xsl:for-each>
                  </ul>
                </xsl:if>

                <xsl:if test="$badProfiles != 0 ">
                  <p style="text-decoration:underline">Warnings:</p>
                  <ul style="list-style-type:square">
                    <xsl:for-each select="/GroupAssessmentReport/reports/report[@profile != $groupProfile]">
                      <li>
                        <xsl:value-of select="@hostname"/>
                        <xsl:text> (</xsl:text>
                        <i>Different profile: "
                          <xsl:value-of select="@profile"/>"
                        </i>
                        <xsl:text>)</xsl:text>
                      </li>
                    </xsl:for-each>
                  </ul>
                </xsl:if>

              </td>
            </tr>

          </tbody>
              
        </table>
                    
         <!--
            <div style="padding-top: 10px; color: gray; width: 100%; text-align: left;">
              <span style="cursor:pointer; border:1px solid darkgray; padding:0; margin:0">+</span><xsl:text> </xsl:text>
              <span style="cursor:pointer; border:1px solid darkgray; padding:0; padding-left:2px; padding-right: 2px;margin:0">-</span><xsl:text> </xsl:text>
              <a href="#" style="cursor:pointer" onClick="return expandAll();">Show</a> /
              <a href="#" style="cursor:pointer" onClick="return collapseAll();">Hide</a> all module descriptions.
            </div>
         -->

                        
<!--
    ================================================================ 
         List all clients which have a failure or error
    ================================================================
-->
        <xsl:if test="count(/GroupAssessmentReport/modules/module/clients/client[@results='Fail' or @results='Error']) != 0">
          <table id="listClients" class="sortable" title="Click on hostname for module details.">
            <thead>
              <tr class="firstRow">
                <th colspan="3">Systems with Failures or Errors</th>
                <th colspan="3" style="text-align:center">Security Modules</th>
              </tr>
              <tr>
                <th width="30%">Hostname</th>
                <th width="20%">Client Name</th>
                <th width="10%">Assessment Date</th>
                <th width="10%" style="text-align:center">Failed</th>
                <th width="10%" style="text-align:center">Errors</th>
                <th width="10%" style="text-align:center">% Passed/Other</th>
              </tr>
            </thead>

            <tbody>
              <xsl:for-each select="/GroupAssessmentReport/reports/report">
                <xsl:sort select="@hostname"/>
                <tr>
                  <td id="{@hostname}">
                    <a style="cursor:pointer" onclick="toggleDisplay(this)">
                      <xsl:value-of select="@hostname"/>
                    </a>
                    <xsl:variable name="host_name" select="@hostname"/>
                    <div class="hostnameDetails" style="display: none">
                      <ul>
                        <li>
                          <b>OS: </b>
                          <xsl:value-of select="@dist"/>
                          <xsl:text> </xsl:text>
                          <xsl:value-of select="@distVersion"/>
                          <xsl:text> (</xsl:text>
                          <xsl:value-of select="@arch"/>
                          <xsl:text>)</xsl:text>
                        </li>
                        <li>
                          <b>Kernel: </b>
                          <xsl:value-of select="@kernel"/>
                        </li>
                      </ul>
                      <!-- List failed and errored modules under the client -->
                      <xsl:if test="count(/GroupAssessmentReport/modules/module/clients/client[@hostname = $host_name and (@results='Fail' or @results='Error')]) != 0">
                        <p style="text-decoration:underline;font-style:normal;padding-left: 1em">Failed and Errored Modules:</p>
                        <ul style="font-style: normal; list-style-type:square">
                          <xsl:for-each select="/GroupAssessmentReport/modules/module/clients/client[@hostname = $host_name and (@results='Fail' or @results='Error')]">
                            <xsl:sort select="@results"/>
                            <li>
                              <a href="#{generate-id(../../@name)}">
                                <xsl:value-of select="@results"/>
                                <xsl:text>ed - </xsl:text>
                                <xsl:value-of select="../../@name"/>
                              </a>
                            </li>
                          </xsl:for-each>
                        </ul>
                      </xsl:if>

                    </div>

                  </td>

                  <td>
                    <xsl:variable name="host_name" select="@hostname"/>
                    <xsl:for-each select="/GroupAssessmentReport/modules/module/clients/client[@results='Fail' and @hostname = $host_name]">
                      <xsl:if test="position() = 1">
                        <xsl:value-of select="@name"/>
                      </xsl:if>
                    </xsl:for-each>
                  </td>

                  <td style="border-right: 1px dotted black">
                    <xsl:value-of select="@created"/>
                  </td>

                  <xsl:variable name="host_name" select="@hostname"/>
                  <xsl:variable name="fail_count" select="count(/GroupAssessmentReport/modules/module/clients/client[@hostname = $host_name and @results='Fail'])"/>
                  <xsl:variable name="error_count" select="count(/GroupAssessmentReport/modules/module/clients/client[@hostname = $host_name and @results='Error'])"/>
                  <xsl:variable name="total_count" select="count(/GroupAssessmentReport/modules/module/clients/client[@hostname = $host_name])"/>

                  <td style="text-align:center;font-weight:bold;color:#CE1126" >
                    <xsl:copy-of select="$fail_count"/>
                  </td>
                  <td style="text-align:center;color:orange; font-weight:bold; border-right:1px dotted black">
                    <xsl:copy-of select="$error_count"/>
                  </td>

                  <td style="text-align:center">
                    <xsl:value-of select="ceiling( (($total_count - ($fail_count + $error_count)) div $total_count)*100)"/>
                    <xsl:text>% </xsl:text>
                    <!-- <xsl:value-of select="$total_count"/><xsl:text> total)</xsl:text> -->
                  </td>

                </tr>
              </xsl:for-each>
            </tbody>
          </table>
        </xsl:if>

<!--
    ================================================================ 
          List all modules which has a client fail or error
    ================================================================
-->
        <xsl:if test="count(/GroupAssessmentReport/modules/module/clients/client[@results='Fail' or @results='Error']) != 0">
          <table id="modulesClient" class="sortable" style="margin-top: 3em" title="Click on module name for compliancy details and impacted hosts.">
            <thead>
              <tr class="firstRow">
                <th colspan="1">OS Lockdown Modules</th>
                <th colspan="5" style="text-align:center">Systems</th>
              </tr>

              <tr>
                <th width="60%">Module Name</th>
                <th style="text-align:center">Failed</th>
                <th style="text-align:center">Errors</th>
                <th style="text-align:center">Passed</th>
                <th style="text-align:center">Other</th>
                <th style="text-align:center">% Passed/Other</th>
              </tr>
            </thead>

            <tbody>
              <xsl:for-each select="/GroupAssessmentReport/modules/module">
                <xsl:sort select="@name"/>
         
                <xsl:variable name="module_name" select="@name"/>


                <xsl:variable name="fail_count" select="count(./clients/client[@results='Fail'])" />
                <xsl:variable name="error_count" select="count(./clients/client[@results='Error'])"/>
                <xsl:variable name="pass_count" select="count(./clients/client[@results='Pass'])"/>
                <xsl:variable name="other_count" select="count(./clients/client[@results != 'Pass' and @results != 'Error' and @results != 'Fail'])"/>
                <xsl:variable name="total_count" select="$fail_count + $error_count + $pass_count + $other_count"/>

                <xsl:variable name="rowClass">
                  <xsl:choose>
                    <xsl:when test="position() mod 2 = 0">even</xsl:when>
                    <xsl:otherwise>odd</xsl:otherwise>
                  </xsl:choose>
                </xsl:variable>





               <!-- Show Module Name and Details -->
                <tr class="{$rowClass}">
                  <td id="{generate-id(@name)}" style="border-right:1px dotted black">
                    <a style="cursor:pointer" onclick="toggleDisplay(this)">
                      <xsl:value-of select="@name"/>
                    </a>
                    <div class="moduleDescription" style="display: none">
                      <xsl:value-of select="./description"/>
                      <xsl:call-template name="module.message.details" >
                        <xsl:with-param name="details" select="./details"/>
                      </xsl:call-template>

                      <xsl:if test="$show.compliancy = 1">
                        <xsl:text>
                        </xsl:text>
                        <ul>

        		  <xsl:choose>
			    <xsl:when test="count(./compliancy/line-item) = 0">
        		 	  None
        		    </xsl:when>
			    <xsl:otherwise>

  			      <xsl:for-each select="compliancy/line-item[not(./@source=preceding-sibling::line-item/@source) or not(./@name=preceding-sibling::line-item/@name) or not(./@version=preceding-sibling::line-item/@version)]">
        		 	  <xsl:variable name="source" select="@source"/>
			 	  <xsl:variable name="name" select="@name"/>
			 	  <xsl:variable name="version" select="@version"/>
			 	  <li>
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
        		 	  </li>

  			      </xsl:for-each>
			    </xsl:otherwise>
			  </xsl:choose>

                        </ul>
                      </xsl:if>
                      <xsl:if test="count(./clients/client[@results = 'Fail' or @results='Error']) != 0">
                        <p style="text-decoration:underline;font-style:normal;padding-left: 1em">Clients with Failures or Errors:</p>
                        <ul style="font-style: normal; list-style-type:square">
                          <xsl:for-each select="./clients/client[@results = 'Fail' or @results='Error']">
                            <xsl:sort select="@hostname"/>
                            <li>
                              <a href="#{@hostname}">
                                <xsl:value-of select="@results"/>
                                <xsl:text>ed - </xsl:text>
                                <xsl:value-of select="@hostname"/>
                              </a>
                            </li>
                          </xsl:for-each>
                        </ul>
                      </xsl:if>

                    </div>
                  </td>
                  <xsl:text>
                  </xsl:text>


               <!-- Show Module Result Counts -->

                  <td style="color:#CE1126; text-align:center; font-weight:bold">
                    <xsl:copy-of select="$fail_count"/>
                  </td>
                  <xsl:text>
                  </xsl:text>
                  <td style="color: orange; text-align:center; font-weight:bold;  border-right:1px dotted black">
                    <xsl:copy-of select="$error_count"/>
                  </td>
                  <xsl:text>
                  </xsl:text>
                  <td style="color: green; text-align:center; font-weight:bold">
                    <xsl:copy-of select="$pass_count"/>
                  </td>
                  <xsl:text>
                  </xsl:text>
                  <td style="text-align:center;  border-right:1px dotted black">
                    <xsl:copy-of select="$other_count"/>
                  </td>
                  <xsl:text>
                  </xsl:text>
                  <td style="text-align:center">
                    <xsl:value-of select="ceiling( (($total_count - ($fail_count + $error_count)) div $total_count)*100)"/>
                    <xsl:text>%</xsl:text>
                  </td>
                  <xsl:text>
                  </xsl:text>
                </tr>
              </xsl:for-each>
              <xsl:text>
              </xsl:text>
            </tbody>
          </table>
        </xsl:if>
               <!-- Report Footer -->
              <xsl:if test="$footer.display != 'false'">
                  <xsl:call-template name="footer">
                      <xsl:with-param name="sbVersion" select="/GroupAssessmentReport/@sbVersion"/>
                  </xsl:call-template>
        </xsl:if>

      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
