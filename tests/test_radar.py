import unittest

from radar import (
    build_embed,
    format_timestamp,
    image_url,
    is_non_token_collectible,
    parse_furnidata,
    shop_status,
)


SAMPLE_XML = """
<furnidata>
  <roomitemtypes>
    <furnitype id="18690" classname="nft_h26_cactussofa">
      <revision>75858</revision>
      <category>other</category>
      <name>nft_h26_cactussofa name</name>
      <description>nft_h26_cactussofa desc</description>
      <offerid>123</offerid>
      <furniline>nft2026</furniline>
      <specialtype>0</specialtype>
    </furnitype>
  </roomitemtypes>
</furnidata>
"""

SAMPLE_ITEM = {
    "name": "Cactus Sofa",
    "image_url": "nft_h26_cactussofa.png",
    "productCode": "nft_h26_cactussofa",
    "rarity": "Epic",
    "collection": "furniture",
    "itemType": "Furni",
    "mintCost": 800,
    "minted": 1,
    "startsAtTimestamp": "2026-09-23T08:45:00.000Z",
    "visibleAtTimestamp": "2026-09-23T08:42:00.000Z",
    "createdAt": "2026-09-23T08:45:20.111Z",
    "endsAtTimestamp": "2099-10-07T11:00:00.000Z",
    "hidden": False,
    "staging": False,
    "mintLimit": None,
}


class RadarTests(unittest.TestCase):
    def test_parse_furnidata(self):
        parsed = parse_furnidata(SAMPLE_XML)
        self.assertEqual(parsed["nft_h26_cactussofa"]["furni_id"], "18690")
        self.assertEqual(parsed["nft_h26_cactussofa"]["revision"], "75858")
        self.assertEqual(parsed["nft_h26_cactussofa"]["furniline"], "nft2026")

    def test_token_is_excluded(self):
        token = {
            "productCode": "nft_emerald_100",
            "itemType": "Token",
            "collection": "tokens",
        }
        self.assertFalse(is_non_token_collectible(token))
        self.assertTrue(is_non_token_collectible(SAMPLE_ITEM))

    def test_image_url(self):
        self.assertEqual(
            image_url(SAMPLE_ITEM),
            "https://nft-tokens.habbo.com/collectibles/furni/images/nft_h26_cactussofa.png",
        )

    def test_timestamp_conversion(self):
        formatted = format_timestamp("2026-09-23T08:45:00.000Z")
        self.assertIn("23/09/2026 10:45:00", formatted)
        self.assertIn("UTC 08:45:00Z", formatted)

    def test_status_active(self):
        self.assertEqual(shop_status(SAMPLE_ITEM), "Activo")

    def test_hidden_status(self):
        self.assertEqual(
            shop_status({**SAMPLE_ITEM, "hidden": True}),
            "Oculto",
        )

    def test_embed_is_within_discord_limits(self):
        embed = build_embed(
            SAMPLE_ITEM,
            {"price": 0.001, "link": "https://example.com/market"},
            {"usd": 2500.0, "eur": 2100.0},
            "2026-09-25T10:00:00.000Z",
        )
        self.assertLessEqual(len(embed.get("description", "")), 2048)
        total = len(embed.get("title", "")) + len(embed.get("description", ""))
        total += len(embed.get("footer", {}).get("text", ""))
        for field in embed.get("fields", []):
            self.assertLessEqual(len(field["name"]), 256)
            self.assertLessEqual(len(field["value"]), 1024)
            total += len(field["name"]) + len(field["value"])
        self.assertLessEqual(total, 6000)
        self.assertTrue(embed["image"]["url"].startswith("https://"))
        self.assertIn("Cactus Sofa", embed["title"])
        self.assertIn("🚀 **Lanzamiento:**", embed["description"])
        self.assertIn("### 🔎 Identificación", embed["description"])
        self.assertIn("### 🔗 Mercado", embed["description"])
        self.assertIn("color", embed)
        self.assertEqual(
            embed["url"],
            "https://collectibles.habbo.com/shop/?tab=shop",
        )


if __name__ == "__main__":
    unittest.main()
