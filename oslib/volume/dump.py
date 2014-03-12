import oslib

class Dump(oslib.command.Dump):
    object = 'volume'
    verb = 'dump'

    def to_str(self, volume):
        status = """==== %s ====
    size: %s
    status: %s
    snapshot_id: %s
""" % (volume.id, volume.size, volume.status, volume.snapshot_id)
        if volume.status == 'in-use':
            status += "    device: %s\n" % volume.attach_data.device

        if len(volume.tags.keys()) > 0:
            status += "    tags =\n"
            for k,v in volume.tags.items():
                status += "            %s: %s\n" % (k, v)

        return status