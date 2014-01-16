import oslib

class Dump(oslib.command.Dump):
    object = 'snapshot'
    verb = 'dump'

    def to_str(self, snap):
        ret_value = """==== %s ====
    description: %s
    size: %s
    volume_id: %s
    status: %s
""" % (snap.id, snap.description, snap.volume_size, snap.volume_id, snap.status)
        if snap.status != 'completed':
            ret_value = """%sprogress: %d
""" % (ret_value, snap.progress)
        return ret_value
        
