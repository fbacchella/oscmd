from oslib.command import Command
import copy
import boto.exception

def parse_range(option, opt_str, value, parser, *args, **kwargs):

    if value.lower() == 'all':
        parser.values.from_port = -1
        parser.values.to_port = -1
    else:
        port_range = value.split(":")
        if len(port_range) == 1:
            parser.values.from_port = port_range[0]
            parser.values.to_port = port_range[0]
        elif len(port_range) == 2:
            parser.values.from_port = port_range[0]
            parser.values.to_port = port_range[1]
    delattr(parser.values, 'port_range')

def fill_sg_parser(parser):
        parser.add_option("-p", "--protocol", dest="ip_protocol", help="protocol allowed", default=[], action='append')
        parser.add_option("-P", "--port_range", dest="port_range", help="Port range (from[:to]|ALL)", default=None, action="callback", callback=parse_range, nargs=1, type="string")
        parser.add_option("-f", "--from", dest="from_port", help="Start port range", default=None)
        parser.add_option("-t", "--to", dest="to_port", help="end port range", default=None)
        parser.add_option("-m", "--mask", dest="cidr_ip", help="source network in CIDR notation", default=None)
        parser.add_option("-s", "--source_group", dest="src_group", help="source group", default=None)
    
class Authorize(Command):
    object = 'securitygroup'
    verb = 'add_rule'
    
    def fill_parser(self,parser):
        fill_sg_parser(parser)
        
    def execute(self, *args, **kwargs):
        kwargs['group_name'] = self.ec2_object.get().name
        src_group = kwargs['src_group']
        if src_group != None:
            (sg_owner_id,name) = src_group.split(':')
            kwargs['src_security_group_name'] = name
            kwargs['src_security_group_owner_id'] = sg_owner_id
            group = boto.ec2.securitygroup.SecurityGroup(connection=self.ctxt.cnx_ec2, owner_id=sg_owner_id, name=name)
        del kwargs['src_group']
        protos = kwargs['ip_protocol']
        del kwargs['ip_protocol']
        for proto in protos:
            sg_kswargs = copy.copy(kwargs)
            sg_kswargs['ip_protocol'] = proto.lower()
            if kwargs['from_port'] == -1 and kwargs['to_port'] == -1:
                if sg_kswargs['ip_protocol'] != 'icmp':
                    sg_kswargs['from_port'] = 0
                    sg_kswargs['to_port'] = 65535
            try:
                yield self.ctxt.cnx_ec2.authorize_security_group(**sg_kswargs)
            except boto.exception.EC2ResponseError as e:
                yield e.error_message
    
    def to_str(self, status):
        if status.__class__ == "".__class__:
            return status + "\n"
        elif not status:
            return status + "\n"

class DeAuthorize(Command):
    object = 'securitygroup'
    verb = 'remove_rule'
    
    def fill_parser(self,parser):
        fill_sg_parser(parser)
        
    def execute(self, *args, **kwargs):
        kwargs['group_name'] = self.ec2_object.get().name
        src_group = kwargs['src_group']
        if src_group != None:
            (sg_owner_id,name) = src_group.split(':')
            kwargs['src_security_group_name'] = name
            kwargs['src_security_group_owner_id'] = sg_owner_id
            group = boto.ec2.securitygroup.SecurityGroup(connection=self.conn, owner_id=sg_owner_id, name=name)
        del kwargs['src_group']
        
        return self.ctxt.cnx_ec2.revoke_security_group(**kwargs)

    def to_str(self, status):
        return status

