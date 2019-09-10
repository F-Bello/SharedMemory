#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 10:38:13 2019

@author: fb
"""
import SharedMemory
import time
import TestChild
import sys


if __name__ == "__main__":
   '''Starts TestChild.main as a subprocess and initiates a SharedMemory connection with it. The updates the 
   SharedMemory object's value repeatedly for 3 seconds'''
   #Spawns a subprocess (equivaent to multiprocess.Process()) and opens a connection with it 
   #via multiprocess.Pipe()
   parent_conn = SharedMemory.SharedMemoryProcess(target=TestChild.main, daemon=True)
   
   msg = 0
   smo = SharedMemory.SharedMemoryObject('msg', parent_conn)#locally initiates the SgaredMemory object
   
   print('TestParent has initiated')
   sys.stdout.flush()
   
   start = time.time()
   while time.time()-start < 3:
      time.sleep(0.1)
      msg += 1
      
      print('TestParent is updating smo to {}'.format(msg))
      sys.stdout.flush()
      
      smo.Set(msg)# Sets the value related to smo to msg. 
      #This value can now be acessed both locally and remotely