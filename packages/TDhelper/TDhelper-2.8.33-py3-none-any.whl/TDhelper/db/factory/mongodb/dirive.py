from TDhelper.db.factory.interface import dbDrive,logging
import pymongo
from urllib.parse import quote_plus
from TDhelper.generic.requier import InstanceCall

class mongoDbDrive(dbDrive):
    def __init__(self,logger:logging.Logger):
        super(mongoDbDrive,self).__init__()
        self.__logger__= logger
        self.__current_pos__=0
        self.__query_set__= None
        self.__query_cmd__={"cmd":""}
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.__query_set__:
            if self.__current_pos__<=self.__query_set__.length():
                o= self.__query_set__[self.__current_pos__]
                self.__current_pos__+=1
                return o
            else:
                raise StopIteration
        else:
            raise StopIteration
        
    def __exec__(self):
        self.__query_set__= None
        if self.__query_cmd__['cmd']:
            try:
                __cmd__= self.__query_cmd__["cmd"].lower()
                if 'query' not in self.__query_cmd__:
                    if __cmd__ == "save" or __cmd__ == "update_one" or __cmd__=="get":
                        self.__query_set__= InstanceCall(self,self.__query_cmd__['cmd'].lower())()
                else:
                    self.__query_set__= InstanceCall(self,self.__query_cmd__['cmd'].lower())(**self.__query_cmd__['query'])
            except Exception as e:
                self.__query_set__= None
                self.__logger__.error(e)
        return self.__query_set__
    
    def __connection__(self,**kwargs):
        if kwargs["usr"] and kwargs["pw"]:
            self.__url__= "mongodb://%s:%s@%s:%s" % (kwargs["usr"],kwargs["pw"],kwargs["host"],str(kwargs["port"]))
        else:
            self.__url__= "mongodb://%s:%s" % (kwargs["host"],str(kwargs["port"]))
        if self.__url__:
            self.__db_name__= kwargs["db"]
            self.__client__= pymongo.MongoClient(self.__url__,connect=False)
            self.__conn__= self.__client__[kwargs["db"]]
        else:
            raise Exception("mongodb url is none.")

    def __where__(self,**kwargs):
        self.__query_cmd__={
            "cmd":"where",
            "query":kwargs
        }
        return self
    
    def __delete__(self):
        self.__query_cmd__={
            "cmd":"delete"
        }
        return self.__conn__.delete
    
    def __save__(self,**kwargs):
        self.__query_cmd__={
            "cmd":"save",
            "query":kwargs
        }
        pass
    
    def __skip__(self,num):
        pass
    
    def __limit__(self,num):
        pass
    
    def __order_by__(self,**kwargs):
        pass
    
    def __group_by__(self,**kwargs):
        pass
    
    