import boto
import os
import oslib
import oslib.getuser as getuser
import re
import time
from oslib.command import Command
from boto.ec2.blockdevicemapping import BlockDeviceMapping, BlockDeviceType

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

    def execute(self, *args, **kwargs):
        instance = self.ec2_object.get()
        last = ord('f')
        for device in instance.block_device_mapping:
            device_match = device_re.search(device)
            if device_match: 
                last = max(last, ord(device_match.group(1)))
        
        volume = self.conn.create_volume(kwargs['size'], instance.placement)
        while volume.status != 'available':
            volume.update(True)
            yield (".")
            time.sleep(1)
        yield ("\n")
        self.conn.attach_volume(volume.id, instance.id, "/dev/sd%s" % chr(last + 1))
        tags ={}
        user = getuser.user
        tags['creator'] = user
        tags['Name'] = instance.tags['Name'] + '/' + kwargs['name']
        tags['instance'] = instance.tags['Name']
        self.conn.create_tags([ volume.id ], tags)
        yield volume
        
    def to_str(self, volume):
        return volume
