from dump import Dump
from authorize import Authorize, DeAuthorize
from oslib import OSLibError
from oslib.command import Command, GenericExist, List, Delete

class Create(Command):
    object = 'securitygroup'
    verb = 'create'
    
    def validate(self, options):
        return True
        
    def fill_parser(self,parser):
        parser.add_option("-n", "--name", dest="name", help="name", default=None)
        parser.add_option("-d", "--description", dest="description", help="description", default=None)
        
    def execute(self, *args, **kwargs):
        if not 'name' in kwargs or not kwargs['name']:
            raise OSLibError("name missing")
        
        self.ctxt.cnx_ec2.create_security_group(**kwargs)

class Delete(Delete):
    object = 'securitygroup'
    verb = 'delete'

class Exist(GenericExist):
    """set exit code to 1 if the security group don't exist """
    object = 'securitygroup'
    verb = 'exist'

class List(List):
    object = 'securitygroup'
    verb = 'list'

class_ref = [Dump, Authorize, Create, DeAuthorize, Exist, List, Delete]
