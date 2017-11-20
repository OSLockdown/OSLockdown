/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher
*/

#include <iostream>
#include <string>

using namespace std;
class SB_Update
{
  private:
    bool m_updateRequired;
    string m_logText;
  public:
    bool updateRequired();
    SB_Update(string version = "1.2.3");
    string toXml(string transactionId="Not given");
    string logText();
};
