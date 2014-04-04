## Ohouse

* Implement `get_credentials` methods (for SLICE and MEMBER objects)
* Implement `speaking_for` option parameter (see code from Marshall)
* Implement registration portal
  * Out-of-band XML-RPC interface for membership (MEMBER) administration
  * Consider [xml-signer](https://github.com/duerig/xml-signer)
* Implement example CH client
* Document an example Ohouse workflow
* Determine appropriate authorisation (AuthZ) levels (LEAD, ADMIN, MEMBER, OPERATOR, AUDITOR, for example)
  * Consider the existing [OFELIA privileges](https://github.com/fp7-ofelia/ocf/blob/ofelia.stable/expedient/src/python/expedient/clearinghouse/project/permissions.py)
  * Enforce 'match' lookup authorization ('PRIVATE' and 'IDENTIFYING' values in 'PROTECT' field)
* Implement/use certificate and credential checks
* Add parsing of the admin cert and creds for both SA and MA (see section below and discussion on Wednesday 26th of Aug)
* Check SLICE_EXPIRATION and PROJECT_EXPIRATION updates are valid: expiration may only be extended, never reduced
* Consider implementation-specific restrictions for both the [MA](http://groups.geni.net/geni/wiki/CommonFederationAPIv2#MemberServiceMethods) and [SA](http://groups.geni.net/geni/wiki/CommonFederationAPIv2#SliceServiceMethods), and how to load and use these from `config.json`
* Add test monitoring for github in travis-ci.org (can we install SWIG and `xmlsec1` dependencies in this environment?)
* Use pyPElib to enforce policies (and feed this back to AMsoil)
* Add an `additional_info` return value to the extract_certificate_info
* Test with jProbe
* Remove authentication from nginx config
* Document gen-certs
* Trust Plugin: add servicemethod where possible
* Make MongoDB database configurable (IP, port, database name etc.)
* Reimplement Delegate Guards for v2 SA and MA (see omavonedelegateguard.py)
* Increase UnitTest coverage
* Increase/structure documentation

**Admin Credential Discussion**

> I don't think there is anything much to look for... the only thing that
is different is that the credential target is the authority itself.
(Normally, the CM generates credentials with a sliver as a target, and
of course then they are useless outside that sliver.)  I don't believe
that genadmincredential credentials issued by the SA do anything special
right now.

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
