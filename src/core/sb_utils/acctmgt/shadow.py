#!/usr/bin/env python
#
# Copyright (c) 2013-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.

# Not all platforms provide the spwd python module.  Right now, only one SB module needs access to the
# data contained therein, although this will change.  So we need to provide our own little stub to just
# do the right thing and provide an element.  This stub isolates SB from the guts of getting the required
# line of data, and ensures that we can access the shadow file to get a single line of user information as
# though the spwd module existed.

# To provide this, we're gratefully using the 'superTuple' cookbook recipe found in the O'Reilly Python Cookbook
# The Oreilly code is between the '#================================' markers

## Python Cookbook 2nd Edition
## Martelli, Martelli, Ascher  Copyright 2005
## ISBN: 0-596-00797-3
## http://www.oreilly.com/catalog/pythonian2
## from cb_6_7_sol_1.py

#=============================Copied gratefully from O'Reilly 'Python Cookbook 2nd Edition  ==============
# use operator.itemgetter if we're in 2.4, roll our own if we're in 2.3
try:                                                                                    
    from operator import itemgetter                                                     
except ImportError:                                                                     
    def itemgetter(i):                                                                  
        def getter(self): return self[i]                                                
        return getter                                                                   

def itemsetter(i):                                                                      
    def setter(self,val): self[i]=val                                                   
    return setter                                                                       
def superTuple(typename, *attribute_names):                                             
    """ create and return a subclass of `tuple', with named attributes                  
        Example:                                                                        
        >>> Point = supertuple.superTuple('Point','x','y')                              
        >>> Point                                                                       
        <class 'supertuple.Point'>                                                      
        >>> p = Point(1,2,3)   # wrong number of fields                                 
        Traceback (most recent call last):                                              
        ...                                                                             
        TypeError: Point exactly 2 arguments (3 given)                                  
        >>> p = Point(1,2)     # Do it right this time.                                 
        >>> p                                                                           
        Point(1,2)                                                                      
        >>> print p.x, p.y                                                              
        1 2                                                                             
    """                                                                                 
    # make the subclass with appropriate __new__ and __repr__ specials                  
    nargs = len(attribute_names)                                                        
    class supertup(tuple):                                                              
        __slots__ = ()         # save memory, we don't need per-instance dict           
        def __new__(cls, *args):                                                        
            if len(args) != nargs:                                                      
                raise TypeError, '%s takes exactly %d arguments (%d given)' % (         
                                  typename, nargs, len(args))                           
            return tuple.__new__(cls, args)                                             
        def __repr__(self):                                                             
            return '%s(%s)' % (typename, ', '.join(map(repr, self)))                    
    # add a few key touches to our new subclass of `tuple'                              
    for index, attr_name in enumerate(attribute_names):                                 
        setattr(supertup, attr_name, property(itemgetter(index),itemsetter(index)))     
    supertup.__name__ = typename                                                        
    return supertup                                                                     
#===============================================================================

# never used if 'spwd' module actually exists.
SpwdStubClass = superTuple('spwd','sp_nam', 'sp_pwd', 'sp_lstchg','sp_min','sp_max','sp_warn','sp_inact','sp_expire', 'sp_flag')


spwdUsed = True
try:
    import spwd
except ImportError:    
    spwdUsed = False
spwdUsed = False
    
def processLine(line):
    fields = line.strip().split(":")
    newfields = fields[:2]
    for field in fields[2:]:
        if field == '':
            field=-1
        else:
            field=int(field)
        newfields.append(field)
    tup = tuple(newfields)
    return SpwdStubClass(*tup)
    
def getspnam(userName):
    spwdInfo = None
    if spwdUsed:
        spwdInfo = spwd.getspnam(userName)
    else:
        spwdInfo = [processLine(line) for line in open('/etc/shadow') if line.startswith(userName+":")][0]
    return spwdInfo       

