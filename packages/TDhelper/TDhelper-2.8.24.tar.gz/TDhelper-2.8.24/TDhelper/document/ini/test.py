from TDhelper.document.ini.model import model
from TDhelper.document.ini.fields import FieldType

class t(model):
    a= FieldType(str,"SERVICE.host")
    b= FieldType(int,"SERVICE.name")

if __name__ == "__main__":
    a= t(r"/home/ubuntu/dev/pyLib/TDhelper/document/ini/1.ini")
    print(a.a)
    print(a.b)