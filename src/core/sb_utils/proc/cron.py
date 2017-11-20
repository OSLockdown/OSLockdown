#!/usr/bin/python

#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#
# Cron Job Management

import datetime
import os
import sha
import re
import sys
import shutil

sys.path.append("/usr/share/oslockdown")
import TCSLogger
from sb_utils.file.FileManip import move_file_over


##################################
# Module Attributes (Constants)
##################################
CRON_USER          = "root"
SB_COMMENT_IDENT   = "#OSLOCKDOWN CREATED" #TODO: possibly append date


class CronError(Exception): pass

#################################
# Report Generator
#################################
class Cron(object):

    def __init__(self, sb_scheduled=True, event_identifier=SB_COMMENT_IDENT):
        global CRON_USER
        self.module_name     = "Cron"
        self.identifier_str  = event_identifier
        self.__target_file   = "/etc/crontab"
        self.__temp_file     = self.__target_file + '.new'

        self.__user          = CRON_USER
        self.__sb_scheduled  = sb_scheduled
    
    def __getitem__(self, index):
        """
        Overriden bracket operator for Cron object
        """
        
        return self.list()[index]
    
    def __parse_cron_date(self, date_str):
        """
        Parses the cron date string and returns date object
        """
        # minute hour dom month dow user cmd
        timedict = {}
        
        (timedict['min'], timedict['hour'], timedict['dayofmonth'], \
        timedict['month'], timedict['dayofweek']) = date_str.split()[:5]
        
        for key in timedict.keys():
            if not timedict[key].isdigit():
                del timedict[key]
        
        return timedict
    
    def __create_cron_date(self, timedict=None):
        """
        Return properly formated date string for cron
        """
        
        string_list = []
        param_list = ['min', 'hour', 'dayofmonth', 'month', 'dayofweek']
        
        if not timedict:
            timedict = {}
        
        #Create basis for string
        for param in param_list:
            if timedict.has_key(param):
                string_list.append(str(timedict[param]))
            else:
                string_list.append('*')
        
        return ' '.join(string_list)
    
    def list(self):
        """
        Returns list of tuples containing scheduled tasks with run date.
        Optional boolean sb_scheduled checks to see if task has been scheduled
        by OS Lockdown
        """
              
        if self.__sb_scheduled:
            #TODO: current regular expression will die if we have # symbol
            #      as part of 
            regex = re.compile("^\s*([^#\s]+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.+?)%s$" \
                               % self.identifier_str)
        else:
            regex = re.compile("^\s*([^#\s]+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.+)$")

        results = []
        
        if os.path.exists(self.__target_file):
            crontab = open(self.__target_file, 'r')
            
            for line in crontab:
                match = regex.match(line)
                if match:
                    results.append(line)
            
            crontab.close()
    
        return results
    
    def __len__(self):
        """
        Return number of entries in crontab file
        """
        
        return len(self.list())
    
    def schedule_task(self, command, date_dict):
        """
        Schedules specified command at specified date
        date_dict has following format:
        date_dict = { 'min' = minutes as int or '*'
                      'hour' = hour as int or '*'
                      'dayofmonth' = dayofmonth as int or '*'
                      'month' = month as int or '*'
                      'dayofweek' = dayofweek as int or '*'
                    }
        """
               
        cron_entry =  "%s %s %s" % (self.__create_cron_date(date_dict), \
                                    self.__user, command)
        
        regex = re.compile("^\s*%s\s*(#.*)*$" % re.escape(cron_entry))
        
        #Open file and attempt to search if line already exists
        found = False
        
        if os.path.exists(self.__target_file):
            crontab = open(self.__target_file, 'r')
            crontab_temp = open(self.__temp_file, 'w')

            
            for line in crontab:
                match = regex.match(line)
                crontab_temp.write(line)
                
                if match:
                    found = True
                    
            if not found:
                crontab_temp.write(cron_entry + " %s\n" % self.identifier_str)
            
            crontab.close()
            crontab_temp.close()
            
            move_file_over(self.__temp_file,self.__target_file)
    
    def __delitem__(self, list_index):
        """
        Deletes the schedules task indicated by specified index
        """
        
        regex = re.compile("^%s$" % re.escape(self.list()[list_index]))
        
        #Open file and attempt to search if line already exists
        found = False
        
        if os.path.exists(self.__target_file):
            crontab = open(self.__target_file, 'r')
            crontab_temp = open(self.__temp_file, 'w')

            
            for line in crontab:
                match = regex.match(line)
                
                if not match:
                    crontab_temp.write(line)
                else:
                    found = True
            
            crontab.close()
            crontab_temp.close()
            
            move_file_over(self.__temp_file,self.__target_file)
            
        return found
    
def schedule_task(command, date_dict):
    """
    Schedules specified command at specified date
    date_dict has following format:
    date_dict = { 'min' = minutes as int or '*'
                  'hour' = hour as int or '*'
                  'dayofmonth' = dayofmonth as int or '*'
                  'month' = month as int or '*'
                  'dayofweek' = dayofweek as int or '*'
                }
    """
    
    Cron.schedule_task(command, date_dict)
