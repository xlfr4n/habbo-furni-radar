import unittest

from radar import item_key, is_nft, parse_furnidata


SAMPLE = """\
<furnidata>
  <roomitemtypes>
    <furnitype id="100" classname="classic_chair">
      <revision>70001</revision>
      <category>furniture</category>
      <name>classic_chair name</name>
      <description>classic_chair desc</description>
      <offerid>42</offerid>
      <furniline>classic</furniline>
    </furnitype>
  </roomitemtypes>
  <wallitemtypes>
    <furnitype id="200" classname="nft_h26_testitem">
      <revision>70002</revision>
      <name>nft_h26_testitem name</name>
      <furniline>nft2026</furniline>
    </furnitype>
  </wallitemtypes>
</furnidata>
"""


class RadarParserTests(unittest.TestCase):
    def test_parse_and_nft_detection(self):
        items = parse_furnidata(SAMPLE)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["id"], "100")
        self.assertFalse(is_nft(items[0]))
        self.assertTrue(items[1]["is_nft"])
        self.assertEqual(item_key(items[1]), "200|nft_h26_testitem")


if __name__ == "__main__":
    unittest.main()
