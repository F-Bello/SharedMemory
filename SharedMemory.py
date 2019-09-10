#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 10:43:20 2019

@author: fb
"""
import threading
from multiprocessing import Pipe, Process

class SharedMemoryObject():
   '''Handles the shared memory objects. 
   Fields :   
      
      DataDict : A map of {name (str): shared_memory (obj)}. This should never be altered directly, 
         but is updated by the self.Set(shared_memory) method (where self.Name == name).
      
      Pipes : A list of active pipes, referenced when deciding if a new shared_memory_variable 
         requires a new listener thread.
      
      Lock : A threading.Lock for use on the DataDict to prevent race conditions.
   
   Methods : 
      
      Listener : Spawns a new thread to act as a listener and update the DataDict according to the 
         signals sent by the script on the other end of the connection
   '''
      
   DataDict = {}
   Pipes = []
   Lock = threading.RLock()#make lock
   
   def __init__(self, name, subprocess_connection):
      '''Makes a shared memory object with the given name. The object is synced along the given connection
      
      Parameters : 
         
         name : (str) The key used to reference this object in the DataDict.
         
         subprocess_connection : A connection of the type created by multiprocessing.Pipe(). The object will be shared
         with the code on the other end, if it is set to recieve it.
      
      Fields : 
         
         Name : (str) The key used to reference this object in the DataDict.
            
         Connection : A connection of the type created by multiprocessing.Pipe(). The object will be shared
         with the code on the other end, if it is set to recieve it.
         
      Methods : 
         
         Set : Changes the object associated with Name in the DataDict and sends an appropiate sync message
            down the Connection.
         
         Get : Gets the value of a variable from the DataDict, implementing the lock over the dictionary
      '''
      
      self.Name = str(name)
      self.Connection = subprocess_connection
      #if the commection is closed, open it
      if self.Connection not in self.Pipes:
         listener = threading.Thread(target=self.Listener, args=(self.Connection, ), daemon=True) #start a listener on a separate thread
         listener.start()
         self.Pipes.append(self.Connection)
      
      self.Lock.acquire()#get lock
      if self.Name not in self.DataDict.keys():
         self.DataDict[self.Name] = 'Undefined SharedMemory object'
      self.Lock.release()
   
   def Set(self, item):
      '''Sets the Shared Object's data the given item, both locally and in the shared scripts
      
      Parameters :
         
         item : (obj) the updated value of the shared memory object such that, after this method executes,
            self.Get() will return(item) both locally and on the synced script
      '''

      self.Lock.acquire()#get lock  
      self.DataDict[self.Name] = item
      self.Lock.release()#release lock
      try:
         self.Connection.send((self.Name, item))#send a tuple, (Name, item)
      except BrokenPipeError:
         pass#the listerner must have exited
   
   def Get(self):
      '''Gets the value of the variable from the DataDict, while properly employing the Lock 
      over the variable to avoid race conditions.
      
      Return:
         
         self.DataDict[self.Name] (obj)
      '''
      self.Lock.acquire()
      copy_dict = self.DataDict[self.Name]
      self.Lock.release()
      return(copy_dict)

   @classmethod
   def Listener(cls, connection):
      '''Spawns a thread to listen to the given connection, unpack the incoming messages and
      set the value to the DataDict (it doesn't call the Set method as this would cause an 
      infinite loop)
      
      Parameters : 
         
         connection : A connection of the type created by multiprocessing.Pipe(). This is what the 
         listener will monitor.
      '''
      item = None
      while True: #infinite loop
         try:
            name, item = connection.recv()#unpack
            cls.Lock.acquire()#get lock
            cls.DataDict[name] = item#change DataDict
            cls.Lock.release()#relese lock
         except BrokenPipeError:
            return(None) #exits the thread

def SharedMemoryProcess(*args, **kwargs):
   '''Starts a subprocess and opens a pipe to it. The child's pipe is atuomatically passed in as the keyword
   "shared_memory_conn". All input arguments are passed straight into a multiprocess.Process call. '''
   
   parent_conn, child_conn = Pipe()
   
   #adds the child connection to kwargs with the key shared_memory_conn
   if 'kwargs' not in kwargs.keys():#creates a key word argument called kwargs if it doesn't already exist
      kwargs['kwargs'] = {}
   kwargs['kwargs']['shared_memory_conn'] = child_conn #adds the desired key word argument
   
   #start the child process
   proc = Process(*args, **kwargs)
   proc.start()
   #it is the child's responsibility to connect to the pipe and start a SharedMemory instance

   return(parent_conn)
   