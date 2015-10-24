__author__ = 'adean'


class Utils:
    @staticmethod
    def reflect_class_from_classname(package, classname):
        mod = __import__(package + '.' + classname, fromlist=[classname])
        klass = getattr(mod, classname)
        return klass()
