import boto

from oslib.command import Command

class List(Command):
    object = 'iam'
    verb = 'list'

    def fill_parser(self, parser):
        parser.add_option("-i", "--instance", dest="instance", help="list instance profile", default=False, action='store_true')
        parser.add_option("-r", "--roles", dest="roles", help="list roles", default=False, action='store_true')

    def execute(self, *args, **kwargs):
        iamcnx = self.ec2_object.get()

        force=False
        if 'instance' in kwargs and kwargs['instance']:
            profiles = iamcnx.list_instance_profiles()
            for p in profiles['list_instance_profiles_response']['list_instance_profiles_result']['instance_profiles']:
                yield p
        if 'roles' in kwargs and kwargs['roles']:
            roles = iamcnx.list_roles()
            for r in roles[u'list_roles_response'][u'list_roles_result']['roles']:
                yield r
    
    def to_str(self, status):
        if u'instance_profile_name' in status:
            return "name=%s, id=%s, arn=%s\n" % (status[u'instance_profile_name'], status[u'instance_profile_id'], status[ u'arn'])
        if u'role_name' in status:
            return "name=%s, id=%s, arn=%s\n" % (status[u'role_name'], status[u'role_id'], status[ u'arn'])
        else:
            return status
            
