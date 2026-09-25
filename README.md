# 🏠 Habbo Furni Radar

> 📡 **Detector automático de nuevos Habbo Collectibles → Discord**
>
> 🕐 Consulta la tienda oficial cada 5 minutos · 🖼️ imagen oficial · 🧾 metadatos exactos · 🕒 timestamps exactos · 💰 mercado cuando existe.

![Habbo Furni Radar](https://img.shields.io/badge/Habbo-Furni%20Radar-ff5f57?style=for-the-badge)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automatic-2ea44f?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge)

## ✨ Qué hace

Habbo Furni Radar vigila la **API pública que utiliza la tienda oficial de Habbo Collectibles** y publica automáticamente en Discord cada nuevo Collectible que aparece.

No necesita servidor propio, VPS, Supabase, Vercel ni un ordenador encendido.

El primer arranque realiza un **bootstrap silencioso**: registra el catálogo existente y no manda cientos de avisos históricos. A partir de ese momento solo se notifican novedades.

## 📡 Fuente de verdad

🏪 **Shop oficial:**

https://collectibles.habbo.com/api/shop/items/?walletAddress=

La detección de novedades utiliza `productCode` en la Shop oficial.

Esto separa:

🏪 **lanzamientos reales de la tienda**
🧩 **assets preparados con antelación en furnidata**

### 🧠 Por qué

`furnidata` puede contener assets antes de que el objeto esté realmente publicado en la tienda. Por eso:

**Shop API = detector del lanzamiento**  
**Furnidata = enriquecimiento de información**

## 🎨 Alertas de Discord

Cada Collectible se envía como **un mensaje individual** para que el canal sea limpio y fácil de leer.

El embed incluye, cuando las fuentes lo proporcionan:

✨ nombre
🎨 tipo
💎 rareza
🗂️ colección y set
🧵 subtipo
🛠️ product type
📊 score
💰 coste de emisión en Emeralds
🪙 cantidad acuñada
♾️ límite de acuñación
📍 estado
🚀 fecha y hora exactas de lanzamiento
👁️ fecha y hora exactas de visibilidad
📦 fecha y hora exactas de creación
🔄 fecha y hora exactas de actualización
🏁 fecha y hora exactas de fin
💸 fecha y hora exactas del último registro de venta
📝 descripción disponible en furnidata
🔑 productCode
🧩 blueprint
🪑 Furni ID
🔢 revision
🏷️ classname
📋 furniline
🎁 Offer ID
📈 precio de mercado en ETH
💵 equivalencia aproximada en USD
💶 equivalencia aproximada en EUR
🔗 enlace de mercado
🖼️ imagen oficial

El color del embed cambia según la rareza cuando existe información de rareza:

⚪ Common · 🟢 Uncommon · 🔵 Rare · 🟣 Epic · 🟡 Legendary

## 🕒 Fechas y horas

Las fechas se muestran en **Europe/Madrid** y también conservan la referencia UTC.

Ejemplo:

`🚀 Lanzamiento: 25/09/2026 10:23:00 CEST · UTC 08:23:00Z`

No se redondean las horas originales recibidas de Habbo.

## 📝 Furnidata

Fuente secundaria:

https://www.habbo.es/gamedata/furnidata_xml/1

Se utiliza para enriquecer los avisos con:

🔢 Furni ID
🔄 revision
🏷️ classname
📋 furniline
🎁 Offer ID
🗂️ categoría
📝 descripción

Si furnidata no está disponible en un ciclo, el radar no se detiene: envía la alerta con los datos disponibles de la Shop.

## 💹 Mercado y precios

Fuente:

https://collectibles.habbo.com/api/shop/prices/?productCodes=...

Cuando existe información, el radar muestra:

📈 precio en ETH
💵 aproximadamente USD
💶 aproximadamente EUR
🔗 enlace de mercado

La conversión utiliza la cotización de ETH consultada durante ese ciclo.

Un HTTP 429 o una caída temporal del endpoint de precios **no bloquea la alerta**.

## 🚀 Instalarlo en tu propio Discord

### 1️⃣ Crea el canal

Crea un canal como `#new-furni` en el servidor donde quieras recibir las alertas.

### 2️⃣ Crea un Webhook

En Discord:

**Servidor → Ajustes del servidor → Integraciones → Webhooks → Nuevo webhook**

Selecciona el canal y copia la URL del webhook.

🔐 **No compartas esa URL.** Un webhook permite publicar mensajes en el canal.

### 3️⃣ Crea tu copia del proyecto

La opción sencilla es hacer **Fork** de este repositorio.

También puedes crear una copia propia basada en estos archivos.

### 4️⃣ Guarda el webhook como Secret

En GitHub:

**Settings → Secrets and variables → Actions → New repository secret**

Nombre exacto:

`DISCORD_WEBHOOK_URL`

Valor:

**la URL privada de tu webhook de Discord**

Nunca lo pongas en código, README, issues o commits.

### 5️⃣ Activa GitHub Actions

Ve a:

**Actions → Habbo Furni Radar**

GitHub debe permitir que el workflow se ejecute.

En un fork de un repositorio público, los workflows programados pueden quedar desactivados inicialmente y deben habilitarse desde Actions.

Más información:

https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows

### 6️⃣ Primera ejecución

Pulsa:

**Actions → Habbo Furni Radar → Run workflow**

La primera ejecución hace el bootstrap silencioso y registra el catálogo actual.

### 7️⃣ ✅ Listo

Después de esa primera ejecución no necesitas lanzar el radar manualmente.

Queda funcionando automáticamente con GitHub Actions.

## ♾️ Automatización continua

La arquitectura es:

~~~text
GitHub Actions
      ↓
cada 5 minutos
      ↓
API oficial Habbo Shop
      ↓
¿nuevo productCode?
      ↓
¿ya está visible?
      ↓
Furnidata + precios
      ↓
Embed Discord
      ↓
state/known_shop_items.json
~~~

El workflow utiliza una franja de 5 minutos desplazada del minuto 00 para reducir el riesgo de retrasos durante picos de carga de GitHub.

GitHub documenta que el intervalo mínimo de un workflow programado es de 5 minutos y permite zonas horarias IANA como `Europe/Madrid`:

https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

## ❤️ Protección frente a la inactividad

GitHub puede desactivar workflows programados de repositorios públicos cuando no ha habido actividad del repositorio durante 60 días.

https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows

Para reducir este riesgo, el proyecto incluye `/.github/workflows/heartbeat.yml`.

El heartbeat realiza periódicamente una pequeña actualización automática del repositorio.

Además, el workflow de producción dispone de un mecanismo keepalive para reactivar la programación cuando sea necesario.

Así no dependemos de que tengas que entrar periódicamente al proyecto para mantenerlo activo.

## 💾 Deduplicación y estado

La memoria persistente está en:

`state/known_shop_items.json`

La clave de deduplicación es `productCode`.

Si el mismo Collectible aparece en 100 comprobaciones consecutivas:

**se notifica una sola vez.**

El radar tampoco genera un commit cada 5 minutos. El estado solo cambia cuando aparece un Collectible nuevo o durante el bootstrap inicial.

Esto evita llenar el historial de Git con commits innecesarios.

## 🛡️ Robustez

✅ reintentos de red
✅ reintentos ante HTTP 429
✅ reintentos ante HTTP 5xx
✅ respeto de `Retry-After` cuando existe
✅ timeout del workflow
✅ deduplicación por `productCode`
✅ bootstrap silencioso
✅ exclusión de tokens Emerald
✅ precios como enriquecimiento opcional
✅ imágenes oficiales
✅ cronología exacta
✅ límites seguros para Discord
✅ separación de mensajes para evitar ráfagas excesivas
✅ tests automatizados
✅ heartbeat anti-inactividad
✅ keepalive

Discord documenta límites para embeds y webhooks, incluyendo descripción de 2.048 caracteres, hasta 25 fields, 6.000 caracteres por embed y límite de mensajes por webhook:

https://discord.com/safety/using-webhooks-and-embeds

## 🧪 Prueba manual

Existe un workflow separado:

**Actions → Test Latest Collectibles → Run workflow**

Envía los **10 Collectibles actualmente visibles más recientes**, ordenados:

⏪ más antiguo → más reciente ⏩

La prueba no modifica el estado del radar.

## 🧩 Estructura

~~~text
habbo-furni-radar/
├── .github/
│   └── workflows/
│       ├── radar.yml
│       ├── heartbeat.yml
│       └── test-discord.yml
├── scripts/
│   └── test_latest.py
├── state/
│   └── known_shop_items.json
├── tests/
│   └── test_radar.py
├── radar.py
├── README.md
└── LICENSE
~~~

### 📡 radar.py

Detector principal, enriquecimiento, imágenes, precios y publicación en Discord.

### ⏰ radar.yml

Workflow automático cada 5 minutos.

### ❤️ heartbeat.yml

Actividad periódica automática para reducir el riesgo de desactivación por inactividad.

### 🧪 test-discord.yml

Prueba manual del formato real en Discord.

### 🔬 test_latest.py

Envía los 10 últimos Collectibles visibles para comprobar el aspecto del canal.

### 💾 known_shop_items.json

Memoria de los `productCode` ya notificados.

## 🔐 Seguridad

El proyecto no requiere:

❌ wallet
❌ private key
❌ seed phrase
❌ Supabase
❌ Vercel
❌ VPS
❌ ordenador encendido

La única credencial utilizada para publicar en Discord es `DISCORD_WEBHOOK_URL` y se almacena en **GitHub Actions Secrets**.

## 🧑‍💻 Desarrollo local

El proyecto usa únicamente la librería estándar de Python 3.12.

No necesita `requirements.txt`.

### Ejecutar tests

~~~bash
python -m unittest discover -s tests -v
~~~

### Probar el radar sin enviar mensajes

~~~bash
python radar.py --dry-run
~~~

### Probar Discord localmente

Linux/macOS:

~~~bash
export DISCORD_WEBHOOK_URL="https://tu-webhook"
python scripts/test_latest.py
~~~

Windows PowerShell:

~~~powershell
$env:DISCORD_WEBHOOK_URL="https://tu-webhook"
python scripts/test_latest.py
~~~

## 🏪 Fuentes

### 🏪 Habbo Collectibles Shop
https://collectibles.habbo.com/api/shop/items/?walletAddress=

### 💹 Habbo Collectibles Prices
https://collectibles.habbo.com/api/shop/prices/?productCodes=

### 🪑 Habbo Furnidata
https://www.habbo.es/gamedata/furnidata_xml/1

### 💱 CoinGecko
https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd,eur

## ✅ Estado actual

✅ detector por Shop API oficial
✅ bootstrap inicial sin spam histórico
✅ 493 Collectibles registrados en el bootstrap inicial
✅ deduplicación activa
✅ Discord probado con mensajes reales
✅ 10/10 mensajes de prueba enviados correctamente
✅ embed validado contra las restricciones de Discord
✅ imagen oficial
✅ timestamps exactos
✅ descripción de furnidata
✅ datos técnicos
✅ precios ETH/USD/EUR cuando están disponibles
✅ tests automatizados
✅ commits de estado solo cuando hay cambios
✅ heartbeat
✅ keepalive
✅ ejecución automática

## ⚠️ Sobre “para siempre”

El proyecto está diseñado para requerir **cero mantenimiento manual en condiciones normales**.

No existe una garantía literal de funcionamiento para siempre cuando intervienen servicios externos: GitHub, Discord, Habbo o sus APIs pueden cambiar sus políticas, endpoints, límites o disponibilidad.

La implementación actual automatiza detección, enriquecimiento, imagen, mercado, Discord, estado, actividad y programación.

## 📚 Documentación oficial

### GitHub Actions
https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

### Discord Webhooks / Embeds
https://discord.com/safety/using-webhooks-and-embeds

## 📜 Licencia

MIT.