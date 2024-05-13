TYPE_MAPPING = {
    "ancestor": "Ancestor",
    "celestial": "Celestial",
    "clock": "Clock",
    "event": "Event",
    "follower": "Follower",
    "holding": "Holding",
    "item": "Item",
    "other": "Other",
    "personality": "Personality",
    "proxy": "Proxy",
    "region": "Region",
    "ring": "Ring",
    "sensei": "Sensei",
    "spell": "Spell",
    "strategy": "Strategy",
    "stronghold": "Stronghold",
    "territory": "Territory",
    "wind": "Wind",
}

DECK_MAPPING = {
    "Dynasty": {"celestial", "event", "holding", "personality", "region"},
    "Fate": {"ancestor", "follower", "item", "ring", "spell", "strategy"},
    "Other": {"other", "clock", "territory", "proxy"},
    "Pre-Game": {"stronghold", "sensei", "wind"},
}

CLAN_MAPPING = {
    "akasha": "Akasha",
    "monk": "Brotherhood of Shinsei",
    "crab": "Crab",
    "crane": "Crane",
    "dragon": "Dragon",
    "lion": "Lion",
    "mantis": "Mantis",
    "naga": "Naga",
    "ninja": "Ninja",
    "phoenix": "Phoenix",
    "ratling": "Ratling",
    "scorpion": "Scorpion",
    "shadowlands": "Shadowlands",
    "spider": "Spider",
    "spirit": "Spirit",
    "toturi": "Toturi's Army",
    "unaligned": "Unaligned",
    "unicorn": "Unicorn",
}

EXTENSION_MAPPING = {
    "TwentyFestivals": "Twenty Festivals",
    "ThA": "Thunderous Acclaim",
    "SCW": "Siege: Clan War",
    "EP": "Evil Portents",
    "TBS": "The Blackest Storm",
    "HFW": "Hidden Forest War",
    "Onyx": "Onyx Edition",
    "RoJ": "Rise of Jigoku",
    "RtR": "Road to Ruin",
    "ROU": "Rise of Otosan Uchi",
    "GS": "Gathering Storm",
    "CZE": "Cubic Zirconia Edition",
    "CRI": "Chaos Reigns I",
}

RARITY_MAPPING = {
    "c": "Common",
    "u": "Uncommon",
    "r": "Rare",
    "f": "Fixed",
    "p": "Promo",
    "P": "Premium",
    "n": "None",
}

LEGALITY_MAPPING = {
    "open": "Open",
    "onyx": "Onyx",
    "shattered_empire": "Shattered Empire",
}
