import boto
import optparse
from oslib import OSLibError
from oslib.ec2_objects import EC2Object

class command_info(object):
    def __init__(self, object, verb, class_ref=None):
        self.attrs = {
            'object': object,
            'verb': verb,
        }
        self.class_ref = class_ref

    def __call__(self, clazz):
        for (k, v) in self.attrs.items():
            setattr(clazz, k, v)
        if self.class_ref is not None:
            self.class_ref.append(clazz)
        return clazz

class Command(object):
    """A abstract class, used to implements actual verb"""
    def __init__(self):
        pass

    def set_context(self, ctxt):
        if ctxt != None:
            self.ctxt = ctxt
        else:
            raise NameError('Undefined context')
        
    def fill_parser(self, parser):
        pass

    def validate(self, options):
        """try to validate the object needed by the commande, should be overriden if the no particular object is expected"""
        if not self.ec2_object:
             raise OSLibError("id missing")
        self.ec2_object.get()
        return True
    
    def parse(self, args):
        parser = optparse.OptionParser(usage=self.__doc__)
        self.fill_parser(parser)

        (verb_options, verb_args) = parser.parse_args(args)

        return (verb_options, verb_args)

    def execute(self, *args, **kwargs):
        raise NameError('Not implemented')
    
    def to_str(self, value):
        if value == True:
            print "success"
        else:
            print value
    
    def status(self):
        """A default status command to run on success"""
        return 0;

class Dump(Command):
    def validate(self, options):
        if self.ec2_object.id or self.ec2_object.tag_name:
            self.ec2_object.get()
            return True
        return True

    def execute(self, *args, **kwargs):
        if self.ec2_object.id or self.ec2_object.tag_name:
            yield self.ec2_object.get()
        else:
            for ec2_object in self.ec2_object.get_all(*args, **kwargs):
                yield ec2_object

class List(Dump):
    pattern = '%(id)s %(name)s'
    def fill_parser(self, parser):
        super(List, self).fill_parser(parser)
        parser.add_option("-p", "--pattern", dest="pattern", help="output pattern, default: \n%s" % self.pattern, default=self.pattern)
        parser.add_option("-s", "--showattributes", dest="showattributes", default=False, action="store_true", help="list object attributes")

    def parse(self, args):
        (verb_options, verb_args) = super(List, self).parse(args)
        self.pattern = verb_options.pattern.decode('string_escape')
        delattr(verb_options, 'pattern')
        return (verb_options, verb_args)

    def execute(self, *args, **kwargs):
        showattributes = kwargs['showattributes']
        del kwargs['showattributes']
        for ec2_object in super(List, self).execute(*args, **kwargs):
            if not showattributes:
                yield ec2_object
            else: 
                yield ec2_object.__dict__
                break
                
    def to_str(self, instance):
        if instance.__class__ == {}.__class__:
            print ", ".join(instance.keys())
        else:
            values_map = {}
            if EC2Object.identify(instance).can_tag:
                if 'Name' in instance.tags:
                    values_map['name'] = instance.tags['Name']
                else:
                    values_map['name'] = ''
            for (name, body) in instance.__dict__.items():
                if dir(body).__contains__('__dict__'):
                    pass
                else:
                    values_map[name] = body
            for attr in values_map:
                value = None
                if attr == 'name' and 'tags' in vars(instance) and 'Name' in instance.tags:
                    value = instance.tags['Name']
                elif hasattr(instance, attr):
                    value = getattr(instance, attr)
                if value == None:
                    value = ''
                values_map[attr] = value
            return self.pattern % values_map + "\n"

class GenericExist(Command):
    """An almost empty command, used to generate a return code"""
    def validate(self, options):
        return True
        
    def fill_parser(self, parser):
        pass
    
    def execute(self, *args, **kwargs):
        #a trick to return an empty iterator
        return
        yield

    def status(self):
        """A default status command to run on success"""
        if not self.ec2_object:
             raise OSLibError("id missing")
        try:
            self.ec2_object.get()
        except boto.exception.EC2ResponseError as e:
            (object_type,code) = e.error_code.split('.')
            print e.error_code
            if code == u'NotFound':
                return 1
            else:
                raise e
        except OSLibError:
            return 1

        return 0

class AttachVolume(Command):

    def fill_parser(self, parser):
        if self.object == 'volume':
            other = 'instance'
        else:
            other = 'volume'
        parser.add_option("-d", "--device", dest="device", help="device", default=None)
        parser.add_option("-i", "--id", dest="id", help="%s id" % other, default=None)
        parser.add_option("-n", "--name", dest="name", help="%s name" % other, default=None)

    def execute(self, *args, **kwargs):
        raise NameError('Not implemented')
        
    def attach(self, volume, instance, device):
        i = instance.get()
        v = volume.get()
        if not device:
            devices = sorted(i.block_device_mapping.keys())
            last = devices[-1].replace("/dev/sd","")
            if last < "e":
                last = "e"
            device = "/dev/sd%s" % chr( ord(last[0]) + 1)
        elif device.rfind('/dev/') < 0:
            device = "/dev/" + device
        if v.attach(instance.id, device):
            return device
        else:
            return False

    def to_str(self, volume):
        if not volume:
            return "attachement failed"
        else:
            return "attached as %s" % volume

class Delete(Command):
    
    def execute(self, *args, **kwargs):
        self.ec2_object.delete(*args, **kwargs)
    
