# The Clearinghouse

This is/shall a Clearinghouse for all the projects mentioned.

## Installation

### Environment

This software is based on AMsoil, please refer to the [installation guide there](https://github.com/fp7-ofelia/amsoil/wiki/Installation).  
Please follow at least the "Base" and "Plugins" steps.

### Dependencies

Please install [Swig](http://www.swig.org/) (needed for the M2Crypto Python package). Ohouse currently relies on a [MongoDB](mongodb.org) database running on the local host (and default port).

Python dependencies can then be installed using `pip install -r requirements.txt`.  

## Run

Fire up the server via `python src/main.py` and install the packages which are not found.

Note that sometimes the output is only given to the log in `log/amsoil.log`.

### Additional

* Copy the `deploy/config.json.example` to `deploy/config.json` and adjust the entries (should be self-explanatory).
* Either
  * Install trust root certificates to `deploy/trust` (as pem) and a admin cert (`admin-key.pem` and `admin-cert.pem`) to `admin`.
  * Or create test certificates and credentials and copy them to the respective places (see `test/creds/TODO.md`).
* Run the server with `python src/main.py`
* In a new cosole run the config client `python admin/config_client.py --interactive` and make change according to your setup

### Test drive

You may run the `xx_tests.py` scripts in `test/unit` to make sure everything works fine.
The test scripts assume that there are test certificates and credentials in `test/creds` (for creating them please see `test/creds/TODO.md`).

## Architectural decisions

* Please see the `ofed` - `plugin.py` for considerations on how to protect information regarding authZ.
* Ohouse will support both [v1](http://groups.geni.net/geni/wiki/UniformClearinghouseAPI) and [v2](http://groups.geni.net/geni/wiki/UniformClearinghouseAPIV2) of the Uniform Clearinghouse API. This is realised through different service endpoints for each version.
