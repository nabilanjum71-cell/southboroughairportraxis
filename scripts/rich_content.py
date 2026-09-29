# Long-form content for the priority route pages.
# Facts here are deliberately conservative. Anything about C Line Cars' own
# policies (tolls, drop-off fees, child seats, payment, cancellations) is NOT
# asserted -- only what the existing site already claims.

TOWN_INFO = {
    "southborough": {
        "lat": 51.163, "lng": 0.262,
        "postcodes": "TN4",
        "intro": "Southborough sits just north of Royal Tunbridge Wells, and it is where C Line Cars is based. That means pick-ups here are among the shortest positioning runs we make, and a driver can usually be with you quickly.",
        "pickup": "We collect from all TN4 addresses, including London Road, Modest Corner, Southborough Common, St John's Road and the streets around High Brooms station. Give us your full postcode when you book and your driver will come to your door rather than a fixed meeting point.",
    },
    "tunbridge-wells": {
        "lat": 51.132, "lng": 0.263,
        "postcodes": "TN1, TN2, TN3 and TN4",
        "intro": "Royal Tunbridge Wells is the main town in this part of Kent, and it is one of the most common starting points for airport transfers we run, from town-centre flats to family homes on the edge of the Weald.",
        "pickup": "We cover TN1, TN2, TN3 and TN4, including The Pantiles, Calverley Road, Royal Victoria Place and the roads around Tunbridge Wells station. Give us the full address or postcode when you book and your driver will pick you up from your door.",
    },
    "maidstone": {
        "lat": 51.272, "lng": 0.529,
        "postcodes": "ME14, ME15 and ME16",
        "intro": "Maidstone is Kent's county town, and its position beside the M20 makes the run to the western London airports quicker than many people expect, provided you avoid the worst of the morning rush.",
        "pickup": "We collect from ME14, ME15 and ME16, including the town centre around Week Street and Fremlin Walk, the streets near Maidstone East, Maidstone Barracks and Maidstone West stations, Mote Park and the County Hall area. Tell us your postcode and we come to your door.",
    },
    "sevenoaks": {
        "lat": 51.272, "lng": 0.190,
        "postcodes": "TN13 and TN14",
        "intro": "Sevenoaks sits right beside the M25, which gives it one of the shortest motorway approaches of any town we serve. That is a real advantage on early departures, when the ring road is at its quietest.",
        "pickup": "We collect from TN13 and TN14, including the High Street, the roads around Sevenoaks station and Bat and Ball station, Riverhead, and the edge of Knole Park. Give us your full postcode when you book and your driver will meet you at your door.",
    },
    "paddock-wood": {
        "lat": 51.181, "lng": 0.390,
        "postcodes": "TN12",
        "intro": "Paddock Wood is a Weald village-town surrounded by orchards and old hop country. It is a little further from the motorway network than Tonbridge or Sevenoaks, so a fixed door-to-door fare removes the guesswork of getting to a distant station first.",
        "pickup": "We collect from TN12, including the High Street, the roads around Paddock Wood station, and surrounding villages such as Five Oak Green, Brenchley and Matfield. Give us your full postcode when you book so your driver can find rural addresses without delay.",
    },
    "east-grinstead": {
        "lat": 51.126, "lng": -0.007,
        "postcodes": "RH19",
        "intro": "East Grinstead is a West Sussex town on the Kent and Surrey border, close to the A22 and the M25. It is a long way from Stansted, but a taxi turns what is otherwise a multi-change rail journey into one door-to-door run.",
        "pickup": "We collect from RH19, including the High Street, the roads around East Grinstead station, Saint Hill Road, Felbridge and the villages towards Ashdown Forest. Give us your full postcode when you book and your driver will come to your door.",
    },
}

