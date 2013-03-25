#!/usr/bin/env python

import sys
import os.path
import xmlrpclib
from datetime import datetime
from dateutil import parser as dateparser



class SafeTransportWithCert(xmlrpclib.SafeTransport): 
    """Helper class to foist the right certificate for the transport class."""
    def __init__(self, key_path, cert_path):
        xmlrpclib.SafeTransport.__init__(self) # no super, because old style class
        self._key_path = key_path
        self._cert_path = cert_path
        
    def make_connection(self, host):
        """This method will automatically be called by the ServerProxy class when a transport channel is needed."""
        host_with_cert = (host, {'key_file' : self._key_path, 'cert_file' : self._cert_path})
        return xmlrpclib.SafeTransport.make_connection(self, host_with_cert) # no super, because old style class

class GENI3ClientError(Exception):
    def __init__(self, message, code):
        self._message = message
        self._code = code

    def __str__(self):
        return "%s (code: %s)" % (self._message, self._code)


class GENI3Client(object):
    """This class encapsulates a connection to a GENI AM API v3 server.
    It implements all methods of the API and manages the interaction regarding the client certificate.
    For all the client methods (e.g. listResources, describe) the given options (e.g. compress) have the default value None.
    This means if the caller does not change the value the client will not send this option and hence force the server to use the default.
    If true or false are given the options are set accordingly.
    If a time is given (e.g. end_time), please provide the method call with a Python datetime object, the RPC-conversion will then be done for you.
    
    Please also see the helper methods below.
    """
    
    RFC3339_FORMAT_STRING = '%Y-%m-%d %H:%M:%S.%fZ'
    
    def __init__(self, host, port, key_path, cert_path):
        """
        Establishes a connection proxy with the client certificate given.
        {host} e.g. 127.0.0.1
        {port} e.g. 8001
        {key_path} The file path to the client's private key.
        {cert_path} The file path to the client's certificate.
        """
        transport = SafeTransportWithCert(key_path, cert_path)
        self._proxy = xmlrpclib.ServerProxy("https://%s:%s/RPC2" % (host, str(port)), transport=transport)
    
    def getVersion(self):
        """Calls the GENI GetVersion method and returns a dict. See [geniv3rpc] GENIv3DelegateBase for more information."""
        return self._proxy.GetVersion()
        

    def listResources(self, credentials, available=None, compress=None):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        if available != None:
            options["geni_available"] = available
        if compress != None:
            options["geni_compress"] = compress
        return self._proxy.ListResources(credentials, options)
    
    def describe(self, urns, credentials, compress=None):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        if compress != None:
            options["geni_compress"] = compress
        return self._proxy.ListResources(credentials, options)
            
    def allocate(self, slice_urn, credentials, rspec, end_time=None):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        if end_time != None:
            options["geni_end_time"] = self.datetime2str(end_time)
        return self._proxy.Allocate(slice_urn, credentials, rspec, options)
    
    def renew(self, urns, credentials, expiration_time, best_effort=None):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        if best_effort != None:
            options["geni_best_effort"] = best_effort
        return self._proxy.Renew(urns, credentials, self.datetime2str(expiration_time), options)
        
    def provision(self, urns, credentials, best_effort=None, end_time=None, users=None):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        if best_effort != None:
            options["geni_best_effort"] = best_effort
        if end_time != None:
            options["geni_end_time"] = self.datetime2str(end_time)
        if users != None:
            options["geni_users"] = users
        return self._proxy.Provision(urns, credentials, options)

    def status(self, urns, credentials):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        return self._proxy.Status(urns, credentials, options)
        
    def performOperationalAction(self, urns, credentials, action, best_effort=None):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        if best_effort != None:
            options["geni_best_effort"] = best_effort
        return self._proxy.PerformOperationalAction(urns, credentials, action, options)
        
    def delete(self, urns, credentials, best_effort=None):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        if best_effort != None:
            options["geni_best_effort"] = best_effort
        return self._proxy.Delete(urns, credentials, options)

    def shutdown(self, slice_urn, credentials):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        return self._proxy.Shutdown(slice_urn, credentials, options)

    def _default_options(self):
        """Private method for generating the default option hash, which is parsed on the server."""
        return {"geni_rspec_version" : {"version" : 3, "type" : "geni"}}

    # helper methods
    def datetime2str(self, dt):
        """Convers a datetime to a string which can be parsed by the GENI AM API server."""
        return dt.strftime(self.RFC3339_FORMAT_STRING)
    def str2datetime(self, strval):
        """Coverts a date string given by the GENI AM API server to a python datetime object.
        It parses the given date string and converts the timestamp to utc and the date unaware of timezones."""
        result = dateparser.parse(strval)
        if result:
            result = result - result.utcoffset()
            result = result.replace(tzinfo=None)
        return result

    def raiseIfError(self, response):
        """Raises an GENI3ClientError if the server response contained an error."""
        if self.isError(response):
            raise GENI3ClientError(self.errorMessage(response), self.errorCode(response))
        return

    def errorMessage(self, response):
        return response['output']
    def errorCode(self, response):
        return int(response['code']['geni_code'])
    def isError(self, response):
        return self.errorCode(response) != 0
        

