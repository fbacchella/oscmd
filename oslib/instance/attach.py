import boto
import oslib
from oslib.ec2_objects import Volume
from oslib.command import AttachVolume

class Attach(AttachVolume):
    object = 'instance'
    verb = 'attach'

    def execute(self, *args, **kwargs):
        i = self.ec2_object
        v = Volume(self.ctxt, id=kwargs['id'],name=kwargs['name'])
        yield self.attach(v, i, kwargs['device'])
