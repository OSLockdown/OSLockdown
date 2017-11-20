/*
 * Original file generated 2014 by Grails v2.3.7 under the Apache 2 License.
 * Modifications are Copyright 2014 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
modules = {

    application {
        dependsOn 'jquery' 
 	resource url:'/js/application.js'
	resource url:'/js/taconite/taconite-client.js'
	resource url:'/js/taconite/taconite-parser.js'
	resource url:'/js/tcs/common.js'
	resource url:'/js/jquery/jquery.corners.js'
    }
    
    showedit {
        dependsOn 'application'
//	resource url:'/js/json2.js'
	resource url:'/js/jquery/jquery.blockUI.js'
	resource url:'/js/tcs/detach.js'
    }
    
    MyPick {
	resource url:'/js/tcs/MyPick.js'
    }

    tcs_sbmodules{
        dependsOn 'application' 
    	resource url:'/js/tcs/sbmodules.js'
    }
}
