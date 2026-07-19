#!/usr/bin/env python3
"""
Generates real, static, crawlable HTML pages for every route listed in
sitemap.xml (12 towns x 10 destinations = 120 pages). Fixes the root
SEO problem: the sitemap advertised these URLs but the site only ever
served one client-side-only index.html with no matching routes, so
every one of these URLs 404'd for Google.
"""
import os

BASE = "https://southboroughairporttaxis.co.uk"
PHONE_DISPLAY = "07808 065494"
PHONE_TEL = "07808065494"
PHONE_INTL = "+447808065494"
EMAIL = "clinetaxi@gmail.com"

AP = [
    {"slug":"gatwick","name":"Gatwick Airport","code":"LGW","icon":"✈️","km":38,"time":"40–55 mins","price":72,"desc":"North and South terminals covered. Closest major airport to Southborough. Fixed price, flight tracking, meet & greet — all included."},
    {"slug":"heathrow","name":"Heathrow Airport","code":"LHR","icon":"✈️","km":50,"time":"55–70 mins","price":95,"desc":"All 5 terminals covered. UK's busiest airport. Meet & greet in every terminal. Your driver tracks your flight automatically."},
    {"slug":"city","name":"London City Airport","code":"LCY","icon":"✈️","km":48,"time":"55–70 mins","price":90,"desc":"Business travel hub in the Docklands. Quick check-in airport. Executive car service available for corporate travel."},
    {"slug":"stansted","name":"Stansted Airport","code":"STN","icon":"✈️","km":75,"time":"80–95 mins","price":130,"desc":"Popular with Ryanair, easyJet and Wizz Air. Fixed price, guaranteed — no surprises on the day."},
    {"slug":"luton","name":"Luton Airport","code":"LTN","icon":"✈️","km":85,"time":"90–110 mins","price":148,"desc":"easyJet and Wizz Air hub. Fixed-price taxi from Southborough with real-time flight tracking."},
]
SP = [
    {"slug":"folkestone","name":"Folkestone Eurotunnel","icon":"🚄","km":35,"time":"40–50 mins","price":65,"desc":"Eurotunnel Le Shuttle — drive-on train to Calais, France. Closest seaport from Southborough."},
    {"slug":"dover","name":"Dover Port","icon":"⛴️","km":42,"time":"45–60 mins","price":78,"desc":"P&O and DFDS ferries to France. UK's busiest ferry port. Fixed-price transfer, door to terminal."},
    {"slug":"tilbury","name":"Tilbury Docks","icon":"⚓","km":55,"time":"60–75 mins","price":100,"desc":"Thames cruise terminal for Fred Olsen and other cruise lines. Door-to-terminal, fixed price."},
    {"slug":"southampton","name":"Southampton Cruise Terminal","icon":"🚢","km":68,"time":"75–95 mins","price":120,"desc":"Major cruise hub — Royal Caribbean, P&O, MSC, Cunard, Celebrity. Luggage assistance included."},
    {"slug":"harwich","name":"Harwich International","icon":"⛴️","km":100,"time":"95–120 mins","price":175,"desc":"Stena Line to Hook of Holland. DFDS to Denmark. Fixed price from Southborough."},
]
TW = [
    {"slug":"southborough","name":"Southborough","km":0,"county":"Kent","lm":"London Road, Modest Corner & St John's Road","st":"High Brooms Station"},
    {"slug":"tunbridge-wells","name":"Tunbridge Wells","km":3,"county":"Kent","lm":"The Pantiles, Calverley Road & Royal Victoria Place","st":"Tunbridge Wells Station"},
    {"slug":"tonbridge","name":"Tonbridge","km":6,"county":"Kent","lm":"Tonbridge Castle, the High Street & Tonbridge School","st":"Tonbridge Station"},
    {"slug":"sevenoaks","name":"Sevenoaks","km":14,"county":"Kent","lm":"Knole Park & the town centre","st":"Sevenoaks Station"},
    {"slug":"paddock-wood","name":"Paddock Wood","km":8,"county":"Kent","lm":"the High Street & Mascalls Court Road","st":"Paddock Wood Station"},
    {"slug":"maidstone","name":"Maidstone","km":21,"county":"Kent","lm":"Maidstone town centre & the County Hall area","st":"Maidstone East Station"},
    {"slug":"crowborough","name":"Crowborough","km":11,"county":"East Sussex","lm":"Crowborough Cross & the High Street","st":"Crowborough Station"},
    {"slug":"edenbridge","name":"Edenbridge","km":16,"county":"Kent","lm":"the High Street & Edenbridge Town Station area","st":"Edenbridge Town Station"},
    {"slug":"east-grinstead","name":"East Grinstead","km":22,"county":"West Sussex","lm":"the town centre & Saint Hill Road","st":"East Grinstead Station"},
    {"slug":"westerham","name":"Westerham","km":19,"county":"Kent","lm":"the Green & Quebec Square","st":"nearest Oxted Station"},
    {"slug":"hartfield","name":"Hartfield","km":15,"county":"East Sussex","lm":"the High Street & Ashdown Forest","st":"nearest Forest Row"},
    {"slug":"hawkhurst","name":"Hawkhurst","km":24,"county":"Kent","lm":"the Moor & Rye Road","st":"nearest Etchingham Station"},
]

