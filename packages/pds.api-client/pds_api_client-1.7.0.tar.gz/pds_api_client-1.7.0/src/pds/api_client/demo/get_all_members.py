from __future__ import print_function
from pds.api_client import Configuration
from pds.api_client import ApiClient
from pds.api_client.api.product_references_api import ProductReferencesApi


# create an instance of the API class
configuration = Configuration()
configuration.host = 'https://pds.nasa.gov/api/search/1'
api_client = ApiClient(configuration)

product_references = ProductReferencesApi(api_client)

api_response = product_references.product_members_vers(
    'urn:nasa:pds:mars2020_sherloc::1.0',
    versions='latest',
    limit=20,
    fields=['ops:Label_File_Info.ops:file_ref']
)
id_list = [p.id for p in api_response.data]

for id in sorted(id_list):
    print(id)

print(len(id_list))
