from amsoil.core import pluginmanager as pm


import ext.geni

def setup():
    # setup config items
    # config = pm.getService("config")
    # config.install("worker.dbpath", "deploy/worker.db", "Path to the worker's database (if relative, AMsoil's root will be assumed).")
    pass

    # TEST: create cert
    # please see ca.py
    # TEST: extract info from cert
    # TEST: verify cert against a trusted root
    
    
    

    # # get the cert_root
    # config = pm.getService("config")
    # cert_root = expand_amsoil_path(config.get("geniv3rpc.cert_root"))
    

    # TEST: create cred
    # TEST: extract individual entries in cred
    # TEST: verify cred against a trusted root
    # client_cert = cred.Credential(string=geni_credentials[0]).gidCaller.save_to_string(save_parents=True)
    # try:
    #     cred_verifier = ext.geni.CredentialVerifier(cert_root)
    #     cred_verifier.verify_from_strings(client_cert, geni_credentials, slice_urn, privileges)
    # except Exception as e:
    #     raise RuntimeError("%s" % (e,))
    # 
    # user_gid = gid.GID(string=client_cert)
    # user_urn = user_gid.get_urn()
    # user_uuid = user_gid.get_uuid()
    # user_email = user_gid.get_email()
    # return user_urn, user_uuid, user_email # TODO document return
