import oslib
from oslib.command import Command
import subprocess

class SSH(Command):
    """
This class is used to launch an ssh connection to an instance
it use the config file to find identification information.
In section [Credentials], it uses the key_file and user values.
Argument can be given to ssh after a --"""
    object = 'instance'
    verb = 'ssh'

    def fill_parser(self, parser):
        parser.add_option("-u", "--user", dest="user", help="login user")

    def execute(self, *args, **kwargs):
        instance = self.ec2_object.get()
        if not self.ctxt.key_file:
            print "no private key file"
            return
        if not 'user' in kwargs or not kwargs['user']:
            kwargs['user'] = self.ctxt.user
        if not instance.public_dns_name or instance.state != 'running':
            raise oslib.OSLibError("connecting to an invalid state instance")
        ssh_args=["ssh", "-o", "UserKnownHostsFile=/dev/null",  "-x", "-o", "StrictHostKeyChecking=no", "-i", self.ctxt.key_file,  "-l", kwargs['user'], instance.public_dns_name]
        if len(args) > 0:
            ssh_args.extend(args[0])
        subprocess.call(ssh_args)
        yield None
