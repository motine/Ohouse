#!/usr/bin/env python

import sys
import os.path
import xmlrpclib
from datetime import datetime, timedelta
from dateutil import parser as dateparser


# on purpose: duplicate code with geni_am_api_three_client.py
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

class GENI2ClientError(Exception):
    def __init__(self, message, code):
        self._message = message
        self._code = code

    def __str__(self):
        return "%s (code: %s)" % (self._message, self._code)


class GENI2Client(object):
    """This class encapsulates a connection to a GENI AM API v2 server.
    It implements all methods of the API and manages the interaction regarding the client certificate.
    For all the client methods (e.g. listResources, describe) the given options (e.g. compress) have the default value None.
    This means if the caller does not change the value the client will not send this option and hence force the server to use the default.
    If true or false are given the options are set accordingly.
    If a time is given (e.g. end_time), please provide the method call with a Python datetime object, the RPC-conversion will then be done for you.
    
    Please checkout the date and error helper methods at the end of this class.

    Details regarding the actual method calls and options can be found via: http://groups.geni.net/geni/wiki/GAPI_AM_API_V2_DETAILS
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
        """Calls the GENI GetVersion method and returns a dict."""
        return self._proxy.GetVersion()
        

    def listResources(self, credentials, slice_urn=None, available=None, compress=None):
        """See class description above."""
        options = self._default_options()
        if available != None:
            options["geni_available"] = available
        if compress != None:
            options["geni_compress"] = compress
        if slice_urn != None:
            options["slice_urn"] = compress
        return self._proxy.ListResources(credentials, options)
    
    def createSliver(self, slice_urn, credentials, rspec, users=[]):
        """See class description above and http://groups.geni.net/geni/wiki/GAPI_AM_API_V2_DETAILS#CreateSliverDetails"""
        options = self._default_options()
        return self._proxy.CreateSliver(slice_urn, credentials, rspec, users, options)

    def deleteSliver(self, slice_urn, credentials):
        """See class description above and http://groups.geni.net/geni/wiki/GAPI_AM_API_V2_DETAILS#DeleteSliverDetails"""
        options = self._default_options()
        return self._proxy.DeleteSliver(slice_urn, credentials, options)

    def sliverStatus(self, slice_urn, credentials):
        """See class description above and http://groups.geni.net/geni/wiki/GAPI_AM_API_V2_DETAILS#SliverStatusDetails"""
        options = self._default_options()
        return self._proxy.SliverStatus(slice_urn, credentials, options)

    def renewSliver(self, slice_urn, credentials, expiration_time):
        """See class description above and http://groups.geni.net/geni/wiki/GAPI_AM_API_V2_DETAILS#RenewSliverDetails"""
        options = self._default_options()
        expiration_time = self.datetime2str(expiration_time)
        return self._proxy.RenewSliver(slice_urn, credentials, expiration_time, options)

    def shutdown(self, slice_urn, credentials):
        """See class description above and http://groups.geni.net/geni/wiki/GAPI_AM_API_V2_DETAILS#ShutdownDetails"""
        options = self._default_options()
        return self._proxy.Shutdown(slice_urn, credentials, options)

    def _default_options(self):
        """Private method for generating the default option hash, which is parsed on the server."""
        return {"geni_rspec_version" : {"version" : "3", "type" : "geni"}}

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
            raise GENI2ClientError(self.errorMessage(response), self.errorCode(response))
        return

    def errorMessage(self, response):
        return response['output']
    def errorCode(self, response):
        return int(response['code']['geni_code'])
    def isError(self, response):
        return self.errorCode(response) != 0
        

# Test code

