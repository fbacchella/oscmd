from dump import Dump
from summary import Summary
from oslib.command import Command, List
from attach import Attach

class List(List):
    object = 'volume'
    verb = 'list'

class Delete(Command):
    object = 'volume'
    verb = 'delete'
    
    def execute(self, *args, **kwargs):
        self.ec2_object.delete()
        return True
    
    def to_str(self, status):
        return '%s deleted' % self.ec2_object.id

class Detach(Command):
    object = 'volume'
    verb = 'detach'
    
    def fill_parser(self, parser):
        parser.add_option("-f", "--forced", dest="force", help="force detach", default=False, action='store_true')

    def execute(self, *args, **kwargs):
        self.ec2_object.get().detach(force=kwargs['force'])
        return True
    
    def to_str(self, status):
        return '%s detached' % self.ec2_object.id


class_ref = [Delete, Dump, Summary, List, Detach, Attach]
