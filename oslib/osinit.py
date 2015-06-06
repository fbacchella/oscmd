#!/usr/bin/python

import base64
import email
import gzip
import mimetypes
import optparse
import os
import stat
import subprocess
import sys
import tempfile
import time
import urllib
import urllib2

import StringIO

from email import Encoders
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart


def retry_url(url, retry_on_404=True, num_retries=10):
    for i in range(0, num_retries):
        try:
            req = urllib2.Request(url)
            resp = urllib2.urlopen(req)
            return resp.read()
        except urllib2.HTTPError, e:
            # in 2.6 you use getcode(), in 2.5 and earlier you use code
            if hasattr(e, 'getcode'):
                code = e.getcode()
            else:
                code = e.code
            if code == 404 and not retry_on_404:
                return ''
        except:
            pass
        time.sleep(2**i)
    return ''


def get_instance_userdata(version='latest', sep=None,
                          url='http://169.254.169.254'):
    ud_url = '%s/%s/user-data' % (url, version)
    user_data = retry_url(ud_url, retry_on_404=False)
    if user_data:
        if sep:
            l = user_data.split(sep)
            user_data = {}
            for nvpair in l:
                t = nvpair.split('=')
                user_data[t[0].strip()] = t[1].strip()
    return user_data


starts_with_mappings = {
    '#include': 'text/x-include-url',
    '#include-once': 'text/x-include-once-url',
    '#!': 'text/x-executable',
    '#cloud-config': 'text/cloud-config',
    '#upstart-job': 'text/upstart-job',
    '#part-handler': 'text/part-handler',
    '#cloud-boothook': 'text/cloud-boothook',
    '#cloud-config-archive': 'text/cloud-config-archive',
    'Content-Type: multipart/mixed': 'multipart/mixed',
    '---\n': 'text/x-yaml',
}


def guess_mime_type(content, deftype):
    rtype = deftype
    for possible_type, mimetype in starts_with_mappings.items():
        if content.startswith(possible_type):
            rtype = mimetype
            break

    return(rtype)


def write_mime_multipart(content, compress=False, deftype='text/plain'):
    wrapper = MIMEMultipart()
    for name, part_content, definite_type, content_encondig in content:
        if definite_type is None:
            definite_type = guess_mime_type(part_content, deftype)
        maintype, subtype = definite_type.split('/', 1)
        if maintype == 'multipart' or definite_type == 'message/rfc822':
            mime_con = MIMEBase(maintype, subtype)
            mime_con.set_payload(part_content)
        elif maintype == 'text' and content_encondig is None:
            mime_con = MIMEText(part_content, _subtype=subtype)
        else:
            mime_con = MIMEBase(maintype, subtype)
            mime_con.set_payload(part_content)
            # Encode the payload using Base64
            Encoders.encode_base64(mime_con)
        if content_encondig is not None:
            mime_con.add_header('Content-Encoding', content_encondig)
        if name is not None:
            mime_con.add_header('Content-Disposition', 'attachment', filename=name)
        wrapper.attach(mime_con)
    rcontent = wrapper.as_string()

    if compress:
        buf = StringIO.StringIO()
        gz = gzip.GzipFile(mode='wb', fileobj=buf)
        try:
            gz.write(rcontent)
        finally:
            gz.close()
        rcontent = buf.getvalue()

    return rcontent


class Command:
    def __init__(self):
        pass

    def get_parser(self):
        raise NameError('get_parser need to be overriden')
    
    def parse(self, args):
        parser = self.get_parser()
        (verb_options, verb_args) = parser.parse_args(args)

        if len(verb_args) > 0:
            print "unused arguments: %s" % verb_args
        self.execute(verb_args, **vars(verb_options))

    def execute(self, args, **kwargs):
        raise NameError('execute need to be overriden')


