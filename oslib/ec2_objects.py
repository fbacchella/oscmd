import boto
import boto.iam
from boto.ec2.connection import EC2Connection

from oslib import OSLibError

ec2_objects = {}

class OSDontExistError(OSLibError):
    pass
    
class EC2Object(object):
    can_tag = True
    id_attr_name = 'id'
    
    @staticmethod
    def identify(obj):
        clazz =  mapping["%s.%s" % (obj.__class__.__module__, obj.__class__.__name__)]
        return clazz
    
    """A abstract class, used to implements actual ec2 objects"""
    def __init__(self, context, **kwargs):
        self.ctxt = context
        if 'object' in kwargs:
            self.ec2_object = kwargs['object']
            self._identify()
        elif 'id' in kwargs:
            self.id = kwargs['id']
        else:
            self.id = None
        if 'name' in kwargs:
            self.tag_name = kwargs['name']
        else:
            self.tag_name = None
        self.ec2_object = None
        if self.__class__.can_tag:
            self.tags = {}

    def _identify(self):
        # The object was found
        # try to resolve for sure it's name and it's id
        if self.__class__.can_tag and self.ec2_object.tags:
            self.tags = self.ec2_object.tags
            if 'Name' in self.tags:
                self.tag_name = self.tags['Name']
        self.id = self.ec2_object.__getattribute__(self.__class__.id_attr_name)
        
    def get(self):
        if self.ec2_object:
            return self.ec2_object
        search_by = ''
        if self.id:
            search_by = self.id
            self.ec2_object = self.get_by_id(self.id)
        elif self.tag_name:
            search_by = self.tag_name
            self.ec2_object = self.get_by_name(self.tag_name)
        
        if self.ec2_object == None:
            raise OSDontExistError("The %s '%s' does not exist" % (self.name, search_by))
        
        self._identify()
        return self.ec2_object
    
    def exist(self):
        try:
            self.ec2_object = None
            self.get()
            return True
        except OSDontExistError:
            return False
            
    def get_by_id(self, id):
        found = self.get_all([id])
        if (found.__class__.__name__ == 'ResultSet' or found.__class__.__name__ == 'list') and len(found) == 1:
            return found[0]
        else:
            return None
    
    def get_by_name(self, name):
        get_all = self.__class__.get_all_func
        can_tag = self.__class__.can_tag
        if can_tag:
            found = get_all(self.ctxt.cnx_ec2, filters = {'tag:Name': name})
            if found.__class__.__name__ == 'ResultSet' and len(found) == 1:
                return found[0]
            return None
        else:
            return None
    
    def get_all(self, ids = None, filters = None):
        newkwargs = {}
        if ids != None:
            newkwargs[self.get_all_ids] = ids
        if filters != None:
            newkwargs['filters'] = filters
        return self.__class__.get_all_func(self.ctxt.cnx_ec2, **newkwargs)
    
    def delete(self):
        self.get().delete()
    
    def state(self):
        self.get().update(True)
        return self.get().state
        
class AMI(EC2Object):
    name = 'ami'
    get_all_func = EC2Connection.get_all_images
    get_all_ids = 'image_ids'

    @staticmethod
    def set_parser(parser_object):
        parser_object.add_option("-s", "--self", dest="self_id", action='store_true', default=False, help="get the AMI from the running system")

    def __init__(self, *args, **kwargs):
        if 'self_id' in kwargs and kwargs['self_id']:
            kwargs['id'] = boto.utils.get_instance_metadata(timeout=1, num_retries=2)['ami-id']
        super(AMI, self).__init__(*args, **kwargs)

    def get_by_name(self, name):
        get_all = self.__class__.get_all_func
        can_tag = self.__class__.can_tag
        if can_tag:
            found = get_all(self.ctxt.cnx_ec2, filters = {'name': name})
            if found.__class__.__name__ == 'ResultSet' and len(found) == 1:
                return found[0]
            return None
        else:
            return None

ec2_objects[AMI.name] = AMI

