mkdir tmp/
python src/vendor/geni_trust/gen-certs.py tmp/
cp tmp/sa-cert.pem deploy/trusted/
cp tmp/ma-cert.pem deploy/trusted/
cp tmp/admin-*.pem admin/
cp tmp/*.pem test/creds/
cp tmp/*.xml test/creds/
rm -rf tmp/
