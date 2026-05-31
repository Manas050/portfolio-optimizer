"""
Curated catalog of popular Indian market instruments available on Yahoo Finance.
Provides search functionality across stocks, ETFs, and indices.
"""

from app.schemas import InstrumentInfo


# ── NIFTY 50 Constituents + Popular Stocks ──────────────────────────

INSTRUMENT_CATALOG: list[dict] = [
    # ── Large Cap Stocks (NIFTY 50) ─────────────────────────────────
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "exchange": "NSE", "instrument_type": "Stock", "sector": "Energy"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "INFY.NS", "name": "Infosys", "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever", "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "SBIN.NS", "name": "State Bank of India", "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel", "exchange": "NSE", "instrument_type": "Stock", "sector": "Telecom"},
    {"symbol": "ITC.NS", "name": "ITC Limited", "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "LT.NS", "name": "Larsen & Toubro", "exchange": "NSE", "instrument_type": "Stock", "sector": "Infrastructure"},
    {"symbol": "AXISBANK.NS", "name": "Axis Bank", "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "WIPRO.NS", "name": "Wipro", "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies", "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "ASIANPAINT.NS", "name": "Asian Paints", "exchange": "NSE", "instrument_type": "Stock", "sector": "Consumer Durables"},
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki", "exchange": "NSE", "instrument_type": "Stock", "sector": "Automobile"},
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharma", "exchange": "NSE", "instrument_type": "Stock", "sector": "Pharma"},
    {"symbol": "TATAMOTORS.NS", "name": "Tata Motors", "exchange": "NSE", "instrument_type": "Stock", "sector": "Automobile"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance", "exchange": "NSE", "instrument_type": "Stock", "sector": "Finance"},
    {"symbol": "TATASTEEL.NS", "name": "Tata Steel", "exchange": "NSE", "instrument_type": "Stock", "sector": "Metals"},
    {"symbol": "NTPC.NS", "name": "NTPC Limited", "exchange": "NSE", "instrument_type": "Stock", "sector": "Power"},
    {"symbol": "POWERGRID.NS", "name": "Power Grid Corp", "exchange": "NSE", "instrument_type": "Stock", "sector": "Power"},
    {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement", "exchange": "NSE", "instrument_type": "Stock", "sector": "Cement"},
    {"symbol": "TITAN.NS", "name": "Titan Company", "exchange": "NSE", "instrument_type": "Stock", "sector": "Consumer Durables"},
    {"symbol": "NESTLEIND.NS", "name": "Nestle India", "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "TECHM.NS", "name": "Tech Mahindra", "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "M&M.NS", "name": "Mahindra & Mahindra", "exchange": "NSE", "instrument_type": "Stock", "sector": "Automobile"},
    {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv", "exchange": "NSE", "instrument_type": "Stock", "sector": "Finance"},
    {"symbol": "ADANIENT.NS", "name": "Adani Enterprises", "exchange": "NSE", "instrument_type": "Stock", "sector": "Diversified"},
    {"symbol": "ADANIPORTS.NS", "name": "Adani Ports", "exchange": "NSE", "instrument_type": "Stock", "sector": "Infrastructure"},
    {"symbol": "ONGC.NS", "name": "Oil & Natural Gas Corp", "exchange": "NSE", "instrument_type": "Stock", "sector": "Energy"},
    {"symbol": "JSWSTEEL.NS", "name": "JSW Steel", "exchange": "NSE", "instrument_type": "Stock", "sector": "Metals"},
    {"symbol": "COALINDIA.NS", "name": "Coal India", "exchange": "NSE", "instrument_type": "Stock", "sector": "Mining"},
    {"symbol": "BPCL.NS", "name": "Bharat Petroleum", "exchange": "NSE", "instrument_type": "Stock", "sector": "Energy"},
    {"symbol": "DRREDDY.NS", "name": "Dr Reddy's Laboratories", "exchange": "NSE", "instrument_type": "Stock", "sector": "Pharma"},
    {"symbol": "CIPLA.NS", "name": "Cipla", "exchange": "NSE", "instrument_type": "Stock", "sector": "Pharma"},
    {"symbol": "EICHERMOT.NS", "name": "Eicher Motors", "exchange": "NSE", "instrument_type": "Stock", "sector": "Automobile"},
    {"symbol": "GRASIM.NS", "name": "Grasim Industries", "exchange": "NSE", "instrument_type": "Stock", "sector": "Cement"},
    {"symbol": "DIVISLAB.NS", "name": "Divi's Laboratories", "exchange": "NSE", "instrument_type": "Stock", "sector": "Pharma"},
    {"symbol": "BRITANNIA.NS", "name": "Britannia Industries", "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "HEROMOTOCO.NS", "name": "Hero MotoCorp", "exchange": "NSE", "instrument_type": "Stock", "sector": "Automobile"},
    {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank", "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},
    {"symbol": "APOLLOHOSP.NS", "name": "Apollo Hospitals", "exchange": "NSE", "instrument_type": "Stock", "sector": "Healthcare"},
    {"symbol": "TATACONSUM.NS", "name": "Tata Consumer Products", "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "SBILIFE.NS", "name": "SBI Life Insurance", "exchange": "NSE", "instrument_type": "Stock", "sector": "Insurance"},
    {"symbol": "HDFCLIFE.NS", "name": "HDFC Life Insurance", "exchange": "NSE", "instrument_type": "Stock", "sector": "Insurance"},
    {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto", "exchange": "NSE", "instrument_type": "Stock", "sector": "Automobile"},
    {"symbol": "WIPRO.NS", "name": "Wipro Limited", "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "BEL.NS", "name": "Bharat Electronics", "exchange": "NSE", "instrument_type": "Stock", "sector": "Defence"},
    {"symbol": "HAL.NS", "name": "Hindustan Aeronautics", "exchange": "NSE", "instrument_type": "Stock", "sector": "Defence"},

    # ── Mid Cap Stocks ──────────────────────────────────────────────
    {"symbol": "TRENT.NS", "name": "Trent Limited", "exchange": "NSE", "instrument_type": "Stock", "sector": "Retail"},
    {"symbol": "ZOMATO.NS", "name": "Zomato", "exchange": "NSE", "instrument_type": "Stock", "sector": "Internet"},
    {"symbol": "DMART.NS", "name": "Avenue Supermarts (DMart)", "exchange": "NSE", "instrument_type": "Stock", "sector": "Retail"},
    {"symbol": "PIDILITIND.NS", "name": "Pidilite Industries", "exchange": "NSE", "instrument_type": "Stock", "sector": "Chemicals"},
    {"symbol": "SIEMENS.NS", "name": "Siemens India", "exchange": "NSE", "instrument_type": "Stock", "sector": "Engineering"},
    {"symbol": "GODREJCP.NS", "name": "Godrej Consumer Products", "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "HAVELLS.NS", "name": "Havells India", "exchange": "NSE", "instrument_type": "Stock", "sector": "Consumer Durables"},
    {"symbol": "DABUR.NS", "name": "Dabur India", "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "MARICO.NS", "name": "Marico", "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "BERGEPAINT.NS", "name": "Berger Paints", "exchange": "NSE", "instrument_type": "Stock", "sector": "Consumer Durables"},
    {"symbol": "COLPAL.NS", "name": "Colgate Palmolive India", "exchange": "NSE", "instrument_type": "Stock", "sector": "FMCG"},
    {"symbol": "IRCTC.NS", "name": "IRCTC", "exchange": "NSE", "instrument_type": "Stock", "sector": "Railways"},
    {"symbol": "POLYCAB.NS", "name": "Polycab India", "exchange": "NSE", "instrument_type": "Stock", "sector": "Electricals"},
    {"symbol": "TATAELXSI.NS", "name": "Tata Elxsi", "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "MUTHOOTFIN.NS", "name": "Muthoot Finance", "exchange": "NSE", "instrument_type": "Stock", "sector": "Finance"},
    {"symbol": "PERSISTENT.NS", "name": "Persistent Systems", "exchange": "NSE", "instrument_type": "Stock", "sector": "IT"},
    {"symbol": "PAGEIND.NS", "name": "Page Industries", "exchange": "NSE", "instrument_type": "Stock", "sector": "Textiles"},
    {"symbol": "ASTRAL.NS", "name": "Astral Limited", "exchange": "NSE", "instrument_type": "Stock", "sector": "Pipes"},
    {"symbol": "LICI.NS", "name": "LIC of India", "exchange": "NSE", "instrument_type": "Stock", "sector": "Insurance"},
    {"symbol": "PNB.NS", "name": "Punjab National Bank", "exchange": "NSE", "instrument_type": "Stock", "sector": "Banking"},

    # ── ETFs ────────────────────────────────────────────────────────
    {"symbol": "GOLDBEES.NS", "name": "Nippon India ETF Gold BeES", "exchange": "NSE", "instrument_type": "ETF", "sector": "Commodity - Gold"},
    {"symbol": "SILVERBEES.NS", "name": "Nippon India Silver ETF", "exchange": "NSE", "instrument_type": "ETF", "sector": "Commodity - Silver"},
    {"symbol": "NIFTYBEES.NS", "name": "Nippon India Nifty BeES", "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - NIFTY 50"},
    {"symbol": "BANKBEES.NS", "name": "Nippon India Bank BeES", "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Bank Nifty"},
    {"symbol": "SETFGOLD.NS", "name": "SBI Gold ETF", "exchange": "NSE", "instrument_type": "ETF", "sector": "Commodity - Gold"},
    {"symbol": "GOLDIETF.NS", "name": "ICICI Prudential Gold ETF", "exchange": "NSE", "instrument_type": "ETF", "sector": "Commodity - Gold"},
    {"symbol": "JUNIORBEES.NS", "name": "Nippon India Junior BeES", "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Nifty Next 50"},
    {"symbol": "CPSEETF.NS", "name": "Nippon India CPSE ETF", "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - PSU"},
    {"symbol": "ITBEES.NS", "name": "Nippon India IT ETF", "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Nifty IT"},
    {"symbol": "LIQUIDBEES.NS", "name": "Nippon India Liquid BeES", "exchange": "NSE", "instrument_type": "ETF", "sector": "Liquid / Money Market"},
    {"symbol": "ICICIB22.NS", "name": "ICICI Pru Bharat 22 ETF", "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Bharat 22"},
    {"symbol": "NETFIT.NS", "name": "Nippon India Nifty IT ETF", "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - Nifty IT"},
    {"symbol": "MOM50.NS", "name": "Motilal Oswal NIFTY 50 ETF", "exchange": "NSE", "instrument_type": "ETF", "sector": "Index - NIFTY 50"},

    # ── Indices (for reference / benchmarking) ──────────────────────
    {"symbol": "^NSEI", "name": "NIFTY 50 Index", "exchange": "NSE", "instrument_type": "Index", "sector": "Broad Market"},
    {"symbol": "^BSESN", "name": "S&P BSE SENSEX", "exchange": "BSE", "instrument_type": "Index", "sector": "Broad Market"},
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
        name_lower = item["name"].lower()
        sector_lower = (item.get("sector") or "").lower()
        itype_lower = item["instrument_type"].lower()

        # Exact symbol match (highest priority)
        if q == symbol_lower:
            score = 100
        # Symbol starts with query
        elif symbol_lower.startswith(q):
            score = 80
        # Symbol contains query
        elif q in symbol_lower:
            score = 60
        # Name starts with query
        elif name_lower.startswith(q):
            score = 50
        # Name contains query
        elif q in name_lower:
            score = 40
        # Sector match
        elif q in sector_lower:
            score = 30
        # Instrument type match
        elif q in itype_lower:
            score = 25

        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: (-x[0], x[1]["name"]))
    return [InstrumentInfo(**item) for _, item in scored[:limit]]


def get_popular_instruments(limit: int = 15) -> list[InstrumentInfo]:
    """Return a curated list of popular instruments for the quick-pick section."""
    popular_symbols = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
        "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "LT.NS", "TATAMOTORS.NS",
        "GOLDBEES.NS", "NIFTYBEES.NS", "SILVERBEES.NS", "BANKBEES.NS",
        "BAJFINANCE.NS",
    ]
    symbol_set = set(popular_symbols)
    return [
        InstrumentInfo(**item)
        for item in _UNIQUE_CATALOG
        if item["symbol"] in symbol_set
    ][:limit]


def get_instrument_name(symbol: str) -> str:
    """Look up the display name for a symbol. Returns symbol itself if not found."""
    for item in _UNIQUE_CATALOG:
        if item["symbol"] == symbol:
            return item["name"]
    return symbol


# Sector display order for the UI
SECTOR_ORDER = [
    "Banking", "IT", "FMCG", "Pharma", "Automobile", "Energy",
    "Finance", "Metals", "Infrastructure", "Power", "Telecom",
    "Consumer Durables", "Cement", "Insurance", "Defence",
    "Healthcare", "Diversified", "Mining", "Retail", "Internet",
    "Chemicals", "Engineering", "Electricals", "Railways", "Textiles", "Pipes",
    "ETFs", "Indices",
]


def get_instruments_by_sector() -> dict[str, list[dict]]:
    """
    Group all instruments by sector.
    ETFs and Indices are grouped into their own meta-sectors.
    Returns an ordered dict of sector -> list of instruments.
    """
    grouped: dict[str, list[dict]] = {}

    for item in _UNIQUE_CATALOG:
        itype = item["instrument_type"]
        if itype == "ETF":
            sector_key = "ETFs"
        elif itype == "Index":
            sector_key = "Indices"
        else:
            sector_key = item.get("sector") or "Other"

        if sector_key not in grouped:
            grouped[sector_key] = []
        grouped[sector_key].append(item)

    # Sort by SECTOR_ORDER, unknowns at the end
    order_map = {s: i for i, s in enumerate(SECTOR_ORDER)}
    sorted_grouped = dict(
        sorted(grouped.items(), key=lambda kv: order_map.get(kv[0], 999))
    )
    return sorted_grouped

