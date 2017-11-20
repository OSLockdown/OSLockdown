/*
 * Copyright 2009 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * 
 */
package com.trustedcs.sb.reports.assessment

/**
 * @author amcgrath
 *
 */
public class AssessmentReport {
	/*
	  <xs:element name="report">
	    <xs:complexType>
	      <xs:sequence>
	        <xs:element name="description" minOccurs="0" type="xs:string" maxOccurs="1" />
	      </xs:sequence>
	      <xs:attribute name="created" type="xs:string" use="required" />
	      <xs:attribute name="profile" type="xs:string" use="required" />
	      <xs:attribute name="hostname" type="xs:string" use="required" />
	      <xs:attribute name="dist" type="xs:string" use="required" />
	      <xs:attribute name="distVersion" type="xs:string" use="required" />
	      <xs:attribute name="kernel" type="xs:string" use="required" />
	      <xs:attribute name="cpuInfo" type="xs:string" use="required" />
	      <xs:attribute name="arch" type="xs:string" use="required" />
	      <xs:attribute name="totalMemory" type="xs:string" use="required" />
	    </xs:complexType>
	  </xs:element>
	*/
	
	def clientName;
	def description;
	def created;
	def profile;
	def hostname;
	def dist;
	def distVersion;
	def kernel;
	def cpuInfo;
	def arch;
	def totalMemory;
	
	AssessmentReport(def node) {
		description = node.description?.text();
		created = node.@created.text();
		profile = node.@profile.text();
		hostname = node.@hostname.text();
		dist = node.@dist.text();
		distVersion = node.@distVersion.text();
		kernel = node.@kernel.text();
		cpuInfo = node.@cpuInfo.text();
		arch = node.@arch.text();
		totalMemory = node.@totalMemory.text();
	}
}
