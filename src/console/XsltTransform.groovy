/**
 * Copyright (c) 2007-2014 Forcepoint LLC.
 * This file is released under the GPLv3 license.  
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
 * or visit https://www.gnu.org/licenses/gpl.html instead.
 */

package com.trustedcs.sb.xsl;

//JAXP
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.Source;
import javax.xml.transform.Result;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.sax.SAXResult;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.URIResolver;

/**
 * This class is a simple XSLT transform
 */
public class XsltTransform {

    public XsltTransform() {

    }

    // transformer factory
    private static TransformerFactory transformerFactory;
    static {
    	transformerFactory = TransformerFactory.newInstance();
    }

    /**
     * Transform the input source to the output location using the xsl stream
     * @param xslStream
     * @param inputSource
     * @param outputLocation
     */
    public static void transform(URIResolver resolver, InputStream xslStream,
        InputStream inputSource, OutputStream outputLocation, Map parameterMap)
    throws Exception {

    	// set the uri resolver
    	if ( resolver ) {
            transformerFactory.setURIResolver(resolver);
    	}

        // Load up the stylesheet into a transformer instance.
        def transformer = transformerFactory.newTransformer(new StreamSource(xslStream));

        // load parameter map into the transformer
    	if ( parameterMap ) {
            parameterMap.each { paramName, paramValue ->
                transformer.setParameter(paramName,paramValue);
            }
    	}

        // We have the transformer set up, so now prepare the source
        // XML and wrap the output writer in a Result.
        def input = new StreamSource(inputSource);
        def output = new StreamResult(outputLocation);

        // Perform the transformation!
        transformer.transform(input,output);
    }

    /**
     * Main method.
     * @param args command-line arguments
     */
    public static void main(def args) {
        try {
            //Setup input and output files
            if ( args.length < 2 ) {
                println "Syntax Error!";
                println "usage: groovy XsltTransform.groovy <xsl> <data>";
                System.exit(-1);
            }
            File xslFile = new File(args[0]);
            if ( !xslFile.exists() ) {
                System.out.println("ERROR!");
                println "XslFile: ${xslFile} does not exist";
                System.exit(-1);
            }
            File dataFile = new File(args[1]);
            if ( !dataFile.exists() ) {
                System.out.println("ERROR!");
                println "Data File: ${dataFile} does not exist";
                System.exit(-1);
            }

            XsltTransform xslTransformer = new XsltTransform();
            xslTransformer.transform(null, new FileInputStream(xslFile), new FileInputStream(dataFile), System.out, [:]);

        } catch (Exception e) {
            System.out.println("ERROR!");
            e.printStackTrace(System.err);
            System.exit(-1);
        }
    }
}
