from dump import Dump
from summary import Summary
from ssh import SSH
from ping import Ping
from offering import Offering
from associate import Associate
from newvolume import NewVolume
from start import Start
from console import Console
from attach import Attach
from terminate import Terminate
from windows import GetWindowsPassword
import boto

from oslib.command import Command, GenericExist, List

class Reboot(Command):
    object = 'instance'
    verb = 'reboot'
    
    def execute(self, *args, **kwargs):
        self.ec2_object.reboot()

class Stop(Command):
    object = 'instance'
    verb = 'stop'

    def fill_parser(self, parser):
        parser.add_option("-f", "--forced", dest="force", help="force stop", default=False, action='store_true')

    def execute(self, *args, **kwargs):
        force=False
        if 'force' in kwargs:
            force = kwargs['force']
        self.ec2_object.stop(force)
        return True
    
    def to_str(self, status):
        return '%s stopping' % self.ec2_object.id

class Exist(GenericExist):
    """set exit code to 1 if the instance doesn't exist """
    object = 'instance'
    verb = 'exist'

class List(List):
    object = 'instance'
    verb = 'list'

class_ref = [List, Dump, Start, SSH, Ping, Reboot, Terminate, Start, Stop, Summary, Offering, Associate, Exist, NewVolume, Console, Attach, GetWindowsPassword ]

import getrole
