import oslib
from oslib.ec2_objects import Volume

class Dump(oslib.command.Dump):
    object = 'instance'
    verb = 'dump'
    
    def execute(self, *args, **kwargs):
        for ec2_object in super(Dump, self).execute(args, kwargs):
            for device in ec2_object.block_device_mapping:
                volume = ec2_object.block_device_mapping[device]
                v_object = Volume(self.ctxt, id=volume.volume_id)
                volume.size = v_object.get().size
                volume.snapshot_id = v_object.get().snapshot_id
            yield ec2_object

    def to_str(self, instance):
        status = "==== %s ====\n" % (instance.id)
        if 'Name' in instance.tags:
            status += "    name: %s\n" % instance.tags['Name']
        status +=  "    state: %s\n" % instance.state
        if instance.state == 'running':
            status += "    private IP: %s\n" % instance.private_ip_address
            status += "    private DNS: %s\n" % instance.private_dns_name
            status += "    public IP: %s\n" % instance.ip_address
            status += "    public DNS: %s\n" % instance.public_dns_name
        status += "    instance type: %s\n" % instance.instance_type
        status += "    architecture: %s\n" % instance.architecture
        status += "    root_device_name: %s\n" % instance.root_device_name
        status += "    block_device_mapping = \n"
        for device in instance.block_device_mapping:
            device_type = instance.block_device_mapping[device]
            status += "        %s:\n" % (device)
            status += "            size: %s\n" % device_type.size
            status += "            volume_id: %s\n" % device_type.volume_id
            status += "            snapshot_id: %s\n" % device_type.snapshot_id
        if len(instance.tags.keys()) > 0:
            status += "    tags =\n"
            for k,v in instance.tags.items():
                status += "            %s: %s\n" % (k, v)
        if instance.instance_profile and len(instance.instance_profile.keys()) > 0:
            status += "     profile arn %s\n" % (instance.instance_profile['id'], instance.instance_profile['arn'])
        if instance.interfaces and len(instance.interfaces) > 0:
            print instance.interfaces
        return status