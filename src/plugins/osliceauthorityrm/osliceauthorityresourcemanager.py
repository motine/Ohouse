import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('osliceauthorityrm')

from osliceauthorityexceptions import *

class OSliceAuthorityResourceManager(object):

    def __init__(self):
        super(OSliceAuthorityResourceManager, self).__init__()