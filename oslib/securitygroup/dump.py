import oslib

class Dump(oslib.command.Dump):
    object = 'securitygroup'
    verb = 'dump'

    def to_str(self, sg):
        status = "==== %s ====\n" % sg.id
        status += "    name: %s\n" % sg.name
        status += "    owner_id: %s\n" % sg.owner_id
        status += "    description: %s\n" % sg.description
        status += "    rules:\n"
        for permissions in sg.rules:
            status += "        %s\t%s\t%s\n" % (permissions.ip_protocol, permissions.from_port, permissions.to_port)
            for grant in permissions.grants:
                status +=  "            %s\n" % (grant)
        return status