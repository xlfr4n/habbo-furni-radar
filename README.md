# Habbo Furni Radar

Estado: radar activo en GitHub Actions.
Prueba de validación Discord incluida.

Radar ligero para detectar nuevos Habbo Collectibles desde la API oficial de la tienda y enviar avisos enriquecidos a un canal de Discord mediante webhook.

## Fuente principal

La fuente de lanzamiento es la API pública que utiliza la propia tienda:

https://collectibles.habbo.com/api/shop/items/?walletAddress=

El radar no utiliza la revision de furnidata para decidir qué es un lanzamiento nuevo. Eso sería incorrecto porque Habbo puede cargar assets futuros antes de ponerlos a la venta.

La novedad real se determina por productCode dentro de la tienda oficial y solo se avisan elementos visibles que ya han llegado a startsAtTimestamp o, cuando falta, a visibleAtTimestamp.

## Datos del aviso

Cada Collectible nuevo se envía como un embed con imagen oficial y toda la información disponible en las fuentes consultadas.

Incluye, cuando existe:

- nombre
- tipo
- rareza
- colección
- set
- subtipo
- product type
- material
- score
- precio de emisión en Emeralds
- cantidad acuñada
- límite de acuñación
- estado actual de la venta
- fecha y hora exactas de lanzamiento
- fecha y hora exactas de visibilidad
- fecha y hora exactas de creación
- fecha y hora exactas de actualización de la API
- fecha y hora exactas del último registro soldTimestamp
- productCode
- blueprint
- ID de furni
- revision
- classname
- furniline
- categoría
- offer ID
- precio de mercado retornado por la API oficial de precios
- equivalencia aproximada USD/EUR usando la cotización de ETH consultada en ese mismo ciclo
- enlace de mercado cuando la API lo proporciona
- imagen oficial del Collectible

Todas las horas de los timestamps de Habbo se muestran en Europe/Madrid y también conservan la referencia UTC.

## Enriquecimiento

Para cada novedad, el radar consulta además:

### Furnidata de Habbo

https://www.habbo.es/gamedata/furnidata_xml/1

Se utiliza solo como enriquecimiento por classname/productCode, para obtener datos adicionales como ID, revision, descripción, offer ID y furniline.

### Precios de la tienda

https://collectibles.habbo.com/api/shop/prices/?productCodes=...

La API devuelve el precio de referencia en ETH y un enlace de mercado. El radar lo muestra tal cual y calcula también una equivalencia USD/EUR cuando dispone de las cotizaciones de ETH.

### Imagen

Las rutas relativas de image_url se resuelven usando los assets oficiales de Habbo en nft-tokens.habbo.com.

## Discord

Crea un webhook en el canal donde quieras las alertas, por ejemplo #new-furni.

Después, en GitHub:

Settings → Secrets and variables → Actions → New repository secret

Nombre:

DISCORD_WEBHOOK_URL

El webhook nunca debe aparecer en el código ni en commits.

## Ejecución automática

.github/workflows/radar.yml ejecuta el radar cada 5 minutos mediante GitHub Actions.

Los runners estándar hospedados por GitHub son gratuitos e ilimitados para repositorios públicos. GitHub permite intervalos mínimos de 5 minutos para workflows programados.

El primer ciclo hace bootstrap silencioso: registra todo el catálogo actual y no manda avisos históricos. Desde la siguiente ejecución solo se envían nuevos productCode.

## Prueba

Actions → Test Latest Collectibles → Run workflow

La prueba manda los 10 lanzamientos actuales más recientes, ordenados de más antiguo → más reciente, con imagen, timestamps, metadatos y precios disponibles.

La prueba no modifica state/known_shop_items.json.

## Estado

state/known_shop_items.json es la única memoria persistente necesaria. Solo guarda una entrada mínima por productCode ya procesado.

No se utiliza Supabase, Vercel, una VPS ni un ordenador local encendido.

## Arquitectura

API oficial Shop
→ detección de productCode
→ enriquecimiento furnidata
→ precios + ETH/USD/EUR
→ Discord webhook

El proyecto también conserva el concepto de furnidata como fuente secundaria para investigación de assets anticipados, pero esos descubrimientos no contaminan el canal de lanzamientos reales.

## Licencia

MIT.
