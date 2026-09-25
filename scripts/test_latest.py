#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from radar import (
    enrich_with_furnidata,
    fetch_shop_items,
    filter_shop_items,
    image_url,
)


def post(webhook: str, payload: dict) -> None:
    req = urllib.request.Request(
        webhook,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "habbo-furni-radar/2.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        print("Discord HTTP:", response.status)


def main() -> int:
    webhook = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not webhook:
        raise SystemExit("DISCORD_WEBHOOK_URL no está configurado.")

    items, _ = fetch_shop_items()
    current = [item for item in filter_shop_items(items) if item.get("startsAtTimestamp")]

    current.sort(key=lambda x: x.get("startsAtTimestamp") or "", reverse=True)
    item = current[0]
    enriched, _ = enrich_with_furnidata([item])
    item = enriched[0]

    payload = {
        "username": "Habbo Furni Radar",
        "content": "🧪 Prueba mínima de embed",
        "allowed_mentions": {"parse": []},
        "embeds": [
            {
                "title": "Habbo Furni Radar • " + str(item.get("name", "Collectible")),
                "description": "Lanzamiento: " + str(item.get("startsAtTimestamp", "")),
                "image": {"url": image_url(item)},
            }
        ],
    }

    print("Testing item:", item.get("name"))
    print("Image:", image_url(item))
    post(webhook, payload)
    print("Discord OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
