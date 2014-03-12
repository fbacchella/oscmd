import boto
import os
import oslib
import oslib.getuser as getuser
import re
import time
from oslib.command import Command
from boto.ec2.blockdevicemapping import BlockDeviceMapping, BlockDeviceType
import subprocess

device_re = re.compile('/dev/sd(.)')

class NewVolume(Command):
    """
This class is used to associate an EIP to an instance"""
    object = 'instance'
    verb = 'addvolume'
    def __init__(self):
        super(NewVolume, self).__init__()

    def fill_parser(self, parser):
        parser.add_option("-n", "--name", dest="name", help="New volume name", default=None)
        parser.add_option("-s", "--size", dest="size", help="New volume size (in GB)", default=None)
        parser.add_option("-m", "--mount", dest="mount", help="mount point to attach and extend", default='')
        parser.add_option("-d", "--deviceid", dest="deviceid", help="device id used by blkid", default='')

    def execute(self, *args, **kwargs):
        if not kwargs['name']:
            yield "Missing volume name"
            raise StopIteration 
        instance = self.ec2_object.get()
        last = ord('f')
        for device in instance.block_device_mapping:
            device_match = device_re.search(device)
            if device_match: 
                last = max(last, ord(device_match.group(1)))
        
        volume = self.ctxt.cnx_ec2.create_volume(kwargs['size'], instance.placement)
        while volume.status != 'available':
            volume.update(True)
            yield (".")
            time.sleep(1)
        yield ("\n")
        self.ctxt.cnx_ec2.attach_volume(volume.id, instance.id, "/dev/sd%s" % chr(last + 1))
        tags ={}
        user = getuser.user
        tags['creator'] = user
        tags['Name'] = instance.tags['Name'] + '/' + kwargs['name']
        tags['instance'] = instance.tags['Name']
        self.ctxt.cnx_ec2.create_tags([ volume.id ], tags)
        while volume.status != 'in-use':
            volume.update(True)
            yield (".")
            time.sleep(1)
        yield ("\n")
        if kwargs['mount'] or kwargs['deviceid']:
            key_file = self.ctxt.key_file
            remote_user = self.ctxt.user
            root_embedded = oslib.resources.__path__[0]
            extendvol = open(os.path.join(root_embedded, "extendvol"), 'r')
            # "'%s'" % value is needed to keep empty value
            # anyway ssh eat it
            args=["ssh", "-o", "GSSAPIAuthentication=no", "-tt", "-o", "UserKnownHostsFile=/dev/null",  "-x", "-o", "StrictHostKeyChecking=no", "-i", key_file,  "-l", remote_user, instance.public_dns_name, "sudo", "bash", "-s", volume.attach_data.device, "'%s'" % kwargs['mount'], "'%s'" % kwargs['deviceid'] ]
            print args
            try:
                subprocess.check_call(args, shell=False, stdin=extendvol)
            except subprocess.CalledProcessError as e:
                raise oslib.OSLibError(e)
            extendvol.close()
        yield volume
        
    def to_str(self, volume):
        if volume.__class__ == "".__class__ or volume.__class__ == u"".__class__:
            return volume
        else:
            return "created volume %s as %s" % (volume.id, volume.attach_data.device)
