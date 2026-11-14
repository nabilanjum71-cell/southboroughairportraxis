#!/usr/bin/env node
// Builds the whole static site: homepage, 120 route pages, 12 town hubs,
// 10 destination hubs, route index, guides, about, privacy, 404, sitemap,
// robots.txt and llms.txt. Every page is plain HTML that works without JS,
// so Google, Bing and AI crawlers (which often do not run JS) see everything.
//
//   node scripts/build.mjs            (optionally GA_ID=G-XXXX node scripts/build.mjs)

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  BASE, BRAND, LEGAL, PHONE_DISPLAY, PHONE_TEL, PHONE_INTL, WA, EMAIL, HQ,
  TOWNS, DESTS, TIME_OVERRIDE, TESTIMONIALS, HOME_FAQS,
} from "./data.mjs";
import { GUIDES } from "./guides.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const TODAY = process.env.BUILD_DATE || new Date().toISOString().slice(0, 10);
const YEAR = TODAY.slice(0, 4);
const GA_ID = process.env.GA_ID || "";
const AP = DESTS.filter((d) => d.type === "ap");
const SP = DESTS.filter((d) => d.type === "sp");
const BIZ_ID = `${BASE}/#business`;

// ---------- helpers ----------
const h = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const ld = (o) => `<script type="application/ld+json">${JSON.stringify(o).replace(/</g, "\\u003c")}</script>`;
const idOf = (t) => t.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const r5 = (n) => Math.round(n / 5) * 5;
const wa = (msg) => `https://wa.me/${WA}?text=${encodeURIComponent(msg)}`;
const hhmm = (m) => { m = ((m % 1440) + 1440) % 1440; return `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`; };
const dur = (m) => (m < 60 ? `${m} mins` : `${Math.floor(m / 60)} hr${m % 60 ? " " + (m % 60) : ""}`);
const range = ([a, b]) => (b <= 90 ? `${a}–${b} mins` : `${dur(a)} – ${dur(b)}`);
const human = (s) => new Date(s + "T12:00:00Z").toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });

function haversineKm(a, b) {
  const R = 6371, toR = (x) => (x * Math.PI) / 180;
  const dLat = toR(b.lat - a.lat), dLng = toR(b.lng - a.lng);
  const x = Math.sin(dLat / 2) ** 2 + Math.cos(toR(a.lat)) * Math.cos(toR(b.lat)) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(x));
}

const ROUTES = {};
function route(t, d) {
  const key = `${t.slug}-to-${d.slug}`;
  if (ROUTES[key]) return ROUTES[key];
  const direct = d.slug === "gatwick" && t.gatwickDirect;
  const km = haversineKm(t, d) * (direct ? 1.25 : d.factor);
  const est = [Math.max(15, r5((km / 85) * 60 + 8)), r5((km / 65) * 60 + 12)];
  const t2 = TIME_OVERRIDE[key] || est;
  const price = Math.round(d.price + t.km * 2);
  return (ROUTES[key] = { key, t, d, url: `/taxi/${key}/`, km, miles: Math.round(km * 0.621), time: range(t2), tmin: t2[0], tmax: t2[1], price, direct });
}
const VEHICLES = [["Saloon", "1–4", 1], ["Estate / MPV", "5–6", 1.2], ["Minibus", "7–8", 1.4], ["Executive saloon", "1–4", 1.5]];

function routeText(r) {
  const { t, d } = r;
  if (r.direct) return `From ${t.name}, your driver normally ${t.gatwickDirect}. This cross-country route avoids the M25 altogether. If the A-roads are blocked, the alternative is to join the M25 and approach Gatwick on the M23.`;
  if (d.group === "m20") return `From ${t.name}, your driver normally ${t.m20}, ${d.approach}.`;
  if (d.group === "acw" || d.group === "city") return `From ${t.name}, your driver normally ${t.dart || t.m25}, ${d.approach}.`;
  let s = `From ${t.name}, your driver normally ${t.m25}, ${d.approach}.`;
  if (d.slug === "gatwick" && t.gatwickAlt) s += ` When the M25 is congested, ${t.gatwickAlt} is the usual alternative.`;
  return s;
}
function trafficText(r) {
  const { d } = r;
  if (r.direct) return "The A22 and A264 are mostly single-carriageway, so roadworks, school traffic and slow vehicles can hold things up, but the distance is short and the route avoids the M25's peak-time queues.";
  const m = {
    gatwick: "The stretch most likely to slow you down is the M25 between Junctions 5 and 7, which can queue at weekday peaks and after incidents, so we build in a buffer for morning departures.",
    heathrow: "The west side of the M25, between the M23 and the Heathrow junctions, is one of the busiest roads in the country, so morning and Friday departures are planned with extra margin.",
    southampton: "The M25 between Junctions 5 and 12 is the main variable, and the M3 can be busy on summer Saturdays when most cruises turn around, so we plan with a generous buffer.",
    luton: "The west and north-west sides of the M25 up to the M1 are the busiest part of the journey, so we plan extra time for weekday morning and Friday departures.",
    city: "The Blackwall Tunnel approach is often congested at peak times; the Silvertown Tunnel, which opened in 2025, gives an alternative. Both tunnels carry a user charge, so ask us how it is handled on your fare.",
    m20: "The M20 is usually free-flowing east of Maidstone, but cross-Channel traffic management (Operation Brock) can be in place at busy times, particularly in summer and around holidays. Your driver checks the latest before setting off.",
    acw: "The Dartford Crossing is the main pinch-point: northbound queues can build quickly at peak times and after incidents, and the crossing has a road-user charge (Dart Charge). Ask us how the charge is handled on your fixed fare.",
  };
  return m[d.slug] || m[d.group];
}

// ---------- shared chrome ----------
const NAV_LINKS = [["/", "Home"], ["/taxi/#airports", "Airports"], ["/taxi/#towns", "Towns"], ["/guides/", "Guides"], ["/about/", "About"]];
const nav = () => `<nav id="nav">
  <a class="logo" href="/" aria-label="${BRAND} home"><div class="lbox" aria-hidden="true">🚖</div>Southborough <span>Airport Taxis</span></a>
  <ul class="nl">${NAV_LINKS.map(([u, n]) => `<li><a href="${u}">${n}</a></li>`).join("")}<li><a href="/#bsec" style="color:var(--R)">Book Now</a></li></ul>
  <div class="nr">
    <button class="tbtn" id="tb" type="button" aria-label="Toggle dark mode">🌙</button>
    <a href="tel:${PHONE_TEL}" class="ncall" data-tr="phone:nav">📞 ${PHONE_DISPLAY}</a>
    <button class="hbg" id="hbtn" type="button" aria-label="Open menu" aria-controls="mm"><span></span><span></span><span></span></button>
  </div>
</nav>
<div class="mm" id="mm">
  ${NAV_LINKS.map(([u, n]) => `<a class="ml" href="${u}">${n}</a>`).join("\n  ")}
  <a class="ml" href="/#bsec" style="color:var(--R)">Book Now →</a>
  <div class="ma">
    <a href="tel:${PHONE_TEL}" class="btn br" data-tr="phone:mob">📞 ${PHONE_DISPLAY}</a>
    <a href="${wa(`Hi ${BRAND}! I need to book a taxi.`)}" target="_blank" rel="noopener" class="btn bw" data-tr="wa:mob">💬 WhatsApp</a>
    <a href="mailto:${EMAIL}" class="btn bo">📧 Email Us</a>
  </div>
</div>`;

