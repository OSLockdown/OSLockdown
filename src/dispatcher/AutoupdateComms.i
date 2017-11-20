/*
* Copyright (c) 2009-2015 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*/

%module AutoupdateComms
%include "stl.i"
%include "std_string.i"
%include "typemaps.i"
%include "cdata.i"
%{
extern std::string getData();
extern int getReturnCode();
extern void getRemoteFile(std::string serviceURL,std::string hostname, std::string pkgRoot, std::string cpeShortName, std::string majorVersion, std::string minorVersion, std::string arch, bool withDocs);
extern void sendNotification(std::string serviceURL, std::string notificationText, std::string transactionId, bool isOK );
%}
extern std::string getData();
extern int getReturnCode();
extern void getRemoteFile(std::string serviceURL,std::string hostname, std::string pkgRoot, std::string cpeShortName, std::string majorVersion, std::string minorVersion, std::string arch, bool withDocs);
extern void sendNotification(std::string serviceURL, std::string notificationText, std::string transactionId, bool isOK );