NAV = f"""<nav id="nav">
  <a class="logo" href="/"><div class="lbox">🚖</div>C Line <span>Cars</span></a>
  <ul class="nl">
    <li><a href="/">Home</a></li>
    <li><a href="/#airports">Airports</a></li>
    <li><a href="/#towns">Towns</a></li>
    <li><a href="tel:{PHONE_TEL}" style="color:var(--R)">Book Now</a></li>
  </ul>
  <div class="nr">
    <a href="tel:{PHONE_TEL}" class="ncall">📞 {PHONE_DISPLAY}</a>
  </div>
</nav>"""

def footer_html():
    ap_links = "".join(f'<li><a href="/taxi/southborough-to-{a["slug"]}/">{a["icon"]} {a["name"]}</a></li>' for a in AP)
    tw_links = "".join(f'<li><a href="/taxi/{t["slug"]}-to-heathrow/">📍 {t["name"]}</a></li>' for t in TW[:6])
    return f"""<footer><div class="fgrd">
    <div><div class="flogo">C Line <span>Cars</span></div><p style="margin-bottom:.85rem">Southborough's most trusted airport taxi. Fixed prices, professional drivers, 24/7, any UK destination.</p><div style="display:flex;flex-direction:column;gap:.28rem"><a href="tel:{PHONE_TEL}" style="color:rgba(255,255,255,.35);font-size:.73rem">📞 {PHONE_DISPLAY}</a><a href="https://wa.me/{PHONE_INTL.replace('+','')}" target="_blank" style="color:rgba(255,255,255,.35);font-size:.73rem">💬 {PHONE_INTL}</a><a href="mailto:{EMAIL}" style="color:rgba(255,255,255,.35);font-size:.73rem">📧 {EMAIL}</a><span style="color:rgba(255,255,255,.18);font-size:.7rem">📍 Southborough, TN4 · Kent</span></div></div>
    <div><h5>Airports</h5><ul>{ap_links}</ul></div>
    <div><h5>Quick Links</h5><ul><li><a href="/">🏠 Home</a></li><li><a href="tel:{PHONE_TEL}">📋 Book Now</a></li></ul></div>
    <div><h5>Locations</h5><ul>{tw_links}</ul></div>
  </div><div class="fbot"><span>© 2025 C Line Cars · southboroughairporttaxis.co.uk · Licensed Private Hire · Kent</span><span>Serving Southborough, Tunbridge Wells, Tonbridge, Sevenoaks &amp; all of Kent 24/7</span></div></footer>"""

