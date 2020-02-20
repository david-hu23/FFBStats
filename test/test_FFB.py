import unittest
import os
import main
import json

def get_sample_JSON():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    open_file = open(os.path.join(current_directory, "sampleJSON.txt"))
    JSON = json.load(open_file)
    open_file.close()
    return JSON

class ApplicationWindowTests(unittest.TestCase):

    def setUp(self):
        self.sample_json = get_sample_JSON()

    def test_sample_JSON_exists(self):
        self.assertGreater(len(self.sample_json), 0)

    def test_clear_cache(self):
        main.FFB.on_click_clear_cache_button(self.sample_json)
        self.assertFalse(self.sample_json) #Empty list = false

        #Rebuild
        self.sample_json = get_sample_JSON()

if __name__ == "__main__":
    unittest.main()