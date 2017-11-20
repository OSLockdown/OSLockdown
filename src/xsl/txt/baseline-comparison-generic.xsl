<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- =========================================================================
      Copyright (c) 2007-2014 Forcepoint LLC.
      This file is released under the GPLv3 license.  
      See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
      or visit https://www.gnu.org/licenses/gpl.html instead.
      
      Purpose: Baseline Comparison Report XML to Text
     =========================================================================
-->
    <xsl:preserve-space  elements="*"/>
    <xsl:include href="common-text.xsl"/>
    <xsl:output method="text" encoding="UTF-8" indent="yes" />
    
    <xsl:template match="/">
        <xsl:text>&#x0A;</xsl:text>
        
        <!-- 
              ================================================================ 
                      Baseline Comparison Report Summary 
              ================================================================
          -->
        <xsl:text>BASELINE COMPARISON REPORT&#x0A;</xsl:text>
        <xsl:text>Generated </xsl:text><xsl:value-of select="substring(/BaselineReportDelta/@created,1,20)"/>
        <xsl:text> by OS Lockdown v</xsl:text>
        <xsl:value-of select="/BaselineReportDelta/@sbVersion"/>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:variable name="leaders">.............................</xsl:variable>
        
        <!-- System Names -->
        <xsl:value-of select="substring(concat('    System A / B', $leaders, $leaders), 1, 25)"/>
        <xsl:value-of select="/BaselineReportDelta/report[1]/@hostname"/>
        <xsl:text> / </xsl:text>
        <xsl:value-of select="/BaselineReportDelta/report[2]/@hostname"/>
        <xsl:text>&#x0A;</xsl:text>
        
        <!-- Creation Date of sub-reports -->
        <xsl:value-of select="substring(concat('   Created A / B', $leaders, $leaders), 1, 25)"/>
        <xsl:value-of select="/BaselineReportDelta/report[1]/@created"/>
        <xsl:text> / </xsl:text>
        <xsl:value-of select="/BaselineReportDelta/report[2]/@created"/>
        <xsl:text>&#x0A;</xsl:text>
        
        <!-- Cpu Information -->
        <xsl:value-of select="substring(concat('Processors A / B', $leaders, $leaders), 1, 25)"/>
        <xsl:value-of select="/BaselineReportDelta/report[1]/@cpuInfo"/>
        <xsl:text> / </xsl:text>
        <xsl:value-of select="/BaselineReportDelta/report[2]/@cpuInfo"/>
        <xsl:text>&#x0A;</xsl:text>
        
        <!-- Memory -->
        <xsl:value-of select="substring(concat('    Memory A / B', $leaders, $leaders), 1, 25)"/>
        <xsl:value-of select="/BaselineReportDelta/report[1]/@totalMemory"/>
        <xsl:text> / </xsl:text>
        <xsl:value-of select="/BaselineReportDelta/report[2]/@totalMemory"/>
        <xsl:text>&#x0A;&#x0A;</xsl:text>
        
        <!-- Operating systems -->
        <xsl:value-of select="substring(concat('Operating System A', $leaders, $leaders), 1, 25)"/>
        <xsl:choose>
            <xsl:when test="number(/BaselineReportDelta/report[1]/@distVersion) &gt;= 10 and /BaselineReportDelta/report[1]/@dist = 'redhat'">
                <xsl:text>Fedora </xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="/BaselineReportDelta/report[1]/@dist"/>
                <xsl:text> </xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:value-of select="/BaselineReportDelta/report[1]/@distVersion"/>
        
        <xsl:text> (</xsl:text>
        <xsl:value-of select="/BaselineReportDelta/report[1]/@arch"/>
        <xsl:text>) [Kernel </xsl:text>
        <xsl:value-of select="/BaselineReportDelta/report[1]/@kernel"/>
        <xsl:text>]</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:value-of select="substring(concat('                 B', $leaders, $leaders), 1, 25)"/>
        <xsl:choose>
            <xsl:when test="number(/BaselineReportDelta/report[2]/@distVersion) &gt;= 10 and /BaselineReportDelta/report[1]/@dist = 'redhat'">
                <xsl:text>Fedora </xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="/BaselineReportDelta/report[2]/@dist"/>
                <xsl:text> </xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:value-of select="/BaselineReportDelta/report[2]/@distVersion"/>
        
        <xsl:text> (</xsl:text>
        <xsl:value-of select="/BaselineReportDelta/report[2]/@arch"/>
        <xsl:text>) [Kernel </xsl:text>
        <xsl:value-of select="/BaselineReportDelta/report[2]/@kernel"/>
        <xsl:text>]</xsl:text>
        <xsl:text>&#x0A;&#x0A;</xsl:text>
        
        <!-- ===================================================================== -->
        
        <xsl:variable name="filesRowCount" select="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection) + 1"/>
        <xsl:variable name="totalRows" select="number($filesRowCount) + 6"/>
        
        
        <xsl:text>Summary:&#x0A;</xsl:text>
        <xsl:value-of select="substring(concat(' * Software', $leaders, $leaders), 1, 25)"/>
        <xsl:choose>
            <xsl:when test="./packages[@hasChanged] != 'true'">
                <xsl:text>No changes detected&#x0A;</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>In Report B: </xsl:text>
                <!-- Changed Software -->
                <xsl:variable name="swDelta" 
             select="count(/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages/changed/packageDelta)"/>
                <xsl:copy-of select="$swDelta"/>
                <xsl:text> packages changed, </xsl:text>
                
                <!-- Added Software -->
                <xsl:variable name="swAdded" 
             select="count(/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages/added/package)"/>
                <xsl:copy-of select="$swAdded"/>
                <xsl:text> are new</xsl:text>
                <xsl:text>, and </xsl:text>
                
                <!-- Removed  Software -->
                <xsl:variable name="swRemoved" 
             select="count(/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages/removed/package)"/>
                <xsl:copy-of select="$swRemoved"/>
                <xsl:text> are non-existent.&#x0A;</xsl:text>
                
            </xsl:otherwise>
            
        </xsl:choose>
        
        <!-- General Sections -->
        <xsl:for-each select="/BaselineReportDelta/sections/section[@name != 'Software' and @name != 'Files']">
            <xsl:value-of select="substring(concat(' * ', @name, $leaders, $leaders), 1, 25)"/>
            <xsl:variable name="changeCount" select="count(./subSection/content[@hasChanged = 'true'])"/>
            <xsl:copy-of select="format-number($changeCount, '###,###')"/>
            <xsl:text> changes &#x0A;</xsl:text>
        </xsl:for-each>
        
        <!-- File Changes -->
        <xsl:value-of select="substring(concat(' * Files', $leaders, $leaders), 1, 25)"/>
        <xsl:text>In Report B: </xsl:text>
        
        <xsl:variable name="filesChanged" select="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup/changed/fileDelta)"/>
        <xsl:value-of select="format-number($filesChanged, '###,###')"/>
        <xsl:text> files changed, </xsl:text>
        
        <xsl:variable name="filesAdded" select="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup/added/file)"/>
        <xsl:value-of select="format-number($filesAdded, '###,###')"/>
        <xsl:text> are new, </xsl:text>
        
        <xsl:text>and </xsl:text>
        <xsl:variable name="filesRemoved" select="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup/removed/file)"/>
        <xsl:value-of select="format-number($filesRemoved, '###,###')"/>
        <xsl:text> are non-existent.&#x0A;</xsl:text>
        
        <!-- 
              ================================================================ 
                                         Changed Software
              ================================================================
          -->
        <xsl:variable name="packages" select="/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages"/>
        <xsl:if test="count($packages/changed/packageDelta) != 0">
            <xsl:text>&#x0A;CHANGED SOFTWARE PACKAGES&#x0A;</xsl:text>
            <xsl:text> * Software found in both reports but versions are different (Report A -&gt; B).&#x0A;</xsl:text>
            
            <xsl:for-each select="$packages/changed/packageDelta">
                <xsl:sort select="translate(./package[1]/@summary, $vLower, $vUpper)"/>
                
                <xsl:variable name="package1" select="./package[1]"/>
                <xsl:variable name="package2" select="./package[2]"/>
                
                <xsl:text>&#x0A;</xsl:text>
                <xsl:value-of select="$package1/@summary"/>
                <xsl:text>&#x0A;</xsl:text>
                
                <xsl:text> - Package Name:    </xsl:text>
                <xsl:value-of select="$package1/@name"/>
                <xsl:text>&#x0A;</xsl:text>
                
                
                <xsl:text> - Version-Release: </xsl:text>
                <xsl:value-of select="$package1/@version"/>
                <xsl:text>-</xsl:text>
                <xsl:value-of select="$package1/@release"/>
                <xsl:text> -&gt; </xsl:text>
                
                <xsl:value-of select="$package2/@version"/>
                <xsl:text>-</xsl:text>
                <xsl:value-of select="$package2/@release"/>
                <xsl:text>&#x0A;</xsl:text>
                
                <xsl:text> - Install Time:    </xsl:text>
                <xsl:value-of select="$package1/@install_localtime"/>
                <xsl:text> -&gt; </xsl:text>
                <xsl:value-of select="$package2/@install_localtime"/>
                <xsl:text>&#x0A;</xsl:text>
                
            </xsl:for-each>
        </xsl:if>
        
        <!-- 
              ================================================================ 
                                         Added Software
              ================================================================
          -->
        <xsl:if test="count(/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages/added/package) != 0">
            <xsl:text>&#x0A;NEW SOFTWARE PACKAGES&#x0A;</xsl:text>
            <xsl:text> * This software was found in Report B but not Report A&#x0A;</xsl:text>
            
            <xsl:variable name="newPackages" select="/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages"/>
            <xsl:for-each select="$newPackages/added/package">
                <xsl:sort select="translate(@summary, $vLower, $vUpper)"/>
                <xsl:text>&#x0A;</xsl:text>
                <xsl:value-of select="@summary"/>
                <xsl:text>&#x0A;</xsl:text>
                
                <xsl:text> - Package Name:    </xsl:text>
                <xsl:value-of select="@name"/>
                <xsl:text>&#x0A;</xsl:text>
                
                <xsl:text> - Version-Release: </xsl:text>
                <xsl:value-of select="@version"/>
                <xsl:text>-</xsl:text>
                <xsl:value-of select="@release"/>
                <xsl:text>&#x0A;</xsl:text>
                
                <xsl:text> - Install Time:    </xsl:text>
                <xsl:choose>
                    <xsl:when test="@install_localtime != ''">
                        <xsl:value-of select="@install_localtime"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="@installtime"/>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:text>&#x0A;</xsl:text> 
            </xsl:for-each>
        </xsl:if>
        
        <!-- 
              ================================================================ 
                                         Removed Software
              ================================================================
          -->
        <xsl:variable name="delPackages" select="/BaselineReportDelta/sections/section[@name='Software']/subSection[@name='Packages']/packages"/>
        <xsl:if test="count($delPackages/removed/package) != 0">
            <xsl:text>&#x0A;NON-EXISTENT SOFTWARE PACKAGES&#x0A;</xsl:text>
            <xsl:text> * This software was found in Report A but not Report B.&#x0A;</xsl:text>
            
            <xsl:for-each select="$delPackages/removed/package">
                <xsl:sort select="translate(@summary, $vLower, $vUpper)"/>
                
                <xsl:text>&#x0A;</xsl:text>
                <xsl:value-of select="@summary"/>
                <xsl:text>&#x0A;</xsl:text>
                
                <xsl:text> - Package Name:    </xsl:text>
                <xsl:value-of select="@name"/>
                <xsl:text>&#x0A;</xsl:text>
                
                <xsl:text> - Version-Release: </xsl:text>
                <xsl:value-of select="@version"/>
                <xsl:text>-</xsl:text>
                <xsl:value-of select="@release"/>
                <xsl:text>&#x0A;</xsl:text>
                
                <xsl:text> - Install Time:    </xsl:text>
                <xsl:value-of select="@install_localtime"/>
                <xsl:text>&#x0A;</xsl:text>
                
            </xsl:for-each>
        </xsl:if>
        
        <!-- 
              ================================================================ 
                                         Files Information
              ================================================================
          -->
        <xsl:if test="count(/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup/changed/fileDelta) != 0">
            <xsl:text>&#x0A;CHANGED FILES&#x0A;</xsl:text>
            <xsl:text> * These files exist in both reports but are different (Report A -&gt; B).&#x0A;</xsl:text>
            
            <xsl:variable name="fileTypes" select="/BaselineReportDelta/sections/section[@name = 'Files']/subSection"/>
            <xsl:for-each select="$fileTypes/fileGroups/fileGroup">
                
                <xsl:if test="count(./changed/fileDelta) != 0">
                    
                    <xsl:text>&#x0A; * </xsl:text>
                    <xsl:value-of select="../../@name"/>
                    <xsl:text> - </xsl:text>
                    <xsl:value-of select="@name"/>
                    <xsl:text>&#x0A;</xsl:text>
                    
                    <xsl:for-each select="./changed/fileDelta">
                        <xsl:sort select="./file[1]/@path"/>
                        
                        <xsl:variable name="file1" select="./file[1]"/>
                        <xsl:variable name="file2" select="./file[2]"/>
                        
                        <xsl:text>   </xsl:text>
                        <xsl:value-of select="$file1/@path"/>
                        <xsl:text>&#x0A;</xsl:text>
                        
                        <xsl:text>   - Permissions:      </xsl:text>
                        <xsl:choose>
                            <xsl:when test="$file1/@mode != $file2/@mode">
                                <xsl:value-of select="$file1/@mode"/>
                                <xsl:text> -&gt; </xsl:text>
                                <xsl:value-of select="$file2/@mode"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="$file1/@mode"/>
                            </xsl:otherwise>
                        </xsl:choose>
                        <xsl:text>&#x0A;</xsl:text>
                        
                        <xsl:text>   - Owner / Group ID: </xsl:text>
                        <xsl:choose>
                            <xsl:when test="$file1/@uid != $file2/@uid or $file1/@gid != $file2/@gid">
                                <xsl:value-of select="$file1/@uid"/>
                                <xsl:text> / </xsl:text><xsl:value-of select="$file1/@gid"/>
                                <xsl:text> -&gt; </xsl:text>
                                <xsl:value-of select="$file2/@uid"/>
                                <xsl:text> / </xsl:text><xsl:value-of select="$file2/@gid"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="$file1/@uid"/>
                                <xsl:text> / </xsl:text>
                                <xsl:value-of select="$file1/@gid"/>
                            </xsl:otherwise>
                        </xsl:choose>
                        <xsl:text>&#x0A;</xsl:text>
                        
                        <xsl:text>   - SUID / SGID:      </xsl:text>
                        <xsl:choose>
                            <xsl:when test="$file1/@suid != $file2/@suid or $file1/@sgid != $file2/@sgid">
                                <xsl:value-of select="$file1/@suid"/>
                                <xsl:text> / </xsl:text><xsl:value-of select="$file1/@sgid"/>
                                <xsl:text> -&gt; </xsl:text>
                                <xsl:value-of select="$file2/@suid"/>
                                <xsl:text> / </xsl:text><xsl:value-of select="$file2/@sgid"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="$file1/@suid"/>
                                <xsl:text> / </xsl:text>
                                <xsl:value-of select="$file1/@sgid"/>
                            </xsl:otherwise>
                        </xsl:choose>
                        <xsl:text>&#x0A;</xsl:text>
                        
                        <xsl:text>   - Contents:         </xsl:text>
                        <xsl:choose>
                            <xsl:when test="$file1/@sha1 != $file2/@sha1">
                                <xsl:text>CHANGED</xsl:text>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:text>unchanged</xsl:text>
                            </xsl:otherwise>
                        </xsl:choose>
                        <xsl:text>&#x0A;</xsl:text>
                        
                        <xsl:text>   - Last Modified:    </xsl:text>
                        <xsl:choose>
                            <xsl:when test="$file1/@mtime != $file2/@mtime">
                                <xsl:value-of select="$file1/@mtime"/>
                                <xsl:text> -&gt; </xsl:text>
                                <xsl:value-of select="$file2/@mtime"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="$file2/@mtime"/>
                            </xsl:otherwise>
                        </xsl:choose>
                        <xsl:text>&#x0A;&#x0A;</xsl:text>
                    </xsl:for-each>
                    
                </xsl:if>
            </xsl:for-each>
            
        </xsl:if>
        
        <!-- 
              ================================================================ 
                                       Added/New Files
              ================================================================
          -->
        <xsl:variable name="addedFiles" select="/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup"/>
        <xsl:if test="count($addedFiles/added/file) != 0">
            <xsl:text>&#x0A;NEW FILES&#x0A;</xsl:text>
            <xsl:text> * These files were found in Report B but not Report A.&#x0A; </xsl:text>
            
            <xsl:for-each select="$addedFiles">
                <xsl:if test="count(./added/file) != 0">
                    <xsl:text>&#x0A; * </xsl:text>
                    <xsl:value-of select="../../@name"/>
                    <xsl:text> - </xsl:text>
                    <xsl:value-of select="@name"/>
                    <xsl:text>&#x0A;</xsl:text>
                    
                    <xsl:for-each select="./added/file">
                        <xsl:sort select="@path"/>
                        
                        <xsl:text>   </xsl:text>
                        <xsl:value-of select="@path"/>
                        <xsl:text>&#x0A;</xsl:text>
                        
                        <xsl:text>   - Permissions:      </xsl:text>
                        <xsl:value-of select="@mode"/>
                        <xsl:text>&#x0A;</xsl:text>
                        
                        <xsl:text>   - Owner / Group ID: </xsl:text>
                        <xsl:value-of select="@uid"/>
                        <xsl:text> / </xsl:text>
                        <xsl:value-of select="@gid"/>
                        <xsl:text>&#x0A;</xsl:text>
                        
                        <xsl:text>   - SUID / SGID:      </xsl:text>
                        <xsl:value-of select="@suid"/>
                        <xsl:text> / </xsl:text>
                        <xsl:value-of select="@sgid"/>
                        <xsl:text>&#x0A;</xsl:text>
                        
                        <xsl:text>   - Last Modified:    </xsl:text>
                        <xsl:value-of select="@mtime"/>
                        <xsl:text>&#x0A;&#x0A;</xsl:text>
                        
                    </xsl:for-each>
                </xsl:if>
            </xsl:for-each>
            
        </xsl:if>
        
        <!-- 
              ================================================================ 
                                       Removed Files
              ================================================================
          -->
        <xsl:variable name="removedFiles" select="/BaselineReportDelta/sections/section[@name = 'Files']/subSection/fileGroups/fileGroup"/>
        <xsl:if test="count($removedFiles/removed/file) != 0">
            <xsl:text>&#x0A;NON-EXISTENT FILES&#x0A;</xsl:text>
            <xsl:text> * These files were found in Report A but not Report B.&#x0A;</xsl:text>
            
            <xsl:for-each select="$removedFiles">
                <xsl:if test="count(./removed/file) != 0">
                    <xsl:text>&#x0A; * </xsl:text>
                    <xsl:value-of select="../../@name"/>
                    <xsl:text> - </xsl:text>
                    <xsl:value-of select="@name"/>
                    <xsl:text>&#x0A;</xsl:text>
                    <xsl:for-each select="./removed/file">
                        <xsl:sort select="@path"/>
                        
                        <xsl:text>   - </xsl:text>
                        <xsl:value-of select="@path"/>
                        <xsl:text>&#x0A;</xsl:text>
                        
                    </xsl:for-each>
                </xsl:if>
            </xsl:for-each>
            
        </xsl:if>
        
    </xsl:template>
</xsl:stylesheet>
