from oslib.command import Command
from oslib.capacity import Capacity

InstanceTypes = ['m1.small', 'm1.large', 'm1.xlarge',
                 'c1.medium', 'c1.xlarge', 'm2.xlarge',
                 'm2.2xlarge', 'm2.4xlarge', 'cc1.4xlarge',
                 't1.micro']

class Offering(Command):
    object = 'instance'
    verb = 'offering'
    def fill_parser(self, parser):
        pass

    def execute(self, *args, **kwargs):
        print Capacity.mapping

