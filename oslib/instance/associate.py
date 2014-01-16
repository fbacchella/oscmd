import boto
import oslib
from oslib.command import Command

class Associate(Command):
    """
This class is used to associate an EIP to an instance"""
    object = 'instance'
    verb = 'associate'
    def __init__(self):
        self.__class__.__bases__[0].__init__(self)

    def set_context(self, ctxt):
        self.__class__.__bases__[0].set_context(self, ctxt)

    def fill_parser(self, parser):
        parser.add_option("-i", "--ip", dest="ip", help="EIP", default=None)

    def execute(self, *args, **kwargs):
        instance = self.ec2_object
        tags = instance.get().tags
        if 'ip' in kwargs and kwargs['ip']:
            ip = kwargs['ip']
        elif 'EIP' in tags:
            ip = tags['EIP']            
        else:
            raise oslib.OSLibError("No EIP defined for '%s'" % instance.id)
        eip = oslib.ec2_objects.EIP(self.ctxt, id=ip)
        eip.get().associate(instance.id)
        self.ctxt.conn.create_tags([instance.id], {"EIP": ip})
        return ip
    
    def to_str(self, status):
        if status:
            return "associated to '%s'" % status