AIRPORT_INFO = {
    "heathrow": {
        "terminals": "Heathrow has four passenger terminals: Terminals 2, 3, 4 and 5. Terminal 1 has closed. Your airline confirmation shows which terminal your flight uses, and your driver takes you to the correct drop-off point.",
        "dropoff": "Heathrow charges £7 per vehicle for terminal forecourt drop-off, with a 10-minute limit, at the time of writing. That fee is set by the airport, not by us, and it can change, so check Heathrow's website and ask us at booking how it is handled on your fare.",
        "arrivals": "For arrivals, your driver tracks your flight and waits for you inside the terminal, so a late landing does not change your fare.",
        "short": "Heathrow",
    },
    "gatwick": {
        "terminals": "Gatwick has two terminals, North and South, linked by a short shuttle. Your airline confirmation tells you which one your flight uses, and your driver takes you to the correct drop-off point.",
        "dropoff": "Gatwick charges £10 for up to 10 minutes at its terminal forecourts, at the time of writing, with longer stays costing more. That fee is set by the airport, not by us, and it can change, so check Gatwick's website and ask us at booking how it is handled on your fare.",
        "arrivals": "For arrivals, your driver tracks your flight and waits for you inside the terminal, so a late landing does not change your fare.",
        "short": "Gatwick",
    },
    "stansted": {
        "terminals": "Stansted has a single passenger terminal, so there is no terminal to choose. Your driver drops you at the terminal forecourt and can help with your luggage.",
        "dropoff": "Stansted charges £10 for a short forecourt stop, at the time of writing, and considerably more for longer stays. That fee is set by the airport, not by us, and it can change, so check Stansted's website and ask us at booking how it is handled on your fare.",
        "arrivals": "For arrivals, your driver tracks your flight and waits for you inside the terminal, so a late landing does not change your fare.",
        "short": "Stansted",
    },
}

