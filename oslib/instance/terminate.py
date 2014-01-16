import boto
import oslib
from oslib.command import Command
import time

class Terminate(Command):
    object = 'instance'
    verb = 'terminate'
    
    def fill_parser(self, parser):
        parser.add_option("-p", "--purge", dest="purge", help="purge related objects", default=None, action="store_true")

    def execute(self, *args, **kwargs):
        instance = self.ec2_object
        if kwargs['purge']:
            eip = instance.eip()
            if eip:
                eip.get().delete()
        volumes = []
        volumes.extend(instance.volumes())

        instance.delete()
        while instance.state() != 'terminated':
            yield (".")
            time.sleep(1)
        yield ("\n")

        for v in volumes:
            if v.exist() and v.state() == 'available':
                v.delete()
        yield True
    
    def to_str(self, status):
        if status.__class__ == "".__class__ or status.__class__ == u"".__class__:
            return status
        else:
            return '%s terminated' % self.ec2_object.id

