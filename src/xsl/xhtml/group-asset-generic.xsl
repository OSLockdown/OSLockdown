<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: group-asset-generic.xsl 24016 2017-03-28 16:16:13Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Group Asset Report XML to XHTML
     =========================================================================
-->

  <xsl:key name="distros" match="client" use="@distribution"/>
  <xsl:key name="archs" match="client" use="@architecture"/>
  <xsl:key name="locations" match="client" use="@location"/>
  <xsl:key name="contacts" match="client" use="@contact"/>
    
  <xsl:param name="report.title">Group Asset Inventory Report</xsl:param>
  <xsl:param name="css.file">/OSLockdown/css/asset-report.css</xsl:param>

  <xsl:variable name="countResponding"><xsl:value-of select="count(/AssetReport/client[@errorMsg=''])"/></xsl:variable>    
  <xsl:variable name="countNotResponding"><xsl:value-of select="count(/AssetReport/client[@errorMsg!=''])"/></xsl:variable>    
    
  <xsl:include href="xhtml-report-styles.xsl"/>
  <xsl:include href="common-xhtml.xsl"/>
    
  <xsl:output method="html" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
             doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" indent="yes" encoding="utf-8" />


  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml" dir="ltr" xml:lang="eng" lang="en">
      <xsl:call-template name="html.header"/>
      <body>
        <a name="top"/>
        <xsl:if test="$header.display != 'false'">
          <xsl:call-template name="header"/>
        </xsl:if>

        <xsl:comment>Summary Table</xsl:comment>
        <table id="summaryTable" class="sectionTable">
          <thead>
            <tr>
              <th style="text-align:left;" colspan="2">Summary</th>
              <th style="text-align: right;" colspan="4">
                  <xsl:text>Created: </xsl:text>
                  <xsl:value-of select="substring(/AssetReport/@created, 1, 20)"/>
              </th>
            </tr>
          </thead>

          <tbody>
            <tr>
              <td class="firstCol">Group Name</td>
              <td class="infoItem" colspan="5">
                <xsl:value-of select="/AssetReport/@name" />
              </td>
            </tr>
            <tr>
              <td class="firstCol">Description</td>
              <td class="infoItem" colspan="5">
                <xsl:value-of select="/AssetReport/description"/>
              </td>
            </tr>
            <tr>
              <td class="firstCol">Console Version</td>
              <td class="infoItem" colspan="5">
                OS Lockdown <xsl:value-of select="/AssetReport/@sbVersion" />
                <xsl:variable name="badClients" select="count(/AssetReport/client[substring-after(@clientVersion, 'OS Lockdown ') != /AssetReport/@sbVersion])"/>
                <xsl:if test="$badClients != 0 ">
                  <p style="padding-left: 1em; margin-bottom: 1em;">
                     <img alt="Warning" src="/OSLockdown/images/caution.png" style="border:none; vertical-align: text-top; float: left; padding-right: 0.5em"/>
                     <span style="text-decoration:underline; font-weight:bold">Warning:</span><xsl:text> </xsl:text>
                     The highlighted items (in the <i>Program Version</i> column below) indicate a difference between the OS Lockdown Console version and the client version. It is strongly recommended to update the client version to maintain proper security posture.</p>
                  <p><xsl:text> </xsl:text></p>
                </xsl:if>
              </td>
            </tr>
            <tr>
              <td class="firstCol">Group Size</td>
              <td class="infoItem" colspan="5">
                <xsl:value-of select="count(/AssetReport/client)" /> Total Clients -- (<xsl:value-of select="$countResponding"/> responding, <xsl:value-of select="$countNotResponding"/> not responding)
              </td>
            </tr>

            <xsl:comment>Mini-tables with statistics</xsl:comment>
            <tr>
              <td class="firstCol">Analysis</td>

              <xsl:comment>Operating System Counts</xsl:comment>
              <td class="infoItem" style="padding-bottom: 1em;" width="25%">
                <table id="osList" class="miniTable sortable">
                  <thead>
                    <tr>
                      <th>Operating Systems</th>
                      <th style="text-align: right">Count</th>
                    </tr>
                  </thead>

                  <tbody>
                    <xsl:for-each select="/AssetReport/client[generate-id() = generate-id(key('distros',@distribution)[1])]">
                      <xsl:sort select="@distribution"/>
                      <xsl:variable name="distro" select="@distribution"/>
                      <tr>
                        <td style="border:none">
                          <xsl:value-of select="@distribution"/>
                        </td>
                        <td style="border:none;text-align:right; padding-right: 1em;">
                          <xsl:value-of select="count(/AssetReport/client[@distribution = $distro ])"/>
                        </td>
                      </tr>
                    </xsl:for-each>
                  </tbody>
                </table>
              </td>

              <xsl:comment>Architecture Counts</xsl:comment>
              <td class="infoItem">
                <table id="archList" class="miniTable sortable">
                  <thead>
                    <tr>
                      <th>Architectures</th>
                      <th style="text-align: right">Count</th>
                    </tr>
                  </thead>

                  <tbody>
                    <xsl:for-each select="/AssetReport/client[generate-id() = generate-id(key('archs',@architecture)[1])]">
                      <xsl:sort select="@architecture"/>
                      <xsl:variable name="arch" select="@architecture"/>
                      <tr>
                        <td style="border:none;text-align:left;">
                          <xsl:choose>
                            <xsl:when test="contains(@architecture, 'SUNW,')">
                              <xsl:value-of select="substring-after(@architecture,'SUNW,')"/>
                            </xsl:when>
                            <xsl:otherwise>
                              <xsl:value-of select="@architecture"/>
                            </xsl:otherwise>
                          </xsl:choose>
                        </td>
                        <td style="border:none; padding-right:1em; text-align:right">
                          <xsl:value-of select="count(/AssetReport/client[@architecture = $arch ])"/>
                        </td>
                      </tr>
                    </xsl:for-each>
                  </tbody>
                </table>

              <xsl:comment>Location Counts</xsl:comment>
              <td class="infoItem">
                <table id="locationList" class="miniTable sortable">
                  <thead>
                    <tr>
                      <th>Locations</th>
                      <th style="text-align: right">Count</th>
                    </tr>
                  </thead>

                  <tbody>
                    <xsl:for-each select="/AssetReport/client[generate-id() = generate-id(key('locations',@location)[1])]">
                      <xsl:sort select="@location"/>
                      <xsl:variable name="loc" select="@location"/>
                      <tr>
                        <td style="border:none;text-align:left;">
                              <xsl:value-of select="@location"/>
                        </td>
                        <td style="border:none; padding-right:1em; text-align:right">
                          <xsl:value-of select="count(/AssetReport/client[@location = $loc ])"/>
                        </td>
                      </tr>
                    </xsl:for-each>
                  </tbody>
                </table>
               </td>

              <xsl:comment>Contact Counts</xsl:comment>
              <td class="infoItem" width="25%" style="padding-right:1em;margin-right:1em;">
                <table id="contactList" class="miniTable sortable" style="width: 97%">
                  <thead>
                    <tr>
                      <th>Contacts</th>
                      <th style="text-align: right">Count</th>
                    </tr>
                  </thead>

                  <tbody>
                    <xsl:for-each select="/AssetReport/client[generate-id() = generate-id(key('contacts',@contact)[1])]">
                      <xsl:sort select="@contact"/>
                      <xsl:variable name="cont" select="@contact"/>
                      <tr>
                        <td style="border:none;text-align:left;">
                              <xsl:value-of select="@contact"/>
                        </td>
                        <td style="border:none; padding-right:1em; text-align:right">
                          <xsl:value-of select="count(/AssetReport/client[@contact = $cont ])"/>
                        </td>
                      </tr>
                    </xsl:for-each>
                  </tbody>
                </table>
               </td>


              </td> <!-- End of mini tables -->
            </tr>
          </tbody>
        </table>
    <!--
         =================================================================
                                     Non Responding Client Listing
         =================================================================
    -->
        
        <xsl:if test="$countNotResponding > 0">
            <xsl:comment> Non Responding Client/Host Listing </xsl:comment>
            <table id="clientList" class="sectionTable sortable">
              <thead>
                <tr>
                  <th width="30%" class="sectionHeader">Non-Responding Client Name</th>
                  <th class="sectionHeader">Error Message</th>
                </tr>
              </thead>

              <tbody>
                <xsl:for-each select="/AssetReport/client[@errorMsg!='']">
                  <xsl:sort select="@name"/>

                 <!-- odd/even row coloring -->
                  <xsl:variable name="rowClass">
                    <xsl:choose>
                      <xsl:when test="position() mod 2 = 0">even</xsl:when>
                      <xsl:otherwise>odd</xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>

                  <tr class="{$rowClass}">
                    <td>
                      <xsl:value-of select="@name"/>
                    </td>
                    <td style="border-left: 1px solid black;background-color: yellow">
                      <xsl:value-of select="@errorMsg"/>
                    </td>


                  </tr>
                </xsl:for-each>
              </tbody>
            </table>
         </xsl:if>                              
    <!--
         =================================================================
                                     Responding Client Listing
         =================================================================
    -->
        <xsl:if test="$countResponding > 0">
            <xsl:comment> Responding Client/Host Listing </xsl:comment>
            <table id="clientList" class="sectionTable sortable">
              <thead>
                <tr>
                  <th width="30%" class="sectionHeader">Client Name</th>
                  <th class="sectionHeader">Operating System</th>
                  <th class="sectionHeader">Program Version</th>
                  <th class="sectionHeader">Location</th>
                  <th class="sectionHeader">Contact</th>
                </tr>
              </thead>

              <tbody>
                <xsl:for-each select="/AssetReport/client[@errorMsg='']">
                  <xsl:sort select="@name"/>

                 <!-- odd/even row coloring -->
                  <xsl:variable name="rowClass">
                    <xsl:choose>
                      <xsl:when test="position() mod 2 = 0">even</xsl:when>
                      <xsl:otherwise>odd</xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>

                  <tr class="{$rowClass}">
                    <td>
                      <a style="cursor:pointer" onclick="toggleDisplay(this)">
                         <xsl:value-of select="@name"/>
                      </a>
                      <div style="display:none">
                       <ul>
                          <li><b>Kernel: </b><xsl:value-of select="@kernel"/> </li>
                          <li><b>Arch: </b><xsl:value-of select="@architecture"/> </li>
                          <li><b>Memory: </b><xsl:value-of select="substring-after(@memory, ' / ')"/> </li>
                       </ul>
                      </div>
                    </td>
                    <td style="border-left: 1px solid black;">
                      <xsl:value-of select="@distribution"/>
                    </td>

                    <!-- color code client versions which don't match the console's -->
                    <xsl:variable name="cltVersion">
                      <xsl:choose>
                        <xsl:when test="contains(@clientVersion, 'OS Lockdown')">
                          <xsl:value-of select="substring-after(@clientVersion, 'OS Lockdown ')"/>
                        </xsl:when>
                        <xsl:otherwise>
                          <xsl:value-of select="@clientVersion"/>
                        </xsl:otherwise>
                      </xsl:choose>
                    </xsl:variable>
                    <xsl:variable name="cellColor">
                      <xsl:choose>
                        <xsl:when test="/AssetReport/@sbVersion != $cltVersion">background-color: yellow</xsl:when>
                        <xsl:otherwise></xsl:otherwise>
                      </xsl:choose>
                    </xsl:variable>

                    <td style="border-left: 1px solid black; {$cellColor}">
                      <xsl:value-of select="$cltVersion" />
                    </td>


                    <td style="border-left: 1px solid black;">
                      <xsl:value-of select="@location"/>
                    </td>

                    <td style="border-left: 1px solid black;">
                      <xsl:value-of select="@contact"/>
                    </td>

                  </tr>
                </xsl:for-each>
              </tbody>
            </table>
        </xsl:if>
        <xsl:comment> Report Footer </xsl:comment>
        <xsl:if test="$footer.display != 'false'">
          <xsl:call-template name="footer">
            <xsl:with-param name="sbVersion" select="/AssetReport/@sbVersion"/>
          </xsl:call-template>
        </xsl:if>

                    
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
