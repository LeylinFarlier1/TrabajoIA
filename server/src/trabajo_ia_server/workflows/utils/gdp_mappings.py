"""
GDP Mappings - Series IDs for 238 countries/territories.

Maps country codes to FRED/World Bank series IDs for different GDP variants.
Based on FRED series patterns and World Bank availability (1960-2024).
"""
from typing import Dict, List, Optional

# ============================================================================
# GDP SERIES PATTERNS (FRED)
# ============================================================================
# Most series follow consistent patterns with 3-letter country codes:
# - Nominal USD: NYGDPMKTPCD{country} or MKTGDP{country}646NWDB
# - Constant 2010: NYGDPMKTPKD{country}
# - Per Capita Constant: NYGDPPCAPKD{country}
# - Per Capita PPP: NYGDPPCAPPPKD{country}
# - Population: POPTOT{country}647NWDB

# ============================================================================
# GDP_MAPPINGS: Complete 238 countries/territories
# ============================================================================

GDP_MAPPINGS: Dict[str, Dict[str, str]] = {
    # === G7 Countries ===
    "usa": {
        "nominal_usd": "GDPA",  # Annual GDP, Billions of Dollars
        "nominal_lcu": "GDPA",  # Same as nominal_usd for USA
        "constant_2010": "GDPCA",  # Real GDP, Billions of Chained 2017 Dollars
        "per_capita_nominal": "A939RC0A052NBEA",  # Per capita GDP (BEA)
        "per_capita_constant": None,  # Computed from GDPCA / population
        "per_capita_ppp": None,  # Not needed for USA
        "ppp_adjusted": None,  # Not needed for USA
        "population": "POPTHM"  # Population (Thousands)
    },
    "canada": {
        "nominal_usd": "MKTGDPCAA646NWDB",  # Verified: Annual, Current USD
        "constant_2010": None,  # Compute from nominal
        "per_capita_constant": "NYGDPPCAPKDCAN",
        "per_capita_ppp": None,
        "ppp_adjusted": None,
        "population": "POPTOTCAA647NWDB"
    },
    "uk": {
        "nominal_usd": "MKTGDPGBA646NWDB",  # Verified: GBA = United Kingdom
        "constant_2010": None,
        "per_capita_constant": "NYGDPPCAPKDGBR",
        "per_capita_ppp": None,
        "ppp_adjusted": None,
        "population": "POPTOTGBA647NWDB"
    },
    "germany": {
        "nominal_usd": "MKTGDPDEA646NWDB",  # Verified: DEA = Germany
        "constant_2010": None,
        "per_capita_constant": "NYGDPPCAPKDDEU",
        "per_capita_ppp": None,
        "ppp_adjusted": None,
        "population": "POPTOTDEA647NWDB"
    },
    "france": {
        "nominal_usd": "MKTGDPFRA646NWDB",  # Verified: FRA = France
        "constant_2010": None,
        "per_capita_constant": "NYGDPPCAPKDFRA",
        "per_capita_ppp": None,
        "ppp_adjusted": None,
        "population": "POPTOTFRA647NWDB"
    },
    "italy": {
        "nominal_usd": "MKTGDPITA646NWDB",  # Verified: ITA = Italy
        "constant_2010": "NYGDPMKTPKDITA",
        "per_capita_constant": "NYGDPPCAPKDITA",
        "per_capita_ppp": "NYGDPPCAPPPKDITA",
        "ppp_adjusted": "PPPGDPITA",
        "population": "POPTOTITA647NWDB"
    },
    "japan": {
        "nominal_usd": "MKTGDPJPA646NWDB",  # Verified: JPA = Japan
        "constant_2010": None,
        "per_capita_constant": "NYGDPPCAPKDJPN",
        "per_capita_ppp": None,
        "ppp_adjusted": None,
        "population": "POPTOTJPA647NWDB"
    },
    
    # === BRICS ===
    "brazil": {
        "nominal_usd": "MKTGDPBRAA646NWDB",
        "constant_2010": None,
        "per_capita_constant": "NYGDPPCAPKDBRA",
        "per_capita_ppp": None,
        "ppp_adjusted": None,
        "population": "POPTOTBRAA647NWDB"
    },
    "russia": {
        "nominal_usd": "MKTGDPRUSA646NWDB",
        "constant_2010": None,
        "per_capita_constant": "NYGDPPCAPKDRUS",
        "per_capita_ppp": None,
        "ppp_adjusted": None,
        "population": "POPTOTRUSA647NWDB"
    },
    "india": {
        "nominal_usd": "MKTGDPINDA646NWDB",
        "constant_2010": None,
        "per_capita_constant": "NYGDPPCAPKDIND",
        "per_capita_ppp": None,
        "ppp_adjusted": None,
        "population": "POPTOTINDA647NWDB"
    },
    "china": {
        "nominal_usd": "MKTGDPCNA646NWDB",
        "constant_2010": None,
        "per_capita_constant": "NYGDPPCAPKDCHN",
        "per_capita_ppp": None,
        "ppp_adjusted": None,
        "population": "POPTOTCNAA647NWDB"
    },
    "south_africa": {
        "nominal_usd": "MKTGDPZAFA646NWDB",
        "constant_2010": None,
        "per_capita_constant": "NYGDPPCAPKDZAF",
        "per_capita_ppp": None,
        "ppp_adjusted": None,
        "population": "POPTOTZAFA647NWDB"
    },
    "india": {
        "nominal_usd": "MKTGDPIND646NWDB",
        "constant_2010": "NYGDPMKTPKDIND",
        "per_capita_constant": "NYGDPPCAPKDIND",
        "per_capita_ppp": "NYGDPPCAPPPKDIND",
        "ppp_adjusted": "PPPGDPIND",
        "population": "POPTOTIND647NWDB"
    },
    "china": {
        "nominal_usd": "MKTGDPCHN646NWDB",
        "constant_2010": "NYGDPMKTPKDCHN",
        "per_capita_constant": "NYGDPPCAPKDCHN",
        "per_capita_ppp": "NYGDPPCAPPPKDCHN",
        "ppp_adjusted": "PPPGDPCHN",
        "population": "POPTOTCHN647NWDB"
    },
    "south_africa": {
        "nominal_usd": "MKTGDPZAF646NWDB",
        "constant_2010": "NYGDPMKTPKDZAF",
        "per_capita_constant": "NYGDPPCAPKDZAF",
        "per_capita_ppp": "NYGDPPCAPPPKDZAF",
        "ppp_adjusted": "PPPGDPZAF",
        "population": "POTOTZAF647NWDB"
    },
    
    # === Latin America ===
    "argentina": {
        "nominal_usd": "MKTGDPARA646NWDB",
        "constant_2010": "NYGDPMKTPKDARG",
        "per_capita_constant": "NYGDPPCAPKDARG",
        "per_capita_ppp": "NYGDPPCAPPPKDARG",
        "ppp_adjusted": "PPPGDPARG",
        "population": "POPTOTARA647NWDB"
    },
    "mexico": {
        "nominal_usd": "MKTGDPMXA646NWDB",
        "constant_2010": "NYGDPMKTPKDMEX",
        "per_capita_constant": "NYGDPPCAPKDMEX",
        "per_capita_ppp": "NYGDPPCAPPPKDMEX",
        "ppp_adjusted": "PPPGDPMEX",
        "population": "POPTOTMXA647NWDB"
    },
    "chile": {
        "nominal_usd": "MKTGDPCHL646NWDB",
        "constant_2010": "NYGDPMKTPKDCHL",
        "per_capita_constant": "NYGDPPCAPKDCHL",
        "per_capita_ppp": "NYGDPPCAPPPKDCHL",
        "ppp_adjusted": "PPPGDPCHL",
        "population": "POPTOTCHL647NWDB"
    },
    "colombia": {
        "nominal_usd": "MKTGDPCOL646NWDB",
        "constant_2010": "NYGDPMKTPKDCOL",
        "per_capita_constant": "NYGDPPCAPKDCOL",
        "per_capita_ppp": "NYGDPPCAPPPKDCOL",
        "ppp_adjusted": "PPPGDPCOL",
        "population": "POPTOTCOL647NWDB"
    },
    "peru": {
        "nominal_usd": "MKTGDPPER646NWDB",
        "constant_2010": "NYGDPMKTPKDPER",
        "per_capita_constant": "NYGDPPCAPKDPER",
        "per_capita_ppp": "NYGDPPCAPPPKDPER",
        "ppp_adjusted": "PPPGDPPER",
        "population": "POPTOTPER647NWDB"
    },
    "uruguay": {
        "nominal_usd": "MKTGDPURY646NWDB",
        "constant_2010": "NYGDPMKTPKDURY",
        "per_capita_constant": "NYGDPPCAPKDURY",
        "per_capita_ppp": "NYGDPPCAPPPKDURY",
        "ppp_adjusted": "PPPGDPURY",
        "population": "POPTOTURY647NWDB"
    },
    "venezuela": {
        "nominal_usd": "MKTGDPVEN646NWDB",
        "constant_2010": "NYGDPMKTPKDVEN",
        "per_capita_constant": "NYGDPPCAPKDVEN",
        "per_capita_ppp": "NYGDPPCAPPPKDVEN",
        "ppp_adjusted": "PPPGDPVEN",
        "population": "POPTOTVEN647NWDB"
    },
    "bolivia": {
        "nominal_usd": "MKTGDPBOL646NWDB",
        "constant_2010": "NYGDPMKTPKDBOL",
        "per_capita_constant": "NYGDPPCAPKDBOL",
        "per_capita_ppp": "NYGDPPCAPPPKDBOL",
        "population": "POPTOTBOL647NWDB"
    },
    "ecuador": {
        "nominal_usd": "MKTGDPECU646NWDB",
        "constant_2010": "NYGDPMKTPKDECU",
        "per_capita_constant": "NYGDPPCAPKDECU",
        "per_capita_ppp": "NYGDPPCAPPPKDECU",
        "population": "POPTOTECU647NWDB"
    },
    "paraguay": {
        "nominal_usd": "MKTGDPPRY646NWDB",
        "constant_2010": "NYGDPMKTPKDPRY",
        "per_capita_constant": "NYGDPPCAPKDPRY",
        "per_capita_ppp": "NYGDPPCAPPPKDPRY",
        "population": "POPTOTPRY647NWDB"
    },
    
    # === Asia-Pacific (Major Economies) ===
    "south_korea": {
        "nominal_usd": "MKTGDPKOR646NWDB",
        "constant_2010": "NYGDPMKTPKDKOR",
        "per_capita_constant": "NYGDPPCAPKDKOR",
        "per_capita_ppp": "NYGDPPCAPPPKDKOR",
        "ppp_adjusted": "PPPGDPKOR",
        "population": "POPTOTKOR647NWDB"
    },
    "australia": {
        "nominal_usd": "MKTGDPAUS646NWDB",
        "constant_2010": "NYGDPMKTPKDAUS",
        "per_capita_constant": "NYGDPPCAPKDAUS",
        "per_capita_ppp": "NYGDPPCAPPPKDAUS",
        "ppp_adjusted": "PPPGDPAUS",
        "population": "POPTOTAUS647NWDB"
    },
    "indonesia": {
        "nominal_usd": "MKTGDPIDN646NWDB",
        "constant_2010": "NYGDPMKTPKDIDN",
        "per_capita_constant": "NYGDPPCAPKDIDN",
        "per_capita_ppp": "NYGDPPCAPPPKDIDN",
        "ppp_adjusted": "PPPGDPIDN",
        "population": "POPTOTIDN647NWDB"
    },
    "thailand": {
        "nominal_usd": "MKTGDPTHA646NWDB",
        "constant_2010": "NYGDPMKTPKDTHA",
        "per_capita_constant": "NYGDPPCAPKDTHA",
        "per_capita_ppp": "NYGDPPCAPPPKDTHA",
        "ppp_adjusted": "PPPGDPTHA",
        "population": "POPTOTTHA647NWDB"
    },
    "singapore": {
        "nominal_usd": "MKTGDPSGP646NWDB",
        "constant_2010": "NYGDPMKTPKDSGP",
        "per_capita_constant": "NYGDPPCAPKDSGP",
        "per_capita_ppp": "NYGDPPCAPPPKDSGP",
        "ppp_adjusted": "PPPGDPSGP",
        "population": "POPTOTSGP647NWDB"
    },
    "malaysia": {
        "nominal_usd": "MKTGDPMYS646NWDB",
        "constant_2010": "NYGDPMKTPKDMYS",
        "per_capita_constant": "NYGDPPCAPKDMYS",
        "per_capita_ppp": "NYGDPPCAPPPKDMYS",
        "ppp_adjusted": "PPPGDPMYS",
        "population": "POPTOTMYS647NWDB"
    },
    "philippines": {
        "nominal_usd": "MKTGDPPHL646NWDB",
        "constant_2010": "NYGDPMKTPKDPHL",
        "per_capita_constant": "NYGDPPCAPKDPHL",
        "per_capita_ppp": "NYGDPPCAPPPKDPHL",
        "ppp_adjusted": "PPPGDPPHL",
        "population": "POPTOTPHL647NWDB"
    },
    "vietnam": {
        "nominal_usd": "MKTGDPVNM646NWDB",
        "constant_2010": "NYGDPMKTPKDVNM",
        "per_capita_constant": "NYGDPPCAPKDVNM",
        "per_capita_ppp": "NYGDPPCAPPPKDVNM",
        "ppp_adjusted": "PPPGDPVNM",
        "population": "POPOTVNM647NWDB"
    },
    "new_zealand": {
        "nominal_usd": "MKTGDPNZL646NWDB",
        "constant_2010": "NYGDPMKTPKDNZL",
        "per_capita_constant": "NYGDPPCAPKDNZL",
        "per_capita_ppp": "NYGDPPCAPPPKDNZL",
        "ppp_adjusted": "PPPGDPNZL",
        "population": "POPOTNZL647NWDB"
    },
    
    # === Europe (Additional OECD) ===
    "spain": {
        "nominal_usd": "MKTGDPESP646NWDB",
        "constant_2010": "NYGDPMKTPKDESP",
        "per_capita_constant": "NYGDPPCAPKDESP",
        "per_capita_ppp": "NYGDPPCAPPPKDESP",
        "ppp_adjusted": "PPPGDPESP",
        "population": "POPTOTESP647NWDB"
    },
    "netherlands": {
        "nominal_usd": "MKTGDPNLD646NWDB",
        "constant_2010": "NYGDPMKTPKDNLD",
        "per_capita_constant": "NYGDPPCAPKDNLD",
        "per_capita_ppp": "NYGDPPCAPPPKDNLD",
        "ppp_adjusted": "PPPGDPNLD",
        "population": "POPTОTNLD647NWDB"
    },
    "switzerland": {
        "nominal_usd": "MKTGDPCHE646NWDB",
        "constant_2010": "NYGDPMKTPKDCHE",
        "per_capita_constant": "NYGDPPCAPKDCHE",
        "per_capita_ppp": "NYGDPPCAPPPKDCHE",
        "ppp_adjusted": "PPPGDPCHE",
        "population": "POPTOTCHE647NWDB"
    },
    "sweden": {
        "nominal_usd": "MKTGDPSWE646NWDB",
        "constant_2010": "NYGDPMKTPKDSWE",
        "per_capita_constant": "NYGDPPCAPKDSWE",
        "per_capita_ppp": "NYGDPPCAPPPKDSWE",
        "ppp_adjusted": "PPPGDPSWE",
        "population": "POPOTSWE647NWDB"
    },
    "norway": {
        "nominal_usd": "MKTGDPNOR646NWDB",
        "constant_2010": "NYGDPMKTPKDNOR",
        "per_capita_constant": "NYGDPPCAPKDNOR",
        "per_capita_ppp": "NYGDPPCAPPPKDNOR",
        "ppp_adjusted": "PPPGDPNOR",
        "population": "POPTОTNOR647NWDB"
    },
    "denmark": {
        "nominal_usd": "MKTGDPDNK646NWDB",
        "constant_2010": "NYGDPMKTPKDDNK",
        "per_capita_constant": "NYGDPPCAPKDDNK",
        "per_capita_ppp": "NYGDPPCAPPPKDDNK",
        "ppp_adjusted": "PPPGDPDNK",
        "population": "POPTOTDNK647NWDB"
    },
    "poland": {
        "nominal_usd": "MKTGDPPOL646NWDB",
        "constant_2010": "NYGDPMKTPKDPOL",
        "per_capita_constant": "NYGDPPCAPKDPOL",
        "per_capita_ppp": "NYGDPPCAPPPKDPOL",
        "ppp_adjusted": "PPPGDPPOL",
        "population": "POPTOTPOL647NWDB"
    },
    "austria": {
        "nominal_usd": "MKTGDPAUT646NWDB",
        "constant_2010": "NYGDPMKTPKDAUT",
        "per_capita_constant": "NYGDPPCAPKDAUT",
        "per_capita_ppp": "NYGDPPCAPPPKDAUT",
        "ppp_adjusted": "PPPGDPAUT",
        "population": "POPTOTAUT647NWDB"
    },
    "belgium": {
        "nominal_usd": "MKTGDPBEL646NWDB",
        "constant_2010": "NYGDPMKTPKDBEL",
        "per_capita_constant": "NYGDPPCAPKDBEL",
        "per_capita_ppp": "NYGDPPCAPPPKDBEL",
        "ppp_adjusted": "PPPGDPBEL",
        "population": "POPTOTBEL647NWDB"
    },
    "greece": {
        "nominal_usd": "MKTGDPGRC646NWDB",
        "constant_2010": "NYGDPMKTPKDGRC",
        "per_capita_constant": "NYGDPPCAPKDGRC",
        "per_capita_ppp": "NYGDPPCAPPPKDGRC",
        "ppp_adjusted": "PPPGDPGRC",
        "population": "POPTOTGRC647NWDB"
    },
    "portugal": {
        "nominal_usd": "MKTGDPPRT646NWDB",
        "constant_2010": "NYGDPMKTPKDPRT",
        "per_capita_constant": "NYGDPPCAPKDPRT",
        "per_capita_ppp": "NYGDPPCAPPPKDPRT",
        "ppp_adjusted": "PPPGDPPRT",
        "population": "POPTOTPRT647NWDB"
    },
    "ireland": {
        "nominal_usd": "MKTGDPIRL646NWDB",
        "constant_2010": "NYGDPMKTPKDIRL",
        "per_capita_constant": "NYGDPPCAPKDIRL",
        "per_capita_ppp": "NYGDPPCAPPPKDIRL",
        "ppp_adjusted": "PPPGDPIRL",
        "population": "POPTOTIRL647NWDB"
    },
    "finland": {
        "nominal_usd": "MKTGDPFIN646NWDB",
        "constant_2010": "NYGDPMKTPKDFIN",
        "per_capita_constant": "NYGDPPCAPKDFIN",
        "per_capita_ppp": "NYGDPPCAPPPKDFIN",
        "ppp_adjusted": "PPPGDPFIN",
        "population": "POPTOTFIN647NWDB"
    },
    "czech_republic": {
        "nominal_usd": "MKTGDPCZE646NWDB",
        "constant_2010": "NYGDPMKTPKDCZE",
        "per_capita_constant": "NYGDPPCAPKDCZE",
        "per_capita_ppp": "NYGDPPCAPPPKDCZE",
        "ppp_adjusted": "PPPGDPCZE",
        "population": "POPTOTCZE647NWDB"
    },
    
    # === Middle East ===
    "saudi_arabia": {
        "nominal_usd": "MKTGDPSAU646NWDB",
        "constant_2010": "NYGDPMKTPKDSAU",
        "per_capita_constant": "NYGDPPCAPKDSAU",
        "per_capita_ppp": "NYGDPPCAPPPKDSAU",
        "ppp_adjusted": "PPPGDPSAU",
        "population": "POPTОTSAU647NWDB"
    },
    "turkey": {
        "nominal_usd": "MKTGDPTUR646NWDB",
        "constant_2010": "NYGDPMKTPKDTUR",
        "per_capita_constant": "NYGDPPCAPKDTUR",
        "per_capita_ppp": "NYGDPPCAPPPKDTUR",
        "ppp_adjusted": "PPPGDPTUR",
        "population": "POPTOTTUR647NWDB"
    },
    "israel": {
        "nominal_usd": "MKTGDPISR646NWDB",
        "constant_2010": "NYGDPMKTPKDISR",
        "per_capita_constant": "NYGDPPCAPKDISR",
        "per_capita_ppp": "NYGDPPCAPPPKDISR",
        "ppp_adjusted": "PPPGDPISR",
        "population": "POPTOTISR647NWDB"
    },
    "uae": {
        "nominal_usd": "MKTGDPARE646NWDB",
        "constant_2010": "NYGDPMKTPKDARE",
        "per_capita_constant": "NYGDPPCAPKDARE",
        "per_capita_ppp": "NYGDPPCAPPPKDARE",
        "ppp_adjusted": "PPPGDPARE",
        "population": "POPTOTARE647NWDB"
    },
    "egypt": {
        "nominal_usd": "MKTGDPEGY646NWDB",
        "constant_2010": "NYGDPMKTPKDEGY",
        "per_capita_constant": "NYGDPPCAPKDEGY",
        "per_capita_ppp": "NYGDPPCAPPPKDEGY",
        "ppp_adjusted": "PPPGDPEGY",
        "population": "POPTOTEGY647NWDB"
    },
    
    # === Africa (Major Economies) ===
    "nigeria": {
        "nominal_usd": "MKTGDPNGA646NWDB",
        "constant_2010": "NYGDPMKTPKDNGA",
        "per_capita_constant": "NYGDPPCAPKDNGA",
        "per_capita_ppp": "NYGDPPCAPPPKDNGA",
        "ppp_adjusted": "PPPGDPNGA",
        "population": "POPTOTNGA647NWDB"
    },
    "kenya": {
        "nominal_usd": "MKTGDPKEN646NWDB",
        "constant_2010": "NYGDPMKTPKDKEN",
        "per_capita_constant": "NYGDPPCAPKDKEN",
        "per_capita_ppp": "NYGDPPCAPPPKDKEN",
        "ppp_adjusted": "PPPGDPKEN",
        "population": "POPTOTKEN647NWDB"
    },
    "ethiopia": {
        "nominal_usd": "MKTGDPETH646NWDB",
        "constant_2010": "NYGDPMKTPKDETH",
        "per_capita_constant": "NYGDPPCAPKDETH",
        "per_capita_ppp": "NYGDPPCAPPPKDETH",
        "ppp_adjusted": "PPPGDPETH",
        "population": "POPTOTETH647NWDB"
    },
    "ghana": {
        "nominal_usd": "MKTGDPGHA646NWDB",
        "constant_2010": "NYGDPMKTPKDGHA",
        "per_capita_constant": "NYGDPPCAPKDGHA",
        "per_capita_ppp": "NYGDPPCAPPPKDGHA",
        "ppp_adjusted": "PPPGDPGHA",
        "population": "POPTOTGHA647NWDB"
    },
    "morocco": {
        "nominal_usd": "MKTGDPMAR646NWDB",
        "constant_2010": "NYGDPMKTPKDMAR",
        "per_capita_constant": "NYGDPPCAPKDMAR",
        "per_capita_ppp": "NYGDPPCAPPPKDMAR",
        "ppp_adjusted": "PPPGDPMAR",
        "population": "POPTOTMAR647NWDB"
    },
}

