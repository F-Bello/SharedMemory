#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 10:43:01 2019

@author: fb
"""
import SharedMemory
import time
import sys

def main(*args, shared_memory_conn=None, **kwargs):
   '''Prints the shared memory value to the screen repeatedly'''
   
   #The connection to the parent script is automatically passed in as shared_memory_conn
   
   smo = SharedMemory.SharedMemoryObject('msg', shared_memory_conn)#Initiates the SharedMemory object locally
   
   print('TestChild has initiated')
   sys.stdout.flush()
   
   start = time.time()
   while time.time()-start < 2.5:
      #gets the loval value for the smo Shared memory object
      print("Variable 'smo' has value '{}' in TestChild".format(smo.Get()))
      sys.stdout.flush()
      
      time.sleep(0.05)
   
   