const footer = () => `<footer><div class="fgrd">
    <div><div class="flogo">Southborough <span>Airport Taxis</span></div><p style="margin-bottom:.85rem">Fixed-price airport and seaport taxis from Southborough, Tunbridge Wells and West Kent. Licensed, DBS-checked drivers, 24/7.</p>
      <address style="font-style:normal;display:flex;flex-direction:column;gap:.28rem">
        <a href="tel:${PHONE_TEL}" style="color:rgba(255,255,255,.55);font-size:.73rem">📞 ${PHONE_DISPLAY}</a>
        <a href="https://wa.me/${WA}" target="_blank" rel="noopener" style="color:rgba(255,255,255,.55);font-size:.73rem">💬 WhatsApp ${PHONE_INTL}</a>
        <a href="mailto:${EMAIL}" style="color:rgba(255,255,255,.55);font-size:.73rem">📧 ${EMAIL}</a>
        <span style="color:rgba(255,255,255,.45);font-size:.7rem">📍 Southborough, Tunbridge Wells, Kent ${HQ.postcode}</span>
      </address></div>
    <div><h2 class="fh">Airports</h2><ul>${AP.map((d) => `<li><a href="/taxi-to/${d.slug}/">${d.icon} ${h(d.name)} taxi</a></li>`).join("")}</ul>
      <h2 class="fh" style="margin-top:1rem">Seaports</h2><ul>${SP.map((d) => `<li><a href="/taxi-to/${d.slug}/">${d.icon} ${h(d.short)} taxi</a></li>`).join("")}</ul></div>
    <div><h2 class="fh">Towns</h2><ul>${TOWNS.map((t) => `<li><a href="/airport-taxi/${t.slug}/">📍 ${t.name} airport taxi</a></li>`).join("")}</ul></div>
    <div><h2 class="fh">Company</h2><ul><li><a href="/about/">About us</a></li><li><a href="/taxi/">All routes &amp; prices</a></li><li><a href="/guides/">Travel guides</a></li><li><a href="/#bsec">Book online</a></li><li><a href="/privacy/">Privacy policy</a></li></ul></div>
  </div><div class="fbot"><span>© ${YEAR} ${BRAND} (operated by ${LEGAL}) · Licensed private hire operator · Southborough, Kent</span><span>Serving Southborough, Tunbridge Wells, Tonbridge, Sevenoaks &amp; West Kent 24/7</span></div></footer>
<div class="fab">
  <a href="https://wa.me/${WA}" target="_blank" rel="noopener" class="fabtn" style="background:#25d366" aria-label="WhatsApp us" data-tr="wa:fab">💬</a>
  <a href="tel:${PHONE_TEL}" class="fabtn" style="background:var(--R);color:#fff" aria-label="Call us" data-tr="phone:fab">📞</a>
</div>`;

const BIZ = {
  "@type": "LocalBusiness", "@id": BIZ_ID, name: BRAND, alternateName: LEGAL, url: BASE + "/",
  telephone: PHONE_INTL, email: EMAIL, priceRange: "££",
  address: { "@type": "PostalAddress", addressLocality: HQ.locality, addressRegion: HQ.region, postalCode: HQ.postcode, addressCountry: "GB" },
  geo: { "@type": "GeoCoordinates", latitude: HQ.lat, longitude: HQ.lng },
};
const bizRef = { "@type": "LocalBusiness", "@id": BIZ_ID, name: BRAND, telephone: PHONE_INTL, address: BIZ.address };
const crumbs = (items) => ({ "@context": "https://schema.org", "@type": "BreadcrumbList", itemListElement: items.map(([n, u], i) => ({ "@type": "ListItem", position: i + 1, name: n, item: BASE + u })) });
const crumbHtml = (items) => `<nav class="crumb" aria-label="Breadcrumb">${items.map(([n, u], i) => (i < items.length - 1 ? `<a href="${u}">${h(n)}</a>` : `<span aria-current="page">${h(n)}</span>`)).join(" › ")}</nav>`;
const faqLd = (faqs) => ({ "@context": "https://schema.org", "@type": "FAQPage", mainEntity: faqs.map(([q, a]) => ({ "@type": "Question", name: q, acceptedAnswer: { "@type": "Answer", text: a } })) });
const faqHtml = (faqs) => faqs.map(([q, a]) => `<div class="qa"><h3>${h(q)}</h3><p>${h(a)}</p></div>`).join("\n  ");
const H2 = (t, id) => `<h2 class="rh2" id="${id || idOf(t)}">${h(t)}</h2>`;
const P = (t) => `<p class="rp">${h(t)}</p>`;
const updated = () => `<p class="upd">Last reviewed ${human(TODAY)} · Fares and times are checked against our current price list.</p>`;

function page({ url, title, desc, schema = [], body, ogType = "website", extraHead = "" }) {
  const full = BASE + url;
  const ga = GA_ID ? `<script async src="https://www.googletagmanager.com/gtag/js?id=${GA_ID}"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag("js",new Date());gtag("config","${GA_ID}");</script>` : "";
  return `<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${h(title)}</title>
<meta name="description" content="${h(desc)}">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">
<link rel="canonical" href="${full}">
<meta property="og:site_name" content="${BRAND}">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="${h(title)}">
<meta property="og:description" content="${h(desc)}">
<meta property="og:type" content="${ogType}">
<meta property="og:url" content="${full}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="${h(title)}">
<meta name="twitter:description" content="${h(desc)}">
<meta name="geo.region" content="GB-KEN">
<meta name="geo.placename" content="Southborough, Tunbridge Wells">
<meta name="theme-color" content="#c0392b">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<script>document.documentElement.classList.add("js")</script>
${schema.map(ld).join("\n")}
${ga}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
${extraHead}
</head>
<body>
${nav()}
${body}
${footer()}
<script src="/assets/site.js" defer></script>
</body>
</html>
`;
}

const ctaButtons = (msg, where) => `<div class="ctas"><a href="tel:${PHONE_TEL}" class="btn br" data-tr="phone:${where}">📞 Call ${PHONE_DISPLAY}</a>
    <a href="${wa(msg)}" target="_blank" rel="noopener" class="btn bw" data-tr="wa:${where}">💬 WhatsApp Quote</a></div>`;

