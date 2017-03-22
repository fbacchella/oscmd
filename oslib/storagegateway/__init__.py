import oslib.command

class_ref = []

@oslib.command.command_info(object='storagegateway', verb='list', class_ref=class_ref)
class List(oslib.command.List):
    def execute(self, *args, **kwargs):
        showattributes = kwargs['showattributes']
        del kwargs['showattributes']
        for ec2_object in super(List, self).execute(*args, **kwargs):
            if not showattributes:
                yield ec2_object
            else:
                if isinstance(ec2_object, dict):
                    yield ec2_object
                else:
                    yield ec2_object.__dict__
                break


@oslib.command.command_info(object='storagegateway', verb='dump', class_ref=class_ref)
class Dump(oslib.command.Dump):
    def to_str(self, gateway):
        ret_value = "==== %s ====\n" % gateway.id
        ret_value += "    name: %s\n" % gateway.tag_name
        for k in ('type', 'state', 'tz'):
            if hasattr(gateway, k):
                ret_value += "    %s: %s\n" % (k, getattr(gateway, k))
        if hasattr(gateway, 'interfaces'):
            ret_value += "    IP:\n"
            for ip in getattr(gateway, 'interfaces'):
                ret_value += "        %s\n" % ip.values()[0]
        if len(gateway.tags.keys()) > 0:
            ret_value += "    tags =\n"
            for k, v in gateway.tags.items():
                ret_value += "            %s: %s\n" % (k, v)
        return ret_value


@oslib.command.command_info(object='storagegateway', verb='disable', class_ref=class_ref)
class Disable(oslib.command.Command):
    def execute(self, *args, **kwargs):
        self.ec2_object.disable()


@oslib.command.command_info(object='storagegateway', verb='start', class_ref=class_ref)
class Start(oslib.command.Command):
    pass


