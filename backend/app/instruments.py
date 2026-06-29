"""
Curated catalog of Indian market instruments available on Yahoo Finance.
Covers NIFTY 50, NIFTY Next 50, Nifty Midcap 150, small-caps, ETFs, and indices.
350+ instruments across 30+ sectors.
"""

from app.schemas import InstrumentInfo


INSTRUMENT_CATALOG: list[dict] = [

    # ── NIFTY 50 ────────────────────────────────────────────────────
    {"symbol": "RELIANCE.NS",   "name": "Reliance Industries",            "exchange": "NSE", "instrument_type": "Stock", "sector": "Energy"},
    {"symbol": "TCS.NS",        "name": "Tata Consultancy Services",      "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "HDFCBANK.NS",   "name": "HDFC Bank",                      "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "INFY.NS",       "name": "Infosys",                        "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "ICICIBANK.NS",  "name": "ICICI Bank",                     "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever",             "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "SBIN.NS",       "name": "State Bank of India",            "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Telecom"},
    {"symbol": "ITC.NS",        "name": "ITC Limited",                    "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "KOTAKBANK.NS",  "name": "Kotak Mahindra Bank",            "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "LT.NS",         "name": "Larsen & Toubro",                "exchange": "NSE", "instrument_type": "Stock", "sector": "Infrastructure"},
    {"symbol": "AXISBANK.NS",   "name": "Axis Bank",                      "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "HCLTECH.NS",    "name": "HCL Technologies",               "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "ASIANPAINT.NS", "name": "Asian Paints",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "Consumer Durables"},
    {"symbol": "MARUTI.NS",     "name": "Maruti Suzuki",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Automobile"},
    {"symbol": "SUNPHARMA.NS",  "name": "Sun Pharma",                     "exchange": "NSE", "instrument_type": "Stock", "sector": "Pharma"},
    {"symbol": "TATAMOTORS.NS", "name": "Tata Motors",                    "exchange": "NSE", "instrument_type": "Stock", "sector": "Automobile"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Finance"},
    {"symbol": "TATASTEEL.NS",  "name": "Tata Steel",                     "exchange": "NSE", "instrument_type": "Stock", "sector": "Metals"},
    {"symbol": "NTPC.NS",       "name": "NTPC Limited",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "Power"},
    {"symbol": "POWERGRID.NS",  "name": "Power Grid Corp",                "exchange": "NSE", "instrument_type": "Stock", "sector": "Power"},
    {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement",               "exchange": "NSE", "instrument_type": "Stock", "sector": "Cement"},
    {"symbol": "TITAN.NS",      "name": "Titan Company",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Consumer Durables"},
    {"symbol": "NESTLEIND.NS",  "name": "Nestle India",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "TECHM.NS",      "name": "Tech Mahindra",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "M&M.NS",        "name": "Mahindra & Mahindra",            "exchange": "NSE", "instrument_type": "Stock", "sector": "Automobile"},
    {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Finance"},
    {"symbol": "ADANIENT.NS",   "name": "Adani Enterprises",              "exchange": "NSE", "instrument_type": "Stock", "sector": "Diversified"},
    {"symbol": "ADANIPORTS.NS", "name": "Adani Ports",                    "exchange": "NSE", "instrument_type": "Stock", "sector": "Infrastructure"},
    {"symbol": "ONGC.NS",       "name": "Oil & Natural Gas Corp",         "exchange": "NSE", "instrument_type": "Stock", "sector": "Energy"},
    {"symbol": "JSWSTEEL.NS",   "name": "JSW Steel",                      "exchange": "NSE", "instrument_type": "Stock", "sector": "Metals"},
    {"symbol": "COALINDIA.NS",  "name": "Coal India",                     "exchange": "NSE", "instrument_type": "Stock", "sector": "Mining"},
    {"symbol": "BPCL.NS",       "name": "Bharat Petroleum",               "exchange": "NSE", "instrument_type": "Stock", "sector": "Energy"},
    {"symbol": "DRREDDY.NS",    "name": "Dr Reddy's Laboratories",        "exchange": "NSE", "instrument_type": "Stock", "sector": "Pharma"},
    {"symbol": "CIPLA.NS",      "name": "Cipla",                          "exchange": "NSE", "instrument_type": "Stock", "sector": "Pharma"},
    {"symbol": "EICHERMOT.NS",  "name": "Eicher Motors",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Automobile"},
    {"symbol": "GRASIM.NS",     "name": "Grasim Industries",              "exchange": "NSE", "instrument_type": "Stock", "sector": "Cement"},
    {"symbol": "DIVISLAB.NS",   "name": "Divi's Laboratories",            "exchange": "NSE", "instrument_type": "Stock", "sector": "Pharma"},
    {"symbol": "BRITANNIA.NS",  "name": "Britannia Industries",           "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "HEROMOTOCO.NS", "name": "Hero MotoCorp",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Automobile"},
    {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "APOLLOHOSP.NS", "name": "Apollo Hospitals",               "exchange": "NSE", "instrument_type": "Stock", "sector": "Healthcare"},
    {"symbol": "TATACONSUM.NS", "name": "Tata Consumer Products",         "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "SBILIFE.NS",    "name": "SBI Life Insurance",             "exchange": "NSE", "instrument_type": "Stock", "sector": "Insurance"},
    {"symbol": "HDFCLIFE.NS",   "name": "HDFC Life Insurance",            "exchange": "NSE", "instrument_type": "Stock", "sector": "Insurance"},
    {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto",                     "exchange": "NSE", "instrument_type": "Stock", "sector": "Automobile"},
    {"symbol": "WIPRO.NS",      "name": "Wipro",                          "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "BEL.NS",        "name": "Bharat Electronics",             "exchange": "NSE", "instrument_type": "Stock", "sector": "Defence"},
    {"symbol": "HAL.NS",        "name": "Hindustan Aeronautics",          "exchange": "NSE", "instrument_type": "Stock", "sector": "Defence"},
    {"symbol": "SHRIRAMFIN.NS", "name": "Shriram Finance",                "exchange": "NSE", "instrument_type": "Stock", "sector": "Finance"},

    # ── NIFTY Next 50 ───────────────────────────────────────────────
    {"symbol": "TRENT.NS",      "name": "Trent Limited",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Retail"},
    {"symbol": "ZOMATO.NS",     "name": "Zomato",                         "exchange": "NSE", "instrument_type": "Stock", "sector": "Internet"},
    {"symbol": "DMART.NS",      "name": "Avenue Supermarts (DMart)",      "exchange": "NSE", "instrument_type": "Stock", "sector": "Retail"},
    {"symbol": "PIDILITIND.NS", "name": "Pidilite Industries",            "exchange": "NSE", "instrument_type": "Stock", "sector": "Chemicals"},
    {"symbol": "SIEMENS.NS",    "name": "Siemens India",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Engineering"},
    {"symbol": "GODREJCP.NS",   "name": "Godrej Consumer Products",       "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "HAVELLS.NS",    "name": "Havells India",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Consumer Durables"},
    {"symbol": "DABUR.NS",      "name": "Dabur India",                    "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "MARICO.NS",     "name": "Marico",                         "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "BERGEPAINT.NS", "name": "Berger Paints",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Consumer Durables"},
    {"symbol": "COLPAL.NS",     "name": "Colgate Palmolive India",        "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "IRCTC.NS",      "name": "IRCTC",                          "exchange": "NSE", "instrument_type": "Stock", "sector": "Railways"},
    {"symbol": "POLYCAB.NS",    "name": "Polycab India",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Electricals"},
    {"symbol": "TATAELXSI.NS",  "name": "Tata Elxsi",                     "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "MUTHOOTFIN.NS", "name": "Muthoot Finance",                "exchange": "NSE", "instrument_type": "Stock", "sector": "Finance"},
    {"symbol": "PERSISTENT.NS", "name": "Persistent Systems",             "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "PAGEIND.NS",    "name": "Page Industries",                "exchange": "NSE", "instrument_type": "Stock", "sector": "Textiles"},
    {"symbol": "ASTRAL.NS",     "name": "Astral Limited",                 "exchange": "NSE", "instrument_type": "Stock", "sector": "Pipes"},
    {"symbol": "LICI.NS",       "name": "LIC of India",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "Insurance"},
    {"symbol": "PNB.NS",        "name": "Punjab National Bank",           "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "BANDHANBNK.NS", "name": "Bandhan Bank",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "NAUKRI.NS",     "name": "Info Edge (Naukri)",             "exchange": "NSE", "instrument_type": "Stock", "sector": "Internet"},
    {"symbol": "INDHOTEL.NS",   "name": "Indian Hotels (Taj)",            "exchange": "NSE", "instrument_type": "Stock", "sector": "Hospitality"},
    {"symbol": "BOSCHLTD.NS",   "name": "Bosch India",                    "exchange": "NSE", "instrument_type": "Stock", "sector": "Automobile"},
    {"symbol": "MOTHERSON.NS",  "name": "Samvardhana Motherson",          "exchange": "NSE", "instrument_type": "Stock", "sector": "Automobile"},
    {"symbol": "OFSS.NS",       "name": "Oracle Financial Services",      "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "MCDOWELL-N.NS", "name": "United Spirits (McDowell's)",    "exchange": "NSE", "instrument_type": "Stock", "sector": "Beverages"},
    {"symbol": "NYKAA.NS",      "name": "Nykaa (FSN E-Commerce)",         "exchange": "NSE", "instrument_type": "Stock", "sector": "Internet"},
    {"symbol": "PAYTM.NS",      "name": "Paytm (One97 Communications)",   "exchange": "NSE", "instrument_type": "Stock", "sector": "Fintech"},
    {"symbol": "POLICYBZR.NS",  "name": "PB Fintech (Policybazaar)",      "exchange": "NSE", "instrument_type": "Stock", "sector": "Fintech"},
    {"symbol": "ICICIGI.NS",    "name": "ICICI Lombard General Insurance","exchange": "NSE", "instrument_type": "Stock", "sector": "Insurance"},
    {"symbol": "PIIND.NS",      "name": "PI Industries",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Agrochemicals"},
    {"symbol": "LTIM.NS",       "name": "LTIMindtree",                    "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "COFORGE.NS",    "name": "Coforge",                        "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "MPHASIS.NS",    "name": "Mphasis",                        "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},

    # ── Banking & Finance ────────────────────────────────────────────
    {"symbol": "FEDERALBNK.NS", "name": "Federal Bank",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "IDFCFIRSTB.NS", "name": "IDFC First Bank",                "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "BANKBARODA.NS", "name": "Bank of Baroda",                 "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "CANBK.NS",      "name": "Canara Bank",                    "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "UNIONBANK.NS",  "name": "Union Bank of India",            "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "AUBANK.NS",     "name": "AU Small Finance Bank",          "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "RBLBANK.NS",    "name": "RBL Bank",                       "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "KARURVYSYA.NS", "name": "Karur Vysya Bank",               "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "CHOLAFIN.NS",   "name": "Cholamandalam Investment",       "exchange": "NSE", "instrument_type": "Stock", "sector": "Finance"},
    {"symbol": "MANAPPURAM.NS", "name": "Manappuram Finance",             "exchange": "NSE", "instrument_type": "Stock", "sector": "Finance"},
    {"symbol": "M&MFIN.NS",     "name": "M&M Financial Services",         "exchange": "NSE", "instrument_type": "Stock", "sector": "Finance"},
    {"symbol": "LICHSGFIN.NS",  "name": "LIC Housing Finance",            "exchange": "NSE", "instrument_type": "Stock", "sector": "Finance"},
    {"symbol": "POONAWALLA.NS", "name": "Poonawalla Fincorp",             "exchange": "NSE", "instrument_type": "Stock", "sector": "Finance"},
    {"symbol": "ABCAPITAL.NS",  "name": "Aditya Birla Capital",           "exchange": "NSE", "instrument_type": "Stock", "sector": "Finance"},
    {"symbol": "HDFCAMC.NS",    "name": "HDFC AMC",                       "exchange": "NSE", "instrument_type": "Stock", "sector": "Finance"},
    {"symbol": "NIPPONLTD.NS",  "name": "Nippon Life India Asset Mgmt",   "exchange": "NSE", "instrument_type": "Stock", "sector": "Finance"},

    # ── IT & Technology ──────────────────────────────────────────────
    {"symbol": "LTTS.NS",       "name": "L&T Technology Services",        "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "HEXAWARE.NS",   "name": "Hexaware Technologies",          "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "KPITTECH.NS",   "name": "KPIT Technologies",              "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "TANLA.NS",      "name": "Tanla Platforms",                "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "ROUTE.NS",      "name": "Route Mobile",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "BIRLASOFT.NS",  "name": "Birlasoft",                      "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "NEWGEN.NS",     "name": "Newgen Software",                "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "MASTEK.NS",     "name": "Mastek",                         "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "INTELLECT.NS",  "name": "Intellect Design Arena",         "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},

    # ── Pharma & Healthcare ──────────────────────────────────────────
    {"symbol": "LUPIN.NS",      "name": "Lupin",                          "exchange": "NSE", "instrument_type": "Stock", "sector": "Pharma"},
    {"symbol": "AUROPHARMA.NS", "name": "Aurobindo Pharma",               "exchange": "NSE", "instrument_type": "Stock", "sector": "Pharma"},
    {"symbol": "TORNTPHARM.NS", "name": "Torrent Pharmaceuticals",        "exchange": "NSE", "instrument_type": "Stock", "sector": "Pharma"},
    {"symbol": "ALKEM.NS",      "name": "Alkem Laboratories",             "exchange": "NSE", "instrument_type": "Stock", "sector": "Pharma"},
    {"symbol": "IPCALAB.NS",    "name": "IPCA Laboratories",              "exchange": "NSE", "instrument_type": "Stock", "sector": "Pharma"},
    {"symbol": "ABBOTINDIA.NS", "name": "Abbott India",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "Pharma"},
    {"symbol": "PFIZER.NS",     "name": "Pfizer India",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "Pharma"},
    {"symbol": "GLAXO.NS",      "name": "GSK Pharma India",               "exchange": "NSE", "instrument_type": "Stock", "sector": "Pharma"},
    {"symbol": "FORTIS.NS",     "name": "Fortis Healthcare",              "exchange": "NSE", "instrument_type": "Stock", "sector": "Healthcare"},
    {"symbol": "MAXHEALTH.NS",  "name": "Max Healthcare",                 "exchange": "NSE", "instrument_type": "Stock", "sector": "Healthcare"},
    {"symbol": "METROPOLIS.NS", "name": "Metropolis Healthcare",          "exchange": "NSE", "instrument_type": "Stock", "sector": "Healthcare"},
    {"symbol": "LALPATHLAB.NS", "name": "Dr Lal PathLabs",                "exchange": "NSE", "instrument_type": "Stock", "sector": "Healthcare"},
    {"symbol": "SYNGENE.NS",    "name": "Syngene International",          "exchange": "NSE", "instrument_type": "Stock", "sector": "Healthcare"},

    # ── Automobile & Auto Ancillaries ────────────────────────────────
    {"symbol": "ASHOKLEY.NS",   "name": "Ashok Leyland",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Automobile"},
    {"symbol": "TVSMOTOR.NS",   "name": "TVS Motor Company",              "exchange": "NSE", "instrument_type": "Stock", "sector": "Automobile"},
    {"symbol": "MINDA.NS",      "name": "Uno Minda",                      "exchange": "NSE", "instrument_type": "Stock", "sector": "Auto Ancillaries"},
    {"symbol": "BHARATFORG.NS", "name": "Bharat Forge",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "Auto Ancillaries"},
    {"symbol": "BALKRISIND.NS", "name": "Balkrishna Industries",          "exchange": "NSE", "instrument_type": "Stock", "sector": "Auto Ancillaries"},
    {"symbol": "CEATLTD.NS",    "name": "CEAT Tyres",                     "exchange": "NSE", "instrument_type": "Stock", "sector": "Auto Ancillaries"},
    {"symbol": "MRF.NS",        "name": "MRF",                            "exchange": "NSE", "instrument_type": "Stock", "sector": "Auto Ancillaries"},
    {"symbol": "APOLLOTYRE.NS", "name": "Apollo Tyres",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "Auto Ancillaries"},
    {"symbol": "EXIDEIND.NS",   "name": "Exide Industries",               "exchange": "NSE", "instrument_type": "Stock", "sector": "Auto Ancillaries"},

    # ── Energy & Utilities ───────────────────────────────────────────
    {"symbol": "ADANIGREEN.NS", "name": "Adani Green Energy",             "exchange": "NSE", "instrument_type": "Stock", "sector": "Power"},
    {"symbol": "ADANIPOWER.NS", "name": "Adani Power",                    "exchange": "NSE", "instrument_type": "Stock", "sector": "Power"},
    {"symbol": "TORNTPOWER.NS", "name": "Torrent Power",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Power"},
    {"symbol": "CESC.NS",       "name": "CESC Limited",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "Power"},
    {"symbol": "TATAPOWER.NS",  "name": "Tata Power",                     "exchange": "NSE", "instrument_type": "Stock", "sector": "Power"},
    {"symbol": "SJVN.NS",       "name": "SJVN Limited",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "Power"},
    {"symbol": "NHPC.NS",       "name": "NHPC Limited",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "Power"},
    {"symbol": "IOC.NS",        "name": "Indian Oil Corporation",         "exchange": "NSE", "instrument_type": "Stock", "sector": "Energy"},
    {"symbol": "HINDPETRO.NS",  "name": "Hindustan Petroleum",            "exchange": "NSE", "instrument_type": "Stock", "sector": "Energy"},
    {"symbol": "PETRONET.NS",   "name": "Petronet LNG",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "Energy"},
    {"symbol": "GAIL.NS",       "name": "GAIL India",                     "exchange": "NSE", "instrument_type": "Stock", "sector": "Energy"},
    {"symbol": "IGL.NS",        "name": "Indraprastha Gas",               "exchange": "NSE", "instrument_type": "Stock", "sector": "Energy"},
    {"symbol": "MGL.NS",        "name": "Mahanagar Gas",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Energy"},
    {"symbol": "ATGL.NS",       "name": "Adani Total Gas",                "exchange": "NSE", "instrument_type": "Stock", "sector": "Energy"},

    # ── Infrastructure & Construction ────────────────────────────────
    {"symbol": "IRCON.NS",      "name": "IRCON International",            "exchange": "NSE", "instrument_type": "Stock", "sector": "Infrastructure"},
    {"symbol": "RITES.NS",      "name": "RITES Limited",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Infrastructure"},
    {"symbol": "KEC.NS",        "name": "KEC International",              "exchange": "NSE", "instrument_type": "Stock", "sector": "Infrastructure"},
    {"symbol": "KALPATPOWR.NS", "name": "Kalpataru Power",                "exchange": "NSE", "instrument_type": "Stock", "sector": "Infrastructure"},
    {"symbol": "CUMMINSIND.NS", "name": "Cummins India",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Engineering"},
    {"symbol": "ABB.NS",        "name": "ABB India",                      "exchange": "NSE", "instrument_type": "Stock", "sector": "Engineering"},
    {"symbol": "BHEL.NS",       "name": "Bharat Heavy Electricals",       "exchange": "NSE", "instrument_type": "Stock", "sector": "Engineering"},
    {"symbol": "THERMAX.NS",    "name": "Thermax",                        "exchange": "NSE", "instrument_type": "Stock", "sector": "Engineering"},
    {"symbol": "GMRAIRPORT.NS", "name": "GMR Airports Infrastructure",    "exchange": "NSE", "instrument_type": "Stock", "sector": "Infrastructure"},
    {"symbol": "CONCOR.NS",     "name": "Container Corporation of India", "exchange": "NSE", "instrument_type": "Stock", "sector": "Logistics"},
    {"symbol": "BLUEDART.NS",   "name": "Blue Dart Express",              "exchange": "NSE", "instrument_type": "Stock", "sector": "Logistics"},
    {"symbol": "DELHIVERY.NS",  "name": "Delhivery",                      "exchange": "NSE", "instrument_type": "Stock", "sector": "Logistics"},

    # ── Metals & Mining ──────────────────────────────────────────────
    {"symbol": "HINDALCO.NS",   "name": "Hindalco Industries",            "exchange": "NSE", "instrument_type": "Stock", "sector": "Metals"},
    {"symbol": "VEDL.NS",       "name": "Vedanta Limited",                "exchange": "NSE", "instrument_type": "Stock", "sector": "Metals"},
    {"symbol": "NMDC.NS",       "name": "NMDC",                           "exchange": "NSE", "instrument_type": "Stock", "sector": "Mining"},
    {"symbol": "NATIONALUM.NS", "name": "National Aluminium (NALCO)",     "exchange": "NSE", "instrument_type": "Stock", "sector": "Metals"},
    {"symbol": "SAIL.NS",       "name": "Steel Authority of India",       "exchange": "NSE", "instrument_type": "Stock", "sector": "Metals"},
    {"symbol": "APLAPOLLO.NS",  "name": "APL Apollo Tubes",               "exchange": "NSE", "instrument_type": "Stock", "sector": "Metals"},

    # ── Cement & Building Materials ──────────────────────────────────
    {"symbol": "AMBUJACEM.NS",  "name": "Ambuja Cements",                 "exchange": "NSE", "instrument_type": "Stock", "sector": "Cement"},
    {"symbol": "ACC.NS",        "name": "ACC Limited",                    "exchange": "NSE", "instrument_type": "Stock", "sector": "Cement"},
    {"symbol": "SHREECEM.NS",   "name": "Shree Cement",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "Cement"},
    {"symbol": "JKCEMENT.NS",   "name": "JK Cement",                      "exchange": "NSE", "instrument_type": "Stock", "sector": "Cement"},
    {"symbol": "RAMCOCEM.NS",   "name": "Ramco Cements",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Cement"},
    {"symbol": "ORIENTCEM.NS",  "name": "Orient Cement",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Cement"},
    {"symbol": "SUPREMEIND.NS", "name": "Supreme Industries",             "exchange": "NSE", "instrument_type": "Stock", "sector": "Pipes"},

    # ── Consumer & Retail ────────────────────────────────────────────
    {"symbol": "JUBLFOOD.NS",   "name": "Jubilant Foodworks (Domino's)",  "exchange": "NSE", "instrument_type": "Stock", "sector": "Retail"},
    {"symbol": "DEVYANI.NS",    "name": "Devyani International (KFC/PH)", "exchange": "NSE", "instrument_type": "Stock", "sector": "Retail"},
    {"symbol": "SAPPHIRE.NS",   "name": "Sapphire Foods (KFC India)",     "exchange": "NSE", "instrument_type": "Stock", "sector": "Retail"},
    {"symbol": "SHOPERSTOP.NS", "name": "Shoppers Stop",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Retail"},
    {"symbol": "ABFRL.NS",      "name": "Aditya Birla Fashion & Retail",  "exchange": "NSE", "instrument_type": "Stock", "sector": "Retail"},
    {"symbol": "RAYMOND.NS",    "name": "Raymond",                        "exchange": "NSE", "instrument_type": "Stock", "sector": "Textiles"},
    {"symbol": "VARDHMAN.NS",   "name": "Vardhman Textiles",              "exchange": "NSE", "instrument_type": "Stock", "sector": "Textiles"},
    {"symbol": "VSTIND.NS",     "name": "VST Industries",                 "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "GODFRYPHLP.NS", "name": "Godfrey Phillips India",         "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},

    # ── Chemicals & Agrochemicals ────────────────────────────────────
    {"symbol": "SRF.NS",        "name": "SRF Limited",                    "exchange": "NSE", "instrument_type": "Stock", "sector": "Chemicals"},
    {"symbol": "DEEPAKNTR.NS",  "name": "Deepak Nitrite",                 "exchange": "NSE", "instrument_type": "Stock", "sector": "Chemicals"},
    {"symbol": "AAVAS.NS",      "name": "Aavas Financiers",               "exchange": "NSE", "instrument_type": "Stock", "sector": "Finance"},
    {"symbol": "NAVINFLUOR.NS", "name": "Navin Fluorine International",   "exchange": "NSE", "instrument_type": "Stock", "sector": "Chemicals"},
    {"symbol": "CLEAN.NS",      "name": "Clean Science and Technology",   "exchange": "NSE", "instrument_type": "Stock", "sector": "Chemicals"},
    {"symbol": "ATUL.NS",       "name": "Atul Limited",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "Chemicals"},
    {"symbol": "COROMANDEL.NS", "name": "Coromandel International",       "exchange": "NSE", "instrument_type": "Stock", "sector": "Agrochemicals"},
    {"symbol": "UPL.NS",        "name": "UPL Limited",                    "exchange": "NSE", "instrument_type": "Stock", "sector": "Agrochemicals"},
    {"symbol": "BAYER.NS",      "name": "Bayer CropScience India",        "exchange": "NSE", "instrument_type": "Stock", "sector": "Agrochemicals"},
    {"symbol": "SUMICHEM.NS",   "name": "Sumitomo Chemical India",        "exchange": "NSE", "instrument_type": "Stock", "sector": "Agrochemicals"},

    # ── Real Estate & REITs ──────────────────────────────────────────
    {"symbol": "DLF.NS",        "name": "DLF Limited",                    "exchange": "NSE", "instrument_type": "Stock", "sector": "Real Estate"},
    {"symbol": "GODREJPROP.NS", "name": "Godrej Properties",              "exchange": "NSE", "instrument_type": "Stock", "sector": "Real Estate"},
    {"symbol": "OBEROIRLTY.NS", "name": "Oberoi Realty",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Real Estate"},
    {"symbol": "PRESTIGE.NS",   "name": "Prestige Estates",               "exchange": "NSE", "instrument_type": "Stock", "sector": "Real Estate"},
    {"symbol": "BRIGADE.NS",    "name": "Brigade Enterprises",            "exchange": "NSE", "instrument_type": "Stock", "sector": "Real Estate"},
    {"symbol": "SOBHA.NS",      "name": "Sobha Limited",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Real Estate"},
    {"symbol": "MINDSPACE.NS",  "name": "Mindspace Business Parks REIT",  "exchange": "NSE", "instrument_type": "REIT",  "sector": "Real Estate"},
    {"symbol": "EMBASSY.NS",    "name": "Embassy Office Parks REIT",      "exchange": "NSE", "instrument_type": "REIT",  "sector": "Real Estate"},

    # ── Defence & Aerospace ──────────────────────────────────────────
    {"symbol": "COCHINSHIP.NS", "name": "Cochin Shipyard",                "exchange": "NSE", "instrument_type": "Stock", "sector": "Defence"},
    {"symbol": "MAZAGON.NS",    "name": "Mazagon Dock Shipbuilders",      "exchange": "NSE", "instrument_type": "Stock", "sector": "Defence"},
    {"symbol": "GRSE.NS",       "name": "Garden Reach Shipbuilders",      "exchange": "NSE", "instrument_type": "Stock", "sector": "Defence"},
    {"symbol": "PARAS.NS",      "name": "Paras Defence & Space Tech",     "exchange": "NSE", "instrument_type": "Stock", "sector": "Defence"},
    {"symbol": "APOLLOMICRO.NS","name": "Apollo Micro Systems",           "exchange": "NSE", "instrument_type": "Stock", "sector": "Defence"},
    {"symbol": "DATAPATTNS.NS", "name": "Data Patterns (India)",          "exchange": "NSE", "instrument_type": "Stock", "sector": "Defence"},

    # ── Media & Entertainment ────────────────────────────────────────
    {"symbol": "ZEEL.NS",       "name": "Zee Entertainment",              "exchange": "NSE", "instrument_type": "Stock", "sector": "Media"},
    {"symbol": "SUNTV.NS",      "name": "Sun TV Network",                 "exchange": "NSE", "instrument_type": "Stock", "sector": "Media"},
    {"symbol": "PVRINOX.NS",    "name": "PVR INOX",                       "exchange": "NSE", "instrument_type": "Stock", "sector": "Media"},
    {"symbol": "NETWORK18.NS",  "name": "Network18 Media",                "exchange": "NSE", "instrument_type": "Stock", "sector": "Media"},

    # ── Telecom ──────────────────────────────────────────────────────
    {"symbol": "IDEA.NS",       "name": "Vodafone Idea",                  "exchange": "NSE", "instrument_type": "Stock", "sector": "Telecom"},
    {"symbol": "INDUSTOWER.NS", "name": "Indus Towers",                   "exchange": "NSE", "instrument_type": "Stock", "sector": "Telecom"},
    {"symbol": "TTML.NS",       "name": "Tata Teleservices Maharashtra",  "exchange": "NSE", "instrument_type": "Stock", "sector": "Telecom"},

    # ── Hospitality & Travel ─────────────────────────────────────────
    {"symbol": "EIHOTEL.NS",    "name": "EIH (Oberoi Hotels)",            "exchange": "NSE", "instrument_type": "Stock", "sector": "Hospitality"},
    {"symbol": "LEMONTREE.NS",  "name": "Lemon Tree Hotels",              "exchange": "NSE", "instrument_type": "Stock", "sector": "Hospitality"},
    {"symbol": "INTERGLOBE.NS", "name": "InterGlobe Aviation (IndiGo)",   "exchange": "NSE", "instrument_type": "Stock", "sector": "Aviation"},
    {"symbol": "SPICEJET.NS",   "name": "SpiceJet",                       "exchange": "NSE", "instrument_type": "Stock", "sector": "Aviation"},

    # ── Specialty & Miscellaneous ────────────────────────────────────
    {"symbol": "DIXON.NS",      "name": "Dixon Technologies",             "exchange": "NSE", "instrument_type": "Stock", "sector": "Electronics"},
    {"symbol": "AMBER.NS",      "name": "Amber Enterprises",              "exchange": "NSE", "instrument_type": "Stock", "sector": "Electronics"},
    {"symbol": "KAYNES.NS",     "name": "Kaynes Technology",              "exchange": "NSE", "instrument_type": "Stock", "sector": "Electronics"},
    {"symbol": "SYRMA.NS",      "name": "Syrma SGS Technology",           "exchange": "NSE", "instrument_type": "Stock", "sector": "Electronics"},
    {"symbol": "CDSL.NS",       "name": "CDSL",                           "exchange": "NSE", "instrument_type": "Stock", "sector": "Capital Markets"},
    {"symbol": "BSE.NS",        "name": "BSE Limited",                    "exchange": "NSE", "instrument_type": "Stock", "sector": "Capital Markets"},
    {"symbol": "MCX.NS",        "name": "Multi Commodity Exchange",       "exchange": "NSE", "instrument_type": "Stock", "sector": "Capital Markets"},
    {"symbol": "ANGEL.NS",      "name": "Angel One",                      "exchange": "NSE", "instrument_type": "Stock", "sector": "Capital Markets"},
    {"symbol": "ICICIPRULI.NS", "name": "ICICI Prudential Life Insurance","exchange": "NSE", "instrument_type": "Stock", "sector": "Insurance"},
    {"symbol": "STARHEALTH.NS", "name": "Star Health Insurance",          "exchange": "NSE", "instrument_type": "Stock", "sector": "Insurance"},
    {"symbol": "GICRE.NS",      "name": "General Insurance Corp (GIC Re)","exchange": "NSE", "instrument_type": "Stock", "sector": "Insurance"},
    {"symbol": "NIACL.NS",      "name": "New India Assurance",            "exchange": "NSE", "instrument_type": "Stock", "sector": "Insurance"},
    {"symbol": "FINPIPE.NS",    "name": "Finolex Industries",             "exchange": "NSE", "instrument_type": "Stock", "sector": "Pipes"},
    {"symbol": "JINDALSAW.NS",  "name": "Jindal Saw",                     "exchange": "NSE", "instrument_type": "Stock", "sector": "Metals"},
    {"symbol": "JINDALSTEL.NS", "name": "Jindal Steel & Power",           "exchange": "NSE", "instrument_type": "Stock", "sector": "Metals"},
    {"symbol": "WELSPUNLIV.NS", "name": "Welspun Living",                 "exchange": "NSE", "instrument_type": "Stock", "sector": "Textiles"},
    {"symbol": "TRIDENT.NS",    "name": "Trident Limited",                "exchange": "NSE", "instrument_type": "Stock", "sector": "Textiles"},

    # ── ETFs ─────────────────────────────────────────────────────────
    {"symbol": "GOLDBEES.NS",   "name": "Nippon India ETF Gold BeES",     "exchange": "NSE", "instrument_type": "ETF", "sector": "Commodity - Gold"},
    {"symbol": "SILVERBEES.NS", "name": "Nippon India Silver ETF",        "exchange": "NSE", "instrument_type": "ETF", "sector": "Commodity - Silver"},
    {"symbol": "NIFTYBEES.NS",  "name": "Nippon India Nifty BeES",        "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - NIFTY 50"},
    {"symbol": "BANKBEES.NS",   "name": "Nippon India Bank BeES",         "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Bank Nifty"},
    {"symbol": "SETFGOLD.NS",   "name": "SBI Gold ETF",                   "exchange": "NSE", "instrument_type": "ETF", "sector": "Commodity - Gold"},
    {"symbol": "JUNIORBEES.NS", "name": "Nippon India Junior BeES",       "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Nifty Next 50"},
    {"symbol": "CPSEETF.NS",    "name": "Nippon India CPSE ETF",          "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - PSU"},
    {"symbol": "ITBEES.NS",     "name": "Nippon India IT ETF",            "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Nifty IT"},
    {"symbol": "ICICIB22.NS",   "name": "ICICI Pru Bharat 22 ETF",        "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Bharat 22"},
    {"symbol": "MOM50.NS",      "name": "Motilal Oswal NIFTY 50 ETF",     "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - NIFTY 50"},
    {"symbol": "MAFANG.NS",     "name": "Mirae Asset NYSE FANG+ ETF",     "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Global Tech"},
    {"symbol": "N100.NS",       "name": "Nippon India Nasdaq 100 ETF",    "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Nasdaq 100"},
    {"symbol": "HANGSENG.NS",   "name": "Mirae Asset Hang Seng Tech ETF", "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Hang Seng"},
    {"symbol": "MIDSMALL.NS",   "name": "Nippon India Nifty Midcap 150",  "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Midcap"},
    {"symbol": "PSUBNKBEES.NS", "name": "Nippon India PSU Bank BeES",     "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - PSU Bank"},
    {"symbol": "NETFIT.NS",     "name": "Nippon India Nifty IT ETF",      "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Nifty IT"},
    {"symbol": "MOM100.NS",     "name": "Motilal Oswal Midcap 100 ETF",   "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Midcap"},
    {"symbol": "CONSUMPTION.NS","name": "Nippon India Consumption ETF",   "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Consumption"},
    {"symbol": "PHARMABEES.NS", "name": "Nippon India Pharma ETF",        "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Pharma"},

    # ── Indices (benchmarks) ─────────────────────────────────────────
    {"symbol": "^NSEI",  "name": "NIFTY 50 Index",  "exchange": "NSE", "instrument_type": "Index", "sector": "Broad Market"},
    {"symbol": "^BSESN", "name": "S&P BSE SENSEX",  "exchange": "BSE", "instrument_type": "Index", "sector": "Broad Market"},
    {"symbol": "^NSMIDCP","name":"NIFTY Midcap 50", "exchange": "NSE", "instrument_type": "Index", "sector": "Mid Cap"},
]


def _deduplicate_catalog() -> list[dict]:
    """Remove duplicates by symbol, keeping the first occurrence."""
    seen = set()
    unique = []
    for item in INSTRUMENT_CATALOG:
        if item["symbol"] not in seen:
            seen.add(item["symbol"])
            unique.append(item)
    return unique


_UNIQUE_CATALOG = _deduplicate_catalog()


def search_instruments(query: str, limit: int = 20) -> list[InstrumentInfo]:
    """
    Search the catalog by fuzzy-matching against symbol, name, and sector.
    Returns up to `limit` results, ordered by relevance.
    """
    q = query.lower().strip()
    if not q:
        return []

    scored: list[tuple[int, dict]] = []
    for item in _UNIQUE_CATALOG:
        score = 0
        symbol_lower = item["symbol"].lower().replace(".ns", "").replace(".bo", "")
        name_lower   = item["name"].lower()
        sector_lower = (item.get("sector") or "").lower()
        itype_lower  = item["instrument_type"].lower()

        if q == symbol_lower:           score = 100
        elif symbol_lower.startswith(q):score = 80
        elif q in symbol_lower:         score = 60
        elif name_lower.startswith(q):  score = 50
        elif q in name_lower:           score = 40
        elif q in sector_lower:         score = 30
        elif q in itype_lower:          score = 25

        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: (-x[0], x[1]["name"]))
    return [InstrumentInfo(**item) for _, item in scored[:limit]]


def get_popular_instruments(limit: int = 20) -> list[InstrumentInfo]:
    """Return a curated list of popular instruments for the quick-pick section."""
    popular_symbols = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
        "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "LT.NS", "TATAMOTORS.NS",
        "ZOMATO.NS", "ADANIENT.NS", "HAL.NS", "BEL.NS", "BAJFINANCE.NS",
        "GOLDBEES.NS", "NIFTYBEES.NS", "SILVERBEES.NS", "BANKBEES.NS", "N100.NS",
    ]
    sym_set = set(popular_symbols)
    return [
        InstrumentInfo(**item)
        for item in _UNIQUE_CATALOG
        if item["symbol"] in sym_set
    ][:limit]


def get_instrument_name(symbol: str) -> str:
    """Look up the display name for a symbol. Returns the symbol itself if not found."""
    for item in _UNIQUE_CATALOG:
        if item["symbol"] == symbol:
            return item["name"]
    return symbol


# ── Sector ordering for UI display ──────────────────────────────────

SECTOR_ORDER = [
    "Banking", "Finance", "Insurance", "Capital Markets", "Fintech",
    "IT", "Electronics",
    "FMCG", "Retail", "Beverages", "Textiles",
    "Pharma", "Healthcare",
    "Automobile", "Auto Ancillaries",
    "Energy", "Power",
    "Infrastructure", "Logistics", "Engineering",
    "Metals", "Mining", "Cement", "Pipes",
    "Chemicals", "Agrochemicals",
    "Real Estate",
    "Telecom",
    "Media", "Hospitality", "Aviation",
    "Defence",
    "Diversified", "Railways",
    "Electricals", "Consumer Durables",
    "Internet",
    "ETFs", "Indices",
]


def get_instruments_by_sector() -> dict[str, list[dict]]:
    """
    Group all instruments by sector.
    ETFs, REITs, and Indices are grouped into their own meta-sectors.
    Returns an ordered dict of sector → list of instruments.
    """
    grouped: dict[str, list[dict]] = {}

    for item in _UNIQUE_CATALOG:
        itype = item["instrument_type"]
        if itype == "ETF":
            sector_key = "ETFs"
        elif itype == "Index":
            sector_key = "Indices"
        elif itype == "REIT":
            sector_key = "Real Estate"
        else:
            sector_key = item.get("sector") or "Other"

        grouped.setdefault(sector_key, []).append(item)

    order_map = {s: i for i, s in enumerate(SECTOR_ORDER)}
    return dict(sorted(grouped.items(), key=lambda kv: order_map.get(kv[0], 999)))
