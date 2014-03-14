python ../../src/plugins/geni_trust/gen-certs.py .
cp sa-cert.pem ../../deploy/trusted/
cp ma-cert.pem ../../deploy/trusted/
cp admin-*.pem ../../admin/
cp alice-*.pem ../creds/
