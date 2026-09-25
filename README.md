# Habbo Furni Radar

Radar ligero para detectar nuevos furnis publicados en el `furnidata` oficial de Habbo.es y enviar avisos a un canal de Discord mediante un webhook.

## Cómo funciona

```
Habbo.es furnidata
        ↓
   radar.py
        ↓
 compara con state/known_furni.json
        ↓
   ¿furni nuevo?
      ↓       ↓
     no       sí
      │        ↓
   nada   Discord Webhook
```

El workflow de GitHub Actions se ejecuta cada 5 minutos y usa solamente runners estándar de un repositorio público. No necesita Vercel, Supabase, VPS ni un PC encendido.

## Configuración de Discord

1. En tu servidor, crea o abre el canal que quieras utilizar, por ejemplo `#new-furni`.
2. Ve a **Editar canal → Integraciones → Webhooks → Nuevo Webhook**.
3. Copia la URL del webhook.
4. En este repositorio entra en **Settings → Secrets and variables → Actions → New repository secret**.
5. Crea el secreto con el nombre exacto:

```text
DISCORD_WEBHOOK_URL
```

No pegues la URL en ningún archivo del repositorio.

## Primer arranque

La primera ejecución hace un **bootstrap silencioso**: registra el catálogo actual y no manda cientos/miles de avisos históricos. Desde la siguiente comprobación, solo avisa de los furnis cuyo identificador `id + classname` no se había visto anteriormente.

Los elementos cuyo `classname` o `furniline` indica NFT se marcan en el aviso como `NFT / Collectible`.

## Ejecutar manualmente

Desde GitHub: **Actions → Habbo Furni Radar → Run workflow**.

También se puede ejecutar localmente con Python 3.12+:

```bash
python -m unittest discover -s tests -v
python radar.py
```

Para usar otro hotel o endpoint:

```bash
HABBO_FURNIDATA_URL="https://www.habbo.com/gamedata/furnidata_xml/1" python radar.py
```

## Importante

Este proyecto detecta primero que un furni aparece en los datos públicos de furnidata de Habbo. Eso no significa necesariamente que el item ya esté a la venta o que ya exista como NFT en blockchain. Esos estados se pueden añadir después como una segunda capa usando los datos de Collectibles/Immutable.