def page_html(frm, dest, is_ap):
    adjp = round(dest["price"] + frm["km"] * 2)
    dest_label = f'{dest["name"]} ({dest["code"]})' if is_ap else dest["name"]
    url = f'{BASE}/taxi/{frm["slug"]}-to-{dest["slug"]}/'
    title = f'{frm["name"]} to {dest["name"]} Taxi | Fixed Price £{adjp} | C Line Cars'
    desc = f'Fixed-price taxi from {frm["name"]} to {dest["name"]} from £{adjp}. Journey takes {dest["time"]}. {"Flight tracking, no delay surcharge, meet & greet." if is_ap else "Door-to-terminal, fixed price, no hidden charges."} Call {PHONE_DISPLAY}.'

    faqs = [
        (f'How much is a taxi from {frm["name"]} to {dest["name"]}?',
         f'A fixed-price taxi from {frm["name"]} to {dest["name"]} costs from approximately £{adjp} for a saloon (1–4 passengers). Includes door-to-door pickup from {frm["lm"]}, {"flight tracking and no delay surcharge" if is_ap else "direct terminal drop-off"}. Call {PHONE_DISPLAY} for your exact quote.'),
        (f'How long does it take from {frm["name"]} to {dest["name"]}?',
         f'The journey from {frm["name"]} to {dest["name"]} takes approximately {dest["time"]} in normal traffic. Allow extra time during weekday peaks (7–9am and 4–7pm). Your driver will advise on the best departure time when you book.'),
        (f'Does C Line Cars pick up from {frm["name"]}?',
         f'Yes — we provide regular transfers from {frm["name"]}, including pickups from {frm["lm"]}. We serve all postcodes in {frm["name"]} and surrounding areas of {frm["county"]}.'),
        ('Do you charge extra if my flight is delayed?',
         'No — never. C Line Cars tracks your flight in real time and adjusts your pickup automatically. The price you booked is always the price you pay, regardless of delays.') if is_ap else
        (f'Do you provide door-to-terminal drop-off at {dest["name"]}?',
         f'Yes. Your driver takes you directly to the {dest["name"]} terminal building, with luggage assistance included as standard.'),
        ('Are drivers licensed and DBS checked?',
         'Yes. All C Line Cars drivers are licensed by Tunbridge Wells Borough Council, DBS-checked and professionally trained. We are a fully licensed private hire company in Kent.'),
    ]

    faq_items_html = "".join(
        f'<div class="qa"><h3>{q}</h3><p>{a}</p></div>' for q, a in faqs
    )
    faq_schema_items = ",".join(
        '{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}' % (
            q.replace('"','\\"'), a.replace('"','\\"')
        ) for q, a in faqs
    )

    vehicles = [("🚗","Saloon","1–4 pax",1),("🚙","MPV / Estate","5–6 pax",1.2),("🚐","Minibus","7–8 pax",1.4),("🏎️","Executive","1–4 pax",1.5)]
    vehicle_html = "".join(
        f'<div class="vopt"><div style="font-size:1.45rem">{ic}</div><div style="font-weight:700;font-size:.83rem">{nm}</div><div style="font-size:.65rem;color:var(--fg3)">{px}</div><div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.15rem;color:var(--R)">£{round(adjp*m)}</div></div>'
        for ic, nm, px, m in vehicles
    )

    breadcrumb_schema = (
        '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
        '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
        '{"@type":"ListItem","position":2,"name":"%s","item":"%s/taxi/%s-to-%s/"}]}'
    ) % (BASE, f'{frm["name"]} to {dest["name"]}', BASE, frm["slug"], dest["slug"])

    faq_schema = '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[%s]}' % faq_schema_items

    service_schema = (
        '{"@context":"https://schema.org","@type":"TaxiService","name":"C Line Cars","description":"Fixed-price taxi from %s to %s","url":"%s","telephone":"%s",'
        '"areaServed":{"@type":"Place","name":"%s"},"priceRange":"££",'
        '"makesOffer":{"@type":"Offer","itemOffered":{"@type":"Service","name":"%s to %s Taxi"},"price":"%s","priceCurrency":"GBP"}}'
    ) % (frm["name"], dest["name"], url, PHONE_INTL, frm["name"], frm["name"], dest["name"], adjp)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<script type="application/ld+json">{service_schema}</script>
