const url = "https://collectibles.habbo.com/api/shop/items/?walletAddress=";

const response = await fetch(url, {
  headers: {
    "accept": "application/json",
    "user-agent": "habbo-furni-radar/1.0",
    "cache-control": "no-cache",
  },
});

console.log("HTTP:", response.status);
console.log("Content-Type:", response.headers.get("content-type"));
console.log("Cache-Control:", response.headers.get("cache-control"));
console.log("ETag:", response.headers.get("etag"));
console.log("Last-Modified:", response.headers.get("last-modified"));

const body = await response.text();
console.log("BODY_LENGTH:", body.length);
console.log(body.slice(0, 30000));
if (!response.ok) process.exit(1);
