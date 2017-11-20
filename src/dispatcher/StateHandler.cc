/**
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown State Handler Class
*
* Simple class to retrieve information such as last action from
* the OSLockdown state file.
*
*
* Test Build:
*   g++ -o test -I../include -I/usr/include/libxml2 -DGLIBCXX_FORCE_NEW -lxml2 StateHandler.cc
*
*/
#include "StateHandler.h"

/**
 * Private Methods
 */
bool
StateHandler::stateFileExists() {
  assert(filename_.c_str());
  struct stat file_info;
  int retval;
  retval = stat(filename_.c_str(), &file_info);

  if (retval == 0)
    return true;
  else
    return false;
};

/** 
 * Read state file xml and set private variables
*/
void
StateHandler::load() {
  xmlDoc *doc;
  bool retval;
  xmlXPathObjectPtr xpathObj;
  xmlXPathContextPtr xpathCtx;
  xmlNodeSetPtr nodes;
  xmlNodePtr node;
  xmlChar *p;
  const xmlChar *xpathExpression;
  int size;
  // Set private variables
  filename_ = APPLICATION_STATEFILE;
  last_action_ = "-";
  last_action_time_ = "-";
  retval = this->stateFileExists();
  if (retval == true) {
    xmlInitParser();
    doc = xmlReadFile(filename_.c_str(), NULL, XML_PARSE_NOERROR);
    if (doc == NULL) {
      return;
    }
    xpathCtx = xmlXPathNewContext(doc);
    if (xpathCtx == NULL) {
      xmlXPathFreeContext(xpathCtx);
      return;
    }
    xpathExpression =
      reinterpret_cast < const xmlChar *>("/ModuleStates/info");
    xpathObj = xmlXPathEvalExpression(xpathExpression, xpathCtx);
    if (xpathObj == NULL) {
      return;
    }
    nodes = xpathObj->nodesetval;
    size = (nodes) ? nodes->nodeNr : 0;
    if (size == 0) {
      xmlXPathFreeObject(xpathObj);
      xmlXPathFreeContext(xpathCtx);
      xmlCleanupParser();
      xmlFreeDoc(doc);
      return;
    }
    node = nodes->nodeTab[0];
    if (xmlHasProp(node, (const xmlChar *) "lastAction")) {
      p = xmlGetProp(node, (const xmlChar *) "lastAction");
      this->last_action_ = reinterpret_cast < char *>(p);
      xmlFree(p);
    }
    if (xmlHasProp(node, (const xmlChar *) "lastActionTime")) {
      p = xmlGetProp(node, (const xmlChar *) "lastActionTime");
      this->last_action_time_ = reinterpret_cast < char *>(p);
      xmlFree(p);
    }
    // To avoid memory leak reports from valgrind, we must call
    // xml Free functions in the following order:
    xmlXPathFreeObject(xpathObj);
    xmlXPathFreeContext(xpathCtx);
    xmlFreeDoc(doc);
    xmlCleanupParser();
  }
};

/**
 * Public Methods
 */
StateHandler::StateHandler() {
  this->load();
}

void
StateHandler::reload() {
  this->load();
}
std::string StateHandler::getLastAction() {
  this->reload();
  return this->last_action_;
};
std::string StateHandler::getLastActionTime() {
  this->reload();
  return this->last_action_time_;
};


/**
 *  Main - for testing purposes only
 */
int
main() {
  StateHandler *
    stateMgr = new StateHandler();
  std::cout << stateMgr->getLastAction() << std::endl;
  std::cout << stateMgr->getLastActionTime() << std::endl;
  stateMgr->reload();
  delete
    stateMgr;
  return EXIT_SUCCESS;
}