TEST_SLICE_URN = 'urn:publicid:IDN+ofelia:eict:gcf+slice+slicename'
# use the following to get the credential `gcf$ python src/omni.py getusercred`
TEST_CREDENTIAL = '<?xml version="1.0"?>\n<signed-credential xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.planet-lab.org/resources/sfa/credential.xsd" xsi:schemaLocation="http://www.planet-lab.org/resources/sfa/ext/policy/1 http://www.planet-lab.org/resources/sfa/ext/policy/1/policy.xsd"><credential xml:id="ref0"><type>privilege</type><serial>8</serial><owner_gid>-----BEGIN CERTIFICATE-----\nMIICPTCCAaagAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMjA1MDkzMzQ0WhcNMTgw\nMjA0MDkzMzQ0WjAnMSUwIwYDVQQDExxvZmVsaWEvL2VpY3QvL2djZi51c2VyLmFs\naWNlMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCo2FSoOplnAdI5LNAaGPJd\nSyN9Y/RykNhEEcqbHL/fnMcJ6XMUTGSEUmxkp5ubPdJxnGEhwv8cp8txMi6NFeU2\nz2YZUOEXL4xrfsO4G6Eaj9TkiiTprcW74FxDWDkzLfU2ApEdzRXBXuuRJenagEf3\n86e93pSRXd0XNzJdCWRHoQIDAQABo3cwdTAMBgNVHRMBAf8EAjAAMGUGA1UdEQRe\nMFyGK3VybjpwdWJsaWNpZDpJRE4rb2ZlbGlhOmVpY3Q6Z2NmK3VzZXIrYWxpY2WG\nLXVybjp1dWlkOmVhMzBkOThjLWUzYjYtNDIzYy04ZTUxLTA3NGY1OGI1ZTU1YzAN\nBgkqhkiG9w0BAQQFAAOBgQDS5D5o0eThkZOQwLrXs/ME3d/ppEQunmoLGI0ICG4x\n9aSFJZReGLs1vUzYYR7LHn/+sbv6r9p5cAOCArEGzCVdTuPfxKh6SlvXt+cijBKf\n0/ZFGMSFPcnG6dEDlOTK0PnD52MgfmZ83udRClmRoOO9Ph/5ae2KqwvvcCbSL9dD\nlw==\n-----END CERTIFICATE-----\n-----BEGIN CERTIFICATE-----\nMIICRDCCAa2gAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMjA1MDkzMzQ0WhcNMTgw\nMjA0MDkzMzQ0WjApMScwJQYDVQQDEx5vZmVsaWEvL2VpY3QvL2djZi5hdXRob3Jp\ndHkuc2EwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAO5zLoStkSytfhFdRI1t\nqFKHOxf8awNWxSsV229CMcRFfIedyeICEies6xU+bxpNs4Cx79RLdHEo5944VcBR\nl//K2rU0Am79QcA9WfB/l49W0VsscM3L3qD3i6xK5KjToTfMZSDylhfY6Nm05gzx\nXmrKYTuLppJJoQLSMB3DGeEtAgMBAAGjfDB6MA8GA1UdEwEB/wQFMAMBAf8wZwYD\nVR0RBGAwXoYtdXJuOnB1YmxpY2lkOklETitvZmVsaWE6ZWljdDpnY2YrYXV0aG9y\naXR5K3Nhhi11cm46dXVpZDphZmJmNWEwYy1hNjE1LTRjZjEtYjI5OS1mYjc4YzI3\nN2JhMjkwDQYJKoZIhvcNAQEEBQADgYEApKin+EE5CDZvnuQNGJIVJ7AsVSNMM71B\nMDxWKNc6IWn1lPsNwZNTDYNL7oV5MQiqUfsWcAwmBSEymqbw9M1R497BmF11C6fA\nflH25MkjoLBjx212YCkjv92r3OHnJw9Xf9MSYsm4TuMiCGkpPRVkpQyZxLLWY0R2\nIBHno4tcSmA=\n-----END CERTIFICATE-----\n</owner_gid><owner_urn>urn:publicid:IDN+ofelia:eict:gcf+user+alice</owner_urn><target_gid>-----BEGIN CERTIFICATE-----\nMIICPTCCAaagAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMjA1MDkzMzQ0WhcNMTgw\nMjA0MDkzMzQ0WjAnMSUwIwYDVQQDExxvZmVsaWEvL2VpY3QvL2djZi51c2VyLmFs\naWNlMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCo2FSoOplnAdI5LNAaGPJd\nSyN9Y/RykNhEEcqbHL/fnMcJ6XMUTGSEUmxkp5ubPdJxnGEhwv8cp8txMi6NFeU2\nz2YZUOEXL4xrfsO4G6Eaj9TkiiTprcW74FxDWDkzLfU2ApEdzRXBXuuRJenagEf3\n86e93pSRXd0XNzJdCWRHoQIDAQABo3cwdTAMBgNVHRMBAf8EAjAAMGUGA1UdEQRe\nMFyGK3VybjpwdWJsaWNpZDpJRE4rb2ZlbGlhOmVpY3Q6Z2NmK3VzZXIrYWxpY2WG\nLXVybjp1dWlkOmVhMzBkOThjLWUzYjYtNDIzYy04ZTUxLTA3NGY1OGI1ZTU1YzAN\nBgkqhkiG9w0BAQQFAAOBgQDS5D5o0eThkZOQwLrXs/ME3d/ppEQunmoLGI0ICG4x\n9aSFJZReGLs1vUzYYR7LHn/+sbv6r9p5cAOCArEGzCVdTuPfxKh6SlvXt+cijBKf\n0/ZFGMSFPcnG6dEDlOTK0PnD52MgfmZ83udRClmRoOO9Ph/5ae2KqwvvcCbSL9dD\nlw==\n-----END CERTIFICATE-----\n-----BEGIN CERTIFICATE-----\nMIICRDCCAa2gAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMjA1MDkzMzQ0WhcNMTgw\nMjA0MDkzMzQ0WjApMScwJQYDVQQDEx5vZmVsaWEvL2VpY3QvL2djZi5hdXRob3Jp\ndHkuc2EwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAO5zLoStkSytfhFdRI1t\nqFKHOxf8awNWxSsV229CMcRFfIedyeICEies6xU+bxpNs4Cx79RLdHEo5944VcBR\nl//K2rU0Am79QcA9WfB/l49W0VsscM3L3qD3i6xK5KjToTfMZSDylhfY6Nm05gzx\nXmrKYTuLppJJoQLSMB3DGeEtAgMBAAGjfDB6MA8GA1UdEwEB/wQFMAMBAf8wZwYD\nVR0RBGAwXoYtdXJuOnB1YmxpY2lkOklETitvZmVsaWE6ZWljdDpnY2YrYXV0aG9y\naXR5K3Nhhi11cm46dXVpZDphZmJmNWEwYy1hNjE1LTRjZjEtYjI5OS1mYjc4YzI3\nN2JhMjkwDQYJKoZIhvcNAQEEBQADgYEApKin+EE5CDZvnuQNGJIVJ7AsVSNMM71B\nMDxWKNc6IWn1lPsNwZNTDYNL7oV5MQiqUfsWcAwmBSEymqbw9M1R497BmF11C6fA\nflH25MkjoLBjx212YCkjv92r3OHnJw9Xf9MSYsm4TuMiCGkpPRVkpQyZxLLWY0R2\nIBHno4tcSmA=\n-----END CERTIFICATE-----\n</target_gid><target_urn>urn:publicid:IDN+ofelia:eict:gcf+user+alice</target_urn><uuid/><expires>2013-05-18T08:07:21</expires><privileges><privilege><name>refresh</name><can_delegate>false</can_delegate></privilege><privilege><name>resolve</name><can_delegate>false</can_delegate></privilege><privilege><name>info</name><can_delegate>false</can_delegate></privilege></privileges></credential><signatures><Signature xmlns="http://www.w3.org/2000/09/xmldsig#" xml:id="Sig_ref0">\n  <SignedInfo>\n    <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>\n    <SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>\n    <Reference URI="#ref0">\n      <Transforms>\n        <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>\n      </Transforms>\n      <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>\n      <DigestValue>kKuVo2xpp9YRDr/9mVD/2LL+nbQ=</DigestValue>\n    </Reference>\n  </SignedInfo>\n  <SignatureValue>X7ORUm4xco4tSVy1aoOXhhp9AjOXT+hH9zmIIAXz/928u8TDf6UbYkqAhiM216ZA\nMTq5udAO0sVSb0uN/i2Z99pUNYl28gMYIoVq5jBhndSaFC8IW2wEF7Orwn4lD7DQ\nbdTfrKmZexPO1ZUQ7Nu43KhRFy0LYoiWwOBDQZIl3yk=</SignatureValue>\n  <KeyInfo>\n    <X509Data>\n      \n      \n      \n    <X509Certificate>MIICRDCCAa2gAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMjA1MDkzMzQ0WhcNMTgw\nMjA0MDkzMzQ0WjApMScwJQYDVQQDEx5vZmVsaWEvL2VpY3QvL2djZi5hdXRob3Jp\ndHkuc2EwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAO5zLoStkSytfhFdRI1t\nqFKHOxf8awNWxSsV229CMcRFfIedyeICEies6xU+bxpNs4Cx79RLdHEo5944VcBR\nl//K2rU0Am79QcA9WfB/l49W0VsscM3L3qD3i6xK5KjToTfMZSDylhfY6Nm05gzx\nXmrKYTuLppJJoQLSMB3DGeEtAgMBAAGjfDB6MA8GA1UdEwEB/wQFMAMBAf8wZwYD\nVR0RBGAwXoYtdXJuOnB1YmxpY2lkOklETitvZmVsaWE6ZWljdDpnY2YrYXV0aG9y\naXR5K3Nhhi11cm46dXVpZDphZmJmNWEwYy1hNjE1LTRjZjEtYjI5OS1mYjc4YzI3\nN2JhMjkwDQYJKoZIhvcNAQEEBQADgYEApKin+EE5CDZvnuQNGJIVJ7AsVSNMM71B\nMDxWKNc6IWn1lPsNwZNTDYNL7oV5MQiqUfsWcAwmBSEymqbw9M1R497BmF11C6fA\nflH25MkjoLBjx212YCkjv92r3OHnJw9Xf9MSYsm4TuMiCGkpPRVkpQyZxLLWY0R2\nIBHno4tcSmA=</X509Certificate>\n<X509SubjectName>CN=ofelia//eict//gcf.authority.sa</X509SubjectName>\n<X509IssuerSerial>\n<X509IssuerName>CN=ofelia//eict//gcf.authority.sa</X509IssuerName>\n<X509SerialNumber>3</X509SerialNumber>\n</X509IssuerSerial>\n</X509Data>\n    <KeyValue>\n<RSAKeyValue>\n<Modulus>\n7nMuhK2RLK1+EV1EjW2oUoc7F/xrA1bFKxXbb0IxxEV8h53J4gISJ6zrFT5vGk2z\ngLHv1Et0cSjn3jhVwFGX/8ratTQCbv1BwD1Z8H+Xj1bRWyxwzcveoPeLrErkqNOh\nN8xlIPKWF9jo2bTmDPFeasphO4umkkmhAtIwHcMZ4S0=\n</Modulus>\n<Exponent>\nAQAB\n</Exponent>\n</RSAKeyValue>\n</KeyValue>\n  </KeyInfo>\n</Signature></signatures></signed-credential>\n'
# to get the following credential call `gcf$ python src/omni.py getslicecred slicename`
TEST_SLICE_CREDENTIAL = '<?xml version="1.0"?>\n<signed-credential xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.planet-lab.org/resources/sfa/credential.xsd" xsi:schemaLocation="http://www.planet-lab.org/resources/sfa/ext/policy/1 http://www.planet-lab.org/resources/sfa/ext/policy/1/policy.xsd"><credential xml:id="ref0"><type>privilege</type><serial>8</serial><owner_gid>-----BEGIN CERTIFICATE-----\nMIICPTCCAaagAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMjA1MDkzMzQ0WhcNMTgw\nMjA0MDkzMzQ0WjAnMSUwIwYDVQQDExxvZmVsaWEvL2VpY3QvL2djZi51c2VyLmFs\naWNlMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCo2FSoOplnAdI5LNAaGPJd\nSyN9Y/RykNhEEcqbHL/fnMcJ6XMUTGSEUmxkp5ubPdJxnGEhwv8cp8txMi6NFeU2\nz2YZUOEXL4xrfsO4G6Eaj9TkiiTprcW74FxDWDkzLfU2ApEdzRXBXuuRJenagEf3\n86e93pSRXd0XNzJdCWRHoQIDAQABo3cwdTAMBgNVHRMBAf8EAjAAMGUGA1UdEQRe\nMFyGK3VybjpwdWJsaWNpZDpJRE4rb2ZlbGlhOmVpY3Q6Z2NmK3VzZXIrYWxpY2WG\nLXVybjp1dWlkOmVhMzBkOThjLWUzYjYtNDIzYy04ZTUxLTA3NGY1OGI1ZTU1YzAN\nBgkqhkiG9w0BAQQFAAOBgQDS5D5o0eThkZOQwLrXs/ME3d/ppEQunmoLGI0ICG4x\n9aSFJZReGLs1vUzYYR7LHn/+sbv6r9p5cAOCArEGzCVdTuPfxKh6SlvXt+cijBKf\n0/ZFGMSFPcnG6dEDlOTK0PnD52MgfmZ83udRClmRoOO9Ph/5ae2KqwvvcCbSL9dD\nlw==\n-----END CERTIFICATE-----\n</owner_gid><owner_urn>urn:publicid:IDN+ofelia:eict:gcf+user+alice</owner_urn><target_gid>-----BEGIN CERTIFICATE-----\nMIICRzCCAbCgAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwNTE3MDgwMDU3WhcNMTgw\nNTE2MDgwMDU3WjAsMSowKAYDVQQDEyFvZmVsaWEvL2VpY3QvL2djZi5zbGljZS5z\nbGljZW5hbWUwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAL/ZsfpG8iVeUmn1\n5ZP8CjaU/MuwByvX+dvKVxOVyuspVufWcsk9ybF2EbwsogdIl2m35stN71QLfwa9\nR5TF8+1hCb1Jd70UtOUMRFmZil1Hu/XTfn5lq9L7ribDzRX99i0A9Jq1usIdCZHs\nVerbIkxb0veaCCKafclzBA5VkBuZAgMBAAGjfDB6MAwGA1UdEwEB/wQCMAAwagYD\nVR0RBGMwYYYwdXJuOnB1YmxpY2lkOklETitvZmVsaWE6ZWljdDpnY2Yrc2xpY2Ur\nc2xpY2VuYW1lhi11cm46dXVpZDpiYWRlZWM2MS0yMTkzLTRkNWItYmJiNC1lNGRm\nYTMyOGM5NTQwDQYJKoZIhvcNAQEEBQADgYEAPXrin/+bKc1kPFzc9UOymnWdKfts\nehGwZGw7a1i4p+3zBP8WpGNYQhIFnxRDf8suxOzFZCQuVaHHNC6I+Pkrf2I5Apro\nt7VATu69cd46835368vAHf9doad/OKFOFymWllrOOnyurDrBNcglYpVLJHlGcyi7\n54Xs53/Dbi3Zjbg=\n-----END CERTIFICATE-----\n-----BEGIN CERTIFICATE-----\nMIICRDCCAa2gAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMjA1MDkzMzQ0WhcNMTgw\nMjA0MDkzMzQ0WjApMScwJQYDVQQDEx5vZmVsaWEvL2VpY3QvL2djZi5hdXRob3Jp\ndHkuc2EwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAO5zLoStkSytfhFdRI1t\nqFKHOxf8awNWxSsV229CMcRFfIedyeICEies6xU+bxpNs4Cx79RLdHEo5944VcBR\nl//K2rU0Am79QcA9WfB/l49W0VsscM3L3qD3i6xK5KjToTfMZSDylhfY6Nm05gzx\nXmrKYTuLppJJoQLSMB3DGeEtAgMBAAGjfDB6MA8GA1UdEwEB/wQFMAMBAf8wZwYD\nVR0RBGAwXoYtdXJuOnB1YmxpY2lkOklETitvZmVsaWE6ZWljdDpnY2YrYXV0aG9y\naXR5K3Nhhi11cm46dXVpZDphZmJmNWEwYy1hNjE1LTRjZjEtYjI5OS1mYjc4YzI3\nN2JhMjkwDQYJKoZIhvcNAQEEBQADgYEApKin+EE5CDZvnuQNGJIVJ7AsVSNMM71B\nMDxWKNc6IWn1lPsNwZNTDYNL7oV5MQiqUfsWcAwmBSEymqbw9M1R497BmF11C6fA\nflH25MkjoLBjx212YCkjv92r3OHnJw9Xf9MSYsm4TuMiCGkpPRVkpQyZxLLWY0R2\nIBHno4tcSmA=\n-----END CERTIFICATE-----\n</target_gid><target_urn>urn:publicid:IDN+ofelia:eict:gcf+slice+slicename</target_urn><uuid/><expires>2013-05-17T10:00:57</expires><privileges><privilege><name>refresh</name><can_delegate>true</can_delegate></privilege><privilege><name>embed</name><can_delegate>true</can_delegate></privilege><privilege><name>bind</name><can_delegate>true</can_delegate></privilege><privilege><name>control</name><can_delegate>true</can_delegate></privilege><privilege><name>info</name><can_delegate>true</can_delegate></privilege></privileges></credential><signatures><Signature xmlns="http://www.w3.org/2000/09/xmldsig#" xml:id="Sig_ref0">\n  <SignedInfo>\n    <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>\n    <SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>\n    <Reference URI="#ref0">\n      <Transforms>\n        <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>\n      </Transforms>\n      <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>\n      <DigestValue>lJXA/vkej6n9/KRWOZW0+rQeKuA=</DigestValue>\n    </Reference>\n  </SignedInfo>\n  <SignatureValue>JOGag2Ya34MzL5mrYDELs6dZe0fSwuoyTRdeZmMpbnNVTEbUMdjC2IUjTNZRazh2\nB7tNHp3K285xmey6AVRnRXdS1yzob1BYmUlPckuLUEH87Bi22D/K7u3a5YTwj39M\nH1m/CODZ2ajOcuasIw99U4Pyy5cvfWfCB21OGYwyBC8=</SignatureValue>\n  <KeyInfo>\n    <X509Data>\n      \n      \n      \n    <X509Certificate>MIICRDCCAa2gAwIBAgIBAzANBgkqhkiG9w0BAQQFADApMScwJQYDVQQDEx5vZmVs\naWEvL2VpY3QvL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwMjA1MDkzMzQ0WhcNMTgw\nMjA0MDkzMzQ0WjApMScwJQYDVQQDEx5vZmVsaWEvL2VpY3QvL2djZi5hdXRob3Jp\ndHkuc2EwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAO5zLoStkSytfhFdRI1t\nqFKHOxf8awNWxSsV229CMcRFfIedyeICEies6xU+bxpNs4Cx79RLdHEo5944VcBR\nl//K2rU0Am79QcA9WfB/l49W0VsscM3L3qD3i6xK5KjToTfMZSDylhfY6Nm05gzx\nXmrKYTuLppJJoQLSMB3DGeEtAgMBAAGjfDB6MA8GA1UdEwEB/wQFMAMBAf8wZwYD\nVR0RBGAwXoYtdXJuOnB1YmxpY2lkOklETitvZmVsaWE6ZWljdDpnY2YrYXV0aG9y\naXR5K3Nhhi11cm46dXVpZDphZmJmNWEwYy1hNjE1LTRjZjEtYjI5OS1mYjc4YzI3\nN2JhMjkwDQYJKoZIhvcNAQEEBQADgYEApKin+EE5CDZvnuQNGJIVJ7AsVSNMM71B\nMDxWKNc6IWn1lPsNwZNTDYNL7oV5MQiqUfsWcAwmBSEymqbw9M1R497BmF11C6fA\nflH25MkjoLBjx212YCkjv92r3OHnJw9Xf9MSYsm4TuMiCGkpPRVkpQyZxLLWY0R2\nIBHno4tcSmA=</X509Certificate>\n<X509SubjectName>CN=ofelia//eict//gcf.authority.sa</X509SubjectName>\n<X509IssuerSerial>\n<X509IssuerName>CN=ofelia//eict//gcf.authority.sa</X509IssuerName>\n<X509SerialNumber>3</X509SerialNumber>\n</X509IssuerSerial>\n</X509Data>\n    <KeyValue>\n<RSAKeyValue>\n<Modulus>\n7nMuhK2RLK1+EV1EjW2oUoc7F/xrA1bFKxXbb0IxxEV8h53J4gISJ6zrFT5vGk2z\ngLHv1Et0cSjn3jhVwFGX/8ratTQCbv1BwD1Z8H+Xj1bRWyxwzcveoPeLrErkqNOh\nN8xlIPKWF9jo2bTmDPFeasphO4umkkmhAtIwHcMZ4S0=\n</Modulus>\n<Exponent>\nAQAB\n</Exponent>\n</RSAKeyValue>\n</KeyValue>\n  </KeyInfo>\n</Signature></signatures></signed-credential>\n'
# to get a request rspec call listResources on the AM, select the resources you want and change the rspec-type to "request"
TEST_REQUEST_RSPEC = '<?xml version="1.0" encoding="UTF-8"?><rspec xmlns="http://www.geni.net/resources/rspec/3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/ad.xsd" type="request"><node component_manager_id="urn:publicid:ofelia:eict:gcf+authority+am" component_name="f4512d8b-a92a-45e1-a0f1-516ab6a6b661" component_id="urn:publicid:ofelia:eict:gcf+fakevm+f4512d8b-a92a-45e1-a0f1-516ab6a6b661" exclusive="false"/></rspec>'

