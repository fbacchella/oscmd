from oslib.command import Command

class_ref = []

class ListInstanceProfiles(Command):
    object = 'iam'
    verb = 'list-instance-profiles'

    def execute(self, *args, **kwargs):
        profiles = self.ec2_object.run('list_instance_profiles')
        for p in profiles['instance_profiles']:
            yield p
    
    def to_str(self, status):
        return "name=%s, id=%s, arn=%s\n" % (status[u'instance_profile_name'], status[u'instance_profile_id'], status[ u'arn'])
class_ref.append(ListInstanceProfiles) 

class ListRoles(Command):
    object = 'iam'
    verb = 'list-roles'

    def execute(self, *args, **kwargs):
        roles = self.ec2_object.run('list_roles')
        for r in roles['roles']:
            yield r
    
    def to_str(self, status):
        return "name=%s, id=%s, arn=%s\n" % (status[u'role_name'], status[u'role_id'], status[ u'arn'])
class_ref.append(ListRoles) 

import dump
#from dump import DumpRole, DumpInstanceProfile
#from add import Add
#from policy import SetRolePolicy
#from list import List

#class_ref = [ DumpRole, DumpInstanceProfile, Add, ListInstanceProfiles, ListRoles, SetRolePolicy ]
