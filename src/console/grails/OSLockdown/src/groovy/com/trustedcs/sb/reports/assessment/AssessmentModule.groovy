/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
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
public class AssessmentModule {
	/*
  <xs:element name="module">
    <xs:complexType mixed="true"> 
      <xs:sequence>
        <xs:element name="description" type="xs:string" minOccurs="0" maxOccurs="1"/>
        <xs:sequence>
           <xs:element ref="views" minOccurs="0" maxOccurs="unbounded"/>
           <xs:element ref="compliancy" minOccurs="1" maxOccurs="1"/>
        </xs:sequence> 
      </xs:sequence>

      <xs:attribute name="severity" use="required">
        <xs:simpleType>
          <xs:restriction base="xs:NMTOKEN">
            <xs:enumeration value="High" />
            <xs:enumeration value="Medium" />
            <xs:enumeration value="Low" />
          </xs:restriction>
        </xs:simpleType>
      </xs:attribute>

      <xs:attribute ref="name" use="required" />
      <xs:attribute name="results" type="xs:string" use="required" />
      <xs:attribute name="severityLevel" type="xs:string" use="required" />
    </xs:complexType>
  </xs:element>
	 */
	 
	 // attributes
     def name;
     def description;
     def severity;
     def severityLevel;  
     
     // compliancy line item listings
     def compliancyLineItems = [];
     
     //  map [clientName:resultString]
     def results= [:]
     
     // list of views for the module
     def views = [];	 
	 
	 AssessmentModule(def node) {
		 // attributes
		 name = node.@name.text();
		 severity = node.@severity.text();
		 severityLevel = node.@severityLevel.text();
		 description = node.description?.text();
		 
		 // views
		 node.views.view.each { 
			 views << it.text();
		 }
		 
		 // compliancies
		 node.compliancy.'line-item'.each {
			 compliancyLineItems << new AssessmentCompliancyLineItem(it);
		 }
	 }
}
