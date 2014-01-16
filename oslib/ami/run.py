import oslib
from oslib.command import Command
from oslib import build

class Run(Command):
    """
This class is used to launch a new instance, that can be autoconfigured using a known puppet class"""
    object = 'ami'
    verb = 'run'

    def fill_parser(self, parser):
        super(Run, self).fill_parser(parser)
        build.file_parser(parser)
    
    def validate(self, options):
        if self.ec2_object.id or self.ec2_object.tag_name:
            self.ec2_object.get()
            return True
        return True

    def execute(self, *args, **kwargs):
        kwargs['image_id'] = self.ec2_object.id
        for val in build.do_build(self.ctxt, **kwargs):
            yield val

    def to_str(self, status):
        if status.__class__ == "".__class__ or status.__class__ == u"".__class__:
            return status
        else:
            instance = status
            key_file = self.ctxt.key_file
            if hasattr(instance, 'key_file'):
                key_file = instance.key_file
            message = "new instance %s launched\n" % instance.id
            message += "connect with\nssh -i %s %s@%s\n" % (key_file, instance.remote_user, instance.public_dns_name)
            return message
            