# Per-route content. 'time' overrides the generic per-airport time.
ROUTE_INFO = {
    "southborough-to-gatwick": {
        "time": "40–55 mins", "tmax": 55,
        "route": "From Southborough your driver normally joins the A26 towards Tonbridge, then takes the A21 north to Junction 5 of the M25 near Sevenoaks. From there it is a short run anticlockwise to Junction 7, then south on the M23 to Gatwick at Junction 9. When the M25 is congested, the A264 through East Grinstead and on towards Crawley is the usual alternative.",
        "timing": "This is one of the shortest airport runs in Kent, which is why Gatwick is the most popular airport from Southborough. The uncertain part is the M25 between Junctions 5 and 7, which can slow sharply at commuter peaks and after incidents, so we build in a buffer for morning departures.",
        "extra_q": ("Which way do you drive from Southborough to Gatwick?",
                    "Most journeys use the A26 and A21 to the M25 at Junction 5, then the M23 south to Junction 9. If the M25 is congested, your driver may switch to the A264 through East Grinstead instead. The choice is made on the day using live traffic, so you always get the quicker option."),
    },
    "tunbridge-wells-to-heathrow": {
        "time": "60–80 mins", "tmax": 80,
        "route": "From Tunbridge Wells your driver normally takes the A21 north to Junction 5 of the M25 at Sevenoaks, then follows the M25 anticlockwise past the Surrey junctions to the Heathrow turn-offs. The M25 west side is the busiest stretch on the route, so morning and Friday departures are planned with extra margin.",
        "timing": "Heathrow is the longest of the western airport runs from Tunbridge Wells and the one most affected by the M25. Journey time is normally a little over an hour, but incidents near the M23 and M3 junctions can add a lot, so we recommend leaving more time than the minimum, especially for long-haul departures.",
        "extra_q": ("What is the best route from Tunbridge Wells to Heathrow?",
                    "The usual route is the A21 to the M25 at Junction 5, then the M25 anticlockwise to the Heathrow junctions. It is the most direct road route. Your driver checks live traffic before setting off and can change approach if there is an incident, which is one reason a local driver beats a rigid satnav route."),
    },
    "maidstone-to-gatwick": {
        "time": "50–65 mins", "tmax": 65,
        "route": "From Maidstone your driver normally joins the M20 westbound, follows the M26 to the M25 at Junction 5, then goes anticlockwise to Junction 7 and south on the M23 to Gatwick at Junction 9. The M20 and the M25 near Sevenoaks are the two places where delays usually build up.",
        "timing": "Maidstone to Gatwick is almost entirely motorway, which is quick when traffic is light but exposed to delays when it is not. Leaving before the morning peak, or well after it, makes a noticeable difference to the journey time.",
        "extra_q": ("What is the best route from Maidstone to Gatwick Airport?",
                    "The standard route is the M20 west, the M26, then the M25 to Junction 7 and the M23 south to Gatwick. It is mostly motorway and usually the fastest option. Your driver checks live traffic and can switch to A-roads through Sevenoaks if there is a closure on the M20 or M26."),
    },
    "paddock-wood-to-gatwick": {
        "time": "55–70 mins", "tmax": 70,
        "route": "From Paddock Wood your driver normally heads for Tonbridge and joins the A21 north to Junction 5 of the M25, then goes anticlockwise to Junction 7 and south on the M23 to Gatwick. The A264 through Tunbridge Wells and East Grinstead is the alternative when the motorway is slow.",
        "timing": "Paddock Wood is rural, so the first few miles are on smaller roads, then the run is much the same as from Tonbridge or Tunbridge Wells. The A21 and the M25 near Sevenoaks are where delays tend to appear, so a small buffer is sensible for early flights.",
        "extra_q": ("Is there a good taxi option from Paddock Wood to Gatwick?",
                    "Yes. A pre-booked fixed-fare taxi collects you from your door in Paddock Wood and takes you straight to your Gatwick terminal, with no need to reach a station first. That is especially useful for early flights, heavy luggage or groups, when rail connections from a small station are limited."),
    },
    "sevenoaks-to-heathrow": {
        "time": "45–60 mins", "tmax": 60,
        "route": "From Sevenoaks your driver joins the M25 at Junction 5 and drives anticlockwise to the Heathrow junctions. It is one of the most direct approaches to Heathrow from Kent, with very little on smaller roads. The main variable is the west side of the M25, which is busy for much of the day.",
        "timing": "Sevenoaks has the shortest run to Heathrow of any town we serve, because the M25 starts on its doorstep. That advantage is greatest for very early flights, when the ring road is quiet, and smaller at peak times, when the west side is slow.",
        "extra_q": ("What is the quickest way from Sevenoaks to Heathrow?",
                    "By road, the quickest way is the M25 anticlockwise from Junction 5 to the Heathrow junctions, with no complicated changes. A taxi collects you from your door, so there is no rail change into London. Your driver checks live traffic and can adjust the approach if there is an incident on the M25."),
    },
    "east-grinstead-to-stansted": {
        "time": "1 hr 30 – 1 hr 50", "tmax": 110,
        "route": "From East Grinstead your driver normally takes the A22 north to the M25 at Junction 6, then follows the M25 clockwise around the east of London. The route crosses the Thames at the Dartford Crossing, continues to Junction 27 for the M11, and runs north to Stansted at Junction 8. The Dartford Crossing is the main pinch-point and has a road-user charge.",
        "timing": "Stansted is the longest airport run from East Grinstead, and it is the route where planning matters most. The Dartford Crossing can hold up traffic in either direction, so we recommend building in more time than the standard journey, particularly for early morning and Friday departures.",
        "extra_q": ("Do I have to pay the Dartford Crossing charge on the way to Stansted?",
                    "The route from East Grinstead to Stansted normally crosses the Thames at the Dartford Crossing, which has a road-user charge. Ask us when you book how the charge is handled on your fixed fare, so you know the full cost before you travel and there are no surprises on the day."),
    },
}

PRIORITY = list(ROUTE_INFO.keys())
