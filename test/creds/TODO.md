This is a place to copy/generate user credentials for testing.
E.g. if you want to use a client you may put `alice-cert.pem` and `alice-key.pem` in here.

To auto-generate the test credentials please take a look at the `geni_trust` plugin, more specifically the `gen-certs.py` script.
E.g. `python src/plugins/geni_trust/gen-certs.py test/creds/`.

Please note that the [xmlsec1](http://www.aleksey.com/xmlsec/) package is needed to successfully run `gen-certs.py`.
 
When generating these certs, please also add the sa and ma certs to the `deploy/trusted` folder. Also, please copy the `admin-*.pem` to the `admin/` folder.

An example script (`gen-certs.sh`) is included in this folder. This generates the certificates and moves them to the appropriate locations for testing.
