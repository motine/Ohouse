# TODOs

## OHouse


* document and use gen-certs
* TODOs in gen-certs

* Refactor tests to take a good cert, a bad cert and a server host/port

* Trust Plugin: add servicemethod where possible

* add authentication and authorization when implementing other MA methods (see http://groups.geni.net/geni/wiki/UniformClearinghouseAPI#MemberAuthorityAPI)
  * Actually implement cred verification
  * Add tests for it

* add update_member_info and get_credentials
* add CREDENTIAL_TYPES in CH (incl. test)
* add changes in mail marshall (see below)
* move get version to delegate base? /or/ move MA code to RM
* move info from RM to Delegate?
* add test case to test an error / bad arguments (MA, SA)
* add real certs to config file
* add servicemethod where possible
* Wrap the delegate for auth?

* test with jProbe
* do deployment
  * write doc (incl. cert stuff)
  * remove authentication from nginx config

## AMsoil

* document how to create certs
* add test tools
* Bump trust plugin
  * Remove auth method from delegate base
  * Adjust example (incl. translate exceptions)
* Remove lib include from genirpc
* Update to new version of Flask in AMsoil


## Marshall

	- Added an 'OBJECTS' field to the get_version (to indicate that, e.g. the SA might represent a PROJECT object)

	- Clarified the return type of lookup_authorities_for_urns

	- Clarified the semantics of the 'speaks-for' call sequence.

	- Clarified that the CH get_* calls take match and filter methods like other lookup_* methods (see below).

	- Changed SERVICE_DESCRIPTION to (hypothetical) SERVICE_PROVIDER in CH get_version return

	- Updated that the get_version call CREDENTIAL_TYPES field is a dictionary of type => list of supported versions.(e.g. {"SFA" : ["1"], "ABAC : ["1", "2"]}

	- Fixed the error of type of MEMBER_FIRSTNAME, MEMBER_LASTNAME and MEMBER_USERNAME to STRING

	- Added "MATCH" as an additional field on FIELDS in get_version, indicating (as in the subsequent tables) whether a field is allowed as a 'match' criterion in lookup calls.

	- Corrected the description of the return type of lookup_slice_members, lookup_slices_for_member and lookup_project members to indicate that these are lists of dictionaries, not dictionaries.



## Prio Mail
Now, I try to get my priorities regarding the development straight. I would move in the following order:
- Review your CH code.
- Create plugin which deals handles with URNs, Certificates, Credentials (sfa_geni_trust).
- Implement the OFELIA CH along side.
- Refactor existing AMsoil code to use the sfa_geni_trust plugin.
- Find a better solution to enable, disable plugins and to collaborate on multiple plugins.

Do you have any thoughts on the proposed plan? Also:
- Please let me know how you are testing the current CH implementation
- Please check in your latest code to the BBN repo, so I can review the correct version.
- For the Certificates and Credentials plugin: Which code is the most up-to date regarding these functions (create certs, verify creds, etc.)? the one in the gcf repo or does Rob have the latest?
