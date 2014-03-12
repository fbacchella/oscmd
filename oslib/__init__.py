import boto
import codecs
import locale
import optparse
import sys

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

# needed because default unicode to ascii encoding is strict
# we will use replace instead
output_locale = locale.getpreferredencoding()

def unicodetoascii(string):
    return codecs.encode(string, output_locale, 'replace')

def print_run_phrase(context, ec2_object, verb, args=None, **kwargs):
    (cmd, executed) = run_phrase(context, ec2_object, verb, args, **kwargs)
    if cmd == None:
        print "invalid phrase '%s %s'" % (ec2_object.name, verb)
        return 255
    # If execute return a generator, iterate other it
    if executed.__class__.__name__ == 'generator':
        for s in executed:
            if s != None:
                string = cmd.to_str(s)
                if string:
                    print codecs.encode(string, output_locale, 'replace'),
                    sys.stdout.flush()
        return cmd.status()
    # An exception was catched, print it
    elif isinstance(executed, Exception):
        print "'%s %s' failed with \"%s\"" % (ec2_object.name, verb, executed.error_message)
    # Else if it return something, just print it
    elif executed != None and executed:
        string = cmd.to_str(executed)
        if string:
            print unicodetoascii(string),
        return cmd.status()
    #It return false, something went wrong
    elif executed != None:
        print "'%s %s' failed" % (ec2_object.name, verb)
    return 255

def run_phrase(context, ec2_object, verb, args=None, **kwargs):
    cmd = get_cmd(context, ec2_object, verb)
    if cmd:
        if args != None:
            (verb_options, verb_args) = cmd.parse(args)
            verb_options = vars(verb_options)
        else:
            (verb_options, verb_args) = (kwargs, [])
        try:
            if cmd.validate(args):            
                return (cmd, cmd.execute(verb_args, **verb_options))
        except (boto.exception.EC2ResponseError, OSLibError) as e:
            return (cmd, e)
    # Nothing done, return nothing
    return (None, None)
    
for lib in all_libs:
#    try:
            cmd_module = __import__(lib, globals(), locals(), [], -1)
#        try:
            for class_ref in cmd_module.class_ref:
                try:
                    verb_name = class_ref.verb
                    object_name = class_ref.object
                    if not object_name in objects:
                        objects[object_name] = {}
                    objects[object_name][verb_name] = class_ref
                except:
                    print "Invalid verb:", sys.exc_info()[0]
#        except:
#            print "Invalid lib:", sys.exc_info()[0]
#    except AttributeError as e:
#        print "%s is invalid action" % lib
