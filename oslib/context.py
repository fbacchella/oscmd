import boto
from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import RegionInfo
from boto.utils import retry_url

import oslib

class Context(object):
    def __init__(self, **kwargs):
        super(Context, self).__init__()
        
        # Ensure that no none keywords are given
        for k in kwargs.keys():
            if kwargs[k] == None:
                del kwargs[k]
            
        if 'config' in kwargs:
            self.config = kwargs['config']
            del kwargs['config']
        elif 'config_file' in kwargs and kwargs['config_file']:
            self.config = boto.pyami.config.Config(path=kwargs['config_file'])
            del kwargs['config_file']
        else:
            self.config = boto.config

        if 'security_credentials' in kwargs:
            import json
            credentials_url = 'http://169.254.169.254/latest/meta-data/iam/security-credentials/%s/' % kwargs['security_credentials']
            credentials = json.loads(retry_url(credentials_url, retry_on_404=False))
            identity_url = 'http://169.254.169.254/latest/dynamic/instance-identity/document'
            identity = json.loads(retry_url(identity_url, retry_on_404=False))
            kwargs['aws_access_key_id'] = credentials['AccessKeyId']
            kwargs['aws_secret_access_key'] = credentials['SecretAccessKey']
            self.security_token = credentials['Token']
            kwargs['ec2_region_name'] = identity['region']
            kwargs['ec2_region_endpoint'] = "ec2.%s.amazonaws.com" % identity['region']
            del kwargs['security_credentials']
        else:
            self.security_token = None
        
        # Manually check the config
        # save debug, it's used in each section
        if 'debug' in kwargs:
            debug = kwargs['debug']
            del kwargs['debug']
        else:
            debug = None
        for section_info in (('Boto',
                                ('num_retries', 'ec2_region_name', 'ec2_region_endpoint',
                                 'is_secure', 'default_ami', 'ami_provider')),
                         ('Credentials',
                                ('aws_access_key_id','aws_secret_access_key', 'key_name', 'key_file', 'user'))
                             ):
            section = section_info[0]
            if not self.config.has_section(section):
                self.config.add_section(section)
            for key in section_info[1]:
                if key in kwargs:
                    self.config.set(section, key, kwargs[key].__str__())
                    del kwargs[key]
            if debug:
                self.config.set(section, 'debug', debug.__str__())

        # Create object config
        self.object_defaults = {}
        for obj in oslib.objects.keys():
            self.object_defaults[obj] = {}
            if self.config.has_section(obj):
                for entry in self.config.items(obj):
                    self.object_defaults[obj][entry[0]] = entry[1]
                
        boto.config = self.config

        if debug >= 2:
            import StringIO
            fp = StringIO.StringIO()
            self.config.dump_safe(fp)
            print fp.getvalue()
        
        self.name = self.config.get('Boto','ec2_region_name')
        self.default_ami = self.config.get('Boto','default_ami')
        self.key_name = self.config.get('Credentials','key_name')
        self.key_file = self.config.get('Credentials','key_file')
        self.user = self.config.get('Credentials','user', 'root')

        if 'zone_name' in kwargs:
            self.zone = self.conn.get_all_zones(zones=[kwargs['zone_name']])[0]
            del kwargs['zone_name']
        else:
            self.zone = self.cnx_ec2.get_all_zones()[0]
        
    def get_region(self):
        region_name = self.config.get('Boto', 'ec2_region_name', EC2Connection.DefaultRegionName)
        region_endpoint = self.config.get('Boto', 'ec2_region_endpoint', EC2Connection.DefaultRegionEndpoint)
        return RegionInfo(None, region_name, region_endpoint)
        
    @property
    def cnx_ec2(self):
        if not '_cnx_ec2' in self.__dict__ or not self._cnx_ec2:
            kwargs = {}
            kwargs['aws_access_key_id'] = self.config.get('Credentials', 'aws_access_key_id',  None)
            kwargs['aws_secret_access_key'] = self.config.get('Credentials', 'aws_secret_access_key',  None)
            kwargs['region'] = self.get_region()
            if self.security_token:
                kwargs['security_token'] = self.security_token
            self._cnx_ec2 = EC2Connection(**kwargs)
        return self._cnx_ec2

    @property
    def cnx_iam(self):
        if not '_cnx_iam' in self.__dict__ or not self._cnx_iam:
            kwargs = {}
            kwargs['aws_access_key_id'] = self.config.get('Credentials', 'aws_access_key_id',  None)
            kwargs['aws_secret_access_key'] = self.config.get('Credentials', 'aws_secret_access_key',  None)
            if self.security_token:
                kwargs['security_token'] = self.security_token
            self._cnx_iam = boto.iam.connect_to_region('universal', **kwargs)
        return self._cnx_iam

    def get_identity(self):
        account_id = self.config.get('Account','id')
        account_email = self.config.get('Account','email')
        return (account_id, account_email)
        
