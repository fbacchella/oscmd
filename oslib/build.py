# A set of method to build an instance
import re
from oslib import osinit
import subprocess
import time
from oslib.mime_utils import MimeMessage, URL
import oslib.getuser as getuser
import os
import os.path
from boto.ec2.blockdevicemapping import BlockDeviceMapping, BlockDeviceType
from boto.ec2.networkinterface import NetworkInterfaceSpecification,NetworkInterfaceCollection
import oslib
import socket
import oslib.ec2_objects
import yaml

def parse_facts(option, opt_str, value, parser, *args, **kwargs):
    (key,value) = value
    local_facts = parser.values.local_facts
    if key in local_facts:
        local_facts[key].append(value)
    else:
        local_facts[key] = [value]

def file_parser(parser):
    parser.add_option("-n", "--name", dest="name", help="Instance name", default=None)
    parser.add_option("-s", "--volume_size", dest="volume_size", help="new volume size (GB)", default=[], action='append', type="int")
    parser.add_option("-i", "--snap_id", dest="snap_id", help="some snashop to generate volume from", default=[], action='append')
    parser.add_option("-U", "--url", dest="url_commands", help="URL to os-init command", default=[], action='append')
    parser.add_option("-t", "--instance-type", dest="instance_type", help="Specifies the type of instance to be launched.", default=None)
    parser.add_option("-p", "--placement", dest="placement", help="The availability zone in which to launch the instances")
    parser.add_option("-S", "--security_groups", dest="security_groups", help="The names of the security groups with which to associate instances", action='append')
    parser.add_option("-u", "--user", dest="user", help="login user", default=None)
    parser.add_option("-k", "--key_name", dest="key_name", help="key name", default=None)
    parser.add_option("-f", "--key_file", dest="key_file", help="key file", default=None)
    parser.add_option("-F", "--Fact", dest="local_facts", help="Local facts", default={}, action="callback", callback=parse_facts, nargs=2, type="string")
    parser.add_option("-H", "--hostname", dest="hostname", help="Set the hostname", default=None)
    parser.add_option("-T", "--template", dest="template", help="template file", default=None)
    parser.add_option("-r", "--ressource", dest="embedded_ressources", help="embedded ressource to add", default=[], action='append')
    parser.add_option("-R", "--ressources_dir", dest="ressources_dir", help="ressource dir search path", default=[], action='append')
    parser.add_option("-e", "--elastic_ip", dest="elastic_ip", help="create and associate an EIP for this vm", default=None, action="store_true")
    parser.add_option("-I", "--private_ip", dest="private_ip_address", help="set this IP, if instance is in a VPC", default=None)
    parser.add_option("-P", "--profile", dest="instance_profile_arn", help="The arn of the IAM Instance Profile (IIP) to associate with the instances.", default=None)
    parser.add_option("", "--subnet-id", dest="subnet_id", help="", default=None)

def build_user_data(user_data_properties, **kwargs):
    user_data = MimeMessage()
    
    hostname = kwargs.pop('hostname')
    if hostname != None:
        user_data.append("#!/bin/bash\nhostname %s && uname -a" % hostname)

    #Check for local facts
    local_facts = kwargs.pop('local_facts', None)
    if local_facts != None and len(local_facts) > 0:
        user_data_string = "---\n"
        for k,v in local_facts.iteritems():
            user_data_string += "%s: %s\n" % (k, ",".join(v))
        user_data.append(user_data_string, content_type='application/facter-yaml', filename='localfacts.yaml')

    if len(user_data_properties) != 0:
        user_data.append(user_data_properties)

    url_commands = kwargs.pop('url_commands', None)
    if url_commands != None:
        user_data.append(url_commands)
    
    embedded_commands = kwargs.pop('embedded_ressources', None)
    if embedded_commands != None:
        import oslib.resources
        root_embedded = oslib.resources.__path__
        search_path = [ root_embedded[0] ]
        search_path.extend(kwargs['ressources_dir'])
        for c in embedded_commands:
            # look for the ressource in the ressources search path
            for path in search_path:
                command_path = os.path.join(path, c)
                if os.path.exists(command_path):
                    user_data.append(content_file_path=command_path)

    del kwargs['ressources_dir']
    kwargs['user_data'] = "%s" % user_data
    return kwargs

