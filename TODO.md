# TODOs

## OHouse

* add authentication and authorization when implementing other MA methods
* add CREDENTIAL_TYPES in CH (incl. test)
* add changes in mail marshall (16.08.)
* move get version to delegate base? /or/ move MA code to RM
* move info from RM to Delegate?
* add test case to test an error / bad arguments
* Do Authentication
  * Wrap the delegate for auth?
* add real certs to config file
* add servicemethod where possible

* do deployment
  * write doc (incl. cert stuff)
  * remove authentication from nginx config

## Trust plugin
* Add extract info method (+client_options)
* Add exceptions
* add servicemethod where possible


## AMsoil

* add test tools
* Add trust plugin
  * Remove auth method from delegate base
  * Adjust example (incl. translate exceptions)
* Remove lib include from genirpc
* Update to new version of Flask in AMsoil



## Mail
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
