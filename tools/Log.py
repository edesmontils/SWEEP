#!/usr/bin/env python3.6
# coding: utf8
"""
Tools to manage the log file
"""
#    Copyright (C) 2017 by
#    Emmanuel Desmontils <emmanuel.desmontils@univ-nantes.fr>
#    Patricia Serrano-Alvarado <patricia.serrano-alvarado@univ-nantes.fr>
#    All rights reserved.
#    GPL v 2.0 license.

import sys

import re
import time

from urllib.parse import urlparse, parse_qsl

from tools.tools import *

#==================================================

class LogException(Exception):
  def __init__(self, args):
    Exception.__init__(self,args)

#==================================================

class Log:

    def __init__(self, file_name):
        self.nb_lines = 0
        self.file_name = file_name
        self.pattern = self.makeLogPattern()
        if existFile(self.file_name):
            self.f = open(self.file_name, 'r')
        else :
            raise LogException('Class Log : "%s" does\'nt exist' % file_name)

    def __iter__(self):
        return self
 
    def __next__(self):
        ligne = self.f.readline()
        if len(ligne)==0:
            self.end()
            self.f.close()
            raise StopIteration
        else:
            self.nb_lines += 1
            if self.pattern is None :
                return self.extract(ligne)
            else:
                return self.extract(self.pattern.match(ligne).groupdict())

    def makeLogPattern(self):
        return None

    def extract(self,res):
        raise LogException('Class Log : "extract" is not defined')

    def end(self):
        pass

#==================================================
#==================================================
#==================================================

if __name__ == '__main__':
    print('main de Log.py')

 
