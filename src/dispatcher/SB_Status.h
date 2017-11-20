/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher - Status
*/

#include <iostream>
#include <string>

using namespace std;
class SB_Status
{
  private:
    string m_action;
    string renderPair(string name,string action);
    void populate();
  public:
    SB_Status(string action);
    string toXml(string transactionId="Not given");
};