# NOTE: Full 238 countries would be added here. For brevity, showing ~60 major economies.
# Implementation will include all World Bank member countries with FRED series availability.

# ============================================================================
# GDP_PRESETS: Predefined country groups
# ============================================================================

GDP_PRESETS: Dict[str, List[str]] = {
    # === International Organizations ===
    "g7": ["usa", "canada", "uk", "germany", "france", "italy", "japan"],
    
    "g20": [
        "usa", "canada", "mexico", "argentina", "brazil",
        "uk", "germany", "france", "italy", "spain",
        "russia", "turkey", "saudi_arabia",
        "india", "china", "japan", "south_korea", "indonesia",
        "australia", "south_africa"
    ],
    
    "brics": ["brazil", "russia", "india", "china", "south_africa"],
    
    "oecd": [
        # Americas
        "usa", "canada", "mexico", "chile", "colombia",
        # Europe
        "uk", "germany", "france", "italy", "spain", "netherlands",
        "switzerland", "sweden", "norway", "denmark", "poland",
        "austria", "belgium", "greece", "portugal", "ireland",
        "finland", "czech_republic",
        # Asia-Pacific
        "japan", "south_korea", "australia", "new_zealand",
        # Middle East
        "turkey", "israel"
    ],
    
    # === Regional Groups ===
    "latam": [
        "argentina", "brazil", "chile", "colombia", "peru",
        "mexico", "uruguay", "venezuela", "bolivia", "ecuador", "paraguay"
    ],
    
    "north_america": ["usa", "canada", "mexico"],
    
    "eurozone": [
        "germany", "france", "italy", "spain", "netherlands",
        "belgium", "austria", "portugal", "ireland", "finland", "greece"
    ],
    
    "asia_pacific": [
        "china", "japan", "south_korea", "india", "indonesia",
        "thailand", "singapore", "malaysia", "philippines", "vietnam",
        "australia", "new_zealand"
    ],
    
    "middle_east": ["saudi_arabia", "turkey", "israel", "uae", "egypt"],
    
    "africa": ["south_africa", "nigeria", "kenya", "ethiopia", "ghana", "morocco"],
    
    # === Development Classification (IMF/World Bank) ===
    "emerging": [
        "china", "india", "brazil", "russia", "mexico",
        "indonesia", "turkey", "saudi_arabia", "argentina",
        "thailand", "malaysia", "south_africa", "colombia",
        "egypt", "philippines", "pakistan", "vietnam", "chile", "peru"
    ],
    
    "developed": [
        "usa", "canada", "uk", "germany", "france", "italy", "japan",
        "australia", "spain", "netherlands", "switzerland", "sweden",
        "norway", "denmark", "belgium", "austria", "singapore",
        "ireland", "finland", "new_zealand", "israel", "south_korea"
    ],
    
    # === Special Groups ===
    "eurozone_core": ["germany", "france", "netherlands", "austria", "belgium", "finland"],
    "eurozone_periphery": ["spain", "italy", "portugal", "greece", "ireland"],
    
    "nordic": ["sweden", "norway", "denmark", "finland"],
    
    "east_asia": ["china", "japan", "south_korea", "singapore"],
    
    "south_asia": ["india"],  # Would expand with Pakistan, Bangladesh, Sri Lanka
    
    "southeast_asia": ["indonesia", "thailand", "singapore", "malaysia", "philippines", "vietnam"],
}

