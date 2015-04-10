import sys
import re

all_libs = (
    'ami',
    'eip',
    'volume',
    'snapshot',
    'instance',
    'securitygroup',
    'keypair',
    'iam'
)

objects = {}

class OSLibError(Exception):
    def __init__(self, value):
        self.value = value
        self.error_message = value
        
    def __str__(self):
        return repr(self.value)

def join_default(val, default):
    for key in default:
        if key not in val:
            val[key] = default[key]
            
def get_cmd(context, ec2_object, verb):
    if ec2_object.name in objects and verb in objects[ec2_object.name]:
        cmd_class = objects[ec2_object.name][verb]
        cmd = cmd_class()
        cmd.set_context(context)
        cmd.ec2_object = ec2_object
        return cmd
          
    # Everything failed so return false
    return False

def run_phrase(context, ec2_object, verb, args=None, **kwargs):
    cmd = get_cmd(context, ec2_object, verb)
    if cmd:
        if args != None:
            (verb_options, verb_args) = cmd.parse(args)
            verb_options = vars(verb_options)
        else:
            (verb_options, verb_args) = (kwargs, [])
        if cmd.validate(args):            
            return (cmd, cmd.execute(verb_args, **verb_options))
    # Nothing done, return nothing
    return (None, None)

units = {
    'T': 1099511627776,
    'G': 1073741824,
    'M': 1048576,
    'K': 1024,
    'k': 1024,
    '': 1,
}
size_re = re.compile('(\\d+)([TGMKk]?)');

def parse_size(input_size, out_suffix="", default_suffix=None):
    matcher = size_re.match("%s" % input_size)
    if matcher is not None:
        value = float(matcher.group(1))
        suffix = matcher.group(2)
        if suffix == '' and default_suffix is not None:
            suffix = default_suffix
        return value * units[suffix] / units[out_suffix]


for lib in all_libs:
    cmd_module = __import__(lib, globals(), locals(), [], -1)
    for class_ref in cmd_module.class_ref:
        try:
            verb_name = class_ref.verb
            object_name = class_ref.object
            if not object_name in objects:
                objects[object_name] = {}
            objects[object_name][verb_name] = class_ref
        except:
            print "Invalid verb:", sys.exc_info()[0]
