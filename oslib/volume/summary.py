from oslib.command import Command

class Summary(Command):
    object = 'volume'
    verb = 'summary'
    def fill_parser(self, parser):
        pass

    def execute(self, *args, **kwargs):
        size = 0
        for volume in self.ec2_object.get_all():
            size = size + volume.size
        yield size

    def to_str(self, value):
        return value