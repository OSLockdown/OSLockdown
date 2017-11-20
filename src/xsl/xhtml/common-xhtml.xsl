<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: common-xhtml.xsl 23917 2017-03-07 15:44:30Z rsanders $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <!--
    *************************************************************************
    Copyright (c) 2007-2014 Forcepoint LLC.
    This file is released under the GPLv3 license.  
    See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
    or visit https://www.gnu.org/licenses/gpl.html instead.
    
    OS Lockdown: Common Templates for all XHTML reports
  -->

  <xsl:include href="report-customization.xsl" />

  <xsl:param name="entity.up.arrow" select="'&#x25B4;'" />
  <xsl:param name="entity.down.arrow" select="'&#x25BC;'" />

  <!-- ======================================================================= -->
  <xsl:template name="footer">
    <xsl:param name="sbVersion" />
    <table class="footerTable">
      <tr>
        <td style="text-align: left; vertical-align: top">
          <xsl:text>OS Lockdown v</xsl:text><xsl:value-of select="$sbVersion" />
        </td>
        <td style="text-align: right">
          <a href="{$report.owner.url}">
            <xsl:copy-of select="$report.owner.name" />
          </a>
        </td>
      </tr>
    </table>
  </xsl:template>

  <!-- ======================================================================= -->
  <xsl:template name="header">
    <table class="hdrTable">
      <tr>
        <xsl:choose>
          <xsl:when test="$logo.display = 'false'">
            <th colspan="4"
              style="font-size: {$report.header.font.size}; font-weight: {$report.header.font.weight}; color: {$report.header.font.color}; background-color: {$report.header.bgcolor}; padding: 20px">
              <div>
                <xsl:copy-of select="$report.title" />
              </div>
            </th>
          </xsl:when>
          <xsl:otherwise>
            <th colspan="3"
              style="font-size: {$report.header.font.size}; font-weight: {$report.header.font.weight}; color: {$report.header.font.color}; background-color: {$report.header.bgcolor}">
              <xsl:copy-of select="$report.title" />
            </th>
            <th
              style="padding: 1em; text-align: right; background-color: {$report.header.bgcolor}; color: {$report.header.color};">
              <img src="{$image.header.logo}" alt="OS Lockdown Logo" />
            </th>
          </xsl:otherwise>
        </xsl:choose>
      </tr>
    </table>
  </xsl:template>

  <!-- ======================================================================= -->
  <xsl:template name="module.result">
    <xsl:param name="results" />
    <xsl:choose>
      <xsl:when test="$results = 'Fail'">
        <td class="moduleResults moduleFail">
          <xsl:value-of select="$results" />
        </td>
      </xsl:when>
      <xsl:when test="$results = 'Error'">
        <td class="moduleResults moduleError">
          <xsl:value-of select="$results" />
        </td>
      </xsl:when>
      <xsl:when test="$results = 'Pass'">
        <td class="moduleResults modulePass">
          <xsl:value-of select="$results" />
        </td>
      </xsl:when>
      <xsl:when test="$results = 'Applied'">
        <td class="moduleResults moduleApplied">
          <xsl:value-of select="$results" />
        </td>
      </xsl:when>
      <xsl:when test="$results = 'Undone'">
        <td class="moduleResults moduleUndone">
          <xsl:value-of select="$results" />
        </td>
      </xsl:when>
      <xsl:when test="$results = 'NA'">
        <td class="moduleResults moduleNotApplicable">
          <xsl:text>Not Applicable</xsl:text>
        </td>
      </xsl:when>
      <xsl:when test="$results = 'Not Applicable'">
        <td class="moduleResults moduleNotApplicable">
          <xsl:value-of select="$results" />
        </td>
      </xsl:when>

      <xsl:when test="$results = 'Not Required'">
        <td class="moduleResults moduleNotRequired">
          <xsl:value-of select="$results" />
        </td>
      </xsl:when>

      <xsl:when test="$results = 'Module Unavailable'">
        <td class="moduleResults moduleUnavailable">
          <xsl:value-of select="$results" />
        </td>
      </xsl:when>

      <xsl:when test="$results = 'OS NA'">
        <td class="moduleResults moduleOSnotApplicable">
           <xsl:text>OS N/A</xsl:text>
        </td>
      </xsl:when>

      <xsl:when test="$results = 'Manual Action'">
        <td class="moduleResults moduleManualActionReqd">
          <xsl:value-of select="$results" />
        </td>
      </xsl:when>

      <xsl:when test="$results = 'Not Scanned'">
        <td class="moduleResults moduleNotScanned">
          <xsl:value-of select="$results" />
        </td>
      </xsl:when>
      <xsl:otherwise>
        <td class="moduleResults">
          <xsl:value-of select="$results" />
        </td>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- ======================================================================= -->
  <xsl:template name="module.severity">
    <xsl:param name="severity" />
    <xsl:choose>
      <xsl:when test="$severity = 'High'">
        <td class="moduleSeverity moduleSeverityHigh">
          <xsl:value-of select="$severity" />
        </td>
      </xsl:when>
      <xsl:when test="$severity = 'Medium'">
        <td class="moduleSeverity moduleSeverityMedium">
          <xsl:value-of select="$severity" />
        </td>
      </xsl:when>
      <xsl:when test="$severity = 'Low'">
        <td class="moduleSeverity moduleSeverityLow">
          <xsl:value-of select="$severity" />
        </td>
      </xsl:when>
      <xsl:otherwise>
        <td class="moduleSeverity">
          <xsl:value-of select="$severity" />
        </td>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- ======================================================================= -->
  <xsl:template name="profile.information">
    <xsl:param name="reportRoot" />
    <tr>
      <td class="subSectionTitle" rowspan="2" width="25%" valign="top"
        style="text-align: right; border-right: 1px solid black;">Profile</td>
      <td colspan="5" class="infoItem" style="border-bottom: none;">
        <xsl:value-of select="$reportRoot/report/@profile" />
      </td>
    </tr>
    <tr>
      <td colspan="5">
        <div class="profileDescription" style="adding: 1em">
          <xsl:value-of select="$reportRoot/report/description" />
          <xsl:if test="count($reportRoot/modules/module[@results='Module Unavailable']) != 0">
            <br />
            <span style="color:red">
              <b>NOTE:</b>
            </span>
            <p style="color:red; padding-left: 1em; font-size:90%">
              This profile contained some modules which were not available (marked as
              <i>Module Unavailable</i>
              ). This usually indicates an older version of
              OS Lockdown is installed on client machines.
            </p>
          </xsl:if>
        </div>
      </td>
    </tr>

  </xsl:template>

  <!-- ======================================================================= -->
  <xsl:template name="module.compliancy.list">
    <xsl:param name="compliancy" />
    <h4 class="compliancyList">Compliancy:</h4>
    <ul class="compliancyList">
      <xsl:for-each select="$compliancy/line-item">
        <xsl:sort select="@source" />
        <xsl:sort select="@name" />
        <xsl:sort select="@item" />
        <li>
          <xsl:value-of select="@source" />
          <xsl:text>&#x020;</xsl:text>
          <xsl:value-of select="@name" />
          <xsl:text>&#x020; (</xsl:text>
          <xsl:value-of select="@version" />
          <xsl:text>): </xsl:text>
          <xsl:value-of select="@item" />
        </li>
      </xsl:for-each>
    </ul>
  </xsl:template>

  <!-- ======================================================================= -->
  <xsl:template name="module.message.details">
    <xsl:param name="details" />

    <xsl:if
      test="count($details/statusMessage) != 0 and $details/statusMessage != '' and $details/statusMessage != 'None'">
      <h4 class="moduleMessages">Module Messages:</h4>

      <xsl:variable name="statusColor">
        <xsl:choose>
          <xsl:when test="$details/../@results = 'Fail'">
            red
          </xsl:when>
          <xsl:when test="$details/../@results = 'Error'">
            red
          </xsl:when>
          <xsl:when test="$details/../@results = 'Pass'">
            green
          </xsl:when>
          <xsl:otherwise>
            black
          </xsl:otherwise>
        </xsl:choose>
      </xsl:variable>
      <p class="statusMessage" style="color: {$statusColor}">
        <xsl:value-of select="$details/statusMessage" />
      </p>

      <ul class="moduleMessages">
        <xsl:for-each select="$details/messages/message">
          <li>
            <xsl:variable name="msgColor">
              <xsl:choose>
                <xsl:when test="substring-before(., ':') = 'Error'">
                  <xsl:text>red</xsl:text>
                </xsl:when>
                <xsl:when test="substring-before(., ':') = 'Fail'">
                  <xsl:text>red</xsl:text>
                </xsl:when>
                <xsl:when test="substring-before(., ':') = 'Retired'">
                  <xsl:text>red</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:text>black</xsl:text>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <span style="color: {$msgColor}">
              <xsl:value-of select="." />
            </span>
          </li>
        </xsl:for-each>
      </ul>
    </xsl:if>

  </xsl:template>

  <!-- ======================================================================= -->
  <xsl:template name="software.patch.list">
    <xsl:param name="patches" />
    <xsl:text>Patches:</xsl:text>
    <ul class="patchList">
      <xsl:for-each select="$patches">
        <xsl:sort select="@name" />
        <li>
          <xsl:value-of select="@name" />
        </li>
      </xsl:for-each>
    </ul>
  </xsl:template>

  <!-- ======================================================================= -->
  <xsl:template name="html.header">
    <head>
      <title>
        <xsl:copy-of select="$report.title" />
      </title>
      <link rel="stylesheet" href="{$css.file}" />
      <script language="JavaScript">
