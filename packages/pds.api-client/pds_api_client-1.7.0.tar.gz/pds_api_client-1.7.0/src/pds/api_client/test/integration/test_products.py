import unittest
from pds.api_client import Configuration
from pds.api_client import ApiClient

from pds.api_client.api.all_products_api import AllProductsApi
from .constants import HOST

class ProductsCase(unittest.TestCase):

    def setUp(self):
        # create an instance of the API class
        configuration = Configuration()
        configuration.host = HOST
        api_client = ApiClient(configuration)
        self.products = AllProductsApi(api_client)

    def test_get_properties(self):

        properties = self.products.product_properties_list()
        properties_dict = {p.var_property:{"type": p.type} for p in properties}
        assert '_package_id' in properties_dict.keys()
        assert 'alternate_ids' in properties_dict.keys()
        # TODO remove when insight missing ldd json is published
        assert 'insight:Observation_Information.insight:software_version_id' in properties_dict.keys()
        assert properties_dict['_package_id']['type'] == 'string'
        assert properties_dict['alternate_ids']['type'] == 'string'
        # TODO remove when insight missing ldd json is published
        assert properties_dict['insight:Observation_Information.insight:software_version_id']['type'] == 'string'

    @unittest.skip("keyword is temporarily not implemented in version 1.5.0 of the API")
    def test_products_by_keywords(self):
        results = self.products.product_list(
            keywords=['kernel']
        )

        self.assertEqual(len(results.data), 3)  # add assertion here


if __name__ == '__main__':
    unittest.main()
