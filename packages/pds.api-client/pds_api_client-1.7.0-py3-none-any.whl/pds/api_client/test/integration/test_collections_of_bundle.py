import unittest
from pds.api_client import Configuration
from pds.api_client import ApiClient
from pds.api_client.api.product_references_api import ProductReferencesApi
from .constants import HOST

class CollectionsOfBundleTestCase(unittest.TestCase):
    def setUp(self):
        # create an instance of the API class
        configuration = Configuration()
        configuration.host = HOST
        api_client = ApiClient(configuration)
        self.product_reference = ProductReferencesApi(api_client)

    def test_collections_of_a_bundle_default(self):

        results = self.product_reference.product_members(
            'urn:nasa:pds:mars2020.spice::3.0',
            fields=['ops:Data_File_Info.ops:file_ref']
        )
        for collection in results.data:
            urls = collection.properties['ops:Data_File_Info.ops:file_ref']
            for url in urls:
                print(url)

    def test_all_collections_of_a_bundle_as_deep_archive_does(self):

        def get_collections(bundle_lidvid):
            _apiquerylimit = 50
            _propdataurl = "ops:Data_File_Info.ops:file_ref"
            _propdatamd5 = "ops:Data_File_Info.ops:md5_checksum"
            _proplabelurl = "ops:Label_File_Info.ops:file_ref"
            _proplabelmd5 = "ops:Label_File_Info.ops:md5_checksum"
            _proplabelharvesttime = "ops:Harvest_Info.ops:harvest_date_time"
            _fields = [_propdataurl, _propdatamd5, _proplabelurl, _proplabelmd5, _proplabelharvesttime]

            full_page = True

            kwargs = dict(
                sort=['ops:Harvest_Info.ops:harvest_date_time'],
                limit=_apiquerylimit,
                fields=_fields
            )

            while full_page:
                page = self.product_reference.product_members(bundle_lidvid, **kwargs)
                full_page = len(page.data) == _apiquerylimit
                for c in page.data:
                    yield c
                kwargs['search_after'] = page.data[-1].properties['ops:Harvest_Info.ops:harvest_date_time'][0]

        n = 0
        for collection in get_collections("urn:nasa:pds:mars2020.spice::3.0"):
            print(collection.id)
            n += 1

        assert n == 1

    def test_collection_members(self):
        results = self.product_reference.product_members(
            'urn:nasa:pds:mars2020.spice:spice_kernels::3.0'
        )

        self.assertEqual(len(results.data), 4)  # add assertion here


if __name__ == '__main__':
    unittest.main()