class MimeDecode(Command):
    url_opener = urllib.FancyURLopener()

    def get_parser(self):
        parser = optparse.OptionParser()
        parser.add_option("-f", "--file", dest="mime_file", help="MIME multipart file", default=None, action="append")
        parser.add_option("-u", "--URL", dest="mime_url", help="MIME multipart URL", default=None, action="append")
        parser.add_option("-p", "--packed", dest="do_unpack", help="needs to unpack user date", default=False, action="store_true")
        parser.add_option("-n", "--no-user-date", dest="get_user_date", help="Don't retrieve user data", default=True, action="store_false")

        return parser
    
    def execute(self, args, mime_file=None, mime_url=None, get_user_date=True, **kwargs):
        temp_dir = tempfile.mkdtemp()
        olddir = os.getcwd()
        os.chdir(temp_dir)
        self.enumerate(mime_file, self.get_file)
        self.enumerate(mime_url, self.get_url)
        if get_user_date:
            message = self.get_string(get_instance_userdata())
            self.walk_message(message)
        os.chdir(olddir)
    
    def enumerate(self, sources_list, callback):
        if sources_list is not None and len(sources_list) > 0:
            for source in sources_list:
                message = callback(source)
                if message is not None:
                    self.walk_message(message)

    def get_string(self, content):
        return email.message_from_string(content)

    def get_file(self, mime_file):
        if mime_file == '-':
            fh = sys.stdin
        else:
            fh = open(mime_file)
        message = email.message_from_file(fh)
        return message
        
    def get_url(self, url):
        fh = self.url_opener.open(url)
        txt_message = ''
        url_info = fh.info()
        for h in url_info.headers:
            txt_message += h
        txt_message += '\n'
        txt_message += fh.read()
        message = email.message_from_string(txt_message)
        return message
    
    def walk_message(self, msg):
        #depth first, goes into sub-part
        # walk return the object itself, so the first part is skipped
        first = True
        if msg.is_multipart() or msg.get_content_maintype() == 'multipart':
            for part in msg.walk():
                # skip the first part, it's the whole message again
                if first:
                    first = False
                    continue
                self.walk_message(part)
        else:
            content_type = msg.get_content_type()
            main_type = msg.get_content_maintype()
            if content_type in self.mime_action:
                self.mime_action[content_type](self, msg)
            elif main_type in self.mime_action:
                self.mime_action[main_type](self, msg)
            else:
                self.extract_file(msg)

    def walk_include(self, msg):
        for l in msg.get_payload(None, True).splitlines():
            l = l.strip()
            if l.find('http://') == 0:
                message = self.get_url(l)
                self.walk_message(message)
        return
    
    def extract_file(self, msg, file_name=None, overwrite=None, autoname=False):
        if file_name is None:
            file_name = msg.get_filename()
            
        if file_name is None:
            if autoname:
                (fd, file_name) = tempfile.mkstemp(dir=".")
                os.close(fd)
                overwrite = True
            else:
                return None
        
        # if overwrite not given, take it from headers
        if overwrite is None:
            # Convert a string to a boolean, empty string is false, don't care about the case        
            overwrite = (("%s" % msg.get('X-overwrite'))[0].upper() == 'T')
            
        # We don't override file
        if os.path.isfile(file_name) and not overwrite:
            return os.path.abspath(file_name)
            
        fh = open(file_name, "w")
        fh.write(msg.get_payload(None, True))
        fh.close()
        if msg.get('Content-Encoding') == 'gzip':
            subprocess.call(["gunzip", file_name])
        if 'X-Owner' in msg:
            try:
                import grp
                import pwd
                (user, group) = msg.get('X-Owner').split(':')
                uid = pwd.getpwnam(user).pw_uid
                gid = grp.getgrnam(group).gr_gid
                os.chown(file_name, uid, gid)
            except:
                print "invalid owner: %s for %s" % (msg.get('X-Owner'), file_name)
        if 'X-Mode' in msg:
            try:
                mode = int(msg.get('X-Mode'), 8)
                os.chmod(file_name, mode)
            except:
                print "invalid mode: %s for %s" % (msg.get('X-Mode'), file_name)
        return os.path.abspath(file_name)
    
    def run_command(self, msg):
        cmd_file = self.extract_file(msg, autoname=True)
        print cmd_file
        if cmd_file is not None:
            os.chmod(cmd_file, stat.S_IXUSR | stat.S_IRUSR)
            try:
                subprocess.call([cmd_file], stdout=sys.stdout)
                os.unlink(cmd_file)
            except Exception as e:
                print "execution of %s failed with %s" % (cmd_file, e)

    def run_shell_command(self, msg):
        cmd_file = self.extract_file(msg, autoname=True)
        print cmd_file
        if cmd_file is not None:
            os.chmod(cmd_file, stat.S_IXUSR | stat.S_IRUSR)
            try:
                subprocess.call(["/bin/sh", cmd_file], stdout=sys.stdout)
                os.unlink(cmd_file)
            except Exception as e:
                print "execution of %s failed with %s" % (cmd_file, e)

    def install_rpm(self, msg):
        rpm_file = self.extract_file(msg, autoname=True)
        if rpm_file is not None:
            try:
                os.rename(rpm_file, "%s.rpm" % rpm_file)
                subprocess.call(["/usr/bin/yum", "-y", "install", "%s.rpm" % rpm_file], stdout=sys.stdout)
            except Exception as e:
                print "installation of %s failed with %s" % (rpm_file, e)

    def facter_fact(self, msg):
        file_name = os.path.basename(msg.get_filename())
        file_name = os.path.splitext(file_name)[0]
        if file_name is None:
            return None
        
        if not os.path.isdir('/etc/facter/facts.d'):
            os.makedirs('/etc/facter/facts.d')
        file_name = '/etc/facter/facts.d/%s.yaml' % file_name
        file_name = self.extract_file(msg, file_name=file_name, overwrite=True)
        os.chmod(file_name, 0)
        os.chmod(file_name, stat.S_IRUSR | stat.S_IWUSR)
    
    def set_properties(self, msg):
        for l in msg.get_payload().splitlines(False):
            unsafe_vars = ['PATH', 'IFS', 'HOME']
            l = l.strip()
            (key, value) = l.split(':', 1)
            key = key.strip()
            value = value.strip()
            if key in unsafe_vars:
                continue
            os.environ[key] = value

    def install_packages(self, msg):
        packages_cmd = ["/usr/bin/yum", "-y", "install"]
        for l in msg.get_payload().splitlines(False):
            packages_cmd.append(l.strip())
        try:
            subprocess.call(packages_cmd, stdout=sys.stdout)
        except Exception as e:
            print "installation of packages failed with: %s" % e


