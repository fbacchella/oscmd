import boto

from oslib.command import Command
import urllib
import json
from oslib.iam import class_ref

#print dir(oslib)

class DumpRole(Command):
    object = 'iam'
    verb = 'dump-role'

    def fill_parser(self, parser):
        parser.add_option("-n", "--name", dest="name", help="instance profile name", default=None)

    def execute(self, *args, **kwargs):
        role = self.ec2_object.run('get_role', kwargs['name'])['role']
        role['policy_documents'] = []
        for policy_name in self.ec2_object.run('list_role_policies', kwargs['name'])['policy_names']:
            role['policy_documents'].append(self.ec2_object.run('get_role_policy', kwargs['name'], policy_name))
        return role 
        
    def to_str(self, role):
        status = """==== %s ====
  id: %s
  arn: %s
  policy:
""" % (role['role_name'], role['role_id'], role['arn'])
        for policy_infos in role['policy_documents']:
            status += "  " + policy_infos['policy_name'] + ":\n    "
            policy_document = json.dumps(urllib.unquote(policy_infos['policy_document']), sort_keys=True, indent=2, separators=(',', ': '))
            status += policy_document.replace("\\n", "\n    ").replace("\\", "")[1:-1];
        return status

class_ref.append(DumpRole)

class DumpInstanceProfile(DumpRole):
    object = 'iam'
    verb = 'dump-instance-role'

    def execute(self, *args, **kwargs):
        profile = self.ec2_object.run('get_instance_profile', kwargs['name'])['instance_profile']
        return super(DumpInstanceProfile, self).execute(name = profile['roles']['member']['role_name'])

class_ref.append(DumpInstanceProfile)
