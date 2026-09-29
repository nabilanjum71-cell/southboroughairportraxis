#!/usr/bin/env python3
"""
Generates real, static, crawlable HTML pages for every route listed in
sitemap.xml (12 towns x 10 destinations = 120 pages). Fixes the root
SEO problem: the sitemap advertised these URLs but the site only ever
served one client-side-only index.html with no matching routes, so
every one of these URLs 404'd for Google.
"""
import os, json, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rich_content import TOWN_INFO, AIRPORT_INFO, ROUTE_INFO, PRIORITY

BASE = "https://www.southboroughairporttaxis.co.uk"
PHONE_DISPLAY = "07808 065494"
PHONE_TEL = "07808065494"
PHONE_INTL = "+447808065494"
EMAIL = "clinetaxi@gmail.com"

AP = [
    {"slug":"gatwick","name":"Gatwick Airport","short":"Gatwick","code":"LGW","icon":"✈️","km":38,"time":"40–55 mins","price":72,"desc":"North and South terminals covered. Closest major airport to Southborough. Fixed price, flight tracking, meet & greet — all included."},
    {"slug":"heathrow","name":"Heathrow Airport","short":"Heathrow","code":"LHR","icon":"✈️","km":50,"time":"55–70 mins","price":95,"desc":"All four terminals (2, 3, 4 and 5) covered. UK's busiest airport. Meet & greet in every terminal. Your driver tracks your flight automatically."},
    {"slug":"city","name":"London City Airport","short":"London City","code":"LCY","icon":"✈️","km":48,"time":"55–70 mins","price":90,"desc":"Business travel hub in the Docklands. Quick check-in airport. Executive car service available for corporate travel."},
    {"slug":"stansted","name":"Stansted Airport","short":"Stansted","code":"STN","icon":"✈️","km":75,"time":"80–95 mins","price":130,"desc":"Popular with Ryanair, easyJet and Wizz Air. Fixed price, guaranteed — no surprises on the day."},
    {"slug":"luton","name":"Luton Airport","short":"Luton","code":"LTN","icon":"✈️","km":85,"time":"90–110 mins","price":148,"desc":"easyJet and Wizz Air hub. Fixed-price taxi from Southborough with real-time flight tracking."},
]
SP = [
    {"slug":"folkestone","name":"Folkestone Eurotunnel","short":"Folkestone","icon":"🚄","km":35,"time":"40–50 mins","price":65,"desc":"Eurotunnel Le Shuttle — drive-on train to Calais, France. Closest seaport from Southborough."},
    {"slug":"dover","name":"Dover Port","short":"Dover","icon":"⛴️","km":42,"time":"45–60 mins","price":78,"desc":"P&O and DFDS ferries to France. UK's busiest ferry port. Fixed-price transfer, door to terminal."},
    {"slug":"tilbury","name":"Tilbury Docks","short":"Tilbury","icon":"⚓","km":55,"time":"60–75 mins","price":100,"desc":"Thames cruise terminal for Fred Olsen and other cruise lines. Door-to-terminal, fixed price."},
    {"slug":"southampton","name":"Southampton Cruise Terminal","short":"Southampton","icon":"🚢","km":68,"time":"75–95 mins","price":120,"desc":"Major cruise hub — Royal Caribbean, P&O, MSC, Cunard, Celebrity. Luggage assistance included."},
    {"slug":"harwich","name":"Harwich International","short":"Harwich","icon":"⛴️","km":100,"time":"95–120 mins","price":175,"desc":"Stena Line to Hook of Holland. DFDS to Denmark. Fixed price from Southborough."},
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


def related_html(frm, dest):
    others_ap = [d for d in AP + SP if d["slug"] != dest["slug"]]
    a = "".join(f'<li><a href="/taxi/{frm["slug"]}-to-{d["slug"]}/">{frm["name"]} to {d["short"]} taxi</a></li>' for d in others_ap)
    others_tw = [t for t in TW if t["slug"] != frm["slug"]]
    b = "".join(f'<li><a href="/taxi/{t["slug"]}-to-{dest["slug"]}/">{t["name"]} to {dest["short"]} taxi</a></li>' for t in others_tw)
    return (f'<h2 style="font-family:\'Bebas Neue\',sans-serif;font-size:1.3rem;margin:1.9rem 0 .6rem">More Routes from {frm["name"]}</h2>'
            f'<ul class="rel">{a}</ul>'
            f'<h2 style="font-family:\'Bebas Neue\',sans-serif;font-size:1.3rem;margin:1.6rem 0 .6rem">Other Towns to {dest["short"]}</h2>'
            f'<ul class="rel">{b}</ul>'
            f'<p style="margin-top:1rem;font-size:.8rem"><a href="/taxi/">See every route we cover &rarr;</a></p>')

def page_html(frm, dest, is_ap):
    adjp = round(dest["price"] + frm["km"] * 2)
    dest_label = f'{dest["name"]} ({dest["code"]})' if is_ap else dest["name"]
    url = f'{BASE}/taxi/{frm["slug"]}-to-{dest["slug"]}/'
    title = f'{frm["name"]} to {dest["short"]} Taxi | £{adjp} Fixed Price'
    desc = f'Fixed-price taxi, {frm["name"]} to {dest["short"]}. From £{adjp}, {dest["time"]}. {"Flight tracking, no delay fees." if is_ap else "Door-to-terminal, no hidden fees."} Call {PHONE_DISPLAY}.'

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
        '{"@context":"https://schema.org","@type":"TaxiService","name":"%s to %s Taxi","description":"Fixed-price taxi from %s to %s","url":"%s",'
        '"provider":{"@type":"LocalBusiness","name":"C Line Cars","telephone":"%s","priceRange":"££"},'
        '"areaServed":{"@type":"Place","name":"%s"},'
        '"offers":{"@type":"Offer","price":"%s","priceCurrency":"GBP"}}'
    ) % (frm["name"], dest["name"], frm["name"], dest["name"], url, PHONE_INTL, frm["name"], adjp)

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
.rel{{columns:2;font-size:.82rem;line-height:1.9;padding-left:1.1rem}}
.rel a{{color:var(--R)}}
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
  {related_html(frm, dest)}
