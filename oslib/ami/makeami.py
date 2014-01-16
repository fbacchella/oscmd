from boto.ec2.blockdevicemapping import BlockDeviceMapping, BlockDeviceType
import boto
from oslib.command import Command
import time
import subprocess
import sys

class MakeAmi(Command):
    """
It's used to build a new AMI from a old AMI, a running instance or a volume.
When a old AMI is given, externals volumes can be appended"""
    object = 'ami'
    AMIConf = {}
    verb = 'make'

    def validate(self, options):
        return True

    def fill_parser(self, parser):
        super(MakeAmi, self).fill_parser(parser)
        parser.add_option("-c", "--configuration", dest="configuration", help="Create an instance based on configuration", default=None)
        parser.add_option("-i", "--instance", dest="instance_id", help="Use an instace", default=None)
        parser.add_option("-v", "--volume", dest="volume_id", help="Use A volume", default=None)
        parser.add_option("-n", "--name", dest="name", help="New AMI name", default=None)
        parser.add_option("-d", "--description", dest="description", help="New AMI description", default=None)
        parser.add_option("-s", "--share", dest="do_share", help="Make a shared AMI", default=False, action='store_true')
        parser.add_option("-A", "--shared_account", dest="shared_account", help="Add a shared account", default=None, action='append')
    
    def execute(self, *args, **kwargs):
        if 'configuration' in kwargs and kwargs['configuration']:
            executor = LaunchInstance()
            executor.set_context(self.ctxt)
            conf = MakeAmi.AMIConf[kwargs['configuration']].copy()
            conf['url_commands'] = ['http://ip-10-1-1-52.eu-west-1.compute.internal/os-init/prepareami']
            instance = executor.execute(**conf)
            ami = self.instance2ami(instance.id, kwargs['name'], kwargs['description'])
        elif 'instance_id' in kwargs and kwargs['instance_id']:
            ami = self.instance2ami(kwargs['instance_id'], kwargs['name'], kwargs['description'])
        elif 'volume_id' in kwargs and kwargs['volume_id']:
            ami = self.vol2ami(kwargs['volume_id'], kwargs['name'], kwargs['description'])
        if kwargs['do_share']:
            if kwargs['shared_account'] == None:
                kwargs['shared_account'] = self.ctxt.user_id_share
            executor = Share()
            executor.set_context(self.ctxt)
            executor.execute(ami=ami, users=kwargs['shared_account'])
            
    def instance2ami(self, instance_id, name, description=None):
        instance = boto.ec2.instance.Instance(connection=self.conn)
        instance.id = instance_id
        instance.update(True)
        # If the instance is running, power it off
        if  instance.state == 'running':
            args=["ssh", "-o", "UserKnownHostsFile=/dev/null",  "-x", "-o", "StrictHostKeyChecking=no", "-i", self.ctxt.key_file, "-l", "root", instance.public_dns_name, "poweroff"]
            subprocess.call(args)

        while instance.state == 'running':
            instance.update(True)
            sys.stdout.write(".")
            time.sleep(1)
            sys.stdout.flush()
        sys.stdout.write("\n")
        return self.conn.create_image(instance_id, name, description=description)


    def vol2ami(self, volume_id, name, description=None):
        snap = self.ctxt.cnx_ec2.create_snapshot(volume_id, 'boto snapshot for %s' % name)
        block_map = BlockDeviceMapping() 
        sda = BlockDeviceType() 
        sda.snapshot_id = snap.id
        sda.ebs = True
        root_device_name = '/dev/sda1'
        block_map[root_device_name] = sda
        return self.ctxt.cnx_ec2.register_image(name=name, architecture='x86_64', root_device_name=root_device_name, block_device_map=block_map, description=description)

MakeAmi.AMIConf['webexp'] = {
    'name': 'AMI-Master-webexp',
    'image_id': 'ami-bcc10f94',
    'volume_size': [100],
    'puppet_class': 'webexp'
}
MakeAmi.AMIConf['simple'] = {
    'name': 'AMI-Master-simple',
    'image_id': 'ami-bcc10f94',
    'volume_size': [],
    'puppet_class': None,
}
MakeAmi.AMIConf['cloudview'] = {
    'name': 'AMI-Master-cloudview',
    'image_id': 'ami-bcc10f94',
    'volume_size': [100],
    'puppet_class': 'cloudview',
}
