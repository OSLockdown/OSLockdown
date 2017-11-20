/**
 *
* Copyright (c) 2007-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
 *
 */
package com.trustedcs.sb.updatesb;

//import com.trustedcs.sb.services.sei.UpdateSBQuery;
//import com.trustedcs.sb.services.sei.UpdateSBResponse;
import com.trustedcs.sb.services.sei.PackageInfo;
import org.apache.log4j.Logger;
import java.util.Arrays;
import java.util.List;
import java.util.ArrayList;
import java.io.File;


public class UpdateSBEngine {
	
	// the singleton instance
	static UpdateSBEngine m_instance= null;
    private final static Logger m_log = Logger.getLogger("com.trustedcs.sb.updatesb.UpdateSBEngine");
		
	/**
	 * Private Constructor for the singleton instance
	 */
	private UpdateSBEngine() {
		
	}
	
	/**
	 * Singleton get method
	 * @return the singleton instance
	 */
	public static UpdateSBEngine getInstance() {
		if ( m_instance == null ) {
			m_instance = new UpdateSBEngine();
		}
		return m_instance;
	}
 
    private boolean AddFileNames(ArrayList<String> currentList, String fileBase, String dirName)
    {
//      System.out.println ("Adding files from "+ fileBase + "/" + dirName);
      boolean foundFiles = false;
      
      File thisdir = new File (fileBase + "/" + dirName);
      
      if (thisdir.isDirectory())
      {
//        System.out.println(thisdir.getName() + " is a directory...");
        for (File child : thisdir.listFiles()) 
        {
//          System.out.println( "  Checking  " + child.getName());
          if (! child.isDirectory() && ! child.getName().contains("console"))
          {
            String newName = new String (dirName + "/" + child.getName());
            currentList.add(newName);
	    foundFiles = true;
          }
        } 
      }
      else
      {
//          System.out.println( thisdir.getName() + " is not a directory");
      }
//      System.out.println ("Adding files from "+ dirName + " - found files = "+ foundFiles);
      return foundFiles ; 
    }

    public byte[] listPackages(String hostName, String pkgRoot, String cpeShortName, String majorVersion,  String minorVersion, String arch, boolean withDocs) {
        String fileBase;
        ArrayList<String> filesToGet = new ArrayList<String> ();
        ArrayList<String> pkgsToGet = new ArrayList<String> ();
        
        fileBase = "/var/lib/oslockdown/files/ClientUpdates";
        
        
        // Now we setup an array of files/directories to include stuff from.  This list is *only* of files, so we need to call some helpers to get
        // recursive filelists... 
        
        filesToGet.add("LICENSE");
        filesToGet.add("SB_Remove");
        filesToGet.add("SB_Install");

        // Ok, now get recursive lists from the following, if the exist
        filesToGet.add("Attributions");
        filesToGet.add("toolupdates");
//        System.out.println("Docs required = " + withDocs);
        if (withDocs == true) {
            filesToGet.add("docs");
        }
        
        // Now go get *specifically* the packages that were requested.  We know the Console is the [RPMS|PKG]/noach directory, so explicitly check and remove that
        // entry if it shows up.  We're only updating Enterprise Client packages.
        
        String updateDetails = cpeShortName+ "-"+ majorVersion + "-" + arch + "docs=" + withDocs;  
        
        m_log.info("AUTOUPDATE - request received from "+ hostName + " " + updateDetails);
        
	// Ok, commercial autoupdate provides a yum-like structure. Open source provides a directory for each 
	// version for which we have info, based on the cpeShortname+major+arch
	// choose wisely ;)
	
        AddFileNames(pkgsToGet, fileBase ,  pkgRoot + "/"+ "noarch" ) ;
        AddFileNames(pkgsToGet, fileBase ,  pkgRoot + "/"+ cpeShortName + "/" + "noarch");
        AddFileNames(pkgsToGet, fileBase ,  pkgRoot + "/"+ cpeShortName + "/" + majorVersion + "/" + "noarch");
        AddFileNames(pkgsToGet, fileBase ,  pkgRoot + "/"+ cpeShortName + "/" + majorVersion + "/" + arch);
        AddFileNames(pkgsToGet, fileBase ,  pkgRoot + "/"+ cpeShortName + "/" + majorVersion + "/" + arch);
        AddFileNames(pkgsToGet, fileBase ,  "Packages" + "/"+ cpeShortName + "-" + majorVersion + "-" + arch);
        
        Zipper zipper = new Zipper();

//        for (int i = 0; i< filesToGet.size();i++) {
//          System.out.println(i+ " -> " + filesToGet.get(i));
//          m_log.info("AUTOUPDATE - "+ hostName + " " + updateDetails + " queuing --- " + filesToGet.get(i));
//        }
//        for (int i = 0; i< pkgsToGet.size();i++) {
//          System.out.println(i+ " -> " + pkgsToGet.get(i));
//          m_log.info("AUTOUPDATE - "+ hostName + " " + updateDetails + " queuing --- " + pkgsToGet.get(i));
//        }
        byte [] zipData=null;
        
        try {
            zipData = zipper.createZip(fileBase, filesToGet, pkgsToGet);
	    for (int i = 0 ; i< zipper.fileList.size(); i++) {
	        m_log.info("AUTOUPDATE - " + hostName + " sent " + zipper.fileList.get(i));
	    }
	}
        catch (Exception e) {
            zipData = null;
            if (zipper.numFiles == 0)  {
                m_log.error("AUTOUPDATE - No datafiles to send from "+fileBase+" - returning 'empty' file"); 
            }
            else {
                m_log.error("AUTOUPDATE - " + e.getMessage()); 
            }
        }
        return zipData;
        
    }
	
}
