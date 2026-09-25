const { chromium } = require("playwright");

const SHOP_URL = "https://collectibles.habbo.com/shop/?tab=shop";
const WEBHOOK = (process.env.DISCORD_WEBHOOK_URL || "").trim();

if (!WEBHOOK) {
  throw new Error("DISCORD_WEBHOOK_URL no está configurado.");
}

function unique(values) {
  return [...new Set(values)];
}

async function sendDiscord(items, observedApis) {
  const embeds = items.map((item) => {
    const fields = [];
    if (item.name) {
      fields.push({ name: "Nombre", value: item.name, inline: false });
    }
    if (item.text && item.text !== item.name) {
      fields.push({ name: "Info tienda", value: item.text.slice(0, 900), inline: false });
    }

    return {
      title: "🛍️ TEST • " + item.name,
      url: item.href || undefined,
      fields,
      image: item.image ? { url: item.image } : undefined,
      footer: { text: "Habbo Furni Radar • Official Collectibles Shop" },
    };
  });

  const apiText = observedApis.length
    ? observedApis.slice(0, 10).map((u) => u.slice(0, 180)).join("\n")
    : "No se observaron requests XHR/fetch.";

  const payload = {
    username: "Habbo Furni Radar",
    content: "🧪 **Prueba:** 10 elementos del orden **Newest** de la tienda oficial de Habbo Collectibles, con imagen.",
    embeds,
    allowed_mentions: { parse: [] },
  };

  const response = await fetch(WEBHOOK, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "user-agent": "habbo-furni-radar/1.0",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Discord devolvió HTTP " + response.status);
  }

  const diagnostics = [
    "🔎 **Endpoints XHR/fetch observados**",
    ...(observedApis.length ? observedApis : ["Ninguno observado."]),
  ].join("\n").slice(0, 1900);

  const diagnosticResponse = await fetch(WEBHOOK, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "user-agent": "habbo-furni-radar/1.0",
    },
    body: JSON.stringify({
      username: "Habbo Furni Radar",
      content: diagnostics,
      allowed_mentions: { parse: [] },
    }),
  });

  if (!diagnosticResponse.ok) {
    throw new Error("Discord diagnóstico devolvió HTTP " + diagnosticResponse.status);
  }
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1200 },
  });

  const apis = new Set();

  page.on("response", (response) => {
    const type = response.request().resourceType();
    if (type === "xhr" || type === "fetch") {
      const url = response.url();
      if (!url.startsWith("data:") && !url.includes("google-analytics")) {
        apis.add(url);
      }
    }
  });

  await page.goto(SHOP_URL, {
    waitUntil: "domcontentloaded",
    timeout: 60000,
  });

  await page.waitForTimeout(10000);

  const state = await page.evaluate(() => {
    const images = [...document.querySelectorAll("img")].map((img) => ({
      alt: img.getAttribute("alt") || "",
      src: img.currentSrc || img.src || "",
      width: img.naturalWidth || 0,
      height: img.naturalHeight || 0,
      href: img.closest("a")?.href || "",
    }));

    return {
      title: document.title,
      bodyText: document.body.innerText.slice(0, 16000),
      images,
    };
  });

  console.log("PAGE TITLE:", state.title);
  console.log("\n=== BODY PREVIEW ===\n");
  console.log(state.bodyText.slice(0, 8000));

  const candidates = [];
  for (const img of state.images) {
    const alt = img.alt.trim();
    if (!alt || !img.src || img.width === 0 || img.height === 0) continue;

    const clean = alt.replace(/^Image:\s*/i, "").trim();
    if (!clean) continue;
    if (/^(Token|Habbo|Logo|Connect|Icon|Arrow|Clear|Loading)/i.test(clean)) continue;

    candidates.push({
      name: clean,
      image: img.src,
      href: img.href,
      text: clean,
    });
  }

  const items = [];
  const seen = new Set();

  for (const item of candidates) {
    const key = item.name.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    items.push(item);
    if (items.length >= 10) break;
  }

  console.log("\n=== CANDIDATES ===");
  for (const item of items) {
    console.log(item.name + " -> " + item.image);
  }

  console.log("\n=== XHR/FETCH ENDPOINTS ===");
  for (const url of unique([...apis])) {
    console.log(url);
  }

  if (items.length < 10) {
    await page.screenshot({ path: "official-shop-debug.png", fullPage: true });
    throw new Error("Se encontraron solo " + items.length + " candidatos de imagen/producto.");
  }

  await sendDiscord(items, unique([...apis]));
  await browser.close();
  console.log("\nDiscord: OK");
})().catch(async (error) => {
  console.error(error);
  process.exit(1);
});
