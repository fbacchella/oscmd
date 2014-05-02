import boto
import codecs
from oslib.command import Command
import time
import zlib
import string

class Console(Command):
    """
This class is used to display the console of an existing instance"""
    object = 'instance'
    verb = 'console'

    def fill_parser(self, parser):
        if self.object == 'volume':
            other = 'instance'
        else:
            other = 'volume'
        parser.add_option("-f", "--follow", dest="follow", help="follow console", default=False, action="store_true")


    def execute(self, *args, **kwargs):
        if not kwargs['follow']:
            console_output = self.ec2_object.get().get_console_output()
            if console_output.timestamp == '1970-01-01T00:00:00.000Z':
                yield "broken console, stop/start the instance"
                return
            for l in console_output.output.split('\n'):
                yield l
            return

        last_timestamp = None
        last_digest = None
        depth_search = 10

        while True:
            line_found = False
            console_output = self.ec2_object.get().get_console_output()
            if console_output.timestamp == '1970-01-01T00:00:00.000Z':
                yield "broken console, stop/start the instance"
                return
            #A bug in outscale API, needs to skip time == 0
            if console_output.timestamp == last_timestamp or not console_output.output or len(console_output.output) == 0:
                time.sleep(1)
                continue
            lines = console_output.output.split('\n')
            i = len(lines) - 1
            while i >= 0 and depth_search != 0 :
                l = lines[i]
                line_digest = zlib.adler32(l)
                if last_digest and last_digest ==  line_digest:
                    #skip this line
                    i += 1
                    break
                i -= 1
                depth_search -= 1
            for l in lines[max(i,0):]:
                yield l
                if len(l) > 0:
                    last_non_empty = l
            depth_search = -1
            last_digest = zlib.adler32(last_non_empty)
            last_timestamp = console_output.timestamp

    def to_str(self, line):
        return codecs.decode(line, 'ascii', 'replace') + "\n"
