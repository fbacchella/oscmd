import boto
import oslib
from oslib.ec2_objects import Instance
from oslib.command import AttachVolume

class Attach(AttachVolume):
    object = 'volume'
    verb = 'attach'

    def execute(self, *args, **kwargs):        
        i = Instance(self.ctxt, id=kwargs['id'],name=kwargs['name'])
        v = self.ec2_object
        yield self.attach(v, i, kwargs['device'])

