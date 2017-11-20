/*
 * Original file generated in 2013 by Grails v2.2.1 under the Apache 2 License.
 * Modifications are Copyright 2013-2016 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
grails.servlet.version = "2.5" // Change depending on target container compliance (2.5 or 3.0)
grails.project.class.dir = "target/classes"
grails.project.test.class.dir = "target/test-classes"
grails.project.test.reports.dir = "target/test-reports"
grails.project.target.level = 1.6
grails.project.source.level = 1.6
grails.project.plugins.dir = System.getenv("GRAILS_DEP_HOME") + "/plugins"
grails.reload.enabled = true
grails.auto.recompile = true
grails.dependency.cache.dir = System.getenv("GRAILS_DEP_HOME") + "/dependencies"
//grails.project.war.file = "target/${appName}-${appVersion}.war"

grails.project.fork = [
    // configure settings for compilation JVM, note that if you alter the Groovy version forked compilation is required
    //  compile: [maxMemory: 256, minMemory: 64, debug: false, maxPerm: 256, daemon:true],

    // configure settings for the test-app JVM, uses the daemon by default
    test: [maxMemory: 768, minMemory: 64, debug: false, maxPerm: 256, daemon:true],
    // configure settings for the run-app JVM
    run: [maxMemory: 768, minMemory: 64, debug: false, maxPerm: 256, forkReserve:false],
    // configure settings for the run-war JVM
    war: [maxMemory: 768, minMemory: 64, debug: false, maxPerm: 256, forkReserve:false],
    // configure settings for the Console UI JVM
    console: [maxMemory: 768, minMemory: 64, debug: false, maxPerm: 256]
]

grails.project.dependency.resolver = "ivy"
grails.project.dependency.resolution = {
    // inherit Grails' default dependencies
    inherits("global") {
        // specify dependency exclusions here; for example, uncomment this to disable ehcache:
        // excludes 'ehcache'
        excludes 'h2'
        excludes 'c3p0'
        excludes ([name:'quartz', group:'org.opensymphony.quartz'])
    }    
    log "warn" // log level of Ivy resolver, either 'error', 'warn', 'info', 'debug' or 'verbose'
    checksums true // Whether to verify checksums on resolve
    legacyResolve false // whether to do a secondary resolve on plugin installation, not advised and here for backwards compatibility

    repositories {
        inherits true // Whether to inherit repository definitions from plugins

        grailsPlugins()
        grailsHome()
        mavenLocal()
        grailsCentral()
        mavenCentral()

        // uncomment these (or add new ones) to enable remote dependency resolution from public Maven repositories
        //mavenRepo "http://snapshots.repository.codehaus.org"
        //mavenRepo "http://repository.codehaus.org"
        //mavenRepo "http://download.java.net/maven/2/"
        //mavenRepo "http://repository.jboss.com/maven2/"
        mavenRepo "https://repo.grails.org/grails/plugins"
    }

    dependencies {
        // specify dependencies here under either 'build', 'compile', 'runtime', 'test' or 'provided' scopes e.g.
        runtime 'hsqldb:hsqldb:1.8.0.10'
        runtime 'commons-cli:commons-cli:1.2'
        build 'org.apache.ant:ant:1.9.2'
        compile 'org.apache.tomcat.embed:tomcat-embed-logging-log4j:7.0.52'
    }

    plugins {
        runtime ":resources:1.2.7"
        compile (":quartz:1.0.2")
        //runtime ":database-migration:1.3.2"
        //compile ':cache:1.0.1'

//        runtime   ":jquery:1.11.0.2"
        runtime   ":jquery:1.8.3"
        runtime (":hibernate:3.6.10.10") { 
            excludes "hibernate-jpa-2.0-api"
        }
        compile   (":shiro:1.1.4") {
            excludes "servlet-api"
        }
        compile   (":webflow:2.0.8.1") {
            excludes "javassist"
        }
        build     ":tomcat:7.0.52.1"
    }
}
