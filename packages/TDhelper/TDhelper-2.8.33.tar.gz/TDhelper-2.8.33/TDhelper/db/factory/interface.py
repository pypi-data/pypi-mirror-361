import abc
import six
import logging
class dbDrive:
    __logger__= None
    __conn__= None
    __query_cmd__= {"cmd":""}
    __query_set__=None
    __current_pos__= 0
    
    def __init__(self,logger:logging.Logger):
        pass
    
    @abs.abstractmethod
    def __exec__(self):
        pass
    
    @abs.abstractmethod
    def __connection__(self,**kwargs):
        pass
    
    @abs.abstractmethod
    def __where__(self,**kwargs):
        pass
    
    @abs.abstractmethod
    def __delete__(self,**kwargs):
        pass
    
    @abs.abstractmethod
    def __save__(self,**kwargs):
        pass
    
    @abs.abstractmethod
    def __skip__(self,num):
        pass
    
    @abs.abstractmethod
    def __limit__(self,num):
        pass
    
    @abs.abstractmethod
    def __order_by__(self,**kwargs):
        pass
    
    @abs.abstractmethod
    def __group_by__(self,**kwargs):
        pass
    