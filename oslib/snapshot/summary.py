from oslib.command import Command

class Summary(Command):
    object = 'snapshot'
    verb = 'summary'
    def fill_parser(self, parser):
        pass

    def execute(self, *args, **kwargs):
        size = 0
        for snap in self.ec2_object.get_all():
            size = size + snap.volume_size
        yield size

    def to_str(self, size):
        return size
