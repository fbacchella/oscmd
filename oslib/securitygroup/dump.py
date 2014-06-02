import oslib

class Dump(oslib.command.Dump):
    object = 'securitygroup'
    verb = 'dump'

    def fill_parser(self,parser):
        parser.add_option("-u", "--used", dest="used", help="Only used security group", default=False, action='store_true')
        
    def execute(self, *args, **kwargs):
        only_used = kwargs.pop('used')
        for sg in super(Dump, self).execute(*args, **kwargs):
            instances =  sg.instances()
            sg.instances = instances
            if (not only_used) or (only_used and len(instances) > 0) :
                yield sg
        
    def to_str(self, sg):
        status = "==== %s ====\n" % sg.id
        status += "    name: %s\n" % sg.name
        status += "    owner_id: %s\n" % sg.owner_id
        status += "    description: %s\n" % sg.description
        status += "    used by: [ %s ]\n" % reduce(lambda x, y: "%s, %s" % (x, y.id) , sg.instances, "")[2:]
        status += "    rules:\n"
        for permissions in sg.rules:
            from_port = int(permissions.from_port)
            to_port = int(permissions.to_port)
            if permissions.ip_protocol == 'icmp' and from_port == -1 and to_port == -1:
                port_range = 'ALL'
            elif from_port == 0 and to_port == 65535:
                port_range = 'ALL'
            elif from_port == to_port:
                port_range = permissions.from_port
            else:
                port_range = "%s-%s" % ( permissions.from_port, permissions.to_port )
            status += "        % 4s/%s\n" % ( permissions.ip_protocol, port_range )
            for grant in permissions.grants:
                status +=  "            %s\n" % (grant)
        return status
