# TODOs

## OHouse


# Open issues

**General**

* Factor in changes from Marshal (see Mail from Marshal)

* MA: add update_member_info (incl. tests)
* MA: add get_credentials (incl. tests)
* MA: add implementation for key service (incl. tests)

* MA test if match attributes are rejected if match is not allowed by get_version
* MA test: make sure PROTECT attributes are not given out unless public

* get_version: add roles and objects for MA

* add an `additional_info` return value to the extract_certificate_info
* add admin credentials (see below)
* reflect changes from wiki (outcome from discussion on wednesday 26th of Aug)
* add test case to test an error / bad arguments (MA, SA)
* add servicemethod where possible
* test with jProbe
* do deployment
  * write doc (incl. cert stuff)
  * remove authentication from nginx config
* Implement speaks-for (see code from Marshall)
* Add methods for adding users

**MA delegate**

* add parsing of the admin cert (discussion on wednesday 26th of Aug)
* see TODOs in the file

* document gen-certs in geni_trust in amsoil and link from Ohouse
* Trust Plugin: add servicemethod where possible

* add update_member_info and get_credentials
* Add database

* Refactor delegates
  * either move MA code to RM and move get version to delegate base
  * or move CH info from RM to Delegate?

## AMsoil

* Refactor SSL call from test, 2x Client to own module
* document how to create certs and add slides to quickstart (see todo above). maybe just link the Ohouse stuff
* add test tools from Ohouse
* Bump trust plugin
  * Remove auth method from AM API v3 delegate base
  * Adjust example to do auth* with the geni_trust plugin (incl. translate exceptions)
  * add admin credentials to config client and validate the cert (see Ohouse)
* Remove ext from genirpc
* Fix development server problem to acquire the client cert
* Update to new version of Flask in AMsoil

## Admin creds
> I don't think there is anything much to look for... the only thing that
is different is that the credential target is the authority itself.
(Normally, the CM generates credentials with a sliver as a target, and
of course then they are useless outside that sliver.)  I don't believe
that genadmincredential credentials issued by the SA do anything special
right now.