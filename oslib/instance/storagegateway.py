import boto
import boto3
from oslib.command import Command
import time
import httplib
import urlparse
import botocore
import time
import oslib.b3_objects

class StorageGateway(Command):
    """
This class is used to start a existing instance"""
    object = 'instance'
    verb = 'storagegateway'

    def execute(self, *args, **kwargs):
        instance = self.ec2_object.get()
        sgwrapper = oslib.b3_objects.StorageGateway(self.ctxt)
        print sgwrapper.__dict__
        print sgwrapper.__class__.__dict__
        print sgwrapper.get_all()
        try:
            sg = self.ctxt.client('storagegateway')
            #print sg.__dict__
            #print sg.__class__
            #response = sg.list_gateways()
            #print response
            h1 = httplib.HTTPConnection(instance.public_dns_name)
            h1.request('GET', '/')
            resp =  h1.getresponse()
            resp.read()
            if resp.status == 302:
                o = urlparse.urlsplit(resp.getheader('Location'))
                query = urlparse.parse_qs(o.query)
                activationKey = query['activationKey'][0]
                #print "%s %s %s" % (instance.public_dns_name, resp.getheader('Location'), activationKey)
                #h1 = httplib.HTTPSConnection('console.aws.amazon.com')
                #h1.request('GET', '/storagegateway/home?activationKey=%s&gatewayType=CACHED' % activationKey)
                #resp =  h1.getresponse()
                #resp.read()
                #print resp.status
            time.sleep(5)
            kwargs = {
                'ActivationKey': activationKey,
                'GatewayName': 'newnae',
                'GatewayTimezone': 'GMT+1:00',
                'GatewayRegion': self.ctxt.b3s_sess.region_name,
                'GatewayType': 'FILE_S3'
            }
            print kwargs
            response = sg.activate_gateway(**kwargs)
            print response
        except boto.exception.EC2ResponseError as e:
            return e
        except Exception as e:
            print e
            print e.__dict__
            print e.__class__

    def to_str(self, status):
        return '%s starting' % self.ec2_object.id