def get_remote_user(ctxt, **kwargs):
    if 'user' not in kwargs or not kwargs['user']:
        remote_user = ctxt.user
    else:
        remote_user = kwargs['user']
    if 'user' in kwargs:
        del kwargs['user']
    return (remote_user, kwargs)

def get_key_file(ctxt, **kwargs):
    if 'key_file' not in kwargs or not kwargs['key_file']:
        key_file = ctxt.key_file
    else:
        key_file = kwargs['key_file']
    if 'key_file' in kwargs:
        del kwargs['key_file']
    return (key_file, kwargs)

tag_re = re.compile('tag:(.*)')

def do_tags(**kwargs):
    tags = {}
    for arg in kwargs.keys():
        match_tag = tag_re.match(arg)
        if match_tag!=None:
            key = match_tag.group(1)
            tags[key] = kwargs.pop(arg)

    name = kwargs.pop('name', None)
    if name != None:
        tags['Name'] = name
    
    if not 'creator' in tags:
        user = getuser.user
        tags['creator'] = user

    return (tags, kwargs)

def remote_setup(instance, remote_user, key_file):
    osinit_path = osinit.__file__
    if osinit_path.endswith('.pyc'):
        osinit_path = osinit_path[:len(osinit_path) - 1]
    remote_path="%s@%s:/tmp/osinit.py" % (remote_user, instance.public_dns_name)
    args=["scp", "-o", "GSSAPIAuthentication=no", "-o", "UserKnownHostsFile=/dev/null",  "-o", "StrictHostKeyChecking=no", "-i", key_file, osinit_path, remote_path]
    subprocess.call(args)

    for remote_cmd in ('yum install -y sudo', 'sudo -n python /tmp/osinit.py decode'):
        args=["ssh", "-tt", "-o", "GSSAPIAuthentication=no", "-o", "UserKnownHostsFile=/dev/null",  "-x", "-o", "StrictHostKeyChecking=no", "-i", key_file,  "-l", remote_user, instance.public_dns_name, remote_cmd]
        subprocess.call(args)
    
    # Eventually remove the ssh public host key
    args=["ssh-keygen", "-R", instance.public_dns_name]
    subprocess.call(args)
    args=["ssh-keygen", "-R", instance.ip_address]
    subprocess.call(args)
    
def parse_template(ctxt, template_file_name, kwargs):
    f = open(template_file_name)
    dataMap = yaml.safe_load(f)
    f.close()

    if not 'image_id' in kwargs or kwargs['image_id'] == None :
        ami_kwargs = {}
        if 'ami_name' in dataMap:
            ami_kwargs['name'] = dataMap['ami_name']
            del dataMap['ami_name']
        elif 'ami_id' in dataMap:
            ami_kwargs['id'] = dataMap['id']
            del dataMap['ami_id']
        ami = oslib.ec2_objects.AMI(ctxt, **ami_kwargs)
        ami.get()
        kwargs['image_id'] = ami.id

    # check all the values that needs to be an array
    for varg in ('security_groups', 'embedded_commands', 'snap_id'):
        if varg in dataMap:
            value = dataMap[varg]
            if [].__class__ == value.__class__:
               kwargs[varg] = value
            elif "".__class__ == value.__class__ or u"".__class__ == value.__class__:
                kwargs[varg] = [ value ]
            del dataMap[varg]

    if 'local_facts' in dataMap:
        local_facts = kwargs['local_facts']
        for k in dataMap['local_facts']:
            if not k in local_facts:
                local_facts[k] = dataMap['local_facts'][k]
        del dataMap['local_facts']
    for k in dataMap:
        if k in dataMap and (not k in kwargs or kwargs[k] == None or len(kwargs[k]) == {} or kwargs[k] == []):
            kwargs[k] = dataMap[k]
    return kwargs
    
