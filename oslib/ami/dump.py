import oslib

class Dump(oslib.command.Dump):
    object = 'ami'
    verb = 'dump'

    def to_str(self, ami):
        ret_value = """==== %s ====
    name: %s
    description: %s
    architecture: %s
    root_device_name: %s
    block_device_mapping = 
""" % (ami.id, ami.name, ami.description, ami.architecture, ami.root_device_name)
        for device in ami.block_device_mapping:
            device_type = ami.block_device_mapping[device]
            ret_value = """%s        %s:
            size: %s
            snapshot_id: %s
""" %(ret_value, (device), device_type.size, device_type.snapshot_id)
        return ret_value
