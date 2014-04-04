### What is Ohouse?

Ohouse is a reference implementation of the [Federation Service API](http://groups.geni.net/geni/wiki/CommonFederationAPIv2), and is currently in development. It includes Federation Registry (FR), Slice Authority (SA) and Member Authority (MA) implementations. It also supports both the compulsory and optional object types for each of these entities (`SERVICE`, `SLICE`, `SLIVER_INFO`, `PROJECT`, `MEMBER`, `KEY`).

### System Architecture

Ohouse consists of three main components: Federation Registry (FR), Slice Authority (SA) and Member Authority (MA). These are illustrated below:

![image](https://github.com/motine/Ohouse/docs/ohouse_high_level.png)

**Note:** Bold text indicates a components currently under development. Effort is currently concentrated on [v2 of the Federation Service API](http://groups.geni.net/geni/wiki/CommonFederationAPIv2). However, a partial implementation of [v1 of the Federation Service API](http://groups.geni.net/geni/wiki/CommonFederationAPIv1) is included, although it is unmaintained and incomplete.

### Implementation Details

#### Ohouse

Ohouse is built using the [AMsoil](https://github.com/motine/AMsoil) framework, with functionality spread amongst a number of plugins and services. These are illustrated below:

![image](https://github.com/motine/Ohouse/docs/ohouse_technical.png)

Handler and delegate base classes are realised in two plugins (`fedrpc1` and `fedrpc2`), each supporting a different version of the Federation Service API. Within each plugin, a number of services are used to support calls to the different supported entities (FR, MA, SA).

The Delegates are structured similarly in the `ofed1` and `ofed2` plugins. These are used to delegate calls dependent on the object type of a call and to do some basic parsing of the `options` field passed in an API call.

A number of individual plugins are used as resource managers for the different supported entities (FR, MA, SA). These are realised in `oregistryrm`, `omemberauthorityrm`, and `osliceauthorityrm` plugins respectively.

The `fedtools` plugin provides help to all of the above mentioned elements. In general they provide helper methods for common operations. The plugin is divided into three services, each corresponding to one of the [three layers of the architecture](https://github.com/motine/Ohouse/docs/ohouse_high_level.png).

#### MongoDB

Ohouse uses a [MongoDB document](https://www.mongodb.org/) database for persistent data storage. The services contained within the `fedtools` plugin use `mongodb` to communicate with an existing database instance.

For more details on how to install and run MongoDB, please see their [install documentation](http://docs.mongodb.org/manual/installation/). 

The name (by default) of the database used by Ohouse is `ohouse`. Data is structured into three collections, which are as follows:

* `sa`: holds data relating to the Slice Authority service
* `ma`:  holds data relating to the Member Authority service
* `endpoints`:  holds data corresponding to RPC endpoints

**Note:** The Federation Registry service does not store data in this database. However, data is instead loaded from the configuration files on startup (see below).

Each document (entry) includes a 'type' field, which denotes the object type it represents (`key`, `slice`, `project` for example). This field is removed when returning a result to the user, and is for internal Ohouse use only.

#### Configuration 

Configuration in Ohouse is achieved through the use of a JSON-format configuration file. An example is given at [`deploy/config.json.example`](https://github.com/motine/Ohouse/deploy/config.json.example). To use this example, simply copy the example to `deploy/config.json`.

This file is used to define supplementary fields for each of the object types supported in Ohouse (`SERVICE`, `SLICE`, `SLIVER_INFO`, `PROJECT`, `MEMBER`, `KEY`). See the `SLICE` and `MEMBER` entries in [`deploy/config.json.example`](https://github.com/motine/Ohouse/deploy/config.json.example) for more details. As an example, the following JSON can be used to define a custom field, describing an OFELIA island name field for a `MEMBER` object:


```
"_OFELIA_ISLAND_NAME" : {
	"TYPE"   : "STRING",
	"DESC"   : "Home island of the member",
	"CREATE" : "ALLOWED",
	"UPDATE" : true,
 	"MATCH"  : true,
	"PROTECT": "PUBLIC"
},
```
For more details on potential field attributes and their defaults, please see the [Federation Service API specification](http://groups.geni.net/geni/wiki/CommonFederationAPIv2).

Furthermore, default field settings are given in [`deploy/defaults.json`](https://github.com/motine/Ohouse/deploy/defaults.json). These are taken from the [Federation Service API specification](http://groups.geni.net/geni/wiki/CommonFederationAPIv2) and should not need changing under normal circumstances.

Supplementary field names should be placed in a distinct namespace by a prefix unique to that federation, and starting with an underscore (e.g. `_GENI_`, `_OFELIA_` , `_FED4FIRE_` or `_PROTOGENI_` etc.), as per the [Federation Service API specification](http://groups.geni.net/geni/wiki/CommonFederationAPIv2).

The configuration file (`config.json`) can be used to define supplementary fields for an object type. It can also be used to *override* the default fields and their attributes. To *override* a field, simply name the field the same as the default.

In addition, the configuration file (`config.json`) can also be used to statically define other configuration elements, in addition to the supplementary fields dicussed previously. This is particularly true in the case of the Federation Registry, which uses `config.json` to define the `SERVICES` and `TRUST_ROOTS` it supports. See [`deploy/config.json.example`](https://github.com/motine/Ohouse/deploy/config.json.example) for examples.