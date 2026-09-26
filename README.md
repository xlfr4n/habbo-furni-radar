# 📡 Habbo Furni Radar

> 🏠 **Detector automático de nuevos Habbo Collectibles → Discord**  
> 🏠 **Automatic new Habbo Collectibles detector → Discord**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Habbo](https://img.shields.io/badge/Habbo-Collectibles-111827?style=for-the-badge)

## 🇪🇸 Español

### 🎯 Qué hace

Habbo Furni Radar consulta la **Shop API pública de Habbo Collectibles** y detecta nuevos `productCode`. Cuando aparece un Collectible nuevo, recopila información disponible y publica un embed individual en Discord.

La detección usa la Shop oficial como fuente de lanzamiento y utiliza furnidata/precios como enriquecimiento.

### 📡 Fuentes

- 🏪 Shop: `collectibles.habbo.com/api/shop/items/`
- 💹 Precios: `collectibles.habbo.com/api/shop/prices/`
- 🪑 Furnidata: `habbo.es/gamedata/furnidata_xml/1`
- 💱 Conversión ETH: CoinGecko

### ✨ Información enriquecida

Cuando las fuentes la proporcionan, el embed puede incluir nombre, rareza, colección, score, coste, supply, timestamps, descripción, datos técnicos, precio ETH/USD/EUR, enlace de mercado e imagen oficial.

### ♻️ Automatización

```text
GitHub Actions
      ↓
cada ~5 min
      ↓
Shop API
      ↓
¿nuevo productCode?
      ↓
Furnidata + precios
      ↓
Discord
      ↓
state/known_shop_items.json
```

- 🧠 Bootstrap inicial sin spam histórico.
- ♻️ Deduplicación por `productCode`.
- 🛡️ Reintentos HTTP/429/5xx.
- ❤️ Heartbeat para reducir riesgo de inactividad de workflows programados.
- 🧪 Workflow de prueba independiente.

### 🔐 Seguridad

❌ No requiere wallet, private key, seed phrase, VPS ni servidor propio.  
🔑 El webhook de Discord debe almacenarse únicamente como **GitHub Actions Secret**.

### 🧪 Desarrollo

```bash
python -m unittest discover -s tests -v
python radar.py --dry-run
```

---

## 🇬🇧 English

### 🎯 What it does

Habbo Furni Radar watches the public **Habbo Collectibles Shop API**, detects new `productCode` values and posts one Discord embed per newly detected Collectible.

The Shop API is treated as the launch source, while furnidata and pricing endpoints enrich the alert.

### 📡 Sources

Shop API, pricing API, Habbo furnidata and CoinGecko ETH conversion data.

### ✨ Enrichment

Depending on source availability, alerts can contain name, rarity, collection, score, cost, supply, exact timestamps, description, technical metadata, ETH/USD/EUR market information, market link and official artwork.

### ♻️ Automation

GitHub Actions performs scheduled polling, persistent deduplication, network retries, optional enrichment and Discord publication.

### 🔐 Security

No wallet, private key, seed phrase, VPS or always-on computer is required. The Discord webhook belongs exclusively in GitHub Actions Secrets.

### 🧪 Development

```bash
python -m unittest discover -s tests -v
python radar.py --dry-run
```

## 📌 Status

🟢 **Automated / Automatizado**  
📡 **Public-source driven / Basado en fuentes públicas**  
🌍 **Documentation / Documentación:** ES + EN

