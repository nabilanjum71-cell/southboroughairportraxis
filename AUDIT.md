# SEO / AEO / GEO audit — southboroughairporttaxis.co.uk

Audit date: 15 November 2026. Sources: Google Search Console export (last 6 months), the GitHub repo, and the live site.

## 1. Where the site stands (Search Console)

| Metric (6 months) | Value |
|---|---|
| Clicks | 9 |
| Impressions | about 295 |
| Homepage average position | 17.3 |
| Top query: "tunbridge wells to gatwick taxi" | position 66, 16 impressions |
| "gatwick to tunbridge wells taxi" | position 60, 12 impressions |
| "tunbridge wells airport taxi(s)" | position 87–92 |
| "crowborough to folkestone" | position 7, 7 impressions |

What the data says:

- **Long-tail route pages already rank on page 1.** Crowborough to Folkestone, Maidstone to Folkestone and Hawkhurst to Heathrow all sit around positions 6–8. Google trusts the site for low-competition routes.
- **The money keywords are nowhere.** Tunbridge Wells to Gatwick, the Tunbridge Wells airport taxi queries and Sevenoaks/Maidstone to Gatwick are on pages 5–9. Those are competitive and need much stronger pages.
- **Reverse searches are unserved.** People search "gatwick to tunbridge wells taxi" and "folkestone to crowborough", and no page targeted them.
- **Impressions only started growing in mid-October.** The site is new to Google, and authority will take months to build.

## 2. Problems found and fixed

### Critical

| # | Problem | Fix |
|---|---|---|
| 1 | 114 of 120 route pages were near-identical templates. Only the town and airport names changed, which is a classic "doorway page" pattern. This includes the #1 target, Tunbridge Wells to Gatwick. | Every route page is now unique. Each has its own road route, traffic notes, distance, journey time, town pickup details, terminal info, a return-journey section, a pickup planning table, a key-facts table and 12 FAQs. |
| 2 | The homepage was a JavaScript app. Airports, towns, prices, FAQs, blog and footer were injected by JS, and every link was an `onclick` handler that Google can't follow. AI crawlers (ChatGPT, Claude, Perplexity) don't run JS, so they saw an almost empty page. | The homepage is now pre-rendered HTML with real `<a href>` links to every hub and route. The FAQ and its schema are in the HTML. |
| 3 | Blog posts existed only inside JS and had no URLs, so Google could never index them. | 6 real guide pages at `/guides/…`, each with a short answer, sections, Article schema and links to routes. |
| 4 | There were no pages for "[town] airport taxi" or "[airport] taxi from Kent". | Added 12 town hubs (`/airport-taxi/tunbridge-wells/` etc.) and 10 destination hubs (`/taxi-to/gatwick/` etc.), each with a fares table, FAQs and schema. |
| 5 | The brand was split. Route pages, the logo, the footer and the schema said "C Line Cars", while the homepage said "Southborough Airport Taxis". | "Southborough Airport Taxis" is used everywhere, with "C Line Cars" kept as the trading name (`alternateName` in the schema, plus the footer and About page). |

### Accuracy (these matter for AEO/GEO, because AI answers quote you)

- **M25 directions were reversed.** The old pages said "anticlockwise" to Gatwick and Heathrow, but it's clockwise. Fixed on every page.
- **Heathrow terminals.** The homepage said "All 5 terminals". Heathrow has four (2, 3, 4 and 5).
- **Harwich.** The site claimed "DFDS to Denmark". That route ended in 2014, so it was removed.
- **Journey times were the same from every town.** Hawkhurst to Gatwick showed the same time as Southborough to Gatwick. Times are now calculated per route.
- **Southampton and Harwich times were understated by about an hour.** They said 75–95 mins, and it's really about 2 hours. Corrected.
- **Folkestone.** The site implied you could take a taxi onto Le Shuttle, which carries vehicles only. The page now explains this.
- **Stale content.** "Summer 2025" and "2025" headlines were removed, and each page now carries a visible "last reviewed" date.

### Technical and schema

