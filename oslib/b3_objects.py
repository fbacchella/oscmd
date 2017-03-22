import boto
import boto3
import boto.iam
from boto.ec2.connection import EC2Connection
from ec2_objects import OSDontExistError, ec2_objects, mapping, object_info
import botocore.client

from oslib import OSLibError

class OSDontExistError(OSLibError):
    pass


class B3Object(object):

    def __init__(self, context, **kwargs):
        self._get_done = False
        self.ctxt = context
        if 'object' in kwargs:
            self.ec2_object = kwargs['object']
            self._identify()
        elif 'id' in kwargs:
            self.id = kwargs['id']
        else:
            self.id = None
        if 'name' in kwargs:
            self.tag_name = kwargs['name']
        else:
            self.tag_name = None
        if 'arn' in kwargs:
            self.arn = kwargs['arn']
        if hasattr(self.__class__, 'client'):
            self.access_point = self.ctxt.client(self.__class__.client)
        elif hasattr(self.__class__, 'resource'):
            self.access_point = self.ctxt.client(self.__class__.resource)
        if self.__class__.can_tag:
            self.tags = {}

    def _identify(self):
        # The object was found
        # try to resolve for sure it's name and it's id
        if self.__class__.can_tag and self.ec2_object.tags:
            self.tags = self.ec2_object.tags
            if 'Name' in self.tags:
                self.tag_name = self.tags['Name']

        self.id = getattr(self.ec2_object, self.__class__.id_attr_name)

    def get_all(self, ids = None, filters = None):
        newkwargs = {}
        result =  getattr(self.access_point, self.__class__.get_all_func)(**newkwargs)
        del result['ResponseMetadata']
        return result

    def run(self, action_name, *kwargs):
        action = getattr(self.client, action_name)
        return action(**kwargs)


@object_info(get_all_func='list_gateways', client='storagegateway')
class StorageGateway(B3Object):

    def get_all(self, *args):
        result =  getattr(self.client, self.__class__.get_all_func)()
        for instance in result['Gateways']:
            sg = StorageGateway(self.ctxt, name=instance.pop('GatewayName'), arn=instance.pop('GatewayARN'), id=instance.pop('GatewayId'))
            setattr(sg, 'state', instance.pop('GatewayOperationalState'))
            setattr(sg, 'type', instance.pop('GatewayType'))
            map(lambda x: setattr(sg, x[0], x[1]), instance.items())
            yield sg

    def get(self, *args, **kwargs):
        if not self._get_done:
            arn = "arn:aws:storagegateway:%s:%s:gateway/%s" % (self.ctxt.name, self.ctxt.get_identity()[0], self.id)
            sg = getattr(self.client, 'describe_gateway_information')(GatewayARN=arn)
            setattr(self, 'type', sg.pop('GatewayType'))
            setattr(self, 'tag_name', sg.pop('GatewayName'))
            setattr(self, 'arn', sg.pop('GatewayARN'))
            setattr(self, 'state', sg.pop('GatewayState'))
            setattr(self, 'tz', sg.pop('GatewayTimezone'))
            setattr(self, 'interfaces', sg.pop('GatewayNetworkInterfaces'))
            sg.pop('ResponseMetadata')
            sg.pop('GatewayId')
            for (k, v) in sg:
                setattr(self, 'k', v)
        return self

    def disable(self):
        return self.run('disable_gateway', GatewayARN=self.arn)


@object_info(get_all_func='describe_instances', resource='ec2')
class Instance(B3Object):

    def get_all(self, *args):
        result =  getattr(self.client, self.__class__.get_all_func)()
        for instance in result['Gateways']:
            sg = StorageGateway(self.ctxt, name=instance.pop('GatewayName'), arn=instance.pop('GatewayARN'), id=instance.pop('GatewayId'))
            setattr(sg, 'state', instance.pop('GatewayOperationalState'))
            setattr(sg, 'type', instance.pop('GatewayType'))
            map(lambda x: setattr(sg, x[0], x[1]), instance.items())
            yield sg

    def get(self, *args, **kwargs):
        if not self._get_done:
            arn = "arn:aws:storagegateway:%s:%s:gateway/%s" % (self.ctxt.name, self.ctxt.get_identity()[0], self.id)
            sg = getattr(self.client, 'describe_gateway_information')(GatewayARN=arn)
            setattr(self, 'type', sg.pop('GatewayType'))
            setattr(self, 'tag_name', sg.pop('GatewayName'))
            setattr(self, 'arn', sg.pop('GatewayARN'))
            setattr(self, 'state', sg.pop('GatewayState'))
            setattr(self, 'tz', sg.pop('GatewayTimezone'))
            setattr(self, 'interfaces', sg.pop('GatewayNetworkInterfaces'))
            sg.pop('ResponseMetadata')
            sg.pop('GatewayId')
            for (k, v) in sg:
                setattr(self, 'k', v)
        return self

    def disable(self):
        return self.run('disable_gateway', GatewayARN=self.arn)

