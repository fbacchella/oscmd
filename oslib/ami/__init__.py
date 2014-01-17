from run import Run
from dump import Dump
from share import Share
from makeami import MakeAmi
from oslib.command import GenericExist, List, Delete

class Exist(GenericExist):
    """set exit code to 1 if the AMI don't exist """
    object = 'ami'
    verb = 'exist'

class List(List):
    object = 'ami'
    verb = 'list'
    pattern = '%(ownerId)12s %(id)s %(name)s'
    
    def fill_parser(self, parser):
        super(List, self).fill_parser(parser)
        parser.add_option('-O', "--noowner", dest="owner", action="store_false", help="don't filter AMI by owner")
        ami_provider = None
        if 'owner' in self.ctxt.object_defaults['ami']:
            ami_provider = self.ctxt.object_defaults['ami']['owner']
        if(ami_provider):
            parser.add_option('-o', "--owner", dest="owner", default=ami_provider, help="list only AMI from this owner, default is %s" % ami_provider)
        else:
            parser.add_option('-o', "--owner", dest="owner", default=False, help="list only AMI from this owner")

    def execute(self, *args, **kwargs):
        if kwargs['owner']:
            kwargs['filters'] = {'owner_id': kwargs['owner'] }
        del kwargs['owner']
        for ami in super(List, self).execute(*args, **kwargs):
            yield ami

class Delete(Delete):
    object = 'ami'
    verb = 'delete'
    
    def fill_parser(self, parser):
        parser.add_option("-d", "--delete_snapshot", dest="delete_snapshot", help="delete associated snapshot", default=False, action="store_true")

class_ref = [Run, Dump, Share, MakeAmi, Exist, List, Delete]
