#!/usr/bin/env python3
"""Detect new Habbo furni from the official furnidata XML and notify Discord.

The script is intentionally dependency-free so it can run directly on GitHub's
hosted Actions runners. State is kept in JSON and committed by the workflow.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_URL = "https://www.habbo.es/gamedata/furnidata_xml/1"
DEFAULT_STATE = Path("state/known_furni.json")
USER_AGENT = "habbo-furni-radar/1.0 (+https://github.com/xlfr4n/habbo-furni-radar)"


def clean_text(value: str | None) -> str:
    return " ".join((value or "").split())


def child_text(element: ET.Element, name: str) -> str:
    child = element.find(name)
    return clean_text(child.text if child is not None else "")


def is_nft(item: dict[str, Any]) -> bool:
    classname = item["classname"].lower()
    furniline = item.get("furniline", "").lower()
    return (
        classname.startswith("nft_")
        or classname.startswith("clothing_nft")
        or classname.startswith("pet_nft")
        or "nft" in furniline
    )


def parse_furnidata(raw: str) -> list[dict[str, Any]]:
    """Parse Habbo's furnidata XML into stable, JSON-friendly records."""
    root = ET.fromstring(raw)
    items: list[dict[str, Any]] = []

    for node in root.iter("furnitype"):
        furni_id = node.attrib.get("id", "").strip()
        classname = node.attrib.get("classname", "").strip()
        if not furni_id or not classname:
            continue

        item: dict[str, Any] = {
            "id": furni_id,
            "classname": classname,
            "revision": child_text(node, "revision"),
            "category": child_text(node, "category"),
            "name": child_text(node, "name"),
            "description": child_text(node, "description"),
            "offerid": child_text(node, "offerid"),
            "specialtype": child_text(node, "specialtype"),
            "furniline": child_text(node, "furniline"),
        }
        item["is_nft"] = is_nft(item)
        items.append(item)

    items.sort(key=lambda x: (x["classname"].lower(), x["id"]))
    return items


def item_key(item: dict[str, Any]) -> str:
    return f"{item['id']}|{item['classname']}"


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": 1, "known": {}, "source_sha256": ""}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"No se pudo leer el estado {path}: {exc}") from exc

    if not isinstance(data, dict) or not isinstance(data.get("known", {}), dict):
        raise RuntimeError(
            f"Estado inválido en {path}; se esperaba un objeto JSON con `known`."
        )
    return data