- Removed the self-serving `aggregateRating` (4.9★, 187 reviews) from the schema. Google ignores it for LocalBusiness on your own site and may treat it as spam.
- Added one consistent `LocalBusiness` entity (`#business`) that every page links to. Added TaxiService, FAQPage, BreadcrumbList, Article and WebSite schema, all validated: 566 JSON-LD blocks, all of which parse.
- Removed the placeholder Google Analytics tag (`G-XXXXXXXXXX`) and the missing `og.jpg`.
- Fixed a broken CSS media query that broke the tablet footer layout.
- Content no longer stays invisible if JS fails. The reveal animations now only hide content when JS runs.
- `vercel.json`: forced trailing slashes (`/taxi/x` and `/taxi/x/` used to both return 200), added redirects for old paths, and set cache headers.
- `sitemap.xml` now lists all 153 URLs with `lastmod`. `robots.txt` explicitly welcomes AI search crawlers. Added `llms.txt` as a factual summary for AI assistants.
- Titles are now under 60 characters, with no duplicate titles or descriptions, one H1 per page, and no broken internal links.

### Conversion

- **The booking form was silently failing.** It posted to Netlify Forms, but the site runs on Vercel. It now opens WhatsApp with every field filled in (date, time, passengers, flight, notes). Before, only the name and route got through.

## 3. What only you can do (this decides page 1 for competitive terms)

The website is only half of local SEO. For "tunbridge wells airport taxi" and "tunbridge wells to gatwick taxi", Google weighs these heavily:

1. **Google Business Profile.** This is the single biggest lever. Make sure it exists, is verified, and uses exactly the name "Southborough Airport Taxis" (or tell me to switch the site to whatever name the profile uses). Use the same phone number, category "Airport shuttle service" or "Taxi service", list all 12 towns as service areas, add the website URL, and upload real photos of your cars.
2. **Real Google reviews.** Send every passenger a review link after the trip. Then put the real rating on the site. The "4.9★ / 187 reviews" claim was removed because it couldn't be verified. Also confirm the 6 testimonials kept on the homepage are genuine.
3. **Citations.** List the business with the identical name, phone and town on Yell, Thomson Local, Bing Places, Apple Business Connect, Yelp, FreeIndex and local Tunbridge Wells directories.
4. **Links.** Get a few local links, for example a hotel or wedding venue in Tunbridge Wells, a local blog, or a sponsorship.
5. **Search Console.** Submit `sitemap.xml` again. Use URL Inspection → Request indexing on: the homepage, `/taxi/tunbridge-wells-to-gatwick/`, `/airport-taxi/tunbridge-wells/`, `/taxi-to/gatwick/`, `/airport-taxi/southborough/` and `/taxi/southborough-to-gatwick/`.
6. **Bing Webmaster Tools.** Import the site from Search Console. Bing powers ChatGPT search and Copilot, so this matters for GEO.
7. **Analytics.** Rebuild with your real ID: `GA_ID=G-YOURID node scripts/build.mjs`.
8. **Social image.** Add a photo of your car as `og.jpg` (1200×630) so links look good when shared.

## 4. Pricing anomalies to review (a business decision, not changed)

Fares are worked out as the destination base price plus £2 per km from Southborough. Some results look odd to customers and may cost you bookings:

- East Grinstead to Gatwick is about 10 miles but costs **£116**. Southborough to Gatwick is 25 miles and costs £72.
- Crowborough to Gatwick is about 20 miles and costs **£94**.
- Southampton (about 97 miles) costs **£120**, and Dover (about 60 miles) costs £78. Both are cheap for the distance compared with Gatwick.

If you send the correct fares, they go in `scripts/data.mjs` and every page updates on rebuild.

## 5. Realistic expectations

Nobody can guarantee page 1. Here is what to expect after deploying:

- **2–6 weeks:** Google recrawls. Long-tail routes that already sit at 6–10 should move into the top 5, and the reverse queries should start appearing.
- **2–4 months:** with the Business Profile, reviews and citations in place, "tunbridge wells to gatwick taxi" and "tunbridge wells airport taxi" can realistically reach page 1 or 2. Without them, they will likely stall on page 2–3, however good the pages are.