MimeDecode.mime_action = {
    'text/x-include-url': MimeDecode.walk_include,
    'text/x-shellscript': MimeDecode.run_shell_command,
    'text/x-executable': MimeDecode.run_command,
    'text/x-python': MimeDecode.run_command,
    'application/facter-yaml': MimeDecode.facter_fact,
    'text/properties':  MimeDecode.set_properties,
    'text/plain': MimeDecode.extract_file,
    'application/x-rpm': MimeDecode.install_rpm,
    'text/x-packagelist': MimeDecode.install_packages,
}


class MimeEncode(Command):
    mimetypes.init()

    def get_parser(self):
        parser = optparse.OptionParser()
        parser.add_option("-f", "--file", dest="file_list", help="Files to add", default=[], action="append")
        parser.add_option("-p", "--pack", dest="do_pack", help="needs to pack user date", default=False, action="store_true")
        parser.add_option("-y", "--yaml_content", dest="yaml_content_file", help="The content as a yaml file", default=None, action="store")
        return parser

    def execute(self, args, yaml_content_file=None, file_list=[], **kwargs):
        content = []
        if yaml_content_file is not None:
            # yaml is not a default module
            # so import only when it's needed
            import yaml
            # the yaml file is an array of mime headers
            with open(yaml_content_file, "r") as yaml_file:
                yaml_content = yaml.safe_load(yaml_file)
            for entry in yaml_content:
                mimetype = None
                file_name = None
                contentencondig = None
                source = None
                entry_content = None
                if 'source' in entry and 'content' in entry:
                    print >> sys.stderr, "invalid entry, both source and content given, source is '%s'" % source
                    continue
                if 'source' in entry:
                    source = entry.pop('source')
                    file_name = source
                if 'file_name' in entry:
                    file_name = entry.pop('file_name')
                if source is not None:
                    with open(source) as fh:
                        entry_content = fh.read()
                if 'content' in entry:
                    entry_content = entry.pop('content')
                if 'Content-Type' in entry:
                    mimetype = entry['Content-Type']
                if 'Content-Encoding' in entry:
                    contentencondig = entry['Content-Encoding']
                if mimetype is None:
                    (mimetype, contentencondig) = mimetypes.guess_type(source, strict=False)

                print >> sys.stderr, "%s %s %s" % (file_name, mimetype, contentencondig)
                content.append((file_name, entry_content, mimetype, contentencondig))

        for file_name in file_list:
            try:
                # Try to split on ;
                # the content type is after the ;
                mime_guess = file_name.split(";")
                if(len(mime_guess)) > 1:
                    mimetype = mime_guess[1]
                    contentencondig = None
                    file_name = mime_guess[0]
                else:
                    (mimetype, contentencondig) = mimetypes.guess_type(file_name, strict=False)
                with open(file_name) as fh:
                    content.append((file_name, fh.read(), mimetype, contentencondig))
            except Exception as e:
                print "error while parsing file %s: %s" % (file_name, e)
                
        if kwargs['do_pack']:
            print base64.b64encode(write_mime_multipart(content, compress=True))
        else:
            print write_mime_multipart(content, compress=False)


def main():
    commands = {
        'encode': MimeEncode(),
        'decode': MimeDecode(),
    }

    usage = "usage: %%prog [options] verb verbs_args\nverbs are:\n    %s" % "\n    ".join(commands.keys())
        
    parser = optparse.OptionParser(usage=usage)
    parser.disable_interspersed_args()

    (options, args) = parser.parse_args()

    if len(args) > 0:
        verb = args.pop(0)
        cmd = commands[verb]
        cmd.parse(args)
    else:
        print 'action missing'
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)
