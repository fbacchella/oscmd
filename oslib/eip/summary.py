from oslib.command import Command

class Summary(Command):
    object = 'eip'
    verb = 'summary'
    def fill_parser(self, parser):
        pass

    def validate(self, options):
        return True

    def execute(self, *args, **kwargs):
        count = 0
        for snap in self.ec2_object.get_all():
            count = count + 1
        yield count

    def to_str(self, value):
        return "%d EIP reserved\n" % value