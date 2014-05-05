import boto
import codecs
from oslib.command import Command, OSLibError
import time
import string
import difflib

class Console(Command):
    """This class is used to display the console of an existing instance
"""
    object = 'instance'
    verb = 'console'

    def fill_parser(self, parser):
        if self.object == 'volume':
            other = 'instance'
        else:
            other = 'volume'
        parser.add_option("-f", "--follow", dest="follow", help="follow console", default=False, action="store_true")


    def execute(self, *args, **kwargs):
        console_output = self.ec2_object.get().get_console_output()
        #A bug in outscale API, needs to skip time == 0
        if console_output.timestamp == '1970-01-01T00:00:00.000Z':
            raise OSLibError("broken console, stop/start the instance")
        yield console_output.output

        if not kwargs['follow']:
            return

        last_timestamp = console_output.timestamp
        last_buffer = console_output.output

        while True:
            line_found = False
            console_output = self.ec2_object.get().get_console_output()
            if console_output.timestamp == last_timestamp or not console_output.output or len(console_output.output) == 0:
                time.sleep(1)
                continue
            differ = difflib.SequenceMatcher(a=last_buffer, b=console_output.output)
            matched =  differ.get_matching_blocks()
            #print matched
            # SequenceMatcher add an empty match at the sequence's end
            # check if the sequence make sence, skip it otherwise
            if(len(matched) == 2 and matched[0].b == 0 and matched[1].size == 0):
                yield console_output.output[matched[0].size:]
            last_timestamp = console_output.timestamp
            last_buffer = console_output.output

    def to_str(self, line):
        #Strange things can appen on a console, don't fail on them
        return codecs.decode(line, 'ascii', 'replace')
