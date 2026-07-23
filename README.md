# vector-hub

Landing page for [dumbmodel.com](https://dumbmodel.com) — a hub linking four daily vector-guessing games built on multi-task embedding models:

- Hoops — NBA player-seasons (48-d)
- Gridiron — NFL (32-d)
- Pitch — World Cup (24-d)
- Equities — public companies (96-d)

Static HTML/CSS/JS, no build step. The repo is git-connected to the Vercel project `vector-hub` and serves the dumbmodel.com apex; pushes to `main` deploy automatically.

Model details and metrics live in the individual game repos (vector-hoops, vector-gridiron, vector-pitch, vector-equities).
