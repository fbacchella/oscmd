import boto

import urllib
import json
from oslib.iam import IamCommand

class SetRolePolicy(IamCommand):
    object = 'iam'
    verb = 'set-role-policy'

    def fill_parser(self, parser):
        parser.add_option("-p", "--policy", dest="policy", help="a policy string", default=None)
        parser.add_option("-f", "--policyfile", dest="policy_file", help="a policy file", default=None)

    def execute(self, *args, **kwargs):
        if kwargs['policy']:
            policy_document = urllib.quote(kwargs['policy'])
        elif kwargs['policy_file']:
            policy_file = open(kwargs['policy_file'], 'r')
            policy_json = json.load(policy_file)
            print json.dumps(policy_json, sort_keys=True, indent=2, separators=(',', ': '))
            policy_document = urllib.quote(json.dumps(policy_json))
        return run('put_role_policy', self.ec2_object.tag_name, 'aname', policy_document)
        
    def to_str(self, code):
        return code

