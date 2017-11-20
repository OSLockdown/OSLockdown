/*
 * Copyright 2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
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

// FOP
import org.apache.fop.apps.FOUserAgent;
import org.apache.fop.apps.Fop;
import org.apache.fop.apps.FOPException;
import org.apache.fop.apps.FopFactory;
import org.apache.fop.apps.FormattingResults;
import org.apache.fop.apps.MimeConstants;
import org.apache.fop.apps.PageSequenceResults;

import org.apache.log4j.Logger;

/**
 * This class demonstrates the conversion of an FO file to PDF using FOP.
 */
public class SbReportTransformer {
	
    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.xsl.SbReportTransformer");

    // configure fopFactory as desired
    private static FopFactory fopFactory = FopFactory.newInstance();
    
    // transformer factory
    private static TransformerFactory transformerFactory;
    static {
    	transformerFactory = TransformerFactory.newInstance();
        transformerFactory.setErrorListener(new SbXslErrorListener());
    }
    
    /**
     * Transform the input source to the output location using the xsl stream
     * @param xslStream
     * @param inputSource
     * @param outputLocation
     */
    public static void transform(URIResolver resolver,
        InputStream xslStream,
        InputStream inputSource,
        OutputStream outputLocation,
        Map parameterMap)
    throws Exception {
        
    	// Set the uri resolver
        URIResolver uriResolver = resolver;
    	if ( !resolver ) {
            uriResolver = new SbURIResolver();
    	}    	
        transformerFactory.setURIResolver(uriResolver);
    	 
   	// establish the transformer
        def transformer = transformerFactory.newTransformer(new StreamSource(xslStream));

        // set the parameters on the transformer if necessary
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
     * Converts an FO file to a PDF file using FOP
     * @param fo the FO file
     * @param pdf the target PDF file
     * @throws IOException In case of an I/O problem
     * @throws FOPException In case of a FOP problem
     */
    public static void convertFO2PDF(InputStream foSource, OutputStream outputStream) 
    throws IOException, FOPException {
        
        OutputStream out = null;
        
        try {
            FOUserAgent foUserAgent = fopFactory.newFOUserAgent();
            // configure foUserAgent as desired
            
            // add encryption 
            /*
            foUserAgent.getRendererOptions().put("encryption-params", new PDFEncryptionParams(
            null, "password", false, false, true, true));
             */

    
            // Setup output stream.  Note: Using BufferedOutputStream
            // for performance reasons (helpful with FileOutputStreams).            
            out = new BufferedOutputStream(outputStream);

            // Construct fop with desired output format
            Fop fop = fopFactory.newFop(MimeConstants.MIME_PDF, foUserAgent, out);

            // Setup JAXP using identity transformer            
            Transformer transformer = transformerFactory.newTransformer();
            
            // Setup input stream
            Source src = new StreamSource(foSource);

            // Resulting SAX events (the generated FO) must be piped through to FOP
            Result res = new SAXResult(fop.getDefaultHandler());
            
            // Start XSLT transformation and FOP processing
            transformer.transform(src, res);
            
            // Result processing
            FormattingResults foResults = fop.getResults();
            List pageSequences = foResults.getPageSequences();
            for (Iterator it = pageSequences.iterator(); it.hasNext();) {
                PageSequenceResults pageSequenceResults = (PageSequenceResults)it.next();
                m_log.info("PageSequence " 
                    + (String.valueOf(pageSequenceResults.getID()).length() > 0
                        ? pageSequenceResults.getID() : "<no id>")
                    + " generated " + pageSequenceResults.getPageCount() + " pages.");
            }
            m_log.info("Generated " + foResults.getPageCount() + " pages in total.");

        } 
        catch (Exception e) {
            m_log.error("Unable to convert fo -> pdf",e);            
        }
        finally {
            out.close();
        }
        
    }



    /**
     * Main method.
     * @param args command-line arguments
     */
    public static void main(String[] args) {
        try {
            System.out.println("FOP PdfTransformer\n");
            System.out.println("Preparing...");
            
            //Setup directories
            File baseDir = new File(".");
            File outDir = new File(baseDir, "out");
            outDir.mkdirs();

            //Setup input and output files            
            File fofile = new File(args[0]);
            println "Input File: ${fofile.absolutePath}";
            File pdffile = new File(outDir, "ResultFO2PDF.pdf");
            println "Output File: ${pdffile.absolutePath}";

            System.out.println("Input: XSL-FO (" + fofile + ")");
            System.out.println("Output: PDF (" + pdffile + ")");
            System.out.println();
            System.out.println("Transforming...");
            
            SbReportTransformer app = new SbReportTransformer();
            app.convertFO2PDF(fofile, pdffile);
            
            System.out.println("Success!");
        } catch (Exception e) {
            e.printStackTrace(System.err);
            System.exit(-1);
        }
    }
}