# Test code

TEST_SLICE_URN = 'urn:publicid:IDN+ofelia:eict:gcf+slice+slicename'
TEST_CREDENTIAL = {'geni_value': '<?xml version="1.0"?>\n<signed-credential xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.planet-lab.org/resources/sfa/credential.xsd" xsi:schemaLocation="http://www.planet-lab.org/resources/sfa/ext/policy/1 http://www.planet-lab.org/resources/sfa/ext/policy/1/policy.xsd"><credential xml:id="ref0"><type>privilege</type><serial>8</serial><owner_gid>-----BEGIN CERTIFICATE-----\nMIICPTCCAaagAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMjA1MDkzMzQ0WhcNMTgw\nMjA0MDkzMzQ0WjAnMSUwIwYDVQQDExxvZmVsaWEvL2VpY3QvL2djZi51c2VyLmFs\naWNlMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCo2FSoOplnAdI5LNAaGPJd\nSyN9Y/RykNhEEcqbHL/fnMcJ6XMUTGSEUmxkp5ubPdJxnGEhwv8cp8txMi6NFeU2\nz2YZUOEXL4xrfsO4G6Eaj9TkiiTprcW74FxDWDkzLfU2ApEdzRXBXuuRJenagEf3\n86e93pSRXd0XNzJdCWRHoQIDAQABo3cwdTAMBgNVHRMBAf8EAjAAMGUGA1UdEQRe\nMFyGK3VybjpwdWJsaWNpZDpJRE4rb2ZlbGlhOmVpY3Q6Z2NmK3VzZXIrYWxpY2WG\nLXVybjp1dWlkOmVhMzBkOThjLWUzYjYtNDIzYy04ZTUxLTA3NGY1OGI1ZTU1YzAN\nBgkqhkiG9w0BAQQFAAOBgQDS5D5o0eThkZOQwLrXs/ME3d/ppEQunmoLGI0ICG4x\n9aSFJZReGLs1vUzYYR7LHn/+sbv6r9p5cAOCArEGzCVdTuPfxKh6SlvXt+cijBKf\n0/ZFGMSFPcnG6dEDlOTK0PnD52MgfmZ83udRClmRoOO9Ph/5ae2KqwvvcCbSL9dD\nlw==\n-----END CERTIFICATE-----\n-----BEGIN CERTIFICATE-----\nMIICRDCCAa2gAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMjA1MDkzMzQ0WhcNMTgw\nMjA0MDkzMzQ0WjApMScwJQYDVQQDEx5vZmVsaWEvL2VpY3QvL2djZi5hdXRob3Jp\ndHkuc2EwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAO5zLoStkSytfhFdRI1t\nqFKHOxf8awNWxSsV229CMcRFfIedyeICEies6xU+bxpNs4Cx79RLdHEo5944VcBR\nl//K2rU0Am79QcA9WfB/l49W0VsscM3L3qD3i6xK5KjToTfMZSDylhfY6Nm05gzx\nXmrKYTuLppJJoQLSMB3DGeEtAgMBAAGjfDB6MA8GA1UdEwEB/wQFMAMBAf8wZwYD\nVR0RBGAwXoYtdXJuOnB1YmxpY2lkOklETitvZmVsaWE6ZWljdDpnY2YrYXV0aG9y\naXR5K3Nhhi11cm46dXVpZDphZmJmNWEwYy1hNjE1LTRjZjEtYjI5OS1mYjc4YzI3\nN2JhMjkwDQYJKoZIhvcNAQEEBQADgYEApKin+EE5CDZvnuQNGJIVJ7AsVSNMM71B\nMDxWKNc6IWn1lPsNwZNTDYNL7oV5MQiqUfsWcAwmBSEymqbw9M1R497BmF11C6fA\nflH25MkjoLBjx212YCkjv92r3OHnJw9Xf9MSYsm4TuMiCGkpPRVkpQyZxLLWY0R2\nIBHno4tcSmA=\n-----END CERTIFICATE-----\n</owner_gid><owner_urn>urn:publicid:IDN+ofelia:eict:gcf+user+alice</owner_urn><target_gid>-----BEGIN CERTIFICATE-----\nMIICPTCCAaagAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMjA1MDkzMzQ0WhcNMTgw\nMjA0MDkzMzQ0WjAnMSUwIwYDVQQDExxvZmVsaWEvL2VpY3QvL2djZi51c2VyLmFs\naWNlMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCo2FSoOplnAdI5LNAaGPJd\nSyN9Y/RykNhEEcqbHL/fnMcJ6XMUTGSEUmxkp5ubPdJxnGEhwv8cp8txMi6NFeU2\nz2YZUOEXL4xrfsO4G6Eaj9TkiiTprcW74FxDWDkzLfU2ApEdzRXBXuuRJenagEf3\n86e93pSRXd0XNzJdCWRHoQIDAQABo3cwdTAMBgNVHRMBAf8EAjAAMGUGA1UdEQRe\nMFyGK3VybjpwdWJsaWNpZDpJRE4rb2ZlbGlhOmVpY3Q6Z2NmK3VzZXIrYWxpY2WG\nLXVybjp1dWlkOmVhMzBkOThjLWUzYjYtNDIzYy04ZTUxLTA3NGY1OGI1ZTU1YzAN\nBgkqhkiG9w0BAQQFAAOBgQDS5D5o0eThkZOQwLrXs/ME3d/ppEQunmoLGI0ICG4x\n9aSFJZReGLs1vUzYYR7LHn/+sbv6r9p5cAOCArEGzCVdTuPfxKh6SlvXt+cijBKf\n0/ZFGMSFPcnG6dEDlOTK0PnD52MgfmZ83udRClmRoOO9Ph/5ae2KqwvvcCbSL9dD\nlw==\n-----END CERTIFICATE-----\n-----BEGIN CERTIFICATE-----\nMIICRDCCAa2gAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMjA1MDkzMzQ0WhcNMTgw\nMjA0MDkzMzQ0WjApMScwJQYDVQQDEx5vZmVsaWEvL2VpY3QvL2djZi5hdXRob3Jp\ndHkuc2EwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAO5zLoStkSytfhFdRI1t\nqFKHOxf8awNWxSsV229CMcRFfIedyeICEies6xU+bxpNs4Cx79RLdHEo5944VcBR\nl//K2rU0Am79QcA9WfB/l49W0VsscM3L3qD3i6xK5KjToTfMZSDylhfY6Nm05gzx\nXmrKYTuLppJJoQLSMB3DGeEtAgMBAAGjfDB6MA8GA1UdEwEB/wQFMAMBAf8wZwYD\nVR0RBGAwXoYtdXJuOnB1YmxpY2lkOklETitvZmVsaWE6ZWljdDpnY2YrYXV0aG9y\naXR5K3Nhhi11cm46dXVpZDphZmJmNWEwYy1hNjE1LTRjZjEtYjI5OS1mYjc4YzI3\nN2JhMjkwDQYJKoZIhvcNAQEEBQADgYEApKin+EE5CDZvnuQNGJIVJ7AsVSNMM71B\nMDxWKNc6IWn1lPsNwZNTDYNL7oV5MQiqUfsWcAwmBSEymqbw9M1R497BmF11C6fA\nflH25MkjoLBjx212YCkjv92r3OHnJw9Xf9MSYsm4TuMiCGkpPRVkpQyZxLLWY0R2\nIBHno4tcSmA=\n-----END CERTIFICATE-----\n</target_gid><target_urn>urn:publicid:IDN+ofelia:eict:gcf+user+alice</target_urn><uuid/><expires>2013-03-26T11:14:13</expires><privileges><privilege><name>refresh</name><can_delegate>false</can_delegate></privilege><privilege><name>resolve</name><can_delegate>false</can_delegate></privilege><privilege><name>info</name><can_delegate>false</can_delegate></privilege></privileges></credential><signatures><Signature xmlns="http://www.w3.org/2000/09/xmldsig#" xml:id="Sig_ref0">\n  <SignedInfo>\n    <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>\n    <SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>\n    <Reference URI="#ref0">\n      <Transforms>\n        <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>\n      </Transforms>\n      <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>\n      <DigestValue>VqPsc0rjDm7VRX9FK/Phif8WkQc=</DigestValue>\n    </Reference>\n  </SignedInfo>\n  <SignatureValue>dsJ9/BPOHJM+d6wcYshNgaHaXPEkzXN0xEaJUV4j9IdeSvq9rnpTODUcd0Jg3mSn\nF5sCSpNGCIOroYHZf92gb2R8NC4QRPtC76kyqcNE8WDyCsCcQDu7jsISeD+rUn7s\nOYql1endhY8a7vvScnjwNal3Tpszv18VxmC9dgAwVWE=</SignatureValue>\n  <KeyInfo>\n    <X509Data>\n      \n      \n      \n    <X509Certificate>MIICRDCCAa2gAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMjA1MDkzMzQ0WhcNMTgw\nMjA0MDkzMzQ0WjApMScwJQYDVQQDEx5vZmVsaWEvL2VpY3QvL2djZi5hdXRob3Jp\ndHkuc2EwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAO5zLoStkSytfhFdRI1t\nqFKHOxf8awNWxSsV229CMcRFfIedyeICEies6xU+bxpNs4Cx79RLdHEo5944VcBR\nl//K2rU0Am79QcA9WfB/l49W0VsscM3L3qD3i6xK5KjToTfMZSDylhfY6Nm05gzx\nXmrKYTuLppJJoQLSMB3DGeEtAgMBAAGjfDB6MA8GA1UdEwEB/wQFMAMBAf8wZwYD\nVR0RBGAwXoYtdXJuOnB1YmxpY2lkOklETitvZmVsaWE6ZWljdDpnY2YrYXV0aG9y\naXR5K3Nhhi11cm46dXVpZDphZmJmNWEwYy1hNjE1LTRjZjEtYjI5OS1mYjc4YzI3\nN2JhMjkwDQYJKoZIhvcNAQEEBQADgYEApKin+EE5CDZvnuQNGJIVJ7AsVSNMM71B\nMDxWKNc6IWn1lPsNwZNTDYNL7oV5MQiqUfsWcAwmBSEymqbw9M1R497BmF11C6fA\nflH25MkjoLBjx212YCkjv92r3OHnJw9Xf9MSYsm4TuMiCGkpPRVkpQyZxLLWY0R2\nIBHno4tcSmA=</X509Certificate>\n<X509SubjectName>CN=ofelia//eict//gcf.authority.sa</X509SubjectName>\n<X509IssuerSerial>\n<X509IssuerName>CN=ofelia//eict//gcf.authority.sa</X509IssuerName>\n<X509SerialNumber>3</X509SerialNumber>\n</X509IssuerSerial>\n</X509Data>\n    <KeyValue>\n<RSAKeyValue>\n<Modulus>\n7nMuhK2RLK1+EV1EjW2oUoc7F/xrA1bFKxXbb0IxxEV8h53J4gISJ6zrFT5vGk2z\ngLHv1Et0cSjn3jhVwFGX/8ratTQCbv1BwD1Z8H+Xj1bRWyxwzcveoPeLrErkqNOh\nN8xlIPKWF9jo2bTmDPFeasphO4umkkmhAtIwHcMZ4S0=\n</Modulus>\n<Exponent>\nAQAB\n</Exponent>\n</RSAKeyValue>\n</KeyValue>\n  </KeyInfo>\n</Signature></signatures></signed-credential>\n', 'geni_version': '3', 'geni_type': 'geni_sfa'}
TEST_SLICE_CREDENTIAL = {'geni_value': '<?xml version="1.0"?>\n<signed-credential xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.planet-lab.org/resources/sfa/credential.xsd" xsi:schemaLocation="http://www.planet-lab.org/resources/sfa/ext/policy/1 http://www.planet-lab.org/resources/sfa/ext/policy/1/policy.xsd"><credential xml:id="ref0"><type>privilege</type><serial>8</serial><owner_gid>-----BEGIN CERTIFICATE-----\nMIICPTCCAaagAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMjA1MDkzMzQ0WhcNMTgw\nMjA0MDkzMzQ0WjAnMSUwIwYDVQQDExxvZmVsaWEvL2VpY3QvL2djZi51c2VyLmFs\naWNlMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCo2FSoOplnAdI5LNAaGPJd\nSyN9Y/RykNhEEcqbHL/fnMcJ6XMUTGSEUmxkp5ubPdJxnGEhwv8cp8txMi6NFeU2\nz2YZUOEXL4xrfsO4G6Eaj9TkiiTprcW74FxDWDkzLfU2ApEdzRXBXuuRJenagEf3\n86e93pSRXd0XNzJdCWRHoQIDAQABo3cwdTAMBgNVHRMBAf8EAjAAMGUGA1UdEQRe\nMFyGK3VybjpwdWJsaWNpZDpJRE4rb2ZlbGlhOmVpY3Q6Z2NmK3VzZXIrYWxpY2WG\nLXVybjp1dWlkOmVhMzBkOThjLWUzYjYtNDIzYy04ZTUxLTA3NGY1OGI1ZTU1YzAN\nBgkqhkiG9w0BAQQFAAOBgQDS5D5o0eThkZOQwLrXs/ME3d/ppEQunmoLGI0ICG4x\n9aSFJZReGLs1vUzYYR7LHn/+sbv6r9p5cAOCArEGzCVdTuPfxKh6SlvXt+cijBKf\n0/ZFGMSFPcnG6dEDlOTK0PnD52MgfmZ83udRClmRoOO9Ph/5ae2KqwvvcCbSL9dD\nlw==\n-----END CERTIFICATE-----\n</owner_gid><owner_urn>urn:publicid:IDN+ofelia:eict:gcf+user+alice</owner_urn><target_gid>-----BEGIN CERTIFICATE-----\nMIICRzCCAbCgAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMzI1MTE0MzU0WhcNMTgw\nMzI0MTE0MzU0WjAsMSowKAYDVQQDEyFvZmVsaWEvL2VpY3QvL2djZi5zbGljZS5z\nbGljZW5hbWUwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAK+lc4bTl+CK9bGN\nFFjEefEprkPDy/8H6sdjsMJZd2Yh2NSEmXN5304a3Aw+ibTRlDdfEAz/wLkIqACk\nCNJxFRZkDQkieFEjPv6vz+dOpAhKn2AjsYEkSNCbzPKNErJiYerKA08NTyCH8ikY\nqRxfc604jPF7jA5hXJ4y6APEOo7LAgMBAAGjfDB6MAwGA1UdEwEB/wQCMAAwagYD\nVR0RBGMwYYYwdXJuOnB1YmxpY2lkOklETitvZmVsaWE6ZWljdDpnY2Yrc2xpY2Ur\nc2xpY2VuYW1lhi11cm46dXVpZDowMjdmZTQ3OS04M2ZmLTQ0ZTUtYTJjYi0xZDZh\nNGU0NjFmNDgwDQYJKoZIhvcNAQEEBQADgYEApIuzVl33cgQToT8h3MWKEG0R5jHV\nE6fN7SB2rrWYmIyXb2H9MY9G9gIczOwXTJomY7rGp1Nq6OnFfx0jbKqIUjNvIqNF\nlxhw7fHjL3cgDKKkEF/cgf5a5oYJtAd1OkHm5D0sIcOWOgZ4HuLpOdLgdXi9nDdR\nRpM3lv4gWvvjjbw=\n-----END CERTIFICATE-----\n-----BEGIN CERTIFICATE-----\nMIICRDCCAa2gAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMjA1MDkzMzQ0WhcNMTgw\nMjA0MDkzMzQ0WjApMScwJQYDVQQDEx5vZmVsaWEvL2VpY3QvL2djZi5hdXRob3Jp\ndHkuc2EwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAO5zLoStkSytfhFdRI1t\nqFKHOxf8awNWxSsV229CMcRFfIedyeICEies6xU+bxpNs4Cx79RLdHEo5944VcBR\nl//K2rU0Am79QcA9WfB/l49W0VsscM3L3qD3i6xK5KjToTfMZSDylhfY6Nm05gzx\nXmrKYTuLppJJoQLSMB3DGeEtAgMBAAGjfDB6MA8GA1UdEwEB/wQFMAMBAf8wZwYD\nVR0RBGAwXoYtdXJuOnB1YmxpY2lkOklETitvZmVsaWE6ZWljdDpnY2YrYXV0aG9y\naXR5K3Nhhi11cm46dXVpZDphZmJmNWEwYy1hNjE1LTRjZjEtYjI5OS1mYjc4YzI3\nN2JhMjkwDQYJKoZIhvcNAQEEBQADgYEApKin+EE5CDZvnuQNGJIVJ7AsVSNMM71B\nMDxWKNc6IWn1lPsNwZNTDYNL7oV5MQiqUfsWcAwmBSEymqbw9M1R497BmF11C6fA\nflH25MkjoLBjx212YCkjv92r3OHnJw9Xf9MSYsm4TuMiCGkpPRVkpQyZxLLWY0R2\nIBHno4tcSmA=\n-----END CERTIFICATE-----\n</target_gid><target_urn>urn:publicid:IDN+ofelia:eict:gcf+slice+slicename</target_urn><uuid/><expires>2013-03-25T13:43:54</expires><privileges><privilege><name>refresh</name><can_delegate>true</can_delegate></privilege><privilege><name>embed</name><can_delegate>true</can_delegate></privilege><privilege><name>bind</name><can_delegate>true</can_delegate></privilege><privilege><name>control</name><can_delegate>true</can_delegate></privilege><privilege><name>info</name><can_delegate>true</can_delegate></privilege></privileges></credential><signatures><Signature xmlns="http://www.w3.org/2000/09/xmldsig#" xml:id="Sig_ref0">\n  <SignedInfo>\n    <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>\n    <SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>\n    <Reference URI="#ref0">\n      <Transforms>\n        <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>\n      </Transforms>\n      <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>\n      <DigestValue>2X0t7QWygecINSJxqbyWUUJTTW0=</DigestValue>\n    </Reference>\n  </SignedInfo>\n  <SignatureValue>2t2pBT7Yd4Rmvn7bCLUDW3zN4XDLgmbO849eV7hbeVlhsTyS7w3TBRK2iF6Kr/vj\nenEG4RJpG3X+F/2jLTz9TDVF+2FM9i1y7axmXzYbEplvgcRV7bTQir+9rWputCC2\nD8IxRLLJ7pXTs1MiM9jaAcMTXYPX8gnhvUpdaa1qgUY=</SignatureValue>\n  <KeyInfo>\n    <X509Data>\n      \n      \n      \n    <X509Certificate>MIICRDCCAa2gAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMjA1MDkzMzQ0WhcNMTgw\nMjA0MDkzMzQ0WjApMScwJQYDVQQDEx5vZmVsaWEvL2VpY3QvL2djZi5hdXRob3Jp\ndHkuc2EwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAO5zLoStkSytfhFdRI1t\nqFKHOxf8awNWxSsV229CMcRFfIedyeICEies6xU+bxpNs4Cx79RLdHEo5944VcBR\nl//K2rU0Am79QcA9WfB/l49W0VsscM3L3qD3i6xK5KjToTfMZSDylhfY6Nm05gzx\nXmrKYTuLppJJoQLSMB3DGeEtAgMBAAGjfDB6MA8GA1UdEwEB/wQFMAMBAf8wZwYD\nVR0RBGAwXoYtdXJuOnB1YmxpY2lkOklETitvZmVsaWE6ZWljdDpnY2YrYXV0aG9y\naXR5K3Nhhi11cm46dXVpZDphZmJmNWEwYy1hNjE1LTRjZjEtYjI5OS1mYjc4YzI3\nN2JhMjkwDQYJKoZIhvcNAQEEBQADgYEApKin+EE5CDZvnuQNGJIVJ7AsVSNMM71B\nMDxWKNc6IWn1lPsNwZNTDYNL7oV5MQiqUfsWcAwmBSEymqbw9M1R497BmF11C6fA\nflH25MkjoLBjx212YCkjv92r3OHnJw9Xf9MSYsm4TuMiCGkpPRVkpQyZxLLWY0R2\nIBHno4tcSmA=</X509Certificate>\n<X509SubjectName>CN=ofelia//eict//gcf.authority.sa</X509SubjectName>\n<X509IssuerSerial>\n<X509IssuerName>CN=ofelia//eict//gcf.authority.sa</X509IssuerName>\n<X509SerialNumber>3</X509SerialNumber>\n</X509IssuerSerial>\n</X509Data>\n    <KeyValue>\n<RSAKeyValue>\n<Modulus>\n7nMuhK2RLK1+EV1EjW2oUoc7F/xrA1bFKxXbb0IxxEV8h53J4gISJ6zrFT5vGk2z\ngLHv1Et0cSjn3jhVwFGX/8ratTQCbv1BwD1Z8H+Xj1bRWyxwzcveoPeLrErkqNOh\nN8xlIPKWF9jo2bTmDPFeasphO4umkkmhAtIwHcMZ4S0=\n</Modulus>\n<Exponent>\nAQAB\n</Exponent>\n</RSAKeyValue>\n</KeyValue>\n  </KeyInfo>\n</Signature></signatures></signed-credential>\n', 'geni_version': '3', 'geni_type': 'geni_sfa'}
TEST_REQUEST_RSPEC = '<?xml version="1.0" encoding="UTF-8"?><rspec type="request" xmlns="http://www.geni.net/resources/rspec/3" xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xmlns:dhcp="http://example.com/dhcp" xs:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/ad.xsd http://example.com/dhcp/req.xsd"><dhcp:ip>192.168.1.1</dhcp:ip><dhcp:ip>192.168.1.2</dhcp:ip><dhcp:iprange><from>192.168.1.3</from><to>192.168.1.6</to></dhcp:iprange></rspec>'

