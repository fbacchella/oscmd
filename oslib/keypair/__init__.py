from oslib.command import Command

class_ref = []
class Save(Command):
    object = 'keypair'
    verb = 'save'

    def fill_parser(self,parser):
        parser.add_option("-n", "--name", dest="name", help="name", default=None)
        parser.add_option("-o", "--output-directory", dest="output", help="output directory", default="~/.ssh/")

    def execute(self, *args, **kwargs):
        keypair = self.conn.get_key_pair(kwargs['name'])
        keypair.save(kwargs['output'])

    def validate(self, options):
        return True
class_ref.append(Save)

class Create(Command):
    object = 'keypair'
    verb = 'create'

    def fill_parser(self,parser):
        parser.add_option("-n", "--name", dest="name", help="name", default=None)
        parser.add_option("-o", "--output-directory", dest="output", help="output directory", default="~/.ssh/")
        
    def execute(self, *args, **kwargs):
        keypair = self.conn.create_key_pair(kwargs['name'])
        keypair.save(kwargs['output'])

    def validate(self, options):
        return True
class_ref.append(Create)

import dump
