import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('och1')

GCHv1DelegateBase = pm.getService('gchv1delegatebase')
gch_ex = pm.getService('gchv1exceptions')

AGGREGATE_SERVICE_TYPE = 'aggregate'
SA_SERVICE_TYPE = 'sliceauthority'
MA_SERVICE_TYPE = 'memberauthority'

DATA =[{"stype" : AGGREGATE_SERVICE_TYPE,
        'SERVICE_URL' : 'https://server.com:12345',
        'SERVICE_CERT' : '<certificate>agg1</certificate>',
        'SERVICE_NAME' : 'AGG1',
        'SERVICE_DESCRIPTION' : 'Aggregate 1',
        'SERVICE_URN' : 'urn:publicid:IDN+server.com+authority+am',
        'ISLAND_NAME' : 'Island 1'
        },
        {"stype" : AGGREGATE_SERVICE_TYPE,
         'SERVICE_URL' : 'https://backuup.com:12345', 
         'SERVICE_CERT' : '<certificate>agg2</certificate>', 
         'SERVICE_NAME' : 'AGG2',
         'SERVICE_DESCRIPTION' : 'Aggregate 2',
         'SERVICE_URN' : 'urn:publicid:IDN+backup.com+authority+am',
         'ISLAND_NAME' : 'Island 2'
        },
        {"stype" : SA_SERVICE_TYPE, 
         'SERVICE_URL' : 'https://localhost:8001/SA', 
         'SERVICE_CERT' : '<certificate>foo</certificate>', 
         'SERVICE_NAME' : 'CHAPI-SA',
         'SERVICE_DESCRIPTION' : 'CHAPI Service Authority',
         'SERVICE_URN' : 'urn:publicid:IDN+foo.com+authority+sa',
         'ISLAND_NAME' : 'Island 3'
        },
        {"stype" : SA_SERVICE_TYPE, 
         'SERVICE_URL' : 'https://localhost:8002/SA', 
         'SERVICE_CERT' : '<certificate>bar</certificate>', 
         'SERVICE_NAME' : 'CHAPI-SA2',
         'SERVICE_DESCRIPTION' : 'CHAPI Service Authority (BACKUP)',
         'SERVICE_URN' : 'urn:publicid:IDN+bar.com+authority+sa',
         'ISLAND_NAME' : 'Island 4'
        },
        {"stype" : MA_SERVICE_TYPE, 
         'SERVICE_URL' : 'https://localhost:8001/MA', 
         'SERVICE_CERT' : '<certificate>foo</certificate>', 
         'SERVICE_NAME' : 'CHAPI-MA',
         'SERVICE_DESCRIPTION' : 'CHAPI Member Authority',
         'SERVICE_URN' : 'urn:publicid:IDN+foo.com+authority+ma',
         'ISLAND_NAME' : 'Island 5'
        },
        {"stype" : MA_SERVICE_TYPE, 
         'SERVICE_URL' : 'https://localhost:8002/MA', 
         'SERVICE_CERT' : '<certificate>bar</certificate>', 
         'SERVICE_NAME' : 'CHAPI-MA2',
         'SERVICE_DESCRIPTION' : 'CHAPI Member Authority (BACKUP)',
         'SERVICE_URN' : 'urn:publicid:IDN+bar.com+authority+ma',
         'ISLAND_NAME' : 'Island 6'
        }]


class OCH1Delegate(GCHv1DelegateBase):
    def get_version(self):
        fields = {"ISLAND_NAME" : {"TYPE" : "STRING"}}
        return "0.1", fields

    def get_aggregates(self, field_filter, field_match, options):
        return self._match_and_filter([e for e in DATA if e['stype']==AGGREGATE_SERVICE_TYPE], field_filter, field_match)
