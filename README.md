# 💎 Habbo Furni Radar

![Habbo Furni Radar](https://img.shields.io/badge/Habbo-Collectibles-7C3AED?style=for-the-badge)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Autom%C3%A1tico-24292f?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge)

**Radar automático de Habbo Collectibles para Discord.**

Detecta nuevos lanzamientos directamente desde la API oficial de la tienda de Habbo, enriquece cada objeto con datos oficiales de furnidata y publica un aviso visual completo en tu canal de Discord.

> 🎯 Objetivo: configurarlo una vez y dejarlo funcionando automáticamente sin mantener un PC, VPS, base de datos ni servicio propio.

---

## ✨ ¿Qué hace?

Cada vez que aparece un Collectible nuevo en la tienda oficial, el radar:

1. 🔎 Consulta la API oficial de Habbo.
2. 🆕 Detecta nuevos productCode.
3. 🛡️ Ignora tokens internos y elementos ocultos/staging.
4. 📚 Enriquece el elemento con furnidata oficial.
5. 💰 Consulta el precio disponible en la API de Shop.
6. 💵 Calcula la equivalencia aproximada en USD/EUR si hay cotización ETH disponible.
7. 🖼️ Añade la imagen oficial.
8. 📅 Muestra las fechas y horas exactas disponibles.
9. 📡 Publica un mensaje por Collectible en Discord.
10. 💾 Guarda el productCode para no volver a avisar del mismo lanzamiento.

---

## 🎨 ¿Cómo queda el aviso?

Cada alerta tiene un embed visual con emojis y secciones separadas.

### 📅 Fechas

- 🟢 Lanzamiento exacto
- 👀 Visible en tienda
- 🧾 Creado en catálogo
- 🔄 Última actualización de la API
- ⏳ Fin de venta
- 💸 Último registro de venta

Las horas se muestran en Europe/Madrid y también incluyen la referencia UTC.

### 📝 Descripción

Cuando furnidata contiene una descripción, se incluye como:

**Descripción oficial / furnidata**

sin inventar ni reinterpretar el texto.

### 🎨 Colección

- 🎨 Tipo
- 💎 Rareza
- 📚 Colección
- 🗂️ Set
- 🧩 Subtipo

### 💰 Economía

- 💰 Precio de emisión en Emeralds
- 🔢 Cantidad acuñada
- 📦 Límite
- 🚦 Estado
- 📈 Precio de mercado en ETH
- 💵 Equivalencia USD
- 💶 Equivalencia EUR

### 🧬 Identidad técnica

- 🏷️ Product code
- 🧭 Blueprint
- 🆔 Furni ID
- 🔬 Revision
- 🧬 Classname
- 🏷️ Furniline

### ⚙️ Datos extra

- Product type
- Material
- Score
- Categoría furnidata
- Offer ID
- Special type
- Enlace de mercado cuando la API lo proporciona

### 📡 Radar

- 🕐 Momento exacto de detección
- 🌐 Fuente oficial de Habbo Collectibles
- 🧩 Fuente secundaria de enriquecimiento

---

# 🚀 INSTALACIÓN EN TU PROPIO DISCORD

La replicación está pensada para ser sencilla.

## 1. 🍴 Haz un Fork

Abre el repositorio y pulsa **Fork**.

Esto crea una copia completamente independiente en tu cuenta de GitHub.

También puedes clonar el repositorio directamente y subirlo a uno nuevo.

---

## 2. 💬 Crea el canal de Discord

En tu servidor crea un canal de texto, por ejemplo:

**#new-furni**

Puedes llamarlo como quieras.

El webhook de Discord publicará directamente en ese canal.

---

## 3. 🔗 Crea el Webhook

En Discord:

**Ajustes del servidor → Integraciones → Webhooks → Crear webhook**

Discord permite crear el webhook, elegir el canal donde publicará y copiar su URL.

Documentación oficial:
https://support.discord.com/hc/es/articles/228383668-Introducci%C3%B3n-a-los-webhooks

Recomendación:

**Nombre:** Habbo Furni Radar

Después pulsa **Copiar URL del webhook**.

⚠️ No publiques esa URL en GitHub, README, capturas ni commits.

---

## 4. 🔐 Guarda el Webhook como secreto

En tu repositorio de GitHub:

**Settings → Secrets and variables → Actions**

Después:

**New repository secret**

Nombre exacto:

DISCORD_WEBHOOK_URL

Valor:

TU_URL_DEL_WEBHOOK

Guarda el secreto.

GitHub Actions lo recibirá automáticamente y el código nunca necesita contener la URL real.

---

## 5. ✅ Comprueba GitHub Actions

Ve a:

**Actions**

Y comprueba que los workflows están habilitados.

El proyecto incluye:

### 💎 Habbo Furni Radar

Es el proceso de producción.

### 🧪 Test Latest Collectibles

Es una prueba manual que manda los 10 Collectibles actuales más recientes a Discord.

---

# 🤖 DESPUÉS DE CONFIGURARLO

No tienes que ejecutar Python localmente.

No necesitas:

- 💻 PC encendido
- 🖥️ servidor local
- ☁️ VPS
- 🗄️ Supabase
- ▲ Vercel
- 🐳 Docker
- 📦 npm
- 🌐 navegador automatizado

GitHub Actions hace todo el trabajo.

El radar se ejecuta automáticamente cada 5 minutos. GitHub permite actualmente un intervalo mínimo de 5 minutos para workflows programados y permite definir una zona horaria IANA como Europe/Madrid.

Documentación oficial:
https://docs.github.com/es/actions/reference/workflows-and-actions/workflow-syntax

---

# 🧠 PRIMERA EJECUCIÓN

La primera vez no se envían cientos de avisos históricos.

El radar hace un **bootstrap silencioso**:

catálogo actual → guardar productCodes → no enviar mensajes

Después:

nuevo productCode → alerta Discord

Esto evita inundar el canal al instalar el proyecto por primera vez.

---

# 🛡️ DUPLICADOS

El radar guarda una memoria pequeña en:

state/known_shop_items.json

La clave es el productCode.

Cuando uno ya está registrado, no vuelve a generar una alerta histórica.

---

# 🌐 FUENTES DE DATOS

## 🥇 Fuente principal: Shop oficial

https://collectibles.habbo.com/api/shop/items/?walletAddress=

Es la fuente que decide si algo es un lanzamiento de tienda.

Esto es importante porque furnidata puede contener assets preparados antes de que salgan a la venta.

Por eso:

**furnidata ≠ detector de lanzamientos**

---

## 🥈 Furnidata oficial

https://www.habbo.es/gamedata/furnidata_xml/1

Se utiliza para enriquecer:

- 🆔 ID
- 🔬 revision
- 🧬 classname
- 🏷️ furniline
- 🗃️ categoría
- 🔖 offer ID
- ⭐ special type
- 📝 descripción

Si furnidata no responde, el radar no inventa datos: simplemente continúa con la información disponible de la Shop API.

---

## 🥉 Precios de Shop

https://collectibles.habbo.com/api/shop/prices/?productCodes=...

Se utilizan cuando están disponibles.

Si esta API devuelve un 429, un error temporal o deja de estar disponible, el radar no deja de funcionar: continúa enviando la alerta sin esa parte opcional del precio.

---

## 💱 Conversión ETH → USD/EUR

Cuando hay precio ETH y cotización disponible, se calcula:

ETH × cotización actual = USD/EUR aproximado

La conversión es informativa y corresponde al momento de la consulta.

---

# 🖼️ IMÁGENES

Las rutas de imagen relativas de la Shop API se resuelven contra los assets oficiales de Habbo/NFT.

Por eso el embed puede mostrar automáticamente la imagen del Collectible sin que tengas que subir imágenes manualmente.

---

# ⚙️ ARQUITECTURA

API oficial Shop

↓

detección de nuevo productCode

↓

furnidata oficial

↓

precio Shop + cotización ETH

↓

embed Discord

↓

state/known_shop_items.json

Todo corre desde GitHub Actions.

---

# ⏱️ FRECUENCIA

Producción:

**cada 5 minutos**

Ejemplo:

- 12:00
- 12:05
- 12:10
- 12:15
- 12:20

GitHub documenta que el intervalo mínimo actual para workflows programados es de 5 minutos y que los workflows programados se ejecutan sobre el commit más reciente de la rama por defecto.

Documentación oficial:
https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

⚠️ schedule depende de la infraestructura de GitHub y puede sufrir retrasos puntuales. No es un reloj en tiempo real con garantía de latencia.

---

# ❤️ AUTOMANTENIMIENTO

El repositorio incorpora un pequeño **heartbeat automático** periódico.

Su función es mantener actividad en el repositorio y reducir el riesgo de que un workflow programado de un repositorio público sea desactivado tras un periodo prolongado sin actividad.

GitHub documenta que los workflows programados de repositorios públicos pueden deshabilitarse automáticamente después de 60 días sin actividad del repositorio.

Documentación oficial:
https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows

El heartbeat no publica nada en Discord.

Solo mantiene un timestamp técnico en:

state/heartbeat.json

---

# 🧪 PRUEBA MANUAL

Si quieres comprobar el Discord cuando quieras:

**Actions → Test Latest Collectibles → Run workflow**

La prueba:

- obtiene los lanzamientos actuales
- excluye los futuros
- toma los 10 más recientes
- utiliza el mismo formato visual de producción
- envía un Collectible por mensaje

No cambia la memoria de producción del radar.

---

# 🧰 ARCHIVOS

radar.py

Motor principal del radar.

.github/workflows/radar.yml

Automatización de producción cada 5 minutos.

.github/workflows/test-discord.yml

Prueba manual del Discord.

.github/workflows/heartbeat.yml

Heartbeat técnico periódico.

scripts/test_latest.py

Generador de la prueba de los 10 últimos Collectibles.

tests/test_radar.py

Pruebas automatizadas.

state/known_shop_items.json

Memoria de lanzamientos ya procesados.

state/heartbeat.json

Marca temporal técnica del heartbeat.

---

# 🧪 PRUEBAS AUTOMÁTICAS

Antes de ejecutar producción, GitHub Actions ejecuta la suite de pruebas.

Actualmente cubre:

- 🧩 parser de furnidata
- 🚫 exclusión de tokens
- 🖼️ resolución de imágenes
- 📅 conversión exacta de timestamps
- 🚦 estados de Shop
- 🛡️ límites estructurales de Discord
- 🔗 URL principal del embed
- 📏 tamaño máximo del embed

La suite debe pasar antes de consultar el Shop en el workflow de producción.

---

# 🔐 SEGURIDAD

Nunca guardes el webhook dentro del código.

El lugar correcto es:

**GitHub Secrets → Actions → DISCORD_WEBHOOK_URL**

Si compartes accidentalmente un webhook, elimínalo desde Discord y genera uno nuevo.

---

# 💸 COSTE

No necesitas contratar infraestructura propia.

GitHub ofrece runners estándar hospedados gratuitamente e ilimitados para repositorios públicos.

Documentación oficial:
https://docs.github.com/en/actions/reference/runners/github-hosted-runners

El radar utiliza:

- GitHub Actions
- Python estándar
- API de Habbo
- Webhook de Discord

No necesita un servidor permanente.

---

# ✅ CONFIGURACIÓN FINAL

Una vez hecho:

**Fork → Webhook → Secret → Actions**

y listo.

A partir de ahí:

🕐 GitHub ejecuta el radar  
🔎 Habbo se consulta automáticamente  
🆕 Los nuevos Collectibles se detectan  
🖼️ La imagen se añade automáticamente  
📅 Las fechas exactas se muestran automáticamente  
💰 Los precios disponibles se añaden automáticamente  
💬 Discord recibe el aviso automáticamente  
💾 El productCode queda registrado para evitar duplicados

---

# ❓ SOLUCIÓN DE PROBLEMAS

### ❌ No llega ningún mensaje

Comprueba:

1. Que DISCORD_WEBHOOK_URL existe en GitHub Secrets.
2. Que el workflow está habilitado.
3. Que el webhook sigue existiendo en Discord.
4. Que el webhook apunta al canal correcto.

Discord permite administrar, crear, editar y eliminar webhooks desde la página de Integraciones del servidor.

Documentación oficial:
https://support.discord.com/hc/es/articles/360045093012-P%C3%A1gina-de-integraciones-del-servidor

### ❌ No aparece el precio

No significa que el radar haya fallado.

El precio es un dato opcional y puede no estar disponible temporalmente.

### ❌ Aparece un asset en furnidata pero no hay alerta

Es correcto.

El radar distingue entre:

**asset preparado**

y

**lanzamiento real en Shop**.

---

# 🏁 ESTADO DEL PROYECTO

**Producción:** ✅  
**Detección automática:** ✅  
**Cada 5 minutos:** ✅  
**Discord webhook:** ✅  
**Imágenes:** ✅  
**Timestamps exactos:** ✅  
**Furnidata:** ✅  
**Precios opcionales:** ✅  
**Prevención de duplicados:** ✅  
**Pruebas automáticas:** ✅  
**Heartbeat:** ✅  
**Sin PC encendido:** ✅  
**Sin VPS:** ✅  
**Sin Supabase:** ✅  
**Sin Vercel:** ✅

> 💜 Diseñado para instalarse una vez y dejarlo funcionando automáticamente.
