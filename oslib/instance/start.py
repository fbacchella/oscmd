import boto
from oslib.command import Command
import time

class Start(Command):
    """
This class is used to start a existing instance"""
    object = 'instance'
    verb = 'start'
    
    def fill_parser(self, parser):
        parser.add_option("-w", "--wait", dest="wait", help="Wait for start", default=False, action='store_true')

    def execute(self, *args, **kwargs):
        try:
            instance = self.ec2_object.get()
            tags = instance.tags
            instance.start()
            
            #Do we need to wait for start ?
            if 'EIP' in tags or kwargs['wait']:
                while instance.state != 'running' and instance.state != 'terminated':
                    instance.update(True)
                    time.sleep(1)
            
            #Check if there is an EIP
            if 'EIP' in tags:
                ip = tags['EIP']
                self.ctxt.cnx_ec2.associate_address(instance_id=instance.id, public_ip=ip)

            return True
        except boto.exception.EC2ResponseError as e:
            return e

    def to_str(self, status):
        return '%s starting' % self.ec2_object.id
