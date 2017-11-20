/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

dataSource {
    pooled = true
    driverClassName = "org.hsqldb.jdbcDriver"
    username = "sa"
    password = ""
}

dataSource_memory {
    pooled = true
    driverClassName = "org.hsqldb.jdbcDriver"
    username = "sa"
    password = ""
}



hibernate {
    cache.use_second_level_cache = true
    cache.use_query_cache = false
    cache.region.factory_class = 'net.sf.ehcache.hibernate.EhCacheRegionFactory' // Hibernate 3
//    cache.region.factory_class = 'org.hibernate.cache.ehcache.EhCacheRegionFactory' // Hibernate 4
    singleSession = true // configure OSIV singleSession mode
}

// environment specific settings
environments {
    development {
        dataSource {
            dbCreate = "update"
            url = "jdbc:hsqldb:file:instance;shutdown=true"
        }		
        dataSource_memory {
            dbCreate = "create-drop"
            url = "jdbc:hsqldb:mem:memDB;shutdown=true"
        }     
    }
    test {
        dataSource {
            dbCreate = "update"
            // url = "jdbc:hsqldb:mem:testDb"
            url = "jdbc:hsqldb:file:/var/lib/oslockdown/console/dbtest/instance;shutdown=true"
        }
        dataSource_memory {
            dbCreate = "create-drop"
            url = "jdbc:hsqldb:mem:memDB;shutdown=true"
        }     
    }
    production {
        dataSource {
            dbCreate = "update"
            url = "jdbc:hsqldb:file:/var/lib/oslockdown/console/db/instance;shutdown=true"
        }
        dataSource_memory {
            dbCreate = "create-drop"
            url = "jdbc:hsqldb:mem:memDB;shutdown=true"
        }     
    }
}