def do_build(ctxt, **kwargs):
    conn = ctxt.cnx_ec2
    if 'template' in kwargs and kwargs['template']:
        template_file_name = kwargs['template']
        del kwargs['template']
        kwargs = parse_template(ctxt, template_file_name, kwargs)

    defaultrun = {'instance_type': 'm1.large', 'key_name': ctxt.key_name }
    for key in defaultrun:
        if key not in kwargs or kwargs[key] == None:
            kwargs[key] = defaultrun[key]
                        
    (remote_user, kwargs) = get_remote_user(ctxt, **kwargs)
    (key_file, kwargs) = get_key_file(ctxt, **kwargs)

    (tags,kwargs) = do_tags(**kwargs)

    if 'Name' not in tags:
        yield "instance name is mandatory"
        return
    
    try:
        oslib.ec2_objects.Instance(ctxt, name=tags['Name']).get()
        # if get succed, the name already exist, else get throws an exception
        yield "duplicate name %s" % tags['Name']
        return 
    except:
        pass
        
    user_data_properties = {}
    
    image = kwargs.pop('image_id', None)

    #
    # Check device mapping
    volumes = BlockDeviceMapping(conn)
    l = 'f'
    
    for volume_info in kwargs.pop('volume_size', []):
        volumes["/dev/sd%s"%l] = BlockDeviceType(connection=conn, size=volume_info)
        l = chr( ord(l[0]) + 1)

    # if drive letter is not d, some volumes definition was found
    if l != 'd':
        kwargs['block_device_map'] = volumes
        user_data_properties['volumes'] = ' '.join(volumes.keys())

    # after user_data_properties['volumes']  as the will be lvm'ed
    for snapshot_id in kwargs.pop('snap_id', []):
        volumes["/dev/sd%s"%l] = BlockDeviceType(connection=conn, snapshot_id=snapshot_id)
        l = chr( ord(l[0]) + 1)
    
    kwargs = build_user_data(user_data_properties, **kwargs)

    if kwargs['elastic_ip']:
        eip = True
    else:
        eip = False
    del kwargs['elastic_ip']

    for k in kwargs.keys()[:]:
        value = kwargs[k]
        if kwargs[k] == None:
            del(kwargs[k])
        elif value.__class__ == [].__class__ and len(value) == 0:
            del(kwargs[k])
    
    if 'private_ip_address' in kwargs and kwargs['private_ip_address']:
        netif_specification = NetworkInterfaceCollection()
        netif_kwargs = {}
        if kwargs['private_ip_address']:
            netif_kwargs['private_ip_address'] = kwargs['private_ip_address']
            del kwargs['private_ip_address']
        if 'associate_public_ip_address' in kwargs and kwargs['associate_public_ip_address']:
            netif_kwargs['associate_public_ip_address'] = kwargs['associate_public_ip_address']
            del kwargs['associate_public_ip_address']
        if 'security_groups' in kwargs and kwargs['security_groups']:
            netif_kwargs['groups'] = kwargs['security_groups']
            del kwargs['security_groups']
        
        netif_kwargs['subnet_id'] = kwargs['subnet_id']
        del kwargs['subnet_id']
        print netif_kwargs
        spec = NetworkInterfaceSpecification(**netif_kwargs)
        netif_specification.append(spec)   
        kwargs['network_interfaces'] = netif_specification

    reservation = conn.run_instances(image, **kwargs)
    instance = reservation.instances[0]
    # Quick hack to keep the selected remote user
    instance.remote_user = remote_user
    
    if len(tags) > 0:
        conn.create_tags([ instance.id ], tags)
        
    if instance.interfaces and len(instance.interfaces) > 0:
        for interface in instance.interfaces:
            conn.create_tags([ interface.id ], {'creator': tags['creator']})

    while instance.state != 'running' and instance.state != 'terminated':
        instance.update(True)
        yield (".")
        time.sleep(1)
    yield ("\n")
    
    if eip:
        ip = conn.allocate_address().public_ip
        conn.associate_address(instance_id = instance.id, public_ip=ip)
        conn.create_tags([instance.id], {"EIP": ip})

    #Update tag for this instance's volumes
    for device in instance.block_device_mapping:
        device_type = instance.block_device_mapping[device]
        (vol_tags, vol_kwargs) = do_tags(name='%s/%s' % (tags['Name'], device.replace('/dev/','')))
        conn.create_tags([ device_type.volume_id ], vol_tags)
    instance.update(True)

    while instance.state != 'terminated':
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect((instance.public_dns_name, 22))
            s.close()
            break
        except socket.error, msg:
            yield (".")
            s.close()
            time.sleep(1)
    yield ("\n")
    instance.key_file = key_file
    
    remote_setup(instance, remote_user, key_file)

    yield instance