<script type="application/ld+json">{faq_schema}</script>
<script type="application/ld+json">{breadcrumb_schema}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
<style>
.rtwrap{{max-width:900px;margin:0 auto;padding:2rem 1.1rem 3rem}}
.crumb{{font-size:.75rem;color:var(--fg3);margin-bottom:.9rem}}
.crumb a{{color:var(--fg3)}}
.rth1{{font-family:'Bebas Neue',sans-serif;font-size:clamp(1.9rem,5vw,2.8rem);letter-spacing:.02em;margin-bottom:.6rem}}
.pills{{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:1.2rem}}
.pill{{background:var(--bg2);border:1px solid var(--cb);border-radius:20px;padding:.3rem .8rem;font-size:.72rem}}
.pbox{{background:var(--N);color:#fff;border-radius:10px;padding:1.2rem;margin-bottom:1.5rem}}
.pbox .price{{font-family:'Bebas Neue',sans-serif;font-size:2.2rem;color:var(--R)}}
.aeobox{{background:var(--bg2);border-left:4px solid var(--R);border-radius:6px;padding:1rem 1.2rem;margin:1.3rem 0}}
.aeobox .lbl{{font-size:.65rem;text-transform:uppercase;letter-spacing:.08em;color:var(--R);font-weight:800;margin-bottom:.3rem}}
.vgrid{{display:grid;grid-template-columns:repeat(2,1fr);gap:.55rem;margin:1rem 0 1.6rem}}
.vopt{{background:var(--bg2);border:1.5px solid var(--cb);border-radius:6px;padding:.85rem;text-align:center}}
.ctabox{{margin-top:1.6rem;padding:1.3rem;background:var(--N);border-radius:8px;border:2px solid var(--R);color:#fff}}
.btn{{display:inline-block;padding:.6rem 1.1rem;border-radius:6px;font-weight:700;font-size:.8rem;margin:.25rem .35rem .25rem 0}}
.br{{background:var(--R);color:#fff}}
.bw{{background:#25D366;color:#fff}}
.qa{{margin-bottom:1.1rem}}
.qa h3{{font-size:.92rem;margin-bottom:.3rem}}
.qa p{{font-size:.85rem;line-height:1.7;color:var(--fg2)}}
</style>
</head>
<body>
{NAV}
<div class="rtwrap" style="padding-top:calc(var(--nh) + 1.4rem)">
  <div class="crumb"><a href="/">Home</a> › <a href="/#{'airports' if is_ap else 'towns'}">{"Airports" if is_ap else "Seaports"}</a> › {frm["name"]} to {dest["name"]}</div>
  <h1 class="rth1">{frm["name"]} to {dest_label} Taxi</h1>
  <div class="pills">
    <span class="pill">📍 {frm["name"]}, {frm["county"]}</span>
    <span class="pill">{dest["icon"]} {dest["code"] if is_ap else dest["name"]}</span>
    <span class="pill">⏱ {dest["time"]}</span>
    <span class="pill">🛡️ No delay surcharge</span>
  </div>
  <div class="pbox">
    <div style="font-size:.7rem;opacity:.7;text-transform:uppercase;letter-spacing:.06em">Fixed price from {frm["name"]}</div>
    <div class="price">£{adjp}</div>
    <div style="font-size:.75rem;opacity:.7">Saloon · 1–4 pax · Door to door · {"Meet & greet included" if is_ap else "Direct terminal drop-off"}</div>
  </div>
  <div>
    <a href="tel:{PHONE_TEL}" class="btn br">📞 {PHONE_DISPLAY}</a>
    <a href="https://wa.me/{PHONE_INTL.replace('+','')}?text=Hi C Line Cars! I need a taxi from {frm['name']} to {dest['name']}." target="_blank" class="btn bw">💬 WhatsApp Quote</a>
  </div>

  <h2 style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;margin:1.8rem 0 .6rem">{frm["name"]} → {dest["name"]}: What to Expect</h2>
  <p style="font-size:.87rem;line-height:1.8;color:var(--fg2)">{dest["desc"]} C Line Cars provides professional fixed-price transfers from {frm["name"]} to {dest["name"]} with door-to-door pickup from {frm["lm"]} and {"meet & greet in the arrivals hall" if is_ap else "direct terminal drop-off"} included.</p>
  <p style="font-size:.87rem;line-height:1.8;color:var(--fg2);margin-top:.6rem">We know the area well — including the route from {frm["st"]} for passengers comparing options. All drivers are licensed by Tunbridge Wells Borough Council, DBS-checked and professionally trained.</p>

  <div class="aeobox">
    <div class="lbl">Quick Answer</div>
    <h3 style="font-size:.95rem;margin-bottom:.35rem">How much is a taxi from {frm["name"]} to {dest["name"]}?</h3>
    <p style="font-size:.87rem;line-height:1.7">From <strong>£{adjp} for a saloon</strong> (1–4 passengers). Journey: approximately <strong>{dest["time"]}</strong>. Includes <strong>{"flight tracking, no delay surcharge, meet & greet" if is_ap else "fixed price, door-to-terminal drop-off"}</strong>. Call <strong>{PHONE_DISPLAY}</strong> to confirm your exact fare.</p>
  </div>

  <h2 style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;margin:1.6rem 0 .6rem">Vehicle Options for This Route</h2>
  <div class="vgrid">{vehicle_html}</div>

  <div class="ctabox">
    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.25rem;margin-bottom:.3rem">Book {frm["name"]} → {dest["name"]}</div>
    <div style="font-size:.75rem;opacity:.65;margin-bottom:.7rem">Fixed price from £{adjp} · Confirmed within 30 minutes</div>
    <a href="tel:{PHONE_TEL}" class="btn br">📞 {PHONE_DISPLAY}</a>
    <a href="https://wa.me/{PHONE_INTL.replace('+','')}?text=Hi! Taxi from {frm['name']} to {dest['name']} — please confirm price." target="_blank" class="btn bw">💬 WhatsApp Quote</a>
  </div>

  <h2 style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;margin:1.9rem 0 .8rem">Frequently Asked Questions</h2>
  {faq_items_html}
</div>
{footer_html()}
</body>
</html>"""


def main():
    out_root = os.path.join(os.path.dirname(__file__), "taxi")
    count = 0
    for frm in TW:
        for dest in AP:
            path = os.path.join(out_root, f'{frm["slug"]}-to-{dest["slug"]}')
            os.makedirs(path, exist_ok=True)
            with open(os.path.join(path, "index.html"), "w") as f:
                f.write(page_html(frm, dest, True))
            count += 1
        for dest in SP:
            path = os.path.join(out_root, f'{frm["slug"]}-to-{dest["slug"]}')
            os.makedirs(path, exist_ok=True)
            with open(os.path.join(path, "index.html"), "w") as f:
                f.write(page_html(frm, dest, False))
            count += 1
    print(f"Generated {count} pages")

if __name__ == "__main__":
    main()
