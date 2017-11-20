# OS Lockdown
Welcome to the 'OS Lockdown' main project page.  OS Lockdown is the open source version of the  Forcepoint legacy commercial software package known as 'Security Blanket'.  OS Lockdown is being made available in the hopes that it will be embraced by those currently using the legacy Security Blanket product, new (OS Lockdown) users, and security community developers as excited about this technology as we are.

In brief, OS Lockdown is a software package that helps you harden various Linux and Solaris operating systems.  OS Lockdown provides a library of 339 'Modules', that can be combined together into a 'Profile'.  Many Modules have options to fine-tune their actions (for example, how long should a password be?).  This Profile may then be used to assess how well a box complies with the Profile, try to remediate any discrepancies, or undo the last set of remediations made by OS Lockdown.  Note that some Modules are 'scan-only', with no remediation or undo capability.  An example use of a Profile would be a Profile based on the DISA STIGs, or other industry standards.  

Most interactions are done using the provided web Console application.  This Console operates in either 'Standalone' or 'Enterprise' mode.  The Standalone Console limits actions to the local box, where the Enterprise mode provides extra feature to control many 'Client' boxes remotely.  Communications are over https, with either self-signed certificates or certificates signed by an external CA.  Multiple users can be created with different roles  and allowed actions.   Actions can be automated to run at specified times (no more than once a day), and important results can be fed into a SEIM tool CEF (Common Event Format) messages via syslog.

At this moment OS Lockdown supports the same set of operating systems as Security Blanket v414b:
  * Intel based platforms:
    * Red Hat Enterprise Linux 4/5/6 (and equivalents from CentOS, Oracle, and Scientific Linux)
    * SUSE 10/11, openSUSE 10/11
    * Fedora 10/11/12/13
    * Solaris 10

  * SPARC based platforms:
    * Solaris 10

  * IBM zSeries Linux:
    * Red Hat Enterprise Linux 5/6
    * SUSE 10/11


The initial code release (see the 'BUILDING' step below for more info), is a drop-in replacement for Security Blanket 4.1.4b, release in May 2016.  No testing has been done with versions other than SB4.1.4b.  See the 'Changes_from_SB4.1.4b.txt' file for a detailed list of the functional changes, but in brief:
  * all node-locking, Client count limitations (Enterprise only), and time limitations have been removed
  * easy upgrade from 'Standalone' to 'Enterprise' Console mode.  
  * package building now requires Tomcat 7 instead of Tomcat 6
  * choice of SHA-256 (where supported) for SSL certificate creation

Please note moving forward that the initial release of OS Lockdown will be preserved (either as a protected 'master' branch, or a clearly marked protected branch).  

## LICENSING:
These source code packages are mostly licensed under a combination of the GPLv3, ApacheV2, and GPLv3/ApacheV2 licenses.  Three Java script libraries are included with the Console unit that are under the Apache V2, or dual licnsed MIT/GPLv2.  They have been included due to extensive modifications (Taconite), or to these libraries not having an official 'home' to download them from (jquery-corners.js v0.3 and jquery-blockui.js V2.37).  Additional notes on licensing are in the 'LICENSES.txt' file.  We suggest that contributions are also released under either the GPLv3 or ApacheV2 licenses.  Note that additional packages will need to be downloaded to build OS Lockdown and it it your responsibility to comply with any licenses from these packages.

## BUILDING:
Please refer to the 'BUILDING.txt' file for directions on building OS Lockdown.  Internet access is almost certainly required the first time you build OS Lockdown on a particular box so that package prerequisites can be downloaded.  Note that there is one set of prerequisites that need to be manually downloaded prior to doing a build of OS Lockdown, and another set that will be downloaded automatically when control is passed to the Grails web framework to build the Console web application  These prequisites should only be downloaded once on each box where OS Lockdown is built.  

## CONTRIBUTING TO OS LOCKDOWN
As this is a new open source project, please keep the following themes in mind, until a more concrete 'Code of Conduct' is put in place:
  - Respect each other.
  - There is very likely a reason something was done a certain way.  Please ask if you see something that doesn't appear to make sense.  There may well be better ways of doing something.
 
Enjoy!
