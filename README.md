# southboroughairporttaxis.co.uk

Static site, deployed on Vercel. Every page is generated from data by one script.

## Edit and rebuild

1. Change data in `scripts/data.mjs` (towns, destinations, prices, FAQs), guides in `scripts/guides.mjs`, or the homepage body in `src/home-body.html`.
2. Rebuild everything (needs Node 18+):

   ```
   node scripts/build.mjs
   ```

   Optional: `GA_ID=G-XXXXXXX node scripts/build.mjs` adds Google Analytics to every page.
3. Preview locally: `node scripts/serve.mjs` then open http://localhost:4321
4. Commit and push; Vercel deploys the generated files as they are.

Generated output: `index.html`, `taxi/`, `taxi-to/`, `airport-taxi/`, `guides/`, `about/`, `privacy/`, `404.html`, `sitemap.xml`, `robots.txt`, `llms.txt`. Don't edit those by hand — they are overwritten on every build.

Prices: route fare = destination base price (in `DESTS`) + £2 per km from Southborough (`km` in `TOWNS`).
