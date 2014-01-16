from oslib.command import Command

class Share(Command):
    object = 'ami'
    verb = 'share'
    
    def fill_parser(self, parser):
        super(Share, self).fill_parser(parser)
        default_share_users = []
        if 'share_users' in self.ctxt.object_defaults['ami']:
            for user in self.ctxt.object_defaults['ami']['share_users'].split(','):
                default_share_users.append(user.strip())
        parser.add_option("-u", "--users", dest="users", help="Users list, default: %s" % ", ".join(default_share_users), default=default_share_users, action="append")

    def execute(self, *args, **kwargs):
        ami = self.ec2_object.get()
        user_id = kwargs['users']
        return ami.set_launch_permissions(user_ids=user_id)
