/*
 * Copyright 2011 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package com.trustedcs.sb.util

/**
 *
 * @author kloyevsky
 */
class SBJavaToJavaScriptUtil {
	
    // Assumes that Map javaMap is Map<String,String>.
    // Return a String corresponding to a JSON string representing a JavaScript map where keys and values are String
    // (i.e. key and values are Strings and are enclosed in double-quotes, and each key and value is separated by a colon (:)
    // as that is the JavaScript syntax for String maps), handles an empty javaMap as well. The returned String can then be
    // used in JavaScript as if it were a JavaScript map, by declaring the result of this method call in a
    // JavaScript var variable, like the following :
    //      ...
    //                                                                  <!-- notificationTemplateInstance.dataMap is a JavaMap -->
    //      var localDataMap = ${SBJavaToJavaScriptUtil.convertJavaMapToJavaScriptMap(notificationTemplateInstance.dataMap)};
    //      ...
    //      <!-- Use "var localDataMap" as a JavaScript map -->
    //      for (var key in localDataMap ) {
    //          alert(" key ["+key+"] theDataMap[key] ["+localDataMap[key]+"]");
    //      }
    //
    static String convertJavaMapToJavaScriptMap( Map javaMap ){
        String result
        if( javaMap ){
            StringBuffer buffer = new StringBuffer();
            buffer.append( "{" );

            // This assumes value is a String. If it were an integer/long/double/array etc. double quotes on value
            // are not needed.
            javaMap.each { key, value ->
                buffer.append( "\"" + key + "\":\"" + value + "\"," )
            }
            buffer.deleteCharAt( buffer.length() - 1 )
            buffer.append( "}" );
            result = buffer.toString()
        } else{
            // If passed javaMap is null, return a String corresponding to an empty JavaScript map
            result = "{}"
        }
        return result
    }

    // Assumption is that javaScriptJSONString contains only JSON string representing {keyString_1:valueString_1,keyString_2:valueString_2, ...}
    // format only AND that neither keyStrings not valueString contain contain either commas (",") or semi-colon (":") (i.e. these delimiters
    // are used to delimit {key,value} pairs and keys and values within the pair respectively)
    static Map convertJavaScriptMapToJavaMap( String javaScriptJSONString ){
        Map result = [:]
        if( javaScriptJSONString ){
            // Just strip the enclosing {} and force into a literal mapp
            javaScriptJSONString = javaScriptJSONString[1..javaScriptJSONString.length()-2]

            String [] mapEntryArray = javaScriptJSONString.split( "," )
            for( int i = 0; i < mapEntryArray.length; i++ ){
                String mapEntryString = mapEntryArray[ i ]
                String [] keyAndValueArray = mapEntryString.split( ":" )
                String keyWithoutDoubleQuotes = keyAndValueArray[0][1..keyAndValueArray[0].length()-2]
                String valueWithoutDoubleQuotes = keyAndValueArray[1][1..keyAndValueArray[1].length()-2]
                result[ keyWithoutDoubleQuotes ] = valueWithoutDoubleQuotes
            }
        }
        return result
    }

    // Assumption is that javaScriptJSONString contains only JSON string representing a list ex. [1,22,654]
    static List convertJavaScriptListToJavaList( String javaScriptJSONString ){
        List result = []
        if( javaScriptJSONString && javaScriptJSONString[0] == "[" && javaScriptJSONString[ javaScriptJSONString.size() - 1 ] == "]" ){

            // Strip the enclosing double-quotes ...
            javaScriptJSONString = javaScriptJSONString[1..javaScriptJSONString.size() - 2]

            // ... and split the remainder on the comma
            if( javaScriptJSONString ){
                String [] contentsAsArrayOfStrings = javaScriptJSONString.split( "," )
                if( contentsAsArrayOfStrings ){
                    contentsAsArrayOfStrings.each {
                        result << it
                    }
                }
            }
        }
        return result
    }
}