<![CDATA[
function toggleDisplay (element) {
   var div = element.parentNode.getElementsByTagName("div")
   if (div[0].style.display=='block')  
  {
  div[0].style.display = 'none';
  //element.innerHTML = '&#x25B6;';
  element.style.fontWeight = 'normal';
  }
   else 
  {
  div[0].style.display = 'block';
  //element.innerHTML = '&#x25BC;';
  element.style.fontWeight = 'bold';
  }
}

function expandAll(){
   var togglebutton;
   for( var i=0, e = document.getElementsByTagName("div"); i < e.length; ++i )
  {
  if( e[i].style.display == 'none' )
        {
            e[i].style.display = 'block';
        }
  }
}

function collapseAll(){
   for( var i=0, e = document.getElementsByTagName("div"); i < e.length; ++i )
  {
  if( e[i].style.display == 'block' )
        {
            e[i].style.display = 'none';
        }
  }
}


/*
Table sorting script  by Joost de Valk, check it out at http://www.joostdevalk.nl/code/sortable-table/.
Based on a script from http://www.kryogenix.org/code/browser/sorttable/.
Distributed under the MIT license: http://www.kryogenix.org/code/browser/licence.html .

Copyright (c) 1997-2007 Stuart Langridge, Joost de Valk.

Version 1.5.7
*/

/* You can change these values */
var image_path = "/OSLockdown/images/";
var image_up = "arrowup.gif";
var image_down = "arrowdown.gif";
var image_none = "arrownone.gif";
var europeandate = true;
var alternate_row_colors = true;

/* Don't change anything below this unless you know what you're doing */
addEvent(window, "load", sortables_init);

var SORT_COLUMN_INDEX;
var thead = false;

function sortables_init() {
	// Find all tables with class sortable and make them sortable
	if (!document.getElementsByTagName) return;
	tbls = document.getElementsByTagName("table");
	for (ti=0;ti<tbls.length;ti++) {
		thisTbl = tbls[ti];
		if (((' '+thisTbl.className+' ').indexOf("sortable") != -1) && (thisTbl.id)) {
			ts_makeSortable(thisTbl);
		}
	}
}

function ts_makeSortable(t) {
	if (t.rows && t.rows.length > 0) {
		if (t.tHead && t.tHead.rows.length > 0) {
			var firstRow = t.tHead.rows[t.tHead.rows.length-1];
			thead = true;
		} else {
			var firstRow = t.rows[0];
		}
	}
	if (!firstRow) return;
	
	// We have a first row: assume it's the header, and make its contents clickable links
	for (var i=0;i<firstRow.cells.length;i++) {
		var cell = firstRow.cells[i];
		var txt = ts_getInnerText(cell);
		if (cell.className != "unsortable" && cell.className.indexOf("unsortable") == -1) {
			cell.innerHTML = txt + '<a href="#" class="sortheader" onclick="ts_resortTable(this, '+i+');return false;"><span class="sortarrow">&nbsp;&nbsp;<img title=\"Click to sort\" src="'+ image_path + image_none + '" alt="&darr;"/></span></a>';
		}
	}
	if (alternate_row_colors) {
		alternate(t);
	}
}

function ts_getInnerText(el) {
	if (typeof el == "string") return el;
	if (typeof el == "undefined") { return el };
	if (el.innerText) return el.innerText;	//Not needed but it is faster
	var str = "";
	
	var cs = el.childNodes;
	var l = cs.length;
	for (var i = 0; i < l; i++) {
		switch (cs[i].nodeType) {
			case 1: //ELEMENT_NODE
				str += ts_getInnerText(cs[i]);
				break;
			case 3:	//TEXT_NODE
				str += cs[i].nodeValue;
				break;
		}
	}
	return str;
}

function ts_resortTable(lnk, clid) {
	var span;
	for (var ci=0;ci<lnk.childNodes.length;ci++) {
		if (lnk.childNodes[ci].tagName && lnk.childNodes[ci].tagName.toLowerCase() == 'span') span = lnk.childNodes[ci];
	}
	var spantext = ts_getInnerText(span);
	var td = lnk.parentNode;
	var column = clid || td.cellIndex;
	var t = getParent(td,'TABLE');
	// Work out a type for the column
	if (t.rows.length <= 1) return;
	var itm = "";
	var i = 0;
	while (itm == "" && i < t.tBodies[0].rows.length) {
		var itm = ts_getInnerText(t.tBodies[0].rows[i].cells[column]);
		itm = trim(itm);
		if (itm.substr(0,4) == "<!--" || itm.length == 0) {
			itm = "";
		}
		i++;
	}
	if (itm == "") return; 
	sortfn = ts_sort_caseinsensitive;
	if (itm.match(/^\d\d[\/\.-][a-zA-z][a-zA-Z][a-zA-Z][\/\.-]\d\d\d\d$/)) sortfn = ts_sort_date;
	if (itm.match(/^\d\d[\/\.-]\d\d[\/\.-]\d\d\d{2}?$/)) sortfn = ts_sort_date;
	if (itm.match(/^-?[£$Û¢´]\d/)) sortfn = ts_sort_numeric;
	if (itm.match(/^-?(\d+[,\.]?)+(E[-+][\d]+)?%?$/)) sortfn = ts_sort_numeric;
	SORT_COLUMN_INDEX = column;
	var firstRow = new Array();
	var newRows = new Array();
	for (k=0;k<t.tBodies.length;k++) {
		for (i=0;i<t.tBodies[k].rows[0].length;i++) { 
			firstRow[i] = t.tBodies[k].rows[0][i]; 
		}
	}
	for (k=0;k<t.tBodies.length;k++) {
		if (!thead) {
			// Skip the first row
			for (j=1;j<t.tBodies[k].rows.length;j++) { 
				newRows[j-1] = t.tBodies[k].rows[j];
			}
		} else {
			// Do NOT skip the first row
			for (j=0;j<t.tBodies[k].rows.length;j++) { 
				newRows[j] = t.tBodies[k].rows[j];
			}
		}
	}
	newRows.sort(sortfn);
	if (span.getAttribute("sortdir") == 'down') {
			ARROW = '&nbsp;&nbsp;<img title=\"Click to sort\" src="'+ image_path + image_down + '" alt="&darr;"/>';
			newRows.reverse();
			span.setAttribute('sortdir','up');
	} else {
			ARROW = '&nbsp;&nbsp;<img title=\"Click to sort\" src="'+ image_path + image_up + '" alt="&uarr;"/>';
			span.setAttribute('sortdir','down');
	} 
    // We appendChild rows that already exist to the tbody, so it moves them rather than creating new ones
    // don't do sortbottom rows
    for (i=0; i<newRows.length; i++) { 
		if (!newRows[i].className || (newRows[i].className && (newRows[i].className.indexOf('sortbottom') == -1))) {
			t.tBodies[0].appendChild(newRows[i]);
		}
	}
    // do sortbottom rows only
    for (i=0; i<newRows.length; i++) {
		if (newRows[i].className && (newRows[i].className.indexOf('sortbottom') != -1)) 
			t.tBodies[0].appendChild(newRows[i]);
	}
	// Delete any other arrows there may be showing
	var allspans = document.getElementsByTagName("span");
	for (var ci=0;ci<allspans.length;ci++) {
		if (allspans[ci].className == 'sortarrow') {
			if (getParent(allspans[ci],"table") == getParent(lnk,"table")) { // in the same table as us?
				allspans[ci].innerHTML = '&nbsp;&nbsp;<img title=\"Click to sort\" src="'+ image_path + image_none + '" alt="&darr;"/>';
			}
		}
	}		
	span.innerHTML = ARROW;
	alternate(t);
}

function getParent(el, pTagName) {
	if (el == null) {
		return null;
	} else if (el.nodeType == 1 && el.tagName.toLowerCase() == pTagName.toLowerCase()) {
		return el;
	} else {
		return getParent(el.parentNode, pTagName);
	}
}

function sort_date(date) {	
	// y2k notes: two digit years less than 50 are treated as 20XX, greater than 50 are treated as 19XX
	dt = "00000000";
	if (date.length == 11) {
		mtstr = date.substr(3,3);
		mtstr = mtstr.toLowerCase();
		switch(mtstr) {
			case "jan": var mt = "01"; break;
			case "feb": var mt = "02"; break;
			case "mar": var mt = "03"; break;
			case "apr": var mt = "04"; break;
			case "may": var mt = "05"; break;
			case "jun": var mt = "06"; break;
			case "jul": var mt = "07"; break;
			case "aug": var mt = "08"; break;
			case "sep": var mt = "09"; break;
			case "oct": var mt = "10"; break;
			case "nov": var mt = "11"; break;
			case "dec": var mt = "12"; break;
			// default: var mt = "00";
		}
		dt = date.substr(7,4)+mt+date.substr(0,2);
		return dt;
	} else if (date.length == 10) {
		if (europeandate == false) {
			dt = date.substr(6,4)+date.substr(0,2)+date.substr(3,2);
			return dt;
		} else {
			dt = date.substr(6,4)+date.substr(3,2)+date.substr(0,2);
			return dt;
		}
	} else if (date.length == 8) {
		yr = date.substr(6,2);
		if (parseInt(yr) < 50) { 
			yr = '20'+yr; 
		} else { 
			yr = '19'+yr; 
		}
		if (europeandate == true) {
			dt = yr+date.substr(3,2)+date.substr(0,2);
			return dt;
		} else {
			dt = yr+date.substr(0,2)+date.substr(3,2);
			return dt;
		}
	}
	return dt;
}

function ts_sort_date(a,b) {
	dt1 = sort_date(ts_getInnerText(a.cells[SORT_COLUMN_INDEX]));
	dt2 = sort_date(ts_getInnerText(b.cells[SORT_COLUMN_INDEX]));
	
	if (dt1==dt2) {
		return 0;
	}
	if (dt1<dt2) { 
		return -1;
	}
	return 1;
}
function ts_sort_numeric(a,b) {
	var aa = ts_getInnerText(a.cells[SORT_COLUMN_INDEX]);
	aa = clean_num(aa);
	var bb = ts_getInnerText(b.cells[SORT_COLUMN_INDEX]);
	bb = clean_num(bb);
	return compare_numeric(aa,bb);
}
function compare_numeric(a,b) {
	var a = parseFloat(a);
	a = (isNaN(a) ? 0 : a);
	var b = parseFloat(b);
	b = (isNaN(b) ? 0 : b);
	return a - b;
}
function ts_sort_caseinsensitive(a,b) {
	aa = ts_getInnerText(a.cells[SORT_COLUMN_INDEX]).toLowerCase();
	bb = ts_getInnerText(b.cells[SORT_COLUMN_INDEX]).toLowerCase();
	if (aa==bb) {
		return 0;
	}
	if (aa<bb) {
		return -1;
	}
	return 1;
}
function ts_sort_default(a,b) {
	aa = ts_getInnerText(a.cells[SORT_COLUMN_INDEX]);
	bb = ts_getInnerText(b.cells[SORT_COLUMN_INDEX]);
	if (aa==bb) {
		return 0;
	}
	if (aa<bb) {
		return -1;
	}
	return 1;
}
function addEvent(elm, evType, fn, useCapture)
// addEvent and removeEvent
// cross-browser event handling for IE5+,	NS6 and Mozilla
// By Scott Andrew
{
	if (elm.addEventListener){
		elm.addEventListener(evType, fn, useCapture);
		return true;
	} else if (elm.attachEvent){
		var r = elm.attachEvent("on"+evType, fn);
		return r;
	} else {
		alert("Handler could not be removed");
	}
}
function clean_num(str) {
	str = str.replace(new RegExp(/[^-?0-9.]/g),"");
	return str;
}
function trim(s) {
	return s.replace(/^\s+|\s+$/g, "");
}
function alternate(table) {
	// Take object table and get all it's tbodies.
	var tableBodies = table.getElementsByTagName("tbody");
	// Loop through these tbodies
	for (var i = 0; i < tableBodies.length; i++) {
		// Take the tbody, and get all it's rows
		var tableRows = tableBodies[i].getElementsByTagName("tr");
		// Loop through these rows
		// Start at 1 because we want to leave the heading row untouched
		for (var j = 0; j < tableRows.length; j++) {
			// Check if j is even, and apply classes for both possible results
			if ( (j % 2) == 0  ) {
				if ( !(tableRows[j].className.indexOf('odd') == -1) ) {
					tableRows[j].className = tableRows[j].className.replace('odd', 'even');
				} else {
					if ( tableRows[j].className.indexOf('even') == -1 ) {
						tableRows[j].className += " even";
					}
				}
			} else {
				if ( !(tableRows[j].className.indexOf('even') == -1) ) {
					tableRows[j].className = tableRows[j].className.replace('even', 'odd');
				} else {
					if ( tableRows[j].className.indexOf('odd') == -1 ) {
						tableRows[j].className += " odd";
					}
				}
			} 
		}
	}
}

/*
 * End of table sorting code
 */

//-->
]]>
      </script>
    </head>
  </xsl:template>

  <!-- ======================================================================= -->
  <!-- Software install times and file modified times come in: -->
  <!-- "Tue Jan 26 11:28:25 EST 2010" but we need it to be more like -->
  <!-- "2010-01-26 11:28:25" -->
  <!-- ======================================================================= -->
  <xsl:template name="date.reformat">
    <xsl:param name="iDate" />
    <xsl:variable name="iYear" select="substring($iDate, string-length($iDate)-4)" />
    <xsl:variable name="iMonthName" select="substring($iDate, 5, 3)" />
    <xsl:variable name="iDay" select="substring($iDate, 9, 2)" />
    <xsl:variable name="iTime" select="substring($iDate, 12, 8)" />
    <xsl:variable name="iTimezone" select="substring($iDate, 21, 3)" />
    <xsl:variable name="iMonth">
      <xsl:choose>
        <xsl:when test="$iMonthName = 'Jan'">
          01
        </xsl:when>
        <xsl:when test="$iMonthName = 'Feb'">
          02
        </xsl:when>
        <xsl:when test="$iMonthName = 'Mar'">
          03
        </xsl:when>
        <xsl:when test="$iMonthName = 'Apr'">
          04
        </xsl:when>
        <xsl:when test="$iMonthName = 'May'">
          05
        </xsl:when>
        <xsl:when test="$iMonthName = 'Jun'">
          06
        </xsl:when>
        <xsl:when test="$iMonthName = 'Jul'">
          07
        </xsl:when>
        <xsl:when test="$iMonthName = 'Aug'">
          08
        </xsl:when>
        <xsl:when test="$iMonthName = 'Sep'">
          09
        </xsl:when>
        <xsl:when test="$iMonthName = 'Oct'">
          10
        </xsl:when>
        <xsl:when test="$iMonthName = 'Nov'">
          11
        </xsl:when>
        <xsl:when test="$iMonthName = 'Dec'">
          12
        </xsl:when>
      </xsl:choose>
    </xsl:variable>
    <xsl:copy-of select="$iYear" />
    <xsl:text>-</xsl:text>
    <xsl:copy-of select="$iMonth" />
    <xsl:text>-</xsl:text>
    <xsl:copy-of select="$iDay" />
    <xsl:text> </xsl:text>
    <xsl:copy-of select="$iTime" />
    <xsl:text> </xsl:text>
    <xsl:copy-of select="$iTimezone" />
  </xsl:template>

  <!-- ======================================================================= -->
</xsl:stylesheet>
