# TODOs

## OHouse


# Open issues

**General**

* reflect changes from mail (see below)
* reflect changes from wiki (outcome from discussion on wednesday 26th of Aug)
* add test case to test an error / bad arguments (MA, SA)
* add servicemethod where possible
* test with jProbe
* do deployment
  * write doc (incl. cert stuff)
  * remove authentication from nginx config

**CH delegate**

* if change is approved on wednesday 26th of Aug, rename the get methods to lookup
* also if change is approved, change the lookup methods to return a dict of dicts not a list of dicts

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

* document how to create certs (see todo above)
* add test tools from Ohouse
* Bump trust plugin
  * Remove auth method from AM API v3 delegate base
  * Adjust example to do auth* with the geni_trust plugin (incl. translate exceptions)
* Remove ext from genirpc
* Update to new version of Flask in AMsoil
* Fix development server problem to acquire the client cert

## Change Mail

- Added an 'OBJECTS' field to the get_version (to indicate that, e.g. the SA might represent a PROJECT object)
- Clarified the return type of lookup_authorities_for_urns
- Clarified the semantics of the 'speaks-for' call sequence.
- Clarified that the CH get_* calls take match and filter methods like other lookup_* methods (see below).
- Changed SERVICE_DESCRIPTION to (hypothetical) SERVICE_PROVIDER in CH get_version return
- Updated that the get_version call CREDENTIAL_TYPES field is a dictionary of type => list of supported versions.(e.g. {"SFA" : ["1"], "ABAC : ["1", "2"]}
- Fixed the error of type of MEMBER_FIRSTNAME, MEMBER_LASTNAME and MEMBER_USERNAME to STRING
- Added "MATCH" as an additional field on FIELDS in get_version, indicating (as in the subsequent tables) whether a field is allowed as a 'match' criterion in lookup calls.
- Corrected the description of the return type of lookup_slice_members, lookup_slices_for_member and lookup_project members to indicate that these are lists of dictionaries, not dictionaries.
