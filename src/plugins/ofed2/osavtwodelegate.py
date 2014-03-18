import amsoil.core.pluginsanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('ofed')

GSAv2DelegateBase = pm.getService('gsav2delegatebase')
gfed_ex = pm.getService('gfedv2exceptions')

config = pm.getService('config')
geniutil = pm.getService('geniutil')

class OSAv2Delegate(GSAv2DelegateBase):
    VERSION = '2'

    def get_version(self, client_cert):
        # no auth necessary
        certs = {"SFA": "1"}
        fields = {}
        for fname, f in self.SUPPLEMENTARY_FIELDS.iteritems():
            fields[fname] = {
                "TYPE" : f["TYPE"],
                "PROTECT" : f["PROTECT"]
            }
            if "CREATE" in f:
                fields[fname]["CREATE"] = f["CREATE"]
            if "SATCH" in f:
                fields[fname]["SATCH"] = f["SATCH"]
            if "UPDATE" in f:
                fields[fname]["UPDATE"] = f["UPDATE"]
        return self.VERSION, ['KEY'], certs, fields
