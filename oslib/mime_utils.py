from email import Encoders
from email.generator import Generator 
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from osinit import guess_mime_type
import StringIO

import mimetypes

mimetypes.init()
mimetypes.add_type("application/x-rpm", ".rpm", strict=False)

class URL(object):
    def __init__(self, url):
        self.url = url
    
    def __str__(self):
        return self.url.__str()

class MimeMessage(object):
    def __init__(self):
        self.__class__.__bases__[0].__init__(self)
        self.message = MIMEMultipart()

    def append(self, content=None, content_file_path=None, content_encondig=None, filename=None, content_type=None, **kwargs):
        if content_file_path:
            if content_type == None:
                (content_type, content_encondig) = mimetypes.guess_type(content_file_path, strict=False)
            if content == None:
                with open(content_file_path, 'r') as fh:
                    content = fh.read()

        content_class = content.__class__.__name__
        if content_class in self.mapper:
            message = self.mapper[content_class](self, content, **kwargs)
        else:
            if not content_type:
                content_type = guess_mime_type(content, 'binary/octet-stream')
            (maintype, subtype) = content_type.split('/')
            if maintype == 'text':
                message = MIMEText(content, _subtype=subtype)
            else:
                message = MIMEBase(maintype, subtype)
                message.set_payload(content)
                Encoders.encode_base64(message)
            
        if content_encondig != None:
            message['Content-Encoding'] =  content_encondig
        if filename != None:
            message.add_header('Content-Disposition', 'attachment', filename=filename)

        if message != None:
            self.message.attach(message)
    
    def text_content(self, content, subtype='plain'):
        return MIMEText(content, _subtype=subtype)
    
    def dict_content(self, content, empty=None):
        txt_content = ''
        for key in content:
            txt_content += '%s: %s\n' % (key, content[key])
        return self.text_content(txt_content, subtype='properties')
    
    def url_list(self, content, empty=None):
        txt_content = ''
        if len(content) == 0:
            return None
        for url in content:
            txt_content += '%s\n' % url
        return self.text_content(txt_content, subtype='x-include-url')
    
    def url_content(self, content, empty=None):
        return self.text_content(content.url, subtype='x-include-url')
    
    def __str__(self):
        buf = StringIO.StringIO()
        Generator(buf).flatten(self.message)
        return buf.getvalue()

MimeMessage.mapper = {
    {}.__class__.__name__: MimeMessage.dict_content,
    URL.__name__: MimeMessage.url_content,
    [].__class__.__name__: MimeMessage.url_list,
}
