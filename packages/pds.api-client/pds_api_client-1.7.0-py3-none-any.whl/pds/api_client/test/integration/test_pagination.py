import unittest
from pds.api_client import Configuration
from pds.api_client import ApiClient

from pds.api_client.api.all_products_api import AllProductsApi

from .constants import HOST

class PaginationTestCase(unittest.TestCase):
    def setUp(self):
        # create an instance of the API class
        configuration = Configuration()
        configuration.host = HOST
        api_client = ApiClient(configuration)
        self.products = AllProductsApi(api_client)

    def test_pages(self):
        results_1 = self.products.product_list(
            q='ref_lid_instrument eq "urn:nasa:pds:context:instrument:radiometer.insight"',
            sort=['ops:Harvest_Info.ops:harvest_date_time'],
            limit=3
        )

        self.assertEqual(len(results_1.data), 3)  # add assertion here

        latest_harvest_date_time = results_1.data[-1].properties['ops:Harvest_Info.ops:harvest_date_time'][0]

        results_2 = self.products.product_list(
            q='ref_lid_instrument eq "urn:nasa:pds:context:instrument:radiometer.insight"',
            sort=['ops:Harvest_Info.ops:harvest_date_time'],
            search_after=[latest_harvest_date_time],
            limit=3
        )

        self.assertEqual(len(results_2.data), 3)


if __name__ == '__main__':
    unittest.main()