if __name__ == '__main__':
    # get the right paths together
    local_path = os.path.normpath(os.path.dirname(__file__))
    key_path = os.path.join(local_path, "alice-key.pem") # make sure the CA of the AM is the same which issued this certificate (e.g. copy certificates from omni)
    cert_path = os.path.join(local_path, "alice-cert.pem")
    
    # instanciate the client
    client = GENI2Client('127.0.0.1', 8001, key_path, cert_path)
    
    # all method calls
    # print client.getVersion()
    print client.listResources([TEST_CREDENTIAL], None, True, False)
    # print client.createSliver(TEST_SLICE_URN, [TEST_SLICE_CREDENTIAL], TEST_REQUEST_RSPEC, users=[])
    # print client.deleteSliver(TEST_SLICE_URN, [TEST_SLICE_CREDENTIAL])
    # print client.sliverStatus(TEST_SLICE_URN, [TEST_SLICE_CREDENTIAL]) # smart people create a sliver first before calling sliverStatus on it
    # print client.renewSliver(TEST_SLICE_URN, [TEST_SLICE_CREDENTIAL], datetime.now() + timedelta(0, 60*60))
    # print client.shutdown(TEST_SLICE_URN, [TEST_SLICE_CREDENTIAL])

    
    # simple error handling
    # response = client.createSliver(TEST_SLICE_URN, [TEST_SLICE_CREDENTIAL], TEST_REQUEST_RSPEC, users=[])
    # client.raiseIfError(response)
    
    # catch error the error
    # try:
    #     client.createSliver(TEST_SLICE_URN, [TEST_SLICE_CREDENTIAL], TEST_REQUEST_RSPEC, users=[])
    #     client.raiseIfError(response)
    # except GENI3ClientError as e:
    #     print str(e)
    