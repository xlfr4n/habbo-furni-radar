#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from radar import enrich_with_furnidata, fetch_shop_items, filter_shop_items, image_url


WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"].strip()


def request_json(url: str, method: str, payload=None):
    data = None
    headers = {"User-Agent": "habbo-furni-radar/2.0"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            body = response.read()
            return response.status, json.loads(body) if body else {}
    except Exception as exc:
        if hasattr(exc, "read"):
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP error: {getattr(exc, 'code', '?')} {body}") from exc
        raise


def post_and_delete(payload):
    status, body = request_json(WEBHOOK + "?wait=true", "POST", payload)
    if status not in (200, 204):
        raise RuntimeError(f"Unexpected POST status {status}")
    message_id = body.get("id")
    if not message_id:
        raise RuntimeError("Discord no devolvió message id para borrar la prueba.")
    delete_url = WEBHOOK.rstrip("/") + "/messages/" + str(message_id)
    delete_status, _ = request_json(delete_url, "DELETE")
    if delete_status not in (200, 204):
        raise RuntimeError(f"Unexpected DELETE status {delete_status}")


def main() -> int:
    items, _ = fetch_shop_items()
    current = [x for x in filter_shop_items(items) if x.get("startsAtTimestamp")]
    current.sort(key=lambda x: x.get("startsAtTimestamp") or "", reverse=True)
    item = current[0]
    enriched, _ = enrich_with_furnidata([item])
    item = enriched[0]
    img = image_url(item)
    name = str(item.get("name") or "Test Collectible")
    iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    furnidata = item.get("furnidata") or {}
    base_embed = {
        "title": "TEST • " + name,
        "description": "Lanzamiento: " + str(item.get("startsAtTimestamp", "")),
        "image": {"url": img},
    }

    cases = [
        ("minimal", dict(base_embed)),
        ("timestamp", {**base_embed, "timestamp": iso}),
        ("footer", {**base_embed, "footer": {"text": "Habbo Furni Radar"}}),
        ("url", {**base_embed, "url": "https://collectibles.habbo.com/shop/?tab=shop"}),
        ("field_one", {
            **base_embed,
            "fields": [{"name": "Rareza", "value": str(item.get("rarity") or "—"), "inline": True}],
        }),
        ("fields_many", {
            **base_embed,
            "fields": [
                {"name": "Tipo", "value": str(item.get("itemType") or "—"), "inline": True},
                {"name": "Rareza", "value": str(item.get("rarity") or "—"), "inline": True},
                {"name": "Colección", "value": str(item.get("collection") or "—"), "inline": True},
                {"name": "Precio emisión", "value": str(item.get("mintCost") or "—") + " Emeralds", "inline": True},
                {"name": "Acuñados", "value": str(item.get("minted") or "—"), "inline": True},
                {"name": "Product code", "value": str(item.get("productCode") or "—"), "inline": False},
            ],
        }),
        ("description_long", {
            **base_embed,
            "description": (
                "Lanzamiento: " + str(item.get("startsAtTimestamp", "")) + "\n"
                "Visible: " + str(item.get("visibleAtTimestamp", "")) + "\n"
                "Creado: " + str(item.get("createdAt", "")) + "\n"
                "Actualizado: " + str(item.get("updatedAt", "")) + "\n"
                "Descripción furnidata: " + str(furnidata.get("furni_description") or "—")
            ),
        }),
    ]

    for name_case, embed in cases:
        payload = {
            "username": "Habbo Furni Radar",
            "content": "🧪 embed-matrix " + name_case,
            "allowed_mentions": {"parse": []},
            "embeds": [embed],
        }
        try:
            post_and_delete(payload)
            print(name_case + ": OK (posted + deleted)")
        except Exception as exc:
            print(name_case + ": FAIL -> " + str(exc))
            return 1

    print("ALL CASES OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
