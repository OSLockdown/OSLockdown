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
public class AssessmentCompliancyLineItem {

/*
 <xs:element name="compliancy">
     <xs:complexType>
      <xs:sequence>
        <xs:element name="line-item" minOccurs="0" maxOccurs="unbounded">
          <xs:complexType>
            <xs:attribute name="source"  type="xs:string" use="required">
              <xs:annotation>
                 <xs:documentation>Organization which supplied the guideline. For example, DISA, SANS, or PCI.</xs:documentation>
               </xs:annotation>
            </xs:attribute>
            <xs:attribute name="name"    type="xs:string" use="required">
              <xs:annotation>
                 <xs:documentation>Name of the guideline. For example, UNIX STIG.</xs:documentation>
               </xs:annotation>
            </xs:attribute>
            <xs:attribute name="version" type="xs:string" use="required" >
              <xs:annotation>
                 <xs:documentation>Version or date of the guideline (ref name).</xs:documentation>
               </xs:annotation>
            </xs:attribute>
            <xs:attribute name="item"    type="xs:string" use="required" />
          </xs:complexType>
        </xs:element>
      </xs:sequence>
     </xs:complexType>
</xs:element>
 */
 	def source;
 	def name;
 	def version;
 	def item;
 	
 	AssessmentCompliancyLineItem(def node) {
 		source = node.@source.text();
 		name = node.@name.text();
 		version = node.@version.text();
 		item = node.@item.text();
 	}
}
