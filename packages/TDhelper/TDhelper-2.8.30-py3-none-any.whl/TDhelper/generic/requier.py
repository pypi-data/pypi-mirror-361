#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
"""
@File    :   requier.py
@Time    :   2020/04/18 06:48:15
@Author  :   Tang Jing
@Version :   1.0.0
@Contact :   yeihizhi@163.com
@License :   (C)Copyright 2020
@Desc    :   None
"""

# here put the import lib

# code start

class R:
    def __init__(self, namespace, fromlist=[],loadInstance= True, *args, **kwargs):
        """
        热加载一个类
        参数
         - namespace: string, 格式：generic.requier:R
        """
        self.__userNamespace = namespace
        self.__namespace = None  # namespace
        self.__instance = None  # instance class
        self.__importt(fromlist, loadInstance,*args)  # run import method

    def getNameSpace(self):
        return self.__namespace

    def getInstance(self):
        return self.__instance

    def getType(self):
        if self.__instance:
            return type(self.__instance)
        else:
            raise RuntimeError("instance is null.")

    def __importt(self, fromlist, loadInstance= True, *args):
        """
        Import package
        if import fail will return None
        """
        try:
            if self.__userNamespace:
                local_namespace = str.split(self.__userNamespace, ":")
                if isinstance(local_namespace, list):
                    try:
                        if not fromlist:
                            fromlist.append(local_namespace[1])
                        self.__namespace = __import__(
                            local_namespace[0], fromlist=fromlist
                        )
                    except BaseException as e:
                        raise e
                    if len(local_namespace) == 2 and loadInstance:
                        self.Instance(local_namespace[1], *args)
                else:
                    raise ValueError("namespace(%s) error. namespace:fromlist"%(self.__userNamespace))
            else:
                raise ValueError("TDhelper.generic.requier import 'namespace' is none.")
        except BaseException as e:
            raise e

    def Instance(self, classname, *args):
        """
        Instance class
        If instance fail will return None
        """
        if classname:
            if hasattr(self.__namespace, classname):
                try:
                    self.__instance = getattr(self.__namespace, classname)(*args)
                except Exception as e:
                    raise e
                if self.__instance:
                    return self.__instance
                else:
                    raise RuntimeError("TDhelper.generic.requier(%s) instance %s fail." % (self.__userNamespace,classname))
            else:
                raise RuntimeError("TDhelper.generic.requier(%s) not found %s." % (
                    self.__userNamespace,
                    classname
                ))
        else:
            raise RuntimeError("TDhelper.generic.requier.Instance(%s) classname(%s) is none."%(self.__userNamespace,classname))

    def Call(self, methodname, *args, **kw):
        """
        Call method
        """
        if methodname:
            if self.__instance:
                method = getattr(self.__instance, methodname)
                if method:
                    try:
                        return method(*args, **kw)
                    except Exception as e:
                        raise e
                else:
                    raise RuntimeError("TDhelper.generic.requier.Call '%s' not found in %s." % (
                        methodname,
                        self.__userNamespace,
                    ))
            else:
                raise RuntimeError("TDhelper.generic.requier.Call(%s) instance is none."%(self.__userNamespace))
        else:
            raise RuntimeError("TDhelper.generic.requier.Call(%s) methodname(%s) is none."%(self.__userNamespace,methodname))

    async def call_async(self, methodname, *args, **kw):
        """
        call method by async
        """
        assert methodname, "methodname is none."
        try:
            if methodname:
                if self.__instance:
                    method = getattr(self.__instance, methodname)
                    if method:
                        result = await method(*args, **kw)
                        return True, {"code": 200, "msg": "success", "result": result}
                    else:
                        return False, {
                            "code": 500,
                            "msg": "can not found %s method." % methodname,
                            "result": "",
                        }
                else:
                    return False, {
                        "code": 500,
                        "msg": "instance is none.",
                        "result": "",
                    }
            else:
                return False, {"code": 500, "msg": "methodname is none.", "result": ""}
        except Exception as e:
            return False, {"code": 500, "msg": e, "result": ""}


def InstanceCall(handle, method, *args, **kwargs):
    try:
        method = getattr(handle, method)
        if method:
            return method(*args, **kwargs)
        else:
            raise Exception("%s not have method %s" % (handle, method))
    except Exception as e:
        raise e

'''
if __name__ == "__main__":
    bb = R("a.b:ab").Call("gg")
    print(bb)
    try:
        ccc = R("rest_framework.request:Request",loadInstance=False).getNameSpace().HttpRequest
        print(ccc)
    except Exception as e:
        print(e.args)
    # print(isinstance(1,R(int).getInstance()))
'''