from pds.api_client import Configuration
from pds.api_client import ApiClient
from pds.api_client.api.all_products_api import AllProductsApi

configuration = Configuration()
configuration.host = 'https://pds.nasa.gov/api/search-en-gamma/1'
api_client = ApiClient(configuration)
all_products = AllProductsApi(api_client)
exact_bundle = all_products.select_by_lidvid('urn:nasa:pds:magellan_gxdr::1.0')
print(exact_bundle.title)