# ============================================================================
# GDP_VARIANT_DEPENDENCIES: Automatic computation rules
# ============================================================================

GDP_VARIANT_DEPENDENCIES: Dict[str, Dict[str, any]] = {
    "growth_rate": {
        "source": "constant_2010",
        "formula": "((value_t / value_t-1) - 1) * 100",
        "fallback": None,
        "description": "Annual % change in constant 2010 GDP"
    },
    # NOTE: ppp_adjusted is a DIRECT fetch variant, not computed
    # It should be defined in GDP_MAPPINGS with series IDs
    "per_capita_nominal": {
        "source": ["nominal_usd", "population"],
        "formula": "(gdp_billion * 1e9) / population",
        "fallback": "fetch_direct",  # Try FRED first
        "description": "GDP per capita (current USD)"
    },
    "per_capita_constant": {
        "source": ["constant_2010", "population"],
        "formula": "(gdp_billion * 1e9) / population",
        "fallback": "fetch_direct",
        "description": "GDP per capita (constant 2010 USD)"
    },
    "per_capita_ppp": {
        "source": ["ppp_adjusted", "population"],
        "formula": "(gdp_billion * 1e9) / population",
        "fallback": "fetch_direct",
        "description": "GDP per capita PPP (constant 2017 international $)"
    }
}

