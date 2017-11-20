package com.trustedcs.sb.updatesb;
/*
 * Copyright (c) 2007-2014 Forcepoint LLC.
 * This file is released under the GPLv3 license.  
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
 * or visit https://www.gnu.org/licenses/gpl.html instead.
*/

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.OutputStream;
import java.io.InputStream;
import java.util.Collection;
import java.util.Date;
import java.util.Enumeration;
import java.util.Iterator;
import java.util.ArrayList;
import java.util.List;
import java.io.ByteArrayOutputStream;

import java.util.zip.*; 

public class Zipper {

    public static final int BUFFER = 4096;
    public int numFiles = 0;
    public List<String> fileList = new ArrayList<String>();

    public byte [] createZip(String fileBase, ArrayList<String> filesToGet, ArrayList<String> pkgsToGet) throws Exception {
                
        ByteArrayOutputStream byteStream = new ByteArrayOutputStream();
        
        ZipOutputStream out = new ZipOutputStream( byteStream );
        //  Set method to deflated to compress as well
        out.setMethod( ZipOutputStream.DEFLATED );
    
        byte data[] = new byte[ BUFFER ];
    
        numFiles = 0;
        for ( int i = 0; i < filesToGet.size(); i++ ){
            zipResource( fileBase, filesToGet.get(i), out, data, false);
        }
        int fileCount = pkgsToGet.size();
        for ( int i = 0; i < pkgsToGet.size(); i++ ){
            zipResource( fileBase, pkgsToGet.get(i), out, data, false);  // change terminal 'false' to 'true' to alter hierarchy for packages
        }
        out.close();
        return byteStream.toByteArray();
    }
    
    void zipResource( String fileBase, String fileToGet, ZipOutputStream out, byte data[], boolean flatten ) throws Exception
    {
        File resourceToZip = new File (fileBase + "/" + fileToGet);
        
        if( resourceToZip != null && resourceToZip.exists() ){

            if( resourceToZip.isFile() ){
            
                // Write resourceToZip into the .zip file    
                FileInputStream fi = new FileInputStream( resourceToZip );           
                BufferedInputStream origin = new BufferedInputStream( fi, BUFFER );            
                
                String zipName;
                
                if (flatten == true ) {
                    zipName = "packages/" + resourceToZip.getName();
                } else {
                    zipName = fileToGet;
                }                                                
		ZipEntry entry = new ZipEntry( zipName );
                out.putNextEntry( entry );
    
                int count;
                while( ( count = origin.read( data, 0, BUFFER ) ) != -1 ){
                    out.write( data, 0, count );
                }
                origin.close();
                fileList.add(zipName);
                numFiles = numFiles + 1;
            }                        
            // resourceToZip is a directory. Recursively call zipResource() for all of its children.
            else {                
                File files[] = resourceToZip.listFiles();
                for ( int i = 0; i < files.length; i++ ) {

                    File childResourceToZip = files[ i ];
                    zipResource(fileBase,  new String (fileToGet + "/" + childResourceToZip.getName()), out, data, flatten );
                }
            }
        }
    }
}
