#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from radar import fetch_furnidata, parse_furnidata

WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
URL = os.environ.get("HABBO_FURNIDATA_URL", "https://www.habbo.es/gamedata/furnidata_xml/1")


def send(items):
    if not WEBHOOK:
        raise SystemExit("DISCORD_WEBHOOK_URL no está configurado.")

    embeds = []
    for item in items:
        title = item["name"] or item["classname"]
        nft = item["is_nft"]
        fields = [
            {"name": "Tipo", "value": "💎 NFT / Collectible" if nft else "🪑 Furni", "inline": True},
            {"name": "ID", "value": item["id"], "inline": True},
            {"name": "Revision", "value": item["revision"] or "—", "inline": True},
            {"name": "Classname", "value": "\x60" + item["classname"] + "\x60", "inline": False},
        ]
        if item.get("furniline"):
            fields.append({"name": "Furniline", "value": "\x60" + item["furniline"] + "\x60", "inline": True})
        if item.get("category"):
            fields.append({"name": "Categoría", "value": item["category"], "inline": True})

        embed = {
            "title": "🧪 TEST • " + title,
            "fields": fields,
            "footer": {"text": "Habbo Furni Radar • Discord test"},
        }
        if item.get("description"):
            embed["description"] = item["description"]
        embeds.append(embed)

    payload = {
        "username": "Habbo Furni Radar",
        "content": "🧪 **Prueba del radar:** 10 furnis recientes detectados en Habbo.es.",
        "embeds": embeds,
        "allowed_mentions": {"parse": []},
    }
    request = urllib.request.Request(
        WEBHOOK,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "habbo-furni-radar/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        if response.status not in (200, 204):
            raise SystemExit(f"Discord devolvió HTTP {response.status}.")


raw, digest = fetch_furnidata(URL)
items = parse_furnidata(raw)
if len(items) < 10:
    raise SystemExit(f"Solo se encontraron {len(items)} furnis.")

latest = sorted(
    items,
    key=lambda x: (
        int(x["revision"]) if str(x["revision"]).isdigit() else -1,
        x["id"],
    ),
    reverse=True,
)[:10]

print(f"Furnidata SHA256: {digest}")
print("Últimos 10 por revision:")
for item in latest:
    print(f'- {item["revision"]}: {item["id"]} {item["classname"]} | NFT={item["is_nft"]}')

send(latest)
print("Discord: OK")
