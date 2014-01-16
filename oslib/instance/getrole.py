import boto
import oslib
from oslib.command import Command
from oslib.keypair import class_ref
from oslib.ec2_objects import Iam
import re

filter = re.compile('.*:instance-profile/(.*)')
class GetRole(Command):
    """
This class is used to associate an EIP to an instance"""
    object = 'instance'
    verb = 'getrole'

    def execute(self, *args, **kwargs):
        instance = self.ec2_object.get()
        if len(instance.instance_profile.keys()) == 0:
            return None
        iam = Iam(self.ctxt)
        self.proxy = oslib.get_cmd(self.ctxt, iam, 'dump-instance-role')
        arn = instance.instance_profile['arn']
        name = filter.match(arn).group(1)
        return self.proxy.execute(name = name)
        
    def to_str(self, status):
        return self.proxy.to_str(status)

class_ref.append(GetRole)
