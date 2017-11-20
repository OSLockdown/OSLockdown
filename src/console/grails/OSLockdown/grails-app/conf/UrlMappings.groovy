/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
class UrlMappings {
    static mappings = {
      "/$controller/$action?/$id?"{
	      constraints {
			 // apply constraints here			 
			 controller(matches:/(?!services).+|services.+/)
		  }
	  }
      
      "/" {
    	  controller = "dashboard";
    	  // (view:"/index")
      }
      
      "404"(controller:'dashboard',action:'notfound')
      
      // "500"(controller:'dashboard',action:'error')
      
	  "500"(view:'/error')	  
	  
	}
}
