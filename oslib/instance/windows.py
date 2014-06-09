from oslib.command import Command
from oslib import OSLibError

import oslib.decrypt_windows_passwd

import getpass

class GetWindowsPassword(Command):
    object = 'instance'
    verb = 'getwinpass'

    def __init__(self):
        super(GetWindowsPassword, self).__init__()
        self.key = None

    def fill_parser(self, parser):
        parser.add_option("-f", "--key_file", dest="key_file", help="key file", default=None)

    def execute(self, *args, **kwargs):
        key_file = kwargs.pop('key_file')
        if key_file is None:
            key_file = self.ctxt.key_file

        instance = self.ec2_object.get()

        #Open your keyfile
        if self.key is None:
            try:
                self.key = oslib.decrypt_windows_passwd.import_rsa_key(key_file, None)
            except ValueError:
                passphrase = getpass.getpass('Encrypted Key Password (leave blank if none): ')
                self.key = oslib.decrypt_windows_passwd.import_rsa_key(key_file, passphrase)

        password_data = self.ctxt.cnx_ec2.get_password_data(instance.id)

        if password_data is None or len(password_data) < 1:
            raise OSLibError("invalid password data")

        return oslib.decrypt_windows_passwd.decryptPassword(self.key, password_data)
