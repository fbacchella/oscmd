import oslib

class GetIp(oslib.command.Dump):
    object = 'eip'
    verb = 'dump'

    def to_str(self, addr):
            return """%s -> %s
""" % (addr.public_ip, addr.instance_id)