// ---------- route pages ----------
function routeFaqs(r) {
  const { t, d, price } = r;
  const T = t.name, A = d.short, AF = d.name, ap = d.type === "ap";
  const f = [
    [`How much is a taxi from ${T} to ${AF}?`, `A fixed-price taxi from ${T} to ${AF} costs from £${price} for a saloon carrying one to four passengers. An estate or MPV is about £${Math.round(price * 1.2)}, a minibus about £${Math.round(price * 1.4)} and an executive saloon about £${Math.round(price * 1.5)}. The fare is agreed when you book and does not change with traffic${ap ? " or flight delays" : ""}.`],
    [`How long does a taxi from ${T} to ${A} take?`, `The journey is about ${r.miles} miles by road and normally takes ${r.time}. Allow more time at weekday peaks (roughly 7–9:30am and 4–7pm), on Friday afternoons and at the start of school holidays.`],
    [`Which route do you take from ${T} to ${A}?`, routeText(r) + " Your driver checks live traffic before setting off and can change route if there is an incident."],
  ];
  if (ap) {
    f.push([`What time should I be picked up in ${T} for my flight?`, `Plan to be at ${A} two hours before a short-haul flight or three hours before long-haul. Add the ${r.time} journey and a 30-minute buffer. For a 9am short-haul departure, that means a pickup around ${hhmm(540 - 120 - r.tmax - 30 - ((540 - 120 - r.tmax - 30) % 5))}. We confirm the right pickup time when you book.`]);
    f.push([`Do you charge extra if my flight to or from ${A} is delayed?`, `No. We track your flight and adjust the pickup automatically, so a delay never changes your fixed fare. For arrivals, the first 60 minutes of waiting after landing are free.`]);
    f.push([`Where will my driver meet me at ${AF}?`, `${d.arrivals} Your driver waits with a name board and helps with your luggage to the car.`]);
  } else {
    f.push([`When should I leave ${T} for ${A}?`, `${d.checkin} With a journey of ${r.time} from ${T}, we will suggest a pickup time when you book.`]);
    f.push([`Will the driver help with luggage at ${A}?`, `Yes. Luggage help is included, and your driver takes you to the terminal or address you give us rather than a general drop-off point.`]);
  }
  f.push([`Are there any extra charges on the way to ${A}?`, d.dropoff]);
  f.push([`Can you collect me from home or from ${t.st} in ${T}?`, `Yes. We collect from any address in ${t.postcodes}, or from ${t.st} or a landmark you name when booking. Give us the full postcode so your driver can find rural addresses easily.`]);
  f.push([`Can you take me back from ${A} to ${T}?`, `Yes. We run the same fixed-price service from ${AF} back to any address in ${T}${ap ? ", with flight tracking and meet & greet inside the terminal" : ""}. Book both legs together and we will confirm both fares.`]);
  f.push([`How many passengers and cases fit?`, `A saloon takes up to four passengers with standard luggage, an estate or MPV five or six, and a minibus seven or eight. Tell us how many large cases you have so we send a vehicle with enough room.`]);
  f.push([`Do you run early-morning taxis from ${T}?`, `Yes, we operate 24 hours a day, seven days a week. For pickups before 6am please book at least 48 hours ahead so your driver is confirmed well before the day.`]);
  f.push([`Are your drivers licensed?`, `Yes. All our drivers are licensed by Tunbridge Wells Borough Council, DBS-checked and professionally trained, and we are a licensed private hire operator in Kent.`]);
  return f;
}

function routePage(r) {
  const { t, d, price } = r;
  const T = t.name, A = d.short, AF = d.name, ap = d.type === "ap";
  const title = `${T} to ${A} Taxi | Fixed £${price} | 24/7`;
  const desc = `${T} to ${AF} taxi from £${price}: ${r.time}, ${r.miles} miles. Fixed fare, ${ap ? "flight tracking, no delay fees" : "door to terminal, luggage help"}. 24/7: ${PHONE_DISPLAY}`;
  const faqs = routeFaqs(r);
  const quick = `A taxi from ${T} to ${AF} costs from £${price} for a saloon (1–4 passengers). The fare is fixed when you book, the journey is about ${r.miles} miles and takes ${r.time}, and the price includes door-to-door pickup${ap ? ", flight tracking and meet & greet, with no charge for flight delays" : " and drop-off at the terminal with luggage help"}. Vehicles for up to eight passengers are available. Call ${PHONE_DISPLAY} to book.`;
  const crumbItems = [["Home", "/"], [`${T} airport taxis`, `/airport-taxi/${t.slug}/`], [`${T} to ${A}`, r.url]];
  const vrows = VEHICLES.map(([n, p, m]) => `<tr><td>${n}</td><td>${p}</td><td><strong>£${Math.round(price * m)}</strong></td></tr>`).join("");
  const plan = ap ? [360, 540, 720, 1020].map((dep) => {
    const s = dep - 120 - r.tmax - 30, l = dep - 180 - r.tmax - 30;
    return `<tr><td>${hhmm(dep)}</td><td><strong>${hhmm(s - (((s % 5) + 5) % 5))}</strong></td><td><strong>${hhmm(l - (((l % 5) + 5) % 5))}</strong></td></tr>`;
  }).join("") : "";
  const others = DESTS.filter((x) => x.slug !== d.slug).map((x) => route(t, x));
  const otherTowns = TOWNS.filter((x) => x.slug !== t.slug).map((x) => route(x, d));
  const schema = [
    { "@context": "https://schema.org", "@type": "TaxiService", "@id": BASE + r.url + "#service", name: `${T} to ${AF} taxi`, serviceType: ap ? "Airport transfer" : "Seaport transfer",
      description: `Fixed-price taxi from ${T} to ${AF}, about ${r.miles} miles and ${r.time}.`, url: BASE + r.url, provider: bizRef,
      areaServed: { "@type": "City", name: T, geo: { "@type": "GeoCoordinates", latitude: t.lat, longitude: t.lng } },
      offers: { "@type": "Offer", price: String(price), priceCurrency: "GBP", description: "Saloon, 1–4 passengers, fixed fare", availability: "https://schema.org/InStock" } },
    faqLd(faqs),
    crumbs(crumbItems),
    { "@context": "https://schema.org", "@type": "WebPage", name: title, url: BASE + r.url, dateModified: TODAY, isPartOf: { "@type": "WebSite", url: BASE + "/", name: BRAND },
      speakable: { "@type": "SpeakableSpecification", cssSelector: [".aeobox", ".facts"] } },
  ];
  const body = `<main class="rtwrap">
  ${crumbHtml(crumbItems)}
  <h1 class="rth1">${h(T)} to ${h(AF)} Taxi — Fixed Price from £${price}</h1>
  <div class="pills">
    <span class="pill">📍 ${h(T)}, ${t.county}</span><span class="pill">${d.icon} ${d.code || h(A)}</span>
    <span class="pill">⏱ ${r.time}</span><span class="pill">🛣️ ${r.miles} miles</span><span class="pill">🕐 24/7</span>
  </div>
  <div class="pbox"><div class="plbl">Fixed price from ${h(T)}</div>
    <div class="price">£${price}</div><div class="psub">Saloon · 1–4 passengers · Door to door · ${ap ? "Meet &amp; greet at arrivals" : "Drop-off at the terminal"}</div></div>
  ${ctaButtons(`Hi ${BRAND}! I need a taxi from ${T} to ${AF}.`, "route-top")}
  <div class="aeobox"><div class="lbl">Quick answer</div><p>${h(quick)}</p></div>
  <table class="facts"><caption>${h(T)} to ${h(A)} at a glance</caption><tbody>
    <tr><th scope="row">Fixed fare (saloon)</th><td>From £${price}</td></tr>
    <tr><th scope="row">Distance</th><td>About ${r.miles} miles by road</td></tr>
    <tr><th scope="row">Journey time</th><td>${r.time} in normal traffic</td></tr>
    <tr><th scope="row">Main roads</th><td>${h(r.direct ? "A22, A264, M23" : { cw: "A21/A22, M25 clockwise", acw: "M25 anticlockwise, Dartford Crossing", city: "M25, A2, Blackwall/Silvertown tunnel", m20: "M20 east" }[d.group])}</td></tr>
    <tr><th scope="row">Vehicles</th><td>Saloon, estate/MPV, minibus (up to 8), executive</td></tr>
    <tr><th scope="row">Availability</th><td>24 hours a day, 7 days a week</td></tr>
  </tbody></table>
  <nav class="toc" aria-label="On this page"><strong>On this page:</strong> <a href="#fares">Fares</a> · <a href="#route">Route</a> · <a href="#pickup">Pickup in ${h(T)}</a> · <a href="#arrival">At ${h(A)}</a> · <a href="#return">Return journey</a> · <a href="#faqs">FAQs</a></nav>

  ${H2("Fixed fares by vehicle", "fares")}
  ${P(`Your fare from ${T} to ${AF} is agreed when you book and stays the same whatever the traffic does. It covers door-to-door pickup${ap ? ", flight tracking and a driver who waits for you rather than watching the clock" : " and drop-off at the terminal with help for your luggage"}. Choose the vehicle that fits your group and bags.`)}
  <div class="tw"><table><thead><tr><th>Vehicle</th><th>Passengers</th><th>Fixed fare</th></tr></thead><tbody>${vrows}</tbody></table></div>

  ${H2(`The route from ${T} to ${A}`, "route")}
  ${P(routeText(r))}
  ${P(trafficText(r))}
  ${P(`In normal traffic the ${r.miles}-mile journey from ${T} to ${AF} takes ${r.time}.${ap ? " The planning table below assumes you want to reach the airport two hours before a short-haul flight or three hours before long-haul, uses the upper end of the journey time and adds a 30-minute buffer." : ""}`)}
  ${ap ? `<div class="tw"><table><thead><tr><th>Flight departs</th><th>Pickup (short-haul)</th><th>Pickup (long-haul)</th></tr></thead><tbody>${plan}</tbody></table></div>` : ""}

  ${H2(`Pickup in ${T}`, "pickup")}
  ${P(t.intro)}
  ${P(t.pickup)}

  ${H2(`At ${AF}`, "arrival")}
  ${P(d.terminals)}
  ${P(d.dropoff)}
  ${P(d.checkin)}

  ${H2(`${A} to ${T} taxi`, "return")}
  ${P(ap ? `Flying back into ${AF}? We run the same fixed-price service from ${A} to any address in ${T}. ${d.arrivals} The first 60 minutes of waiting after landing are free, and you can book the return leg at the same time as your outbound journey.` : `Coming home from ${A}? We collect you from ${AF} and drive you back to your door in ${T}. ${d.arrivals} You can book the return leg at the same time as your outbound journey.`)}

  ${H2("How booking works", "booking")}
  <ol class="steps">
    <li><strong>Call or WhatsApp</strong><br><span>Give us your ${h(T)} pickup address, your ${ap ? "flight" : "sailing"} time and the number of passengers.</span></li>
    <li><strong>Get your fixed fare</strong><br><span>We confirm the price for ${h(T)} to ${h(A)} within 30 minutes, and it does not change on the day.</span></li>
    <li><strong>${ap ? "We track your flight" : "We plan around your sailing"}</strong><br><span>${ap ? "Your pickup adjusts automatically if your flight moves, at no extra charge." : "We set the pickup time from your check-in or boarding window, plus a traffic buffer."}</span></li>
    <li><strong>Door to terminal</strong><br><span>Your driver collects you from home and takes you straight to ${h(AF)}.</span></li>
  </ol>
  <div class="ctabox"><div class="ctat">Book ${h(T)} → ${h(A)}</div>
    <div class="ctas2">Fixed price from £${price} · Confirmed within 30 minutes · 24/7</div>
    ${ctaButtons(`Hi ${BRAND}! Please confirm the price for a taxi from ${T} to ${AF}.`, "route-cta")}</div>

  ${H2(`${T} to ${A} taxi: frequently asked questions`, "faqs")}
  ${faqHtml(faqs)}

  ${H2(`More taxis from ${T}`, "more")}
  <ul class="rel">${others.map((o) => `<li><a href="${o.url}">${h(T)} to ${h(o.d.short)} taxi</a> <span class="mut">from £${o.price}</span></li>`).join("")}</ul>
  <p class="rp"><a class="lnk" href="/airport-taxi/${t.slug}/">All ${h(T)} airport &amp; seaport taxis →</a></p>
  ${H2(`Other towns to ${A}`, "towns")}
  <ul class="rel">${otherTowns.map((o) => `<li><a href="${o.url}">${h(o.t.name)} to ${h(A)} taxi</a> <span class="mut">from £${o.price}</span></li>`).join("")}</ul>
  <p class="rp"><a class="lnk" href="/taxi-to/${d.slug}/">${h(AF)} taxis from every town we cover →</a></p>
  ${updated()}
</main>`;
  return page({ url: r.url, title, desc, schema, body });
}

