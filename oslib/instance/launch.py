from oslib.command import Command
import oslib
from oslib import build

class LaunchInstance(Command):
    """
This class is used to launch a new instance, that can be autoconfigured using a known puppet class"""
    object = 'instance'
    verb = 'launch'
    def __init__(self):
        self.__class__.__bases__[0].__init__(self)

    def set_context(self, ctxt):
        self.__class__.__bases__[0].set_context(self, ctxt)

    def fill_parser(self, parser):
        build.file_parser(parser)
        parser.add_option("-a", "--ami", dest="image_id", help="AMI id", default=None)

    def validate(self, options):
        if not options.image_id:
            return False
        return True

    def execute(self, *args, **kwargs):
          for val in build.do_build(self.ctxt, self.conn, **kwargs):
              yield val

class_ref = [LaunchInstance]