/*
 * Copyright 2011-2014 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
package com.trustedcs.sb.util

import org.apache.log4j.Logger;

import groovy.sql.Sql;
import groovy.sql.GroovyRowResult;
import grails.orm.PagedResultList;

/**
 *
 * @author kloyevsky
 */
class SBGSQLUtil {

    private static Logger m_log = Logger.getLogger("com.trustedcs.sb.util.SBGSQLUtil");

    public static def executeSelectWithIdGSQL( def dataSource, String sqlString, Class clazz ){
        // Don't do pagination
        return executeSelectWithIdGSQL( dataSource, sqlString, clazz, null, null )
    }

    /**
    * Executes SQL passed in as sqlString and returns the domain objects corresponding to the ids.
    * sqlString *SHOULD* :
    *   a. be a select statement
    *   b. have an id column selected as part of the select, and the id should be the id of the domain object
    * If BOTH String maxPerPage, String offset are set, uses them and returns an instance of PagedResultList
    * with domain objects (ie. pagination support). Otherwise, returns an ArrayList containing the domain objects.
    *
    * Note: if pagination support is not needed (ie. either or both maxPerPage and offset are null) this method
    * will not limit the number of objects returned. The caller should append to the end of sqlString "limit X" to
    * limit the number of items returned to X.
    *
    * @param dataSource - must be passed as can only have them in Controller and Bootstrap.
    * @param sqlString - sql string to be executed
    * @param clazz - the name of the domain object Class that sqlString executed on; getAll() will be invoked on it
    * @param maxPerPage - the maximum number of items to be on the page [pagination parameter]
    * @param offset - the offset (index of the first item on the requested page) [pagination parameter]
    */
    public static def executeSelectWithIdGSQL( def dataSource, String sqlString, Class clazz, String maxPerPage, String offset ) {

        def selectResultList
        def sqlObject
        
        try {
            sqlObject = new Sql( dataSource ) 

            def rows = sqlObject.rows( sqlString )
            if( rows.size() > 0 )
            {
                // Grab ids from the result of the query (that *SHOULD* have an id element as part of the select)
                def idsList = rows.collect{ it.id }

                // Invoke getAll() on the Class passing in the ids, which will return the domain object instances
                // in the order in which they are on the idsList
                selectResultList = clazz.getAll( idsList )
            }
            else {
                selectResultList = []
            }
        }
        catch( Exception e ){
            m_log.error( "Got an error using GSQL. ", e )
        }
        finally {
            if( sqlObject ) {
                sqlObject.close()
            }
        }

        // Pagination support was requested. The caller expects the returned object to be PagedResultList
        // even if selectResultList was empty or null.
        if( maxPerPage && offset ){

            if( selectResultList ){

                int selectResultListSize = selectResultList.size()

                int maxPerPageAsInt
                try {
                    maxPerPageAsInt = Integer.parseInt( maxPerPage )
                }
                catch( Exception e ){
                    maxPerPageAsInt = 25;
                }                

                // Can only return a page, if there are more total elements than the page size.
                // If there are less, then all elements will be returned (and will be less than the pageSize (i.e. maxPerPage))
                if( selectResultListSize > maxPerPageAsInt )
                {
                    // offset is the index of the first element in the requested *page* (not the index of the
                    // page itself); ex. max=2, so offsets will be :0, 2, 4, etc. and not 0, 1, 2, etc.
                    int firstIndex
                    try {
                        firstIndex = Integer.parseInt( offset )
                    }
                    catch( Exception e ){
                        firstIndex = 0
                    }

                    // If firstIndex is greater than or equal to selectResultListSize, this is invalid condition.
                    // Adjust firstIndex to point to the *last* page (ie. be equal to the index of the first element in the last page)
                    if( firstIndex >= selectResultListSize ){
                        firstIndex = selectResultListSize - ( selectResultListSize % maxPerPageAsInt )
                    }

                    // lastIndex is the index of the last element of the requested *page* assuming max elements.
                    // If there are less then max per-page elements on the requested *page* then need to adjust lastIndex.
                    // This could happen only on the last page.
                    int lastIndex = firstIndex + ( maxPerPageAsInt - 1 )

                    // Adjust lastIndex at selectResultListSize - 1 (the requested *page* has less
                    // than max elements in it).
                    if( lastIndex /* last index from page calc */ > ( selectResultListSize - 1 ) /* last index from selectResultList */)
                    {
                        lastIndex = selectResultListSize - 1
                    }

                    // pageResult is the list containing the number of items within the *page* that user requested
                    // (if this page is the last page, then it might contain less than max items)
                    def pageResult = selectResultList [ firstIndex..lastIndex ]

//                    selectResultList = new PagedResultList( pageResult, selectResultListSize )
                    selectResultList = pageResult
                }
                else
                {
//                    selectResultList = new PagedResultList( selectResultList )
                }
            }
            else {
//                selectResultList = new PagedResultList( selectResultList == null ? [] : selectResultList )
            }
        }

        if( !selectResultList ){
            selectResultList = []
        }

        return selectResultList
    }
}

