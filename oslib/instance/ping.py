import oslib
from oslib.command import Command
import subprocess

class Ping(Command):
    """
This class is used to start a existing instance"""
    object = 'instance'
    verb = 'ping'
    def __init__(self):
        self.__class__.__bases__[0].__init__(self)

    def set_context(self, ctxt):
        self.__class__.__bases__[0].set_context(self, ctxt)

    def fill_parser(self, parser):
        parser.add_option("-c", "--count", dest="count", help="packet count", default=None)

    def execute(self, *args, **kwargs):
        instance = self.ec2_object.get()
        if 'ping' in kwargs:
            ping_cmd = [ kwargs.pop('ping') ]
        else:
            ping_cmd = ['ping']
        if 'count' in kwargs and kwargs['count'] != None:
            ping_cmd.extend([ '-c', kwargs.pop('count')])
            
        if len(args) > 0:
            ping_cmd.extend(args[0])
        ping_cmd.append(instance.public_dns_name)
        print ping_cmd
        subprocess.call(ping_cmd)
