from dump import GetIp
from summary import Summary
from oslib.command import Command, List
from oslib.ec2_objects import Instance

class Allocate(Command):
    object = 'eip'
    verb = 'allocate'
    
    def validate(self, options):
        return True
    
    def execute(self, *args, **kwargs):
        yield self.conn.allocate_address()
    
    def to_str(self, value):
        print value.public_ip

class Associate(Command):
    """Associate an EIP with a instance identified using it's name or instance id"""
    object = 'eip'
    verb = 'associate'

    def fill_parser(self, parser):
        parser.add_option("-i", "--id", dest="id", help="object ID", default=None)
        parser.add_option("-n", "--name", dest="name", help="object tag 'Name'", default=None)
    
    def execute(self, *args, **kwargs):
        public_ip =  self.ec2_object.get().id
        instance = Instance(self.ctxt, name=kwargs['name'], id=kwargs['id'])
        instance_id = instance.get().id
        self.conn.associate_address(instance_id = instance_id, public_ip=public_ip)
        yield True

class Disassociate(Command):
    object = 'eip'
    verb = 'disassociate'

    def execute(self, *args, **kwargs):
        yield self.ec2_object.get().disassociate()
    
    def to_str(self, value):
        pass

class Release(Command):
    object = 'eip'
    verb = 'release'

    def execute(self, *args, **kwargs):
        yield self.ec2_object.get().release()
    
    def to_str(self, value):
        pass

class List(List):
    object = 'eip'
    verb = 'list'
    pattern = '%(public_ip)15s %(instance_id)s'

class_ref = [GetIp, Allocate, Associate, Summary, List, Release]