import oslib
from oslib.keypair import class_ref

class Dump(oslib.command.Dump):
    object = 'keypair'
    verb = 'dump'

    def to_str(self, kp):
        return """%s : %s
""" % (kp.name, kp.fingerprint)

class_ref.append(Dump)
