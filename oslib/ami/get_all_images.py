from oslib import Command

class GetAllImages(Command):
    object = 'ami'
    verb = 'dump'
    def fill_parser(self, parser):
        pass

    def execute(self, *args, **kwargs):
        for ami in self.conn.get_all_images():
            print "==== %s ==== " % ami.id
            print "    name: %s" % ami.name
            print "    description: %s" % ami.description
            print "    architecture: %s" % ami.architecture
            print "    root_device_name: %s" % ami.root_device_name
            print "    block_device_mapping = "
            for device in ami.block_device_mapping:
                device_type = ami.block_device_mapping[device]
                print "        %s:" % (device)
                print "            size: %s" % device_type.size
                print "            snapshot_id: %s" % device_type.snapshot_id
            print