// ---------- town hubs ----------
function townPage(t) {
  const url = `/airport-taxi/${t.slug}/`;
  const rs = DESTS.map((d) => route(t, d));
  const aps = rs.filter((r) => r.d.type === "ap").sort((a, b) => a.km - b.km);
  const g = route(t, DESTS[0]);
  const title = `${t.name} Airport Taxis | Gatwick from £${g.price} | Fixed Prices 24/7`;
  const desc = `${t.name} airport taxis: Gatwick £${g.price}, Heathrow £${route(t, DESTS[1]).price}, plus Stansted, Luton, City & cruise ports. Fixed fares, 24/7: ${PHONE_DISPLAY}`;
  const faqs = [
    [`Which airport is closest to ${t.name}?`, `${aps[0].d.name} is the closest airport to ${t.name}, about ${aps[0].miles} miles and ${aps[0].time} by taxi. ${aps[1].d.name} is next at about ${aps[1].miles} miles (${aps[1].time}).`],
    [`How much is an airport taxi from ${t.name}?`, `Fixed fares from ${t.name} start at £${g.price} to Gatwick, £${route(t, DESTS[1]).price} to Heathrow, £${route(t, DESTS[2]).price} to London City, £${route(t, DESTS[3]).price} to Stansted and £${route(t, DESTS[4]).price} to Luton, for a saloon carrying up to four passengers.`],
    [`Do you pick up from anywhere in ${t.name}?`, t.pickup],
    [`Do you charge for flight delays?`, "No. We track your flight and adjust your pickup automatically, and the first 60 minutes of waiting after landing are free."],
    [`Can I book an airport taxi from ${t.name} at short notice?`, `Often, yes. Call ${PHONE_DISPLAY} and we will tell you what we can arrange. For early-morning pickups, booking at least 48 hours ahead is best.`],
  ];
  const crumbItems = [["Home", "/"], ["Taxi routes", "/taxi/"], [`${t.name} airport taxis`, url]];
  const rows = rs.map((r) => `<tr><td><a href="${r.url}">${h(r.d.name)}</a></td><td>${r.miles} mi</td><td>${r.time}</td><td><strong>£${r.price}</strong></td></tr>`).join("");
  const near = TOWNS.filter((x) => x.slug !== t.slug).sort((a, b) => haversineKm(a, t) - haversineKm(b, t)).slice(0, 5);
  const schema = [
    { "@context": "https://schema.org", "@type": "TaxiService", "@id": BASE + url + "#service", name: `${t.name} airport taxis`, url: BASE + url, provider: bizRef,
      areaServed: { "@type": "City", name: t.name, geo: { "@type": "GeoCoordinates", latitude: t.lat, longitude: t.lng } },
      hasOfferCatalog: { "@type": "OfferCatalog", name: `Fixed fares from ${t.name}`, itemListElement: rs.map((r) => ({ "@type": "Offer", name: `${t.name} to ${r.d.name}`, url: BASE + r.url, price: String(r.price), priceCurrency: "GBP" })) } },
    faqLd(faqs), crumbs(crumbItems),
  ];
  const body = `<main class="rtwrap">
  ${crumbHtml(crumbItems)}
  <h1 class="rth1">${h(t.name)} Airport Taxis — Fixed Prices to Every Airport</h1>
  <div class="pills"><span class="pill">📍 ${h(t.name)}, ${t.county} ${t.postcodes.split(/,| and /)[0]}</span><span class="pill">✈️ 5 London airports</span><span class="pill">⛴️ 5 seaports</span><span class="pill">🕐 24/7</span></div>
  ${ctaButtons(`Hi ${BRAND}! I need an airport taxi from ${t.name}.`, "town-top")}
  <div class="aeobox"><div class="lbl">Quick answer</div><p>${h(`${BRAND} runs fixed-price airport taxis from ${t.name} to all five London airports and the main cruise and ferry ports, 24 hours a day. Fares start at £${g.price} to Gatwick, the closest airport, about ${g.miles} miles and ${g.time} away. Every fare includes door-to-door pickup, flight tracking and meet & greet for arrivals.`)}</p></div>
  ${H2(`Fixed fares from ${t.name}`, "fares")}
  <div class="tw"><table><thead><tr><th>Destination</th><th>Distance</th><th>Journey time</th><th>Saloon fare</th></tr></thead><tbody>${rows}</tbody></table></div>
  <p class="rp mut">Saloon fares for 1–4 passengers. Estate/MPV about 1.2×, minibus about 1.4×, executive about 1.5×. Select a destination for the full route guide.</p>
  ${H2(`About pickups in ${t.name}`, "pickup")}
  ${P(t.intro)}
  ${P(t.pickup)}
  ${H2(`Getting from ${t.name} to the airports`, "roads")}
  ${P(`For Gatwick, Heathrow, Luton and the Southampton cruise terminals your driver normally ${t.m25}, then follows the M25 clockwise.${t.gatwickDirect ? ` For Gatwick there is also a shorter cross-country route: your driver ${t.gatwickDirect}.` : ""}`)}
  ${P(`For Stansted, London City, Tilbury and Harwich the route heads anticlockwise round the M25 towards the Dartford Crossing or the A2. For Folkestone and Dover your driver ${t.m20}, then heads east.`)}
  ${H2(`${t.name} airport taxi FAQs`, "faqs")}
  ${faqHtml(faqs)}
  ${H2("Nearby towns we cover", "nearby")}
  <ul class="rel">${near.map((x) => `<li><a href="/airport-taxi/${x.slug}/">${h(x.name)} airport taxis</a></li>`).join("")}</ul>
  ${updated()}
</main>`;
  return page({ url, title, desc, schema, body });
}

