import unittest

from shs_crawler_full import SHSCrawlerFull


class CategorySelectionTest(unittest.TestCase):
    def test_keeps_every_non_empty_category_option(self):
        options = [
            {"value": "", "text": "請選擇"},
            {"value": "1", "text": "國文類"},
            {"value": "8", "text": "工程技術類"},
            {"value": "13", "text": "資訊類"},
        ]

        self.assertEqual(
            SHSCrawlerFull.extract_valid_categories(options),
            [
                {"value": "1", "text": "國文類"},
                {"value": "8", "text": "工程技術類"},
                {"value": "13", "text": "資訊類"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
