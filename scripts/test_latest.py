#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from radar import (
    enrich_with_furnidata,
    fetch_eth_prices,
    fetch_shop_items,
    fetch_shop_prices,
    filter_shop_items,
    is_visible_release,
    item_key,
    send_discord,
)


def main() -> int:
    webhook = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not webhook:
        raise SystemExit("DISCORD_WEBHOOK_URL no está configurado.")

    items, digest = fetch_shop_items()
    current = [
        item
        for item in filter_shop_items(items)
        if is_visible_release(item)
    ]

    current.sort(
        key=lambda item: (
            item.get("startsAtTimestamp")
            or item.get("visibleAtTimestamp")
            or item.get("createdAt")
            or ""
        ),
        reverse=True,
    )

    latest = list(reversed(current[:10]))
    enriched, furnidata_digest = enrich_with_furnidata(latest)
    markets = fetch_shop_prices([item_key(item) for item in enriched])
    eth_rates = fetch_eth_prices()
    detected_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    print("=== 10 LATEST OFFICIAL SHOP RELEASES ===")
    for index, item in enumerate(enriched, 1):
        print(
            f"{index}. {item.get('name')} | "
            f"{item.get('productCode')} | "
            f"release={item.get('startsAtTimestamp')} | "
            f"visible={item.get('visibleAtTimestamp')}"
        )

    send_discord(webhook, enriched, markets, eth_rates, detected_at)

    print("")
    print(f"Discord OK: {len(enriched)} elementos enviados.")
    print(f"Shop SHA256: {digest}")
    print(f"Furnidata SHA256: {furnidata_digest or 'no disponible'}")
    print("Orden: más antiguo -> más reciente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
