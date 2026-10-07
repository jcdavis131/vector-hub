# Keys

Never commit raw keys. Set in Vercel env:

- DUMBMODEL_API_KEY — primary scout/dev key
- DUMBMODEL_API_KEYS — JSON array or comma list of allowed keys

dm_scout_* = Scout, dm_admin_* = you, dm_ext_* = read-only partner.

Auth: Bearer <key> header or ?key=<key> query for GET.

Rate: 120/min per key, 60/min per IP sliding window in-memory. 429 when hit.

Scopes: read (default anon ok for free data), write (requires dm_scout_* or dm_admin_* for trading proof / deploy writes), admin (deploy).

All GET free — platform is free for users — profitability via own calibrated edge not user billing.

Generated Scout key stored ~/.scout/dumbmodel_api_key locally, chmod 600.