class Instance(EC2Object):
    name = 'instance'
    get_all_func = EC2Connection.get_all_instances
    get_all_ids = 'instance_ids'
    
    @staticmethod
    def set_parser(parser_object):
        parser_object.add_option("-s", "--self", dest="self_id", action='store_true', default=False, help="the instance is the running system")

    def __init__(self, *args, **kwargs):
        if 'self_id' in kwargs and kwargs['self_id']:
            kwargs['id'] = boto.utils.get_instance_metadata(timeout=1, num_retries=2)['instance-id']
        super(Instance, self).__init__(*args, **kwargs)

    def get_by_name(self, name):
        reservation = super(Instance, self).get_by_name(name)
        if reservation != None and len(reservation.instances) == 1:
            return reservation.instances[0]
        else:
            return None

    def get_all(self, ids = None):
        instances = []
        for r in super(Instance, self).get_all(ids):
            for i in r.instances:
                instances.append(i)
        return instances
    
    def eip(self):
        self.get()
        if 'EIP' in self.tags and self.tags['EIP']:
            return EIP(self.ctxt, id=self.tags['EIP'])
        else:
            return None
    
    def volumes(self):
        instance = self.get()
        for device in instance.block_device_mapping:
            device_type = instance.block_device_mapping[device]
            yield Volume(self.ctxt, id=device_type.volume_id)
    
    def delete(self):
        self.get().terminate()

    def stop(self, force):
        self.get().stop(force)

    def reboot(self):
        self.get().reboot()

ec2_objects[Instance.name] = Instance

class EIP(EC2Object):
    can_tag = False
    id_attr_name = 'public_ip'
    name = 'eip'
    get_all_func = EC2Connection.get_all_addresses
    get_all_ids = 'addresses'
    
    def get_all(self, ids = None):
        list_eip = super(EIP, self).get_all(ids)
        for eip in list_eip:
            eip.id = eip.public_ip
        return list_eip

ec2_objects[EIP.name] = EIP

class Volume(EC2Object):
    name = 'volume'
    get_all_func = EC2Connection.get_all_volumes
    get_all_ids = 'volume_ids'
    
    def validate(self, verb):
        return True

    def state(self):
        self.get().update(True)
        return self.get().status

ec2_objects[Volume.name] = Volume

class SecurityGroup(EC2Object):
    name = 'securitygroup'
    get_all_func = EC2Connection.get_all_security_groups
    get_all_ids = 'group_ids'

    #the name is not a tag for security groups
    def get_by_name(self, name):
        get_all = self.__class__.get_all_func
        found = get_all(self.ctxt.cnx_ec2, groupnames = [name] )
        if found.__class__.__name__ == 'ResultSet' and len(found) == 1:
            return found[0]
        return None

ec2_objects[SecurityGroup.name] = SecurityGroup

class Snapshot(EC2Object):
    name = 'snapshot'
    get_all_func = EC2Connection.get_all_snapshots
    get_all_ids = 'snapshot_ids'

ec2_objects[Snapshot.name] = Snapshot

class KeyPair(EC2Object):
    can_tag = False
    name = 'keypair'
    get_all_func = EC2Connection.get_all_key_pairs
    get_all_ids = 'keynames'

    #the name is not a tag for key pairs
    def get_by_name(self, name):
        return EC2Connection.get_key_pair(name)

    #key pairs don't have ids, only names
    def get_by_id(self, id):
        return get_by_name(self, id)

ec2_objects[KeyPair.name] = KeyPair

class Iam(EC2Object):
    can_tag = False
    name = 'iam'
    iamcnx = None
    
    def get(self):
        return self.ctxt.cnx_iam

    def delete(self):
        pass
    
    def state(self):
        return self

    def run(self, command_name, *args, **kwargs):
        self.get()
        command = getattr(self.ctxt.cnx_iam, command_name)
        command_run =  command(*args, **kwargs)
        response = command_run['%s_response' % command_name]
        result = response['%s_result' % command_name]
        return result

ec2_objects[Iam.name] = Iam


mapping = {
    "boto.ec2.instance.Instance": Instance,
    "boto.ec2.image.Image": AMI,
    'boto.ec2.address.Address': EIP,
    'boto.ec2.snapshot.Snapshot': Snapshot,
    'boto.ec2.securitygroup.SecurityGroup': SecurityGroup,
    'boto.ec2.volume.Volume': Volume,
    'boto.iam.connection.IAMConnection': Iam,
}
