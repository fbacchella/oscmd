import oslib
from oslib.command import Command, OSLibError
import subprocess
import os.path


class SSH(Command):
    """
This class is used to launch an ssh connection to an instance
it use the config file to find identification information.
In section [Credentials], it uses the key_file and user values.
Argument can be given to ssh after a --"""
    object = 'instance'
    verb = 'ssh'

    def fill_parser(self, parser):
        parser.add_option("-u", "--user", dest="user", help="login user", default=self.ctxt.user)
        parser.add_option("-f", "--key_file", dest="key_file", help="key file", default=self.ctxt.key_file)

    def execute(self, *args, **kwargs):
        instance = self.ec2_object.get()

        key_file = kwargs['key_file']
        if key_file is None or not os.path.exists(key_file):
            raise OSLibError("no accessible private key file: '%s'" % key_file)

        user = kwargs['user']
        if user is None:
            raise OSLibError("no defined user to user for the connection")

        if not instance.public_dns_name or instance.state != 'running':
            raise oslib.OSLibError("connecting to an invalid state instance")
        ssh_args = ["ssh", "-o", "UserKnownHostsFile=/dev/null",  "-x", "-o", "StrictHostKeyChecking=no",
                    "-i", key_file,  "-l", user, instance.public_dns_name]
        if len(args) > 0:
            ssh_args.extend(args[0])
        subprocess.call(ssh_args)
        yield None
