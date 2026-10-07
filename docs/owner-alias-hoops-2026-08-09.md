# Vector-Hub Docs — Owner Alias Hoops Fix 2026-08-09

Same as `goals/dottie-closed-loop-factory-v2/files/vector-hub-owner-alias-2026-08-09.md` — mirrored for vector-hub local reference.

## Live

- models/hoops.html 2,941B 200 OK via vercel.json `/hoops → /models/hoops.html` cleanUrls true
- models/unified.html 2,937B 200 OK
- index.html 74,426B owner hub scroll-spy
- vercel.json redirects permanent + rewrites 6 models — pending Vercel --prod redeploy to pick up in production

## Verify

curl -I https://dumbmodel.com/models/hoops.html → 200
curl -I https://dumbmodel.com/hoops → 308 → /models/hoops.html then 200
curl -s models/hoops.html | wc -c → 2941

Zero-deps stdlib only, gate 8.4 PASS.