def save_state(
    path: Path,
    source_url: str,
    source_sha256: str,
    items: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    known = {item_key(item): item for item in items}
    data = {
        "schema_version": 1,
        "source_url": source_url,
        "source_sha256": source_sha256,
        "last_successful_check": now,
        "known": known,
    }
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def fetch_furnidata(url: str) -> tuple[str, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/xml,text/xml;q=0.9,*/*;q=0.1",
            "Cache-Control": "no-cache",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
    except urllib.error.URLError as exc:
        raise RuntimeError(f"No se pudo descargar furnidata: {exc}") from exc

    raw = body.decode(charset, errors="replace")
    digest = hashlib.sha256(body).hexdigest()
    if not raw.strip():
        raise RuntimeError("Habbo devolvió furnidata vacío.")
    return raw, digest


def send_discord(webhook_url: str, new_items: list[dict[str, Any]]) -> None:
    """Send new items in batches of up to 10 embeds, retrying rate limits."""
    for start in range(0, len(new_items), 10):
        batch = new_items[start : start + 10]
        embeds = []

        for item in batch:
            nft_tag = "💎 NFT / Collectible" if item["is_nft"] else "🪑 Furni"
            title = item["name"] or item["classname"]
            fields = [
                {"name": "Tipo", "value": nft_tag, "inline": True},
                {"name": "ID", "value": item["id"], "inline": True},
                {
                    "name": "Revision",
                    "value": item["revision"] or "—",
                    "inline": True,
                },
                {
                    "name": "Classname",
                    "value": f"`{item['classname']}`",
                    "inline": False,
                },
            ]

            if item.get("category"):
                fields.insert(
                    1,
                    {
                        "name": "Categoría",
                        "value": item["category"],
                        "inline": True,
                    },
                )

            if item.get("furniline"):
                fields.append(
                    {
                        "name": "Furniline",
                        "value": f"`{item['furniline']}`",
                        "inline": True,
                    }
                )

            embed = {
                "title": f"🆕 {title}",
                "fields": fields,
                "footer": {
                    "text": "Habbo Furni Radar • Habbo.es Furnidata"
                },
                "timestamp": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
            }

            description = item.get("description")
            if description:
                embed["description"] = description

            embeds.append(embed)

        payload = {
            "username": "Habbo Furni Radar",
            "embeds": embeds,
            "allowed_mentions": {"parse": []},
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            webhook_url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )

        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    if response.status in (200, 204):
                        break
                    raise RuntimeError(
                        f"Discord devolvió HTTP {response.status}."
                    )
            except urllib.error.HTTPError as exc:
                if exc.code == 429 and attempt < 2:
                    retry_after = exc.headers.get("Retry-After", "1")
                    try:
                        delay = min(float(retry_after), 10.0)
                    except ValueError:
                        delay = 1.0
                    time.sleep(max(delay, 0.5))
                    continue
                raise RuntimeError(
                    f"Discord devolvió HTTP {exc.code}."
                ) from exc
            except urllib.error.URLError as exc:
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise RuntimeError(
                    f"No se pudo contactar con Discord: {exc}"
                ) from exc
            else:
                break


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detecta nuevos furnis de Habbo y avisa por Discord."
    )
    parser.add_argument(
        "--url",
        default=os.getenv("HABBO_FURNIDATA_URL", DEFAULT_URL),
    )
    parser.add_argument(
        "--state",
        type=Path,
        default=Path(os.getenv("HABBO_STATE_FILE", DEFAULT_STATE)),
    )
    parser.add_argument(
        "--webhook",
        default=os.getenv("DISCORD_WEBHOOK_URL", ""),
    )
    args = parser.parse_args()

    try:
        state = load_state(args.state)
        raw, digest = fetch_furnidata(args.url)
        items = parse_furnidata(raw)
    except (RuntimeError, ET.ParseError) as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1

    if not items:
        print(
            "::error::No se encontraron furnis en la respuesta de Habbo.",
            file=sys.stderr,
        )
        return 1

    previous_known: dict[str, Any] = state.get("known", {})
    first_run = not previous_known
    current_keys = {item_key(item) for item in items}

    if first_run:
        save_state(args.state, args.url, digest, items)
        nft_count = sum(1 for item in items if item["is_nft"])
        print(
            f"Bootstrap inicial completado: {len(items)} furnis "
            f"({nft_count} detectados como NFT)."
        )
        print(
            "No se envió Discord en el primer ciclo para evitar una avalancha "
            "de mensajes."
        )
        return 0

    if state.get("source_sha256") == digest:
        print(
            f"Sin cambios: furnidata SHA256 {digest[:12]}… "
            f"({len(items)} furnis)."
        )
        return 0

    new_items = [
        item for item in items if item_key(item) not in previous_known
    ]

    if new_items:
        print(
            f"Novedades detectadas: {len(new_items)} "
            f"({sum(1 for item in new_items if item['is_nft'])} NFT)."
        )

        if not args.webhook:
            print(
                "::warning::Hay novedades pero DISCORD_WEBHOOK_URL no está "
                "configurado. Se conserva el estado anterior para reintentar "
                "en la próxima ejecución."
            )
            return 0

        try:
            send_discord(args.webhook, new_items)
        except RuntimeError as exc:
            print(f"::error::{exc}", file=sys.stderr)
            return 1
    else:
        print(
            "Furnidata cambió, pero no se añadieron furnis nuevos según el "
            "identificador estable."
        )

    save_state(args.state, args.url, digest, items)
    print(f"Estado actualizado: {len(current_keys)} furnis conocidos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
