from TDhelper.db.mongodb.orm.core.meta import *
from bson.objectid import ObjectId
class model(metaclass= mongo_db_meta):
        '''mongo db orm model class.
        
        define fileds with filed class.
        
        class Meta:
            table - <class, str>: if not set value, it is class name  
        '''
        _id= field(type= field_type.BsonId,default_value=ObjectId)
        
        #class Meta:
        #    table= "testdb_db"
        
        def __init__(self,*args,**kwargs) -> None:
            #super(model,self).__init__(*args,**kwargs)
            try:
                self.__mongo__= self.__db_drives__(connect_conf)
            except Exception as e:
                raise e
            if self.__table__ != "model":
                self.__collect__= self.__mongo__.__db__[self.__table__]
            