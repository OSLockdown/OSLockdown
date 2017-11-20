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
class SB_Info
{
  private:
    string m_reportDirStats;
    string m_ClientVersion;
    string m_Nodename;
    string m_Distro;
    string m_Kernel;
    unsigned long m_Uptime;
    string m_Arch;
    string m_ProcCount;
    string m_LoadAvg;
    string m_Memory;
    string m_assessments;
    string m_apply_rpts;
    string m_undo_rpts;
    string m_baselines;
    string m_corehours;
    string m_maxload;
    string m_baseline_comps;
    string m_assessment_comps;
    string MakeTimeLengthString();
    string renderPair(string name,string text);
    void countFilesInDir(string dname,string suffix,string label,string &result);
    bool get_release(const char *relfile);
    void ReportDirStats();
    void populate();
    void getLoadTimeRestrictions();
  public:
    SB_Info();
    string toXml(string transactionId="Not given");
};
