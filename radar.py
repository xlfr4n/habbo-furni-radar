#!/usr/bin/env python3
"""Habbo Collectibles release radar."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

SHOP_ITEMS_URL = "https://collectibles.habbo.com/api/shop/items/?walletAddress="
SHOP_PRICES_URL = "https://collectibles.habbo.com/api/shop/prices/?productCodes="
FURNIDATA_URL = "https://www.habbo.es/gamedata/furnidata_xml/1"
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd,eur"
DEFAULT_STATE = Path("state/known_shop_items.json")
DEFAULT_TIMEZONE = "Europe/Madrid"
USER_AGENT = "habbo-furni-radar/2.0 (+https://github.com/xlfr4n/habbo-furni-radar)"

IMAGE_BASES = {
    "furniture": "https://nft-tokens.habbo.com/collectibles/furni/images/",
    "clothes": "https://nft-tokens.habbo.com/collectibles/clothes/images/",
    "pets": "https://nft-tokens.habbo.com/collectibles/pets/images/",
    "addons": "https://nft-tokens.habbo.com/collectibles/addons/images/",
}


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_timestamp(value: Any) -> datetime | None:
    text = clean_text(value)
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def format_timestamp(value: Any, tz_name: str = DEFAULT_TIMEZONE) -> str:
    dt = parse_timestamp(value)
    if dt is None:
        return "—"
    local = dt.astimezone(ZoneInfo(tz_name))
    utc = dt.astimezone(timezone.utc)
    label = local.tzname() or tz_name
    return f"{local:%d/%m/%Y %H:%M:%S} {label} · UTC {utc:%H:%M:%SZ}"


def _retry_delay(attempt: int, headers: Any | None = None) -> float:
    retry_after = headers.get("Retry-After") if headers is not None else None
    if retry_after:
        try:
            return min(max(float(retry_after), 0.5), 20)
        except (TypeError, ValueError):
            pass
    return min(1.5 * (2 ** attempt), 10.0)


def get_json(url: str, timeout: int = 30) -> tuple[Any, str]:
    for attempt in range(5):
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
                "Cache-Control": "no-cache",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body = response.read()
                charset = response.headers.get_content_charset() or "utf-8"
                raw = body.decode(charset, errors="replace")
                try:
                    return json.loads(raw), hashlib.sha256(body).hexdigest()
                except json.JSONDecodeError as exc:
                    raise RuntimeError(f"JSON inválido de {url}: {exc}") from exc
        except urllib.error.HTTPError as exc:
            if exc.code == 429 or 500 <= exc.code < 600:
                if attempt < 4:
                    time.sleep(_retry_delay(attempt, exc.headers))
                    continue
            raise RuntimeError(f"HTTP {exc.code} al consultar {url}") from exc
        except urllib.error.URLError as exc:
            if attempt < 4:
                time.sleep(_retry_delay(attempt))
                continue
            raise RuntimeError(f"No se pudo descargar {url}: {exc}") from exc
    raise RuntimeError(f"No se pudo descargar {url}.")


def get_text(url: str, timeout: int = 30) -> tuple[str, str]:
    for attempt in range(5):
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/xml,text/xml;q=0.9,*/*;q=0.1",
                "User-Agent": USER_AGENT,
                "Cache-Control": "no-cache",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body = response.read()
                charset = response.headers.get_content_charset() or "utf-8"
                return body.decode(charset, errors="replace"), hashlib.sha256(body).hexdigest()
        except urllib.error.HTTPError as exc:
            if exc.code == 429 or 500 <= exc.code < 600:
                if attempt < 4:
                    time.sleep(_retry_delay(attempt, exc.headers))
                    continue
            raise RuntimeError(f"HTTP {exc.code} al consultar {url}") from exc
        except urllib.error.URLError as exc:
            if attempt < 4:
                time.sleep(_retry_delay(attempt))
                continue
            raise RuntimeError(f"No se pudo descargar {url}: {exc}") from exc
    raise RuntimeError(f"No se pudo descargar {url}.")


def is_non_token_collectible(item: dict[str, Any]) -> bool:
    item_type = clean_text(item.get("itemType")).lower()
    collection = clean_text(item.get("collection")).lower()
    product = clean_text(item.get("productCode")).lower()
    if item_type == "token" or collection == "tokens":
        return False
    return not product.startswith("nft_emerald_")


def is_visible_release(item: dict[str, Any], current: datetime | None = None) -> bool:
    if item.get("hidden") is True or item.get("staging") is True:
        return False
    current = current or now_utc()
    start = parse_timestamp(item.get("startsAtTimestamp")) or parse_timestamp(item.get("visibleAtTimestamp"))
    return start is None or start <= current


def shop_status(item: dict[str, Any], current: datetime | None = None) -> str:
    current = current or now_utc()
    if item.get("hidden") is True:
        return "Oculto"
    if item.get("staging") is True:
        return "Staging"

    start = parse_timestamp(item.get("startsAtTimestamp"))
    end = parse_timestamp(item.get("endsAtTimestamp"))

    if start and current < start:
        return "Próximo"
    if end and current >= end:
        return "Finalizado"

    limit = item.get("mintLimit")
    minted = item.get("minted")
    if isinstance(limit, (int, float)) and limit > 0 and isinstance(minted, (int, float)) and minted >= limit:
        return "Agotado"
    if end and (end - current).total_seconds() <= 24 * 3600:
        return "Últimas 24h"
    return "Activo"


def image_url(item: dict[str, Any]) -> str:
    raw = clean_text(item.get("image_url"))
    if not raw:
        return ""
    if raw.startswith(("https://", "http://")):
        return raw

    collection = clean_text(item.get("collection")).lower()
    base = IMAGE_BASES.get(collection)
    if base:
        return urllib.parse.urljoin(base, raw)

    item_type = clean_text(item.get("itemType")).lower()
    base = {
        "furni": IMAGE_BASES["furniture"],
        "clothing": IMAGE_BASES["clothes"],
        "clothes": IMAGE_BASES["clothes"],
        "pet": IMAGE_BASES["pets"],
        "pets": IMAGE_BASES["pets"],
        "addon": IMAGE_BASES["addons"],
        "addons": IMAGE_BASES["addons"],
    }.get(item_type)
    return urllib.parse.urljoin(base or "https://nft-tokens.habbo.com/collectibles/", raw)


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": 2, "known": {}, "last_successful_check": None, "last_api_sha256": ""}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"No se pudo leer {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("known"), dict):
        raise RuntimeError(f"Estado inválido en {path}.")
    return data


def save_state(path: Path, known: dict[str, Any], api_sha256: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": 2,
        "source_url": SHOP_ITEMS_URL,
        "last_successful_check": now_utc().isoformat().replace("+00:00", "Z"),
        "last_api_sha256": api_sha256,
        "known": known,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch_shop_items() -> tuple[list[dict[str, Any]], str]:
    data, digest = get_json(SHOP_ITEMS_URL)
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise RuntimeError("La API Shop no devolvió 'items'.")
    items = [x for x in data["items"] if isinstance(x, dict)]
    if not items:
        raise RuntimeError("La API Shop devolvió una lista vacía.")
    return items, digest


def parse_furnidata(raw: str) -> dict[str, dict[str, Any]]:
    root = ET.fromstring(raw)
    result: dict[str, dict[str, Any]] = {}
    for node in root.iter("furnitype"):
        classname = clean_text(node.attrib.get("classname"))
        if not classname:
            continue

        def child(name: str) -> str:
            value = node.find(name)
            return clean_text(value.text if value is not None else "")

        result[classname.lower()] = {
            "furni_id": clean_text(node.attrib.get("id")),
            "classname": classname,
            "revision": child("revision"),
            "category": child("category"),
            "furni_name": child("name"),
            "furni_description": child("description"),
            "offerid": child("offerid"),
            "specialtype": child("specialtype"),
            "furniline": child("furniline"),
        }
    return result


def enrich_with_furnidata(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    try:
        raw, digest = get_text(FURNIDATA_URL)
        table = parse_furnidata(raw)
    except (RuntimeError, ET.ParseError) as exc:
        print(f"::warning::Furnidata no disponible: {exc}", file=sys.stderr)
        return [dict(item, furnidata={}) for item in items], ""

    result = []
    for item in items:
        clone = dict(item)
        clone["furnidata"] = table.get(clean_text(item.get("productCode")).lower(), {})
        result.append(clone)
    return result, digest


def chunks(values: list[str], size: int = 50) -> list[list[str]]:
    return [values[i : i + size] for i in range(0, len(values), size)]


def fetch_shop_prices(product_codes: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for batch in chunks(product_codes, 50):
        query = urllib.parse.quote(",".join(batch), safe=",")
        try:
            data, _ = get_json(SHOP_PRICES_URL + query)
        except RuntimeError as exc:
            print(f"::warning::Price API unavailable for this cycle: {exc}", file=sys.stderr)
            continue
        if not isinstance(data, dict) or not isinstance(data.get("prices"), list):
            continue
        for entry in data["prices"]:
            if isinstance(entry, dict) and clean_text(entry.get("product_code")):
                result[clean_text(entry["product_code"])] = entry
    return result


def fetch_eth_prices() -> dict[str, float]:
    try:
        data, _ = get_json(COINGECKO_URL, timeout=15)
    except RuntimeError as exc:
        print(f"::warning::ETH rates unavailable: {exc}", file=sys.stderr)
        return {}
    eth = data.get("ethereum") if isinstance(data, dict) else None
    if not isinstance(eth, dict):
        return {}
    result = {}
    for currency in ("usd", "eur"):
        if isinstance(eth.get(currency), (int, float)):
            result[currency] = float(eth[currency])
    return result


def usd_eur_from_eth(price_eth: Any, rates: dict[str, float]) -> tuple[float | None, float | None]:
    try:
        eth = float(price_eth)
    except (TypeError, ValueError):
        return None, None
    return (
        eth * rates["usd"] if "usd" in rates else None,
        eth * rates["eur"] if "eur" in rates else None,
    )


def item_key(item: dict[str, Any]) -> str:
    return clean_text(item.get("productCode"))


def release_source(item: dict[str, Any]) -> str:
    for key in ("startsAtTimestamp", "visibleAtTimestamp", "createdAt"):
        if clean_text(item.get(key)):
            return key
    return ""


def short(value: Any, limit: int = 900) -> str:
    value = str(value or "").strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1] + "…"


def add_field(fields: list[dict[str, Any]], name: str, value: Any, inline: bool = True) -> None:
    value = short(value, 1024)
    if value and value != "—":
        fields.append({"name": name, "value": value, "inline": inline})


def build_embed(item: dict[str, Any], market: dict[str, Any] | None, eth_rates: dict[str, float], detected_at: str) -> dict[str, Any]:
    name = clean_text(item.get("name")) or item_key(item) or "Collectible"
    product_code = item_key(item)
    furnidata = item.get("furnidata") or {}
    launch_key = release_source(item)

    chronology = [
        "🚀 **Lanzamiento:** " + format_timestamp(item.get(launch_key)),
        "👁️ **Visible en tienda:** " + format_timestamp(item.get("visibleAtTimestamp")),
        "📦 **Creado en catálogo:** " + format_timestamp(item.get("createdAt")),
        "🔄 **Última actualización:** " + format_timestamp(item.get("updatedAt")),
        "🏁 **Fin de venta:** " + format_timestamp(item.get("endsAtTimestamp")),
        "💸 **Último registro de venta:** " + format_timestamp(item.get("soldTimestamp")),
    ]

    description_parts = [
        "✨ **Nuevo Collectible detectado**",
        "",
        "### 🕒 Cronología exacta",
        *chronology,
    ]

    api_description = clean_text(furnidata.get("furni_description"))
    if api_description:
        description_parts.extend([
            "",
            "### 📝 Descripción",
            api_description,
        ])

    identifiers = [
        "🔑 " + product_code,
        "🧩 Blueprint: " + (clean_text(item.get("blueprint")) or "—"),
    ]
    if furnidata.get("classname"):
        identifiers.append("🏷️ Classname: " + clean_text(furnidata.get("classname")))
    if furnidata.get("furni_id"):
        identifiers.append("🪑 Furni ID: " + clean_text(furnidata.get("furni_id")))

    description_parts.extend([
        "",
        "### 🔎 Identificación",
        "\n".join(identifiers),
    ])

    if market and market.get("link"):
        market_link = str(market.get("link")).strip()
        description_parts.extend([
            "",
            "### 🔗 Mercado",
            market_link,
        ])

    description = short("\n".join(description_parts), 1900)

    fields: list[dict[str, Any]] = []
    field_values = [
        ("🎨 Tipo", item.get("itemType") or item.get("collection")),
        ("💎 Rareza", item.get("rarity")),
        ("🗂️ Colección", item.get("collection")),
        ("📊 Score", item.get("score")),
        ("💰 Emisión", f"{item.get('mintCost')} Emeralds" if item.get("mintCost") is not None else None),
        ("🪙 Acuñados", item.get("minted")),
        ("♾️ Límite", item.get("mintLimit") if item.get("mintLimit") is not None else "∞"),
        ("📍 Estado", shop_status(item)),
    ]

    if market:
        price = market.get("price")
        usd, eur = usd_eur_from_eth(price, eth_rates)
        if price not in (None, ""):
            field_values.append(("📈 Mercado", f"{price} ETH"))
        if usd is not None:
            field_values.append(("💵 ≈ USD", "$" + format(usd, ",.2f")))
        if eur is not None:
            field_values.append(("💶 ≈ EUR", "€" + format(eur, ",.2f")))

    for label, value in field_values:
        add_field(fields, label, value, inline=True)

    extra = [
        ("🧵 Subtipo", item.get("itemSubType")),
        ("🛠️ Product type", item.get("productType")),
        ("🧱 Material", item.get("material")),
        ("🎯 Set", item.get("set") or item.get("setId")),
        ("🔢 Revision", furnidata.get("revision")),
        ("📋 Furniline", furnidata.get("furniline")),
        ("🎁 Offer ID", furnidata.get("offerid")),
        ("💱 FX consultado", format_timestamp(detected_at)),
    ]
    for label, value in extra:
        add_field(fields, label, value, inline=True)

    embed: dict[str, Any] = {
        "title": "🆕✨ " + name,
        "url": "https://collectibles.habbo.com/shop/?tab=shop",
        "description": description,
        "fields": fields[:18],
        "color": 0x7C3AED,
        "footer": {
            "text": "📡 Habbo Furni Radar • detección " + format_timestamp(detected_at),
        },
        "timestamp": detected_at,
    }

    image = image_url(item)
    if image:
        embed["image"] = {"url": image}

    return embed


def post_json(url: str, payload: dict[str, Any], timeout: int = 20) -> None:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status in (200, 204):
                    return
                raise RuntimeError(f"Discord HTTP {response.status}")
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < 2:
                retry = exc.headers.get("Retry-After", "1")
                try:
                    delay = min(float(retry), 10)
                except ValueError:
                    delay = 1
                time.sleep(max(0.5, delay))
                continue

            try:
                detail = exc.read().decode("utf-8", errors="replace")
            except Exception:
                detail = ""
            detail = short(detail, 500)
            suffix = f" Detalle: {detail}" if detail else ""
            raise RuntimeError(f"Discord devolvió HTTP {exc.code}.{suffix}") from exc
        except urllib.error.URLError as exc:
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise RuntimeError(f"No se pudo contactar con Discord: {exc}") from exc


def send_discord(webhook_url: str, items: list[dict[str, Any]], markets: dict[str, dict[str, Any]], eth_rates: dict[str, float], detected_at: str) -> None:
    if not webhook_url:
        raise RuntimeError("DISCORD_WEBHOOK_URL no está configurado.")

    for item in items:
        embed = build_embed(item, markets.get(item_key(item)), eth_rates, detected_at)
        post_json(
            webhook_url,
            {
                "username": "Habbo Furni Radar",
                "content": f"🆕 **Nuevo Collectible** · {format_timestamp(detected_at)}",
                "embeds": [embed],
                "allowed_mentions": {"parse": []},
            },
        )


def filter_shop_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item for item in items if is_non_token_collectible(item) and item_key(item)]


def bootstrap_state(items: list[dict[str, Any]], path: Path, digest: str) -> None:
    known = {
        item_key(item): {
            "name": item.get("name", ""),
            "release": item.get("startsAtTimestamp") or item.get("visibleAtTimestamp") or item.get("createdAt"),
        }
        for item in items
    }
    save_state(path, known, digest)
    print(f"Bootstrap completado: {len(known)} Collectibles conocidos. No se envían avisos históricos.")


def run(state_path: Path, webhook_url: str, dry_run: bool = False) -> int:
    items, digest = fetch_shop_items()
    current = filter_shop_items(items)
    current_by_key = {item_key(item): item for item in current}
    state = load_state(state_path)
    known = state.get("known", {})

    if not known:
        bootstrap_state(current, state_path, digest)
        return 0

    current_time = now_utc()
    new_items = [
        item
        for key, item in current_by_key.items()
        if key not in known and is_visible_release(item, current_time)
    ]
    new_items.sort(
        key=lambda item: (
            parse_timestamp(item.get("startsAtTimestamp"))
            or parse_timestamp(item.get("visibleAtTimestamp"))
            or parse_timestamp(item.get("createdAt"))
            or datetime.min.replace(tzinfo=timezone.utc)
        )
    )

    if not new_items:
        print(f"Sin novedades: {len(current_by_key)} Collectibles monitorizados.")
        return 0

    enriched, _ = enrich_with_furnidata(new_items)
    markets = fetch_shop_prices([item_key(item) for item in enriched])
    eth_rates = fetch_eth_prices()
    detected_at = current_time.isoformat().replace("+00:00", "Z")

    if dry_run:
        for item in enriched:
            print(
                f"{item.get('name')} | {item.get('productCode')} | "
                f"release={item.get('startsAtTimestamp')} | "
                f"visible={item.get('visibleAtTimestamp')} | minted={item.get('minted')}"
            )
    else:
        send_discord(webhook_url, enriched, markets, eth_rates, detected_at)

    for item in enriched:
        key = item_key(item)
        known[key] = {
            "name": item.get("name", ""),
            "release": item.get("startsAtTimestamp") or item.get("visibleAtTimestamp") or item.get("createdAt"),
            "first_seen_at": detected_at,
        }

    save_state(state_path, known, digest)
    print(f"Procesados {len(enriched)} nuevos Collectibles. Precios={len(markets)}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Radar de nuevos Habbo Collectibles.")
    parser.add_argument("--state", type=Path, default=Path(os.getenv("HABBO_STATE_FILE", str(DEFAULT_STATE))))
    parser.add_argument("--webhook", default=os.getenv("DISCORD_WEBHOOK_URL", ""))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        return run(args.state, args.webhook, dry_run=args.dry_run)
    except (RuntimeError, ET.ParseError, KeyError, ValueError) as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
