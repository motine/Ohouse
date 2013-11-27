RSpec is a XML document to specify resources. The format is used to advertise, request or show the status of resources. Typically, an RSpec document is sent from or to an AM by a client (see Entities on the [GENI Page](GENI#entities)).

There are multiple versions of the RSpec type. Here we will only consider version 3, also abbreviated as RSpec3.

## XML and XMLSchema

XML is a human and machine readable markup language and consists of elements and their content. These elements can have attributes and each element can have sub elements. This creates a hierarchy of elements in which the top-most element is called root element. Here a basic example:

```xml
<rootelm>
  <elm attr="some" attr2="more">some <subelm>content</subelm></elm>
</rootelm>
```

Since XML follows a strict rules it can be checked for errors. The first step is to ensure the document is syntacticly correct (also called well-formed). This step is implicitly performed by parsers (see Parsing section) because an XML document can not be read if it is not well-formed. Additional to the syntax check, XML documents can be checked semantically (validation). This validation requires a definition of what is allowed in the document and what is prohibited. One format to specify such limitations on XML documents is called XML Schema (file extension `xsd`). These limitations can be useful for document readers - such as software tools - to ensure a certain format (and hence reduce the complexity of reading such a document).

Multiple schemas can be assigned to one document. Since some names may be similar or equal in different schemas, XML allows to specify prefixes for elements. Each prefix spans a new namespace and directly maps to the a schema. Note, that the schema location (URI) does not necessarily need to map to a downloadable schema file (which the document reader can choose to validate the document with).

More info can be found [here](http://en.wikipedia.org/wiki/XML) and [here](http://en.wikipedia.org/wiki/XML_Schema_(W3C).

The following example was taken from ExoGENI and requests a bare metal compute resource.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rspec type="request"
       xsi:schemaLocation="http://www.geni.net/resources/rspec/3 
                           http://www.geni.net/resources/rspec/3/request.xsd 
                           http://www.protogeni.net/resources/rspec/ext/shared-vlan/1 
                           http://www.protogeni.net/resources/rspec/ext/shared-vlan/1/request.xsd"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:s="http://www.protogeni.net/resources/rspec/ext/shared-vlan/1"
       xmlns="http://www.geni.net/resources/rspec/3">

  <node client_id="BT2" component_manager_id="urn:publicid:IDN+rcivmsite+authority+cm" >
    <sliver_type name="exogeni-m4">
    <disk_image name="http://geni-images.renci.org/images/standard/debian/deb6-neuca-v1.0.6.xml" version="64ad567ce3b1c0dbaa15bad673bbf556a9593e1c" />
    </sliver_type>
  </node>
  <link client_id="lan0">
    <interface_ref client_id="VM:if0"/>
    <s:link_shared_vlan name="1750"/>
  </link>
</rspec>
```

This document uses the uses the `http://www.geni.net/resources/rspec/3` as default. Each element without a prefix is validated against this namespace (the location of the schemas are defined above). Additional to the default, the document defines an element prefix/namespace for XML Schema (`xsi`, unused) and `s` for a VLAN extension (used later to specify a shared VLAN link).

## RSpec types

RSpec documents are XML documents with at least the following XML Schema namespace associated with it: `http://www.geni.net/resources/rspec/3/`.

Depending on the type additional schemas can be associated:
* **Advertisement** Announces which resources/slivers are available and what capabilities they have (http://www.geni.net/resources/rspec/3/ad.xsd).
* **Request** Specifies the wishes of the experimenter/client and includes the parameters needed for allocation/provisioning (http://www.geni.net/resources/rspec/3/request.xsd).
* **Manifest** Shows the status of a sliver (http://www.geni.net/resources/rspec/3/manifest.xsd)

According to these schemas the root node must be named `rspec` and specify the `type` as attribute. Please see the above example. All of the schemas can be downloaded and looked at in order to figure out which limitations are imposed by the respective schemas ([Ad](http://www.geni.net/resources/rspec/3/ad.xsd), [Request](http://www.geni.net/resources/rspec/3/request.xsd), [Manifest](http://www.geni.net/resources/rspec/3/request.xsd)).

## Parsing

In order to read XML documents, there is a multitude of so called parsers. There are two fundamentally different approaches on how to read the input. SAX follows a push principle, where the document is being read through and the program is notified for each element found. DOM on the other hand constructs a so called Document Object Model Tree which represents the hierarchy introduced by the elements.

AMsoil uses the [lxml](http://lxml.de/) library to parse and write documents.

## RSpec problems

Currently there is no centralized repository for RSpecs extensions. Hence, there are RSpecs which fulfill similar purpose, but look differently. This mostly due to the fact that these extensions evolved in different projects and these projects did not know of each other.
The absence of a centralized repository makes it hard to find similar RSpecs.

## Writing your own extension

In order to implement an Aggregate Manager you will need to decide on which extensions (schemas) your AM shall support. The first step would be to find out if there are other AMs like yours, dealing with the same resource type. If so, you may consider using their RSpec format/extension.
If you are treating a new resource type, you should write a schema for each type (advertisement, request, manifest). These extensions can be based on [this example](http://www.geni.net/resources/rspec/3/any-extension-schema.xsd). Please be aware that you do not need to copy the default schemas, you only need to provide rules for additional elements. As you can see in the example above, the document includes the default `xmlns` and one extension `xmlns:s`.

## Additional resources

* [GENI AM API v3 comments on RSpec](http://groups.geni.net/geni/wiki/GAPI_AM_API_V3/CommonConcepts#RSpecdatatype)
* [OpenFlow RSpec](http://groups.geni.net/geni/wiki/HowTo/WriteOFv3Rspecs/Spec)
* [protoGENI's info on RSpec](http://www.protogeni.net/ProtoGeni/wiki/RSpec) (very comprehensive, caution version 2 and this might differ from some GENI/OFELIA implementations)
* [Tutorial on how to acquire resources](http://groups.geni.net/geni/wiki/GENIExperimenter/Tutorials/RunHelloGENI) (How does RSpec fit into the experiment process?)
* [RSpec Examples](http://groups.geni.net/geni/browser/trunk/RSpecExamples) (mainly ExoGENI and InstaGENI)
* [Collection of Tutorials](http://groups.geni.net/geni/wiki/GENIExperimenter/ExampleExperiments) (some of them include RSpecs)