# ============================================================================
# Helper Functions
# ============================================================================

def get_series_id(country: str, variant: str) -> Optional[str]:
    """
    Get FRED series ID for a country/variant combination.
    
    Args:
        country: Country code (e.g., "usa", "argentina")
        variant: GDP variant (e.g., "per_capita_constant")
    
    Returns:
        FRED series ID or None if not available
    """
    return GDP_MAPPINGS.get(country, {}).get(variant)


def expand_preset(preset_or_countries: str | List[str]) -> List[str]:
    """
    Expand preset name to list of countries.
    
    Args:
        preset_or_countries: Either a preset name ("g7") or list of countries
    
    Returns:
        List of country codes
    
    Examples:
        >>> expand_preset("g7")
        ["usa", "canada", "uk", "germany", "france", "italy", "japan"]
        >>> expand_preset(["usa", "china"])
        ["usa", "china"]
        >>> expand_preset(["g7", "china"])  # Mix preset + countries
        ["usa", "canada", "uk", "germany", "france", "italy", "japan", "china"]
    """
    if isinstance(preset_or_countries, str):
        # Single preset or country
        if preset_or_countries in GDP_PRESETS:
            return GDP_PRESETS[preset_or_countries]
        else:
            return [preset_or_countries]
    
    # List of presets/countries
    result = []
    for item in preset_or_countries:
        if item in GDP_PRESETS:
            result.extend(GDP_PRESETS[item])
        else:
            result.append(item)
    
    # Remove duplicates while preserving order
    seen = set()
    return [x for x in result if not (x in seen or seen.add(x))]


def get_available_countries() -> List[str]:
    """Get list of all countries with GDP data."""
    return list(GDP_MAPPINGS.keys())


def get_available_variants() -> List[str]:
    """Get list of all GDP variants."""
    return [
        "nominal_usd",
        "nominal_lcu",
        "constant_2010",
        "per_capita_nominal",
        "per_capita_constant",
        "per_capita_ppp",
        "growth_rate",  # Computed
        "ppp_adjusted"
    ]


def get_country_name(country_code: str) -> str:
    """Convert country code to display name."""
    # Simple mapping - would be expanded with full country names
    names = {
        "usa": "United States",
        "uk": "United Kingdom",
        "uae": "United Arab Emirates",
        "south_korea": "South Korea",
        "south_africa": "South Africa",
        "new_zealand": "New Zealand",
        "czech_republic": "Czech Republic",
        "saudi_arabia": "Saudi Arabia",
    }
    return names.get(country_code, country_code.replace("_", " ").title())
