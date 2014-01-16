from summary import Summary
from dump import Dump
from oslib.command import List

class List(List):
    object = 'snapshot'
    verb = 'list'

class Delete(List):
    object = 'snapshot'
    verb = 'delete'

    def execute(self, *args, **kwargs):
        self.ec2_object.delete()
        return True
    
    def to_str(self, status):
        return '%s deleted' % self.ec2_object.id

class_ref = [ Summary, Dump, List, Delete ]
