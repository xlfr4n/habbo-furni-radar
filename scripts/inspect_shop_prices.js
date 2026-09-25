const products = [
  "clothing_nftemeraldskin",
  "nft_h26_trippypatch",
  "nft_h26_annivfrosty",
  "nft_h26_brewingkit",
  "clothing_nftwesternvest",
];

const url =
  "https://collectibles.habbo.com/api/shop/prices/?productCodes=" +
  encodeURIComponent(products.join(","));

const response = await fetch(url, {
  headers: {
    accept: "application/json",
    "user-agent": "habbo-furni-radar/1.0",
    "cache-control": "no-cache",
  },
});

console.log("HTTP:", response.status);
console.log("Content-Type:", response.headers.get("content-type"));
const body = await response.text();
console.log("BODY_LENGTH:", body.length);
console.log(body.slice(0, 20000));

if (!response.ok) process.exit(1);