// ---------- destination hubs ----------
function destPage(d) {
  const url = `/taxi-to/${d.slug}/`;
  const rs = TOWNS.map((t) => route(t, d));
  const min = Math.min(...rs.map((r) => r.price));
  const ap = d.type === "ap";
  const noun = { city: "London City Airport", folkestone: "Folkestone & Eurotunnel", dover: "Dover Port", tilbury: "Tilbury Cruise", southampton: "Southampton Cruise", harwich: "Harwich Port" }[d.slug] || d.name;
  const title = `${noun} Taxi from Kent | Fixed Prices from £${min}`;
  const desc = `${d.short} taxis from Southborough, Tunbridge Wells, Tonbridge, Sevenoaks & 8 more towns. Fixed fares from £${min}, 24/7: ${PHONE_DISPLAY}`;
  const sb = rs[0], tw = rs[1];
  const faqs = [
    [`How much is a taxi to ${d.name} from Kent?`, `Fixed fares to ${d.name} start at £${sb.price} from Southborough and £${tw.price} from Tunbridge Wells for a saloon carrying up to four passengers. The table on this page lists the fare from every town we cover.`],
    [`How long does it take to get to ${d.short} from Tunbridge Wells?`, `About ${tw.time} in normal traffic for the ${tw.miles}-mile journey. ${trafficText(tw)}`],
    [`Which terminal will I be dropped at?`, d.terminals],
    [`Are there extra charges?`, d.dropoff],
    [ap ? `Do you meet arriving flights at ${d.short}?` : `Can you collect me when I return to ${d.short}?`, d.arrivals],
  ];
  const crumbItems = [["Home", "/"], ["Taxi routes", "/taxi/"], [`${d.short} taxis`, url]];
  const rows = rs.map((r) => `<tr><td><a href="${r.url}">${h(r.t.name)}</a></td><td>${r.miles} mi</td><td>${r.time}</td><td><strong>£${r.price}</strong></td></tr>`).join("");
  const schema = [
    { "@context": "https://schema.org", "@type": "TaxiService", "@id": BASE + url + "#service", name: `${d.name} taxi from Kent`, url: BASE + url, provider: bizRef,
      areaServed: TOWNS.map((t) => ({ "@type": "City", name: t.name })),
      hasOfferCatalog: { "@type": "OfferCatalog", name: `Fixed fares to ${d.name}`, itemListElement: rs.map((r) => ({ "@type": "Offer", name: `${r.t.name} to ${d.name}`, url: BASE + r.url, price: String(r.price), priceCurrency: "GBP" })) } },
    faqLd(faqs), crumbs(crumbItems),
  ];
  const body = `<main class="rtwrap">
  ${crumbHtml(crumbItems)}
  <h1 class="rth1">${h(d.name)} Taxis from Kent &amp; Sussex</h1>
  <div class="pills"><span class="pill">${d.icon} ${d.code || h(d.short)}</span><span class="pill">📍 12 towns</span><span class="pill">💷 From £${min}</span><span class="pill">🕐 24/7</span></div>
  ${ctaButtons(`Hi ${BRAND}! I need a taxi to ${d.name}.`, "dest-top")}
  <div class="aeobox"><div class="lbl">Quick answer</div><p>${h(`${BRAND} runs fixed-price taxis to ${d.name} from 12 towns in West Kent and East and West Sussex. Fares start at £${sb.price} from Southborough and £${tw.price} from Tunbridge Wells (about ${tw.time}). ${d.desc}`)}</p></div>
  ${H2(`Fares to ${d.short} by town`, "fares")}
  <div class="tw"><table><thead><tr><th>From</th><th>Distance</th><th>Journey time</th><th>Saloon fare</th></tr></thead><tbody>${rows}</tbody></table></div>
  ${H2(`About ${d.name}`, "about")}
  ${P(d.terminals)}
  ${P(d.dropoff)}
  ${P(d.checkin)}
  ${H2(`The route to ${d.short}`, "route")}
  ${P(routeText(tw))}
  ${P(trafficText(tw))}
  ${H2(`${d.short} taxi FAQs`, "faqs")}
  ${faqHtml(faqs)}
  ${H2("Other destinations", "other")}
  <ul class="rel">${DESTS.filter((x) => x.slug !== d.slug).map((x) => `<li><a href="/taxi-to/${x.slug}/">${h(x.name)} taxis</a></li>`).join("")}</ul>
  ${updated()}
</main>`;
  return page({ url, title, desc, schema, body });
}

