import boto

from oslib.command import Command
import urllib2

class Add(Command):
    object = 'iam'
    verb = 'add'

    def fill_parser(self, parser):
        parser.add_option("-i", "--instance", dest="instance", help="list instance profile", default=None,)

    def execute(self, *args, **kwargs):
        iamcnx = self.ec2_object.get()
        return iamcnx.add_role_to_instance_profile('EIPManage', 'test')
    
    def to_str(self, status):
        return status
