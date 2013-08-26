This is a place to copy/generate user credentials for testing.
E.g. if you want to use a client you may put `alice-cert.pem` and `alice-key.pem` in here.

To auto-generate the test credentials please take a look at the `geni_trust` plugin, more specifically the `gen-certs.py` script.
E.g. `python src/plugins/geni_trust/gen-certs.py test/creds/`.

**CAUTION**  
When generating these certs, please also add the sa and ma certs to the `deploy/trusted` folder.
And copy the `admin-*.pem` to the `admin/` folder