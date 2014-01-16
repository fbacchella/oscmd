from oslib.command import Command
from oslib.capacity import Capacity
import re

class Summary(Command):
    tina_class_re = re.compile('(?:tina|ows)\.c([0-9]+)r([0-9]+)')
    object = 'instance'
    verb = 'summary'
    def fill_parser(self, parser):
        pass

    def execute(self, *args, **kwargs):
        size_usage = 0
        nb_core = 0
        ram_usage = 0
        cost = 0
        instances = {}
        for instance in self.ec2_object.get_all():
            result = Summary.tina_class_re.match(instance.instance_type)
            if result:
                instance_type = 'tina'
                instance_core = int(result.group(1))
                instance_ram = int(result.group(2))
                instance_cost = 0
            else:
                instance_type = instance.instance_type
                capa = Capacity.mapping[instance.instance_type]
                if capa.__class__ == ''.__class__ :
                    capa =  Capacity.mapping[capa]
                instance_core = capa[0]
                instance_ram = capa[1]
                instance_cost = capa[2]
            if not instance.state in instances:
                instances[instance.state] = {}
            if not instance_type in instances[instance.state]:
                instances[instance.state][instance_type] = 0
            instances[instance.state][instance_type] = instances[instance.state][instance_type] + 1
            if instance.state == 'running':
                nb_core = nb_core + instance_core
                ram_usage = ram_usage + instance_ram
                cost = cost + instance_cost
        yield {'instances': instances, 'nb_core': nb_core, 'ram_usage': ram_usage, 'cost': cost}
    
    def to_str(self, value):
        print value
        return """instances: %s
number of cores: %s
ram usage: %s
cost: %d euro/year
""" % ( len(value['instances']), value['nb_core'], value['ram_usage'],  value['cost'] * 24 * 365)