// ---------- route index ----------
function indexPage() {
  const url = "/taxi/";
  const crumbItems = [["Home", "/"], ["Taxi routes", url]];
  const blocks = TOWNS.map((t) => `<h3 class="rh3"><a href="/airport-taxi/${t.slug}/">${h(t.name)}</a></h3><ul class="rel">${DESTS.map((d) => { const r = route(t, d); return `<li><a href="${r.url}">${h(t.name)} to ${h(d.short)}</a> <span class="mut">£${r.price}</span></li>`; }).join("")}</ul>`).join("\n");
  const body = `<main class="rtwrap">
  ${crumbHtml(crumbItems)}
  <h1 class="rth1">All Fixed-Price Taxi Routes from Southborough &amp; West Kent</h1>
  ${P(`Choose an airport, a seaport or your town to see fixed fares, journey times and booking details. We cover 12 towns and 10 destinations — 120 routes in total — 24 hours a day. Call ${PHONE_DISPLAY} any time.`)}
  ${H2("Airports", "airports")}
  <ul class="rel">${AP.map((d) => `<li><a href="/taxi-to/${d.slug}/">${d.icon} ${h(d.name)} (${d.code}) taxis</a></li>`).join("")}</ul>
  ${H2("Seaports & cruise terminals", "seaports")}
  <ul class="rel">${SP.map((d) => `<li><a href="/taxi-to/${d.slug}/">${d.icon} ${h(d.name)} taxis</a></li>`).join("")}</ul>
  ${H2("Towns", "towns")}
  <ul class="rel">${TOWNS.map((t) => `<li><a href="/airport-taxi/${t.slug}/">📍 ${h(t.name)} airport taxis</a></li>`).join("")}</ul>
  ${H2("Every route", "all")}
  ${blocks}
</main>`;
  return page({ url, title: "All Taxi Routes & Fixed Prices | Southborough Airport Taxis", desc: `120 fixed-price taxi routes from Southborough, Tunbridge Wells and 10 more towns to every London airport and the main cruise and ferry ports.`, schema: [crumbs(crumbItems)], body });
}