if __name__ == '__main__':
    # get the right paths together
    local_path = os.path.normpath(os.path.dirname(__file__))
    key_path = os.path.join(local_path, "test-key.pem")
    cert_path = os.path.join(local_path, "test-cert.pem")
    
    # instanciate the client
    client = GENI3Client('127.0.0.1', 8001, key_path, cert_path)
    
    # all method calls
    # print client.listResources([TEST_CREDENTIAL], True, False)
    # print client.describe(TEST_SLICE_URN, [TEST_SLICE_CREDENTIAL], False)
    # print client.allocate(TEST_SLICE_URN, [TEST_SLICE_CREDENTIAL], TEST_REQUEST_RSPEC, datetime.now())
    # print client.renew([TEST_SLICE_URN], [TEST_SLICE_CREDENTIAL], datetime.now(), best_effort=True)
    # print client.provision([TEST_SLICE_URN], [TEST_SLICE_CREDENTIAL], best_effort=True, end_time= datetime.now())
    # print client.status([TEST_SLICE_URN], [TEST_SLICE_CREDENTIAL])
    # print client.performOperationalAction([TEST_SLICE_URN], [TEST_SLICE_CREDENTIAL], "geni_start")
    # print client.delete([TEST_SLICE_URN], [TEST_SLICE_CREDENTIAL])
    # print client.shutdown([TEST_SLICE_URN], [TEST_SLICE_CREDENTIAL])
    
    # simple error handling
    # response = client.shutdown([TEST_SLICE_URN], [TEST_SLICE_CREDENTIAL])
    # client.raiseIfError(response)
    
    # catch error the error
    # try:
    #     response = client.shutdown([TEST_SLICE_URN], [TEST_SLICE_CREDENTIAL])
    #     client.raiseIfError(response)
    # except GENI3ClientError as e:
    #     print str(e)
    