</div>
{footer_html()}
</body>
</html>"""



PAGE_CSS = """.rtwrap{max-width:900px;margin:0 auto;padding:2rem 1.1rem 3rem}
.crumb{font-size:.75rem;color:var(--fg3);margin-bottom:.9rem}.crumb a{color:var(--fg3)}
.rth1{font-family:'Bebas Neue',sans-serif;font-size:clamp(1.9rem,5vw,2.8rem);letter-spacing:.02em;margin-bottom:.6rem}
.pills{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:1.2rem}
.pill{background:var(--bg2);border:1px solid var(--cb);border-radius:20px;padding:.3rem .8rem;font-size:.72rem}
.pbox{background:var(--N);color:#fff;border-radius:10px;padding:1.2rem;margin-bottom:1.2rem}
.pbox .price{font-family:'Bebas Neue',sans-serif;font-size:2.2rem;color:var(--R)}
.aeobox{background:var(--bg2);border-left:4px solid var(--R);border-radius:6px;padding:1rem 1.2rem;margin:1.3rem 0}
.aeobox .lbl{font-size:.65rem;text-transform:uppercase;letter-spacing:.08em;color:var(--R);font-weight:800;margin-bottom:.3rem}
.toc{font-size:.78rem;background:var(--bg2);border:1px solid var(--cb);border-radius:6px;padding:.7rem 1rem;line-height:1.9}
.toc a{color:var(--R)}
.tw{overflow-x:auto;margin:.6rem 0 1.2rem}
table{border-collapse:collapse;width:100%;font-size:.84rem}
th,td{border:1px solid var(--cb);padding:.55rem .8rem;text-align:left}
th{background:var(--bg2);font-size:.75rem;text-transform:uppercase;letter-spacing:.04em}
.steps{list-style:none;counter-reset:s;display:grid;grid-template-columns:repeat(2,1fr);gap:.7rem;margin:.6rem 0 1.2rem;padding:0}
.steps li{counter-increment:s;background:var(--bg2);border:1.5px solid var(--cb);border-radius:8px;padding:.9rem .9rem .9rem 3rem;position:relative;font-size:.84rem;line-height:1.6}
.steps li::before{content:counter(s);position:absolute;left:.8rem;top:.8rem;width:1.7rem;height:1.7rem;border-radius:50%;background:var(--R);color:#fff;font-weight:800;display:flex;align-items:center;justify-content:center;font-size:.85rem}
.steps span{color:var(--fg2)}
.vgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:.55rem;margin:1rem 0 1.6rem}
.vopt{background:var(--bg2);border:1.5px solid var(--cb);border-radius:6px;padding:.85rem;text-align:center}
.ctabox{margin-top:1.6rem;padding:1.3rem;background:var(--N);border-radius:8px;border:2px solid var(--R);color:#fff}
.btn{display:inline-block;padding:.6rem 1.1rem;border-radius:6px;font-weight:700;font-size:.8rem;margin:.25rem .35rem .25rem 0}
.br{background:var(--R);color:#fff}.bw{background:#25D366;color:#fff}
.qa{margin-bottom:1.1rem}.qa h3{font-size:.92rem;margin-bottom:.3rem}
.qa p{font-size:.85rem;line-height:1.7;color:var(--fg2)}
.rel{columns:2;font-size:.82rem;line-height:1.9;padding-left:1.1rem}.rel a{color:var(--R)}
@media(max-width:600px){.steps{grid-template-columns:1fr}.rel{columns:1}}"""

TERM_SHORT = {
    "heathrow": "Heathrow has four terminals (2, 3, 4 and 5), so tell us yours when you book.",
    "gatwick": "Gatwick has a North and a South terminal, so tell us yours when you book.",
    "stansted": "Stansted has a single terminal, so there is nothing to choose.",
}

def h2(t):
    return f'<h2 style="font-family:\'Bebas Neue\',sans-serif;font-size:1.5rem;margin:2rem 0 .7rem" id="{re.sub(r"[^a-z]+","-",t.lower()).strip("-")}">{t}</h2>'

def P_(t):
    return f'<p style="font-size:.88rem;line-height:1.85;color:var(--fg2);margin-bottom:.8rem">{t}</p>'

def rich_faqs(frm, dest, adjp):
    key = f'{frm["slug"]}-to-{dest["slug"]}'
    ri, ti, ai = ROUTE_INFO[key], TOWN_INFO[frm["slug"]], AIRPORT_INFO[dest["slug"]]
    T, A, AF, TM = frm["name"], dest["short"], dest["name"], ri["time"]
    return [
        (f"How much is a taxi from {T} to {AF}?",
         f"A fixed-price taxi from {T} to {AF} starts from £{adjp} for a saloon carrying one to four passengers. The price is agreed when you book and does not change with traffic or flight delays. Larger vehicles cost more, and the fare table above shows saloon, MPV, minibus and executive prices. Call {PHONE_DISPLAY} to confirm your exact fare."),
        (f"How long does it take to get from {T} to {AF} by taxi?",
         f"Allow about {TM} in normal traffic. Most of the route is on the M25 and connecting motorways, so incidents and rush hours can add time. We recommend leaving more time than the minimum, especially for early flights, and your driver will advise a pickup time when you book so you reach {A} comfortably."),
        (f"What time should I be picked up in {T} for my flight?",
         "As a guide, plan to reach the airport about three hours before departure, then add the journey time and a safety buffer. The planning table above shows suggested pickup times for common departures. Tell us your flight time when you book and we will confirm the pickup time that suits your route."),
        (f"Is it worth taking a taxi instead of the train from {T} to {A}?",
         "Rail suits solo travellers on off-peak trips with light luggage. A taxi usually makes more sense for groups, heavy bags, early or late flights and awkward connections, because it collects you from your door and takes you straight to your terminal with no changes. Compare the total cost for everyone travelling before you decide."),
        ("Do you charge extra if my flight is delayed?",
         f"No. We track your flight and adjust your pickup automatically, so a delay does not change the fixed price you booked. Your driver waits for you at {A} rather than leaving, and you do not need to phone us with updates. The fare you were quoted at booking is the fare you pay."),
        (f"Where will my driver meet me at {AF}?",
         f"Your driver meets you inside the terminal for arrivals, as part of the meet-and-greet service included in your fare. We track your flight, so a late landing does not matter. {TERM_SHORT[dest['slug']]}"),
        (f"Is there a drop-off charge at {AF}?", ai["dropoff"]),
        (f"Can you collect me from {frm['st']} or my home in {T}?",
         f"Yes. We collect across {ti['postcodes']}, from your front door or from a station or landmark you name when booking. Just give us the full address or postcode and your driver will find you, including on rural or hard-to-find roads."),
        (f"How many passengers and bags can you take from {T} to {A}?",
         "A saloon carries up to four passengers, an MPV or estate five or six, and a minibus seven or eight. Tell us the number of passengers and large cases when you book so we send a vehicle that fits comfortably. Executive saloons are also available for one to four passengers who want extra comfort."),
        (f"Do you run early-morning and late-night transfers from {T}?",
         "Yes. C Line Cars operates 24 hours a day, seven days a week, so a 4am pickup for an early flight is a normal booking. Book as soon as you know your flight time, particularly for very early departures, so your driver and vehicle are confirmed well before the day."),
        (f"How far in advance should I book a taxi from {T} to {A}?",
         f"Book as soon as you know your flight, especially for early mornings, weekends and school holidays. Most bookings are confirmed within 30 minutes, and your price is fixed at that point. If you need a taxi at short notice, call {PHONE_DISPLAY} and we will tell you what we can arrange."),
        ("Are your drivers licensed and DBS checked?",
         "Yes. All C Line Cars drivers are licensed by Tunbridge Wells Borough Council, DBS-checked and professionally trained. We are a fully licensed private hire company in Kent, so you can travel knowing your driver is vetted and your vehicle is licensed for hire and reward."),
        (ri["extra_q"][0], ri["extra_q"][1]),
        (f"What happens if there is heavy traffic on the way to {A}?",
         f"Your fare stays fixed, so heavy traffic does not add to your price. Your driver checks live traffic before setting off and can switch route if there is a closure. We also advise leaving earlier than the minimum time for early flights, since that buffer is what protects you from delays on the M25."),
        (f"Which terminal do I need at {AF}?",
         f"{ai['terminals']} Tell us your terminal when you book so your driver is ready."),
    ]

def fmt_time(mins):
    mins %= 24*60
    return f"{mins//60:02d}:{mins%60:02d}"

def page_rich(frm, dest, is_ap):
    key = f'{frm["slug"]}-to-{dest["slug"]}'
    ri, ti, ai = ROUTE_INFO[key], TOWN_INFO[frm["slug"]], AIRPORT_INFO[dest["slug"]]
    adjp = round(dest["price"] + frm["km"] * 2)
    T, A, AF, TM = frm["name"], dest["short"], dest["name"], ri["time"]
    url = f'{BASE}/taxi/{key}/'
    title = f"{T} to {A} Taxi | £{adjp} Fixed Price"
    desc = f"Fixed-price taxi, {T} to {A}. From £{adjp}, about {TM}. Flight tracking, no delay fees, door-to-door pickup, 24/7. Call {PHONE_DISPLAY}."
    faqs = rich_faqs(frm, dest, adjp)

    quick = (f"A taxi from {T} to {AF} costs from £{adjp} for a saloon (1–4 passengers). The fare is fixed when you book, "
             f"the journey takes about {TM}, and the price includes door-to-door pickup and flight tracking with no delay surcharge. "
             f"Vehicles for up to eight passengers are available. Call {PHONE_DISPLAY} for your exact fare.")

    vehicles = [("Saloon","1–4",1),("MPV / Estate","5–6",1.2),("Minibus","7–8",1.4),("Executive saloon","1–4",1.5)]
    vrows = "".join(f"<tr><td>{n}</td><td>{p}</td><td><strong>£{round(adjp*m)}</strong></td></tr>" for n,p,m in vehicles)

    prows = ""
    for dep in (6*60, 9*60, 12*60, 17*60):
        pick = dep - (180 + ri["tmax"] + 30)
        pick -= pick % 5
        prows += f"<tr><td>{fmt_time(dep)}</td><td><strong>{fmt_time(pick)}</strong></td></tr>"

    faq_html = "".join(f'<div class="qa"><h3>{q}</h3><p>{a}</p></div>' for q, a in faqs)
    esc = lambda x: x.replace("\\", "\\\\").replace('"', '\\"')
    faq_schema = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}, ensure_ascii=False)
    service_schema = json.dumps({"@context":"https://schema.org","@type":"TaxiService","name":f"{T} to {AF} Taxi",
        "description":f"Fixed-price taxi from {T} to {AF}","url":url,
        "provider":{"@type":"LocalBusiness","name":"C Line Cars","telephone":PHONE_INTL,"priceRange":"££"},
        "areaServed":{"@type":"Place","name":T,"geo":{"@type":"GeoCoordinates","latitude":ti["lat"],"longitude":ti["lng"]}},
        "offers":{"@type":"Offer","price":str(adjp),"priceCurrency":"GBP"}}, ensure_ascii=False)
    crumb_schema = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},
        {"@type":"ListItem","position":2,"name":"Taxi routes","item":BASE+"/taxi/"},
        {"@type":"ListItem","position":3,"name":f"{T} to {A}","item":url}]}, ensure_ascii=False)
    speak_schema = json.dumps({"@context":"https://schema.org","@type":"WebPage","name":title,"url":url,
        "speakable":{"@type":"SpeakableSpecification","cssSelector":[".aeobox",".qa"]}}, ensure_ascii=False)

    steps = [("Call or WhatsApp",f"Give us your {T} pickup address, your flight time and the number of passengers."),
             ("Get your fixed fare",f"We confirm the price for {T} to {A}, and it does not change on the day."),
             ("We track your flight","Your pickup adjusts automatically if your flight moves, at no extra charge."),
             ("Door to terminal",f"Your driver collects you at home and takes you straight to {AF}.")]
    steps_html = "".join(f'<li><strong>{a}</strong><br><span>{b}</span></li>' for a,b in steps)

    body = f"""
  <div class="crumb"><a href="/">Home</a> › <a href="/taxi/">Taxi routes</a> › {T} to {A}</div>
  <h1 class="rth1">{T} to {AF} Taxi — Fixed Price from £{adjp}</h1>
  <div class="pills">
    <span class="pill">📍 {T}, {frm["county"]}</span><span class="pill">{dest["icon"]} {dest["code"] if is_ap else dest["name"]}</span>
    <span class="pill">⏱ About {TM}</span><span class="pill">🛡️ No delay surcharge</span><span class="pill">🕐 24/7</span>
  </div>
  <div class="pbox"><div style="font-size:.7rem;opacity:.7;text-transform:uppercase;letter-spacing:.06em">Fixed price from {T}</div>
    <div class="price">£{adjp}</div><div style="font-size:.75rem;opacity:.7">Saloon · 1–4 passengers · Door to door · Meet &amp; greet at arrivals</div></div>
  <div><a href="tel:{PHONE_TEL}" class="btn br">📞 {PHONE_DISPLAY}</a>
    <a href="https://wa.me/{PHONE_INTL.replace('+','')}?text=Hi C Line Cars! I need a taxi from {T} to {A}." target="_blank" class="btn bw">💬 WhatsApp Quote</a></div>
  <div class="aeobox"><div class="lbl">Quick Answer</div><p style="font-size:.88rem;line-height:1.75">{quick}</p></div>
  <nav class="toc"><strong>On this page:</strong> <a href="#fixed-fares-by-vehicle">Fares</a> · <a href="#the-journey">Journey</a> · <a href="#pickup-in-{re.sub(r'[^a-z]+','-',T.lower()).strip('-')}">Pickup</a> · <a href="#at-the-airport">At the airport</a> · <a href="#how-booking-works">How it works</a> · <a href="#frequently-asked-questions">FAQs</a></nav>

  {h2("Fixed Fares by Vehicle")}
  {P_(f"Your fare from {T} to {AF} is agreed when you book and stays the same whatever the traffic does. It covers door-to-door pickup, flight tracking and a driver who waits for you rather than watching the clock. The table shows the fare for each vehicle size, so you can pick the one that fits your group and luggage.")}
  <div class="tw"><table><thead><tr><th>Vehicle</th><th>Passengers</th><th>Fixed fare</th></tr></thead><tbody>{vrows}</tbody></table></div>

  {h2("The Journey")}
  {P_(ri["route"])}
  {P_(ri["timing"])}
  {P_(f"In normal traffic, allow about {TM} from {T} to {AF}. The planning table below assumes you want to reach the airport around three hours before departure, adds the upper end of the journey time, then keeps a 30-minute buffer for traffic. Treat it as a guide, and we will confirm the right pickup time for your flight when you book.")}
  <div class="tw"><table><thead><tr><th>Flight departs</th><th>Suggested pickup from {T}</th></tr></thead><tbody>{prows}</tbody></table></div>

  {h2(f"Pickup in {T}")}
  {P_(ti["intro"])}
  {P_(ti["pickup"])}

  {h2("At the Airport")}
  {P_(ai["terminals"])}
  {P_(ai["arrivals"])}
  {P_(ai["dropoff"])}

  {h2("How Booking Works")}
  <ol class="steps">{steps_html}</ol>
  {P_("All C Line Cars drivers are licensed by Tunbridge Wells Borough Council, DBS-checked and professionally trained, and we operate 24 hours a day, so early departures and late arrivals are a normal booking.")}
  <div class="ctabox"><div style="font-family:'Bebas Neue',sans-serif;font-size:1.25rem;margin-bottom:.3rem">Book {T} → {A}</div>
    <div style="font-size:.75rem;opacity:.65;margin-bottom:.7rem">Fixed price from £{adjp} · Confirmed within 30 minutes</div>
    <a href="tel:{PHONE_TEL}" class="btn br">📞 {PHONE_DISPLAY}</a>
    <a href="https://wa.me/{PHONE_INTL.replace('+','')}?text=Hi! Taxi from {T} to {A} — please confirm price." target="_blank" class="btn bw">💬 WhatsApp Quote</a></div>

  {h2("Frequently Asked Questions")}
  {faq_html}
  {related_html(frm, dest)}
"""
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
<script type="application/ld+json">{crumb_schema}</script>
<script type="application/ld+json">{speak_schema}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
<style>{PAGE_CSS}</style>
</head>
<body>
{NAV}
<div class="rtwrap" style="padding-top:calc(var(--nh) + 1.4rem)">{body}</div>
{footer_html()}
</body>
</html>"""

def hub_html():
    blocks = ""
    for t in TW:
        links = "".join(f'<li><a href="/taxi/{t["slug"]}-to-{d["slug"]}/">{t["name"]} to {d["short"]}</a></li>' for d in AP + SP)
        blocks += f'<h2 style="font-family:\'Bebas Neue\',sans-serif;font-size:1.4rem;margin:1.6rem 0 .5rem">Taxis from {t["name"]}</h2><ul class="rel">{links}</ul>'
    url = BASE + "/taxi/"
    title = "Airport & Seaport Taxi Routes from Kent | C Line Cars"
    desc = f"Fixed-price taxis from Southborough, Tunbridge Wells, Tonbridge, Sevenoaks and more to every London airport and UK seaport. Call {PHONE_DISPLAY}."
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}"><link rel="canonical" href="{url}">
<meta name="robots" content="index,follow"><link rel="stylesheet" href="/assets/style.css">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>{PAGE_CSS}</style></head><body>{NAV}
<div class="rtwrap" style="padding-top:calc(var(--nh) + 1.4rem)"><div class="crumb"><a href="/">Home</a> › Taxi routes</div>
<h1 class="rth1">Fixed-Price Taxi Routes from Southborough &amp; Kent</h1>
<p style="font-size:.88rem;line-height:1.8;color:var(--fg2)">Choose your town to see the fixed fare, journey time and booking details for every airport and seaport we serve. Call {PHONE_DISPLAY} any time, day or night.</p>
{blocks}</div>{footer_html()}</body></html>"""


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_root = os.path.join(repo_root, "taxi")
    count = 0
    for frm in TW:
        for dest in AP:
            path = os.path.join(out_root, f'{frm["slug"]}-to-{dest["slug"]}')
            os.makedirs(path, exist_ok=True)
            with open(os.path.join(path, "index.html"), "w") as f:
                f.write(page_rich(frm, dest, True) if f'{frm["slug"]}-to-{dest["slug"]}' in ROUTE_INFO else page_html(frm, dest, True))
            count += 1
        for dest in SP:
            path = os.path.join(out_root, f'{frm["slug"]}-to-{dest["slug"]}')
            os.makedirs(path, exist_ok=True)
            with open(os.path.join(path, "index.html"), "w") as f:
                f.write(page_rich(frm, dest, False) if f'{frm["slug"]}-to-{dest["slug"]}' in ROUTE_INFO else page_html(frm, dest, False))
            count += 1
    os.makedirs(out_root, exist_ok=True)
    open(os.path.join(out_root, "index.html"), "w").write(hub_html())
    print(f"Generated {count} pages + hub")

if __name__ == "__main__":
    main()