// ---------- guides ----------
function guidePage(g) {
  const url = `/guides/${g.slug}/`;
  const crumbItems = [["Home", "/"], ["Travel guides", "/guides/"], [g.title, url]];
  const others = GUIDES.filter((x) => x.slug !== g.slug).slice(0, 3);
  const schema = [
    { "@context": "https://schema.org", "@type": "Article", headline: g.title, description: g.desc, datePublished: g.published, dateModified: TODAY,
      mainEntityOfPage: BASE + url, author: { "@type": "Organization", "@id": BIZ_ID, name: BRAND, url: BASE + "/" }, publisher: { "@type": "Organization", "@id": BIZ_ID, name: BRAND } },
    crumbs(crumbItems),
  ];
  const body = `<main class="rtwrap">
  ${crumbHtml(crumbItems)}
  <article>
  <p class="kick">${h(g.tag)}</p>
  <h1 class="rth1">${h(g.title)}</h1>
  <p class="upd">By the ${BRAND} team · Published ${human(g.published)} · Updated ${human(TODAY)}</p>
  <div class="aeobox"><div class="lbl">Short answer</div><p>${h(g.answer)}</p></div>
  ${g.sections.map(([t, ps]) => `${H2(t)}\n  ${ps.map(P).join("\n  ")}`).join("\n  ")}
  ${H2("Related routes", "related")}
  <ul class="rel">${g.links.map(([u, n]) => `<li><a href="${u}">${h(n)}</a></li>`).join("")}</ul>
  <div class="ctabox"><div class="ctat">Book a fixed-price airport taxi</div><div class="ctas2">Southborough, Tunbridge Wells &amp; West Kent · 24/7</div>${ctaButtons(`Hi ${BRAND}! I'd like a quote for an airport taxi.`, "guide")}</div>
  </article>
  ${H2("More travel guides", "more")}
  <ul class="rel">${others.map((x) => `<li><a href="/guides/${x.slug}/">${h(x.title)}</a></li>`).join("")}</ul>
</main>`;
  return page({ url, title: `${g.title} | ${BRAND}`.length > 70 ? g.title : `${g.title} | ${BRAND}`, desc: g.desc, schema, body, ogType: "article" });
}
function guidesIndex() {
  const url = "/guides/";
  const crumbItems = [["Home", "/"], ["Travel guides", url]];
  const body = `<main class="rtwrap">
  ${crumbHtml(crumbItems)}
  <h1 class="rth1">Airport Travel Guides for Kent &amp; Sussex</h1>
  ${P("Practical advice on fares, timings and routes from Southborough, Tunbridge Wells and West Kent to the London airports and cruise ports, written by our local drivers and booking team.")}
  <div class="bgrid">${GUIDES.map(guideCard).join("")}</div>
</main>`;
  return page({ url, title: `Airport Travel Guides | ${BRAND}`, desc: "Guides to airport taxi fares, pickup times, taxi vs train and cruise transfers from Southborough, Tunbridge Wells and West Kent.", schema: [crumbs(crumbItems)], body });
}
const guideCard = (g) => `<a class="bcard" href="/guides/${g.slug}/"><div class="bp"><div class="btag">${h(g.tag)}</div><div class="bt">${h(g.title)}</div><div class="be">${h(g.desc)}</div><div class="bm"><span>📅 ${human(g.published)}</span></div></div></a>`;

// ---------- about / privacy / 404 ----------
function aboutPage() {
  const url = "/about/";
  const crumbItems = [["Home", "/"], ["About us", url]];
  const body = `<main class="rtwrap">
  ${crumbHtml(crumbItems)}
  <h1 class="rth1">About ${BRAND}</h1>
  <div class="aeobox"><div class="lbl">In brief</div><p>${h(`${BRAND} is a licensed private hire operator based in Southborough, Kent (TN4), trading as ${LEGAL}. We specialise in fixed-price airport and seaport transfers from Southborough, Tunbridge Wells and 10 other towns in West Kent and East and West Sussex, 24 hours a day.`)}</p></div>
  ${H2("What we do")}
  ${P("We focus on one thing: getting people from West Kent to their flight, ferry or cruise on time, at a price agreed in advance. We cover all five London airports — Gatwick, Heathrow, London City, Stansted and Luton — and the ports of Dover, Folkestone, Tilbury, Southampton and Harwich.")}
  ${H2("Licensing and safety")}
  ${P("Our drivers are licensed by Tunbridge Wells Borough Council, DBS-checked and professionally trained. Vehicles are licensed for private hire, insured for hire and reward, and kept clean and well maintained.")}
  ${H2("How our pricing works")}
  ${P("Every journey has a fixed fare, agreed when you book. Traffic does not change it, and neither do flight delays: we track flights and adjust pickups automatically, and the first 60 minutes of waiting after landing are free.")}
  ${H2("Contact details")}
  <table class="facts"><tbody>
    <tr><th scope="row">Business name</th><td>${BRAND} (${LEGAL})</td></tr>
    <tr><th scope="row">Based in</th><td>Southborough, Tunbridge Wells, Kent ${HQ.postcode}</td></tr>
    <tr><th scope="row">Phone &amp; WhatsApp</th><td><a href="tel:${PHONE_TEL}">${PHONE_DISPLAY}</a></td></tr>
    <tr><th scope="row">Email</th><td><a href="mailto:${EMAIL}">${EMAIL}</a></td></tr>
    <tr><th scope="row">Hours</th><td>24 hours a day, 7 days a week</td></tr>
    <tr><th scope="row">Areas covered</th><td>${TOWNS.map((t) => `<a href="/airport-taxi/${t.slug}/">${t.name}</a>`).join(", ")}</td></tr>
  </tbody></table>
  ${updated()}
</main>`;
  const schema = [{ "@context": "https://schema.org", "@type": "AboutPage", url: BASE + url, name: `About ${BRAND}`, mainEntity: { "@id": BIZ_ID } }, crumbs(crumbItems)];
  return page({ url, title: `About Us | ${BRAND} (${LEGAL})`, desc: `${BRAND} is a licensed private hire operator in Southborough, Kent, providing fixed-price airport and seaport taxis across West Kent 24/7.`, schema, body });
}
function privacyPage() {
  const url = "/privacy/";
  const crumbItems = [["Home", "/"], ["Privacy policy", url]];
  const body = `<main class="rtwrap prose">
  ${crumbHtml(crumbItems)}
  <h1 class="rth1">Privacy Policy</h1>
  <p class="upd">Last updated ${human(TODAY)}</p>
  ${P(`${BRAND} ("we", "us"), operated by ${LEGAL}, is based in Southborough, Tunbridge Wells, Kent TN4. This policy explains how we collect, use and protect your personal data when you use our website or book our services.`)}
  ${H2("What data we collect")}<ul><li>Name, phone number and email address</li><li>Pickup and destination addresses</li><li>Journey details (date, time, vehicle type)</li><li>Flight number where provided</li><li>Messages you send us by WhatsApp, phone or email</li></ul>
  ${H2("How we use your data")}<ul><li>To confirm and fulfil your booking</li><li>To contact you about your journey</li><li>To track your flight where a number is provided</li></ul>
  ${H2("How the booking form works")}${P("The booking form on our website does not store your details on our web server. When you submit it, it opens WhatsApp on your device with your booking details filled in, and nothing is sent until you press send in WhatsApp. WhatsApp's own privacy policy applies to that message.")}
  ${H2("Data sharing")}${P("We do not sell your data or share it for marketing. We share only what is needed with the driver carrying out your booking.")}
  ${H2("Data retention")}${P("We keep booking records for up to two years for accounting and legal purposes. You can ask us to delete your data at any time.")}
  ${H2("Your rights")}<ul><li>Access to your personal data</li><li>Correction of inaccurate data</li><li>Erasure</li><li>Restriction of processing</li><li>Data portability</li></ul>
  ${H2("Contact us")}<p class="rp">For any privacy query, email <a href="mailto:${EMAIL}">${EMAIL}</a> or call <a href="tel:${PHONE_TEL}">${PHONE_DISPLAY}</a>.</p>
</main>`;
  return page({ url, title: `Privacy Policy | ${BRAND}`, desc: `How ${BRAND} collects, uses and protects your personal data.`, schema: [crumbs(crumbItems)], body });
}
function notFound() {
  return page({ url: "/404/", title: `Page not found | ${BRAND}`, desc: "This page could not be found.", body: `<main class="rtwrap"><h1 class="rth1">Page not found</h1>${P("Sorry, that page does not exist. Try one of these instead:")}
  <ul class="rel"><li><a href="/">Home</a></li><li><a href="/taxi/">All routes &amp; prices</a></li>${AP.map((d) => `<li><a href="/taxi-to/${d.slug}/">${h(d.name)} taxis</a></li>`).join("")}</ul></main>` }).replace('content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1"', 'content="noindex"');
}

// ---------- homepage ----------
function homePage() {
  const tpl = fs.readFileSync(path.join(ROOT, "src/home-body.html"), "utf8");
  const sb = (d) => route(TOWNS[0], d);
  const apSorted = AP.map(sb).sort((a, b) => a.km - b.km);
  const g = sb(DESTS[0]);
  const faqs = HOME_FAQS;
  const fill = {
    TICKER: [...DESTS, ...DESTS].map((d) => `<span class="ti-i">${d.icon} ${h(d.name)} <span style="opacity:.3">✦</span></span>`).join(""),
    QUOTE_OPTIONS: `<optgroup label="── Airports ──">${AP.map((d) => `<option value="${d.slug}|${sb(d).miles}|${sb(d).price}">${h(d.name)} (${d.code}) — from £${sb(d).price}</option>`).join("")}</optgroup>
          <optgroup label="── Seaports ──">${SP.map((d) => `<option value="${d.slug}|${sb(d).miles}|${sb(d).price}">${h(d.name)} — from £${sb(d).price}</option>`).join("")}</optgroup>
          <optgroup label="── Other ──"><option value="custom|0|0">Another destination →</option></optgroup>`,
    GATWICK_KM: `${g.miles} miles`, GATWICK_TIME: g.time, GATWICK_DIST: `${g.miles} miles (${g.time})`,
    CLOSEST_REST: apSorted.slice(1).map((r) => `${r.d.short} is about ${r.miles} miles (${r.time})`).join(", "),
    AP_CARDS: AP.map((d) => { const r = sb(d); return `<a class="gcard" href="/taxi-to/${d.slug}/"><span class="gi">${d.icon}</span><div class="gt">${h(d.name)} (${d.code})</div><div class="gd">${h(d.desc)}</div><div class="gp">from £${r.price} · ${r.time}</div><div class="gar">Prices from every town →</div></a>`; }).join(""),
    SP_CARDS: SP.map((d) => { const r = sb(d); return `<a class="gcard dk" href="/taxi-to/${d.slug}/"><span class="gi">${d.icon}</span><div class="gt li">${h(d.name)}</div><div class="gd li">${h(d.desc)}</div><div class="gp go">from £${r.price} · ${r.time}</div><div class="gar" style="color:var(--G)">View prices →</div></a>`; }).join(""),
    TW_CARDS: TOWNS.map((t) => { const r = route(t, DESTS[0]); return `<a class="gcard" href="/airport-taxi/${t.slug}/"><span class="gi">📍</span><div class="gt">${h(t.name)} airport taxis</div><div class="gd">${t.county} · ${h(t.lm)}</div><div class="gp">Gatwick from £${r.price}</div><div class="gar">All routes from ${h(t.name)} →</div></a>`; }).join(""),
    PRICE_ROWS: DESTS.map((d) => { const r = sb(d); return `<a class="prow" href="${r.url}"><div class="pd"><span style="font-size:1.05rem">${d.icon}</span><div><div class="pn">${h(d.name)}</div><div class="pm">${r.miles} miles · ${r.time}</div></div></div><div class="pp">£${r.price}</div></a>`; }).join(""),
    TESTIMONIALS: [...TESTIMONIALS, ...TESTIMONIALS].map((x, i) => `<div class="tc"${i >= TESTIMONIALS.length ? ' aria-hidden="true"' : ""}><div class="tcs">★★★★★</div><div class="tct">"${h(x.t)}"</div><div class="tca">${h(x.n)}</div><div class="tcr">${h(x.r)}</div></div>`).join(""),
    GUIDE_CARDS: GUIDES.slice(0, 3).map(guideCard).join(""),
    FAQ: faqs.map(([q, a]) => `<details class="faq-item"><summary class="faq-q">${h(q)}<span class="faq-ic">+</span></summary><div class="faq-a">${h(a)}</div></details>`).join(""),
    FOOTER: "",
  };
  let body = tpl.replace(/\{\{([A-Z_]+)\}\}/g, (_, k) => { if (!(k in fill)) throw new Error("No fill for " + k); return fill[k]; });
  body = body.replace(/ onclick="tr\('(\w+)',\{l:'(\w+)'\}\)"/g, ' data-tr="$1:$2"');
  const schema = [
    { "@context": "https://schema.org", ...BIZ, "@type": "LocalBusiness",
      description: "Fixed-price airport and seaport taxis from Southborough, Tunbridge Wells and West Kent to Gatwick, Heathrow, London City, Stansted, Luton, Dover, Folkestone, Tilbury, Southampton and Harwich. 24/7, licensed drivers.",
      openingHoursSpecification: { "@type": "OpeningHoursSpecification", dayOfWeek: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], opens: "00:00", closes: "23:59" },
      areaServed: TOWNS.map((t) => ({ "@type": "City", name: t.name })),
      paymentAccepted: "Cash, Credit Card, Debit Card, Bank Transfer", currenciesAccepted: "GBP",
      knowsAbout: ["Airport transfers", "Gatwick Airport", "Heathrow Airport", "Stansted Airport", "Luton Airport", "London City Airport", "Cruise transfers", "Port of Dover", "Southampton cruise terminals"],
      hasOfferCatalog: { "@type": "OfferCatalog", name: "Fixed fares from Southborough", itemListElement: DESTS.map((d) => ({ "@type": "Offer", name: `Southborough to ${d.name}`, url: BASE + sb(d).url, price: String(sb(d).price), priceCurrency: "GBP" })) } },
    { "@context": "https://schema.org", "@type": "WebSite", "@id": BASE + "/#website", url: BASE + "/", name: BRAND, alternateName: LEGAL, publisher: { "@id": BIZ_ID }, inLanguage: "en-GB" },
    faqLd(faqs),
  ];
  const scripts = `<script>
function calcQ(){var v=document.getElementById("qto").value,m=parseFloat(document.getElementById("qveh").value)||1,r=document.getElementById("qres");
if(!v){alert("Please select a destination");return}
if(v==="custom|0|0"){location.href="${wa(`Hi ${BRAND}! I need a quote for a custom journey.`)}";return}
var p=v.split("|"),price=Math.round(parseFloat(p[2])*m);document.getElementById("qprice").textContent="£"+price;
document.getElementById("qnote").textContent="About "+p[1]+" miles from Southborough · Fixed estimate · Call ${PHONE_DISPLAY} to confirm";r.classList.add("on");tr("quote",{dest:p[0],price:price})}
function fsub(e){e.preventDefault();tr("booking_submit");var f=document.getElementById("mform"),d=new FormData(f),g=function(k){return d.get(k)||""};
var msg="NEW BOOKING REQUEST\\n\\nName: "+g("name")+"\\nPhone: "+g("phone")+"\\nEmail: "+g("email")+"\\nPassengers: "+g("passengers")+"\\nFrom: "+g("pickup")+"\\nTo: "+g("destination")+"\\nDate: "+g("date")+"  Time: "+g("time")+"\\nVehicle: "+g("vehicle")+"\\nReturn: "+g("return")+"\\nNotes: "+g("notes")+"\\n\\nPlease confirm the fixed price.";
window.open("https://wa.me/${WA}?text="+encodeURIComponent(msg),"_blank");f.style.display="none";document.getElementById("fsuccess").style.display="block"}
</script>`;
  const html = page({
    url: "/",
    title: "Airport Taxis Southborough & Tunbridge Wells | Fixed Prices 24/7",
    desc: `Airport taxis from Southborough & Tunbridge Wells: Gatwick from £72, Heathrow £95, plus Stansted, Luton & cruise ports. Fixed fares, 24/7: ${PHONE_DISPLAY}`,
    schema, body: body + scripts,
  });
  return html;
}

// ---------- write everything ----------
const pages = [];
const write = (url, html, file) => {
  const out = file ? path.join(ROOT, file) : path.join(ROOT, url, "index.html");
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, html);
  if (!file || file === "index.html") pages.push(url);
};

// clean previously generated folders
for (const dir of ["taxi", "airport-taxi", "taxi-to", "guides", "about", "privacy"]) fs.rmSync(path.join(ROOT, dir), { recursive: true, force: true });

write("/", homePage(), "index.html");
write("/taxi/", indexPage());
for (const d of DESTS) write(`/taxi-to/${d.slug}/`, destPage(d));
for (const t of TOWNS) write(`/airport-taxi/${t.slug}/`, townPage(t));
for (const t of TOWNS) for (const d of DESTS) { const r = route(t, d); write(r.url, routePage(r)); }
write("/guides/", guidesIndex());
for (const g of GUIDES) write(`/guides/${g.slug}/`, guidePage(g));
write("/about/", aboutPage());
write("/privacy/", privacyPage());
fs.writeFileSync(path.join(ROOT, "404.html"), notFound());

fs.writeFileSync(path.join(ROOT, "sitemap.xml"), `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${pages.map((u) => `  <url><loc>${BASE}${u}</loc><lastmod>${TODAY}</lastmod></url>`).join("\n")}
</urlset>
`);

fs.writeFileSync(path.join(ROOT, "robots.txt"), `# Search engines and AI assistants are welcome to crawl this site.
User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot-Extended
Allow: /

Sitemap: ${BASE}/sitemap.xml
`);

const sbr = (d) => route(TOWNS[0], d), twr = (d) => route(TOWNS[1], d);
fs.writeFileSync(path.join(ROOT, "llms.txt"), `# ${BRAND}

> ${BRAND} (trading as ${LEGAL}) is a licensed private hire operator based in Southborough, Tunbridge Wells, Kent (TN4), England. It provides fixed-price airport and seaport taxi transfers 24 hours a day from 12 towns in West Kent and East/West Sussex. Phone and WhatsApp: ${PHONE_DISPLAY} (${PHONE_INTL}). Email: ${EMAIL}.

Key facts:
- Fares are fixed when booked; no charge for flight delays; flight tracking and meet & greet inside the terminal for arrivals; first 60 minutes of waiting after landing free.
- Drivers are licensed by Tunbridge Wells Borough Council and DBS-checked.
- Vehicles: saloon (1–4 passengers), estate/MPV (5–6), minibus (7–8), executive saloon (1–4).
- Towns covered: ${TOWNS.map((t) => t.name).join(", ")}.
- Saloon fares from Southborough: ${DESTS.map((d) => `${d.short} £${sbr(d).price}`).join(", ")}.
- Saloon fares from Tunbridge Wells: ${DESTS.map((d) => `${d.short} £${twr(d).price}`).join(", ")}.
- Gatwick is the closest airport to Southborough and Tunbridge Wells (about ${twr(DESTS[0]).miles} miles, ${twr(DESTS[0]).time}).

## Main pages
- [Home](${BASE}/): overview, booking form and FAQs
- [All routes and prices](${BASE}/taxi/): 120 fixed-price routes
- [About](${BASE}/about/): business details and licensing

## Airports and seaports
${DESTS.map((d) => `- [${d.name} taxis](${BASE}/taxi-to/${d.slug}/): fares from every town`).join("\n")}

## Towns
${TOWNS.map((t) => `- [${t.name} airport taxis](${BASE}/airport-taxi/${t.slug}/)`).join("\n")}

## Guides
${GUIDES.map((g) => `- [${g.title}](${BASE}/guides/${g.slug}/): ${g.desc}`).join("\n")}
`);

console.log(`Built ${pages.length} pages (+404, sitemap, robots.txt, llms.txt) on ${TODAY}`);
