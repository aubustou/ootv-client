from __future__ import annotations

import json
import logging
import urllib.parse
from typing import Any, Dict, List, Literal, TypedDict

import typesense
import typesense.collection
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import mappings

logger = logging.getLogger(__name__)

app = FastAPI()


# Liste des origines autorisées (mettez les vôtres ici)
origins = [
    "http://somosierra.flu",
    "http://localhost:8000",  # Si vous testez localement
    "http://somosierra.flu:8000",  # Si vous avez par exemple un front-end React sur le port 3000
]


# Configuration du middleware CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Les origines qui peuvent faire des requêtes
    allow_credentials=True,  # Autoriser les cookies cross-origin
    allow_methods=["*"],  # Autoriser toutes les méthodes
    allow_headers=["*"],  # Autoriser tous les headers
)


@app.get("/updatelog")
async def updatelog(table: str, limit: int, fetchcards: bool):
    """http://somosierra.flu:8000/updatelog?table=l5r&limit=110&fetchcards=true"""
    return {
        "logs": [],
        "cardids": [],
        "cards": {
            "took": 2,
            "timed_out": False,
            "_shards": {"total": 1, "successful": 1, "skipped": 0, "failed": 0},
            "hits": {
                "total": 0,
                "max_score": 1,
                "hits": [],
            },
        },
    }


def get_attributes_query_params(body: bytes) -> dict[str, str]:
    """b'table=l5r&lookup=deck&optgroup=1'"""
    query_params = {}
    decoded_body = body.decode("utf-8")
    for param in decoded_body.split("&"):
        key, value = param.split("=")
        query_params[key] = urllib.parse.unquote(value)

    return query_params


@app.post("/attributes")
async def attributes(request: Request):
    query = get_attributes_query_params(await request.body())
    match query["lookup"]:
        case "legality":
            return [
                {
                    "Arc": [
                        "Clan&nbsp;Wars&nbsp;(Imperial)",
                        "Hidden&nbsp;Emperor&nbsp;(Jade)",
                        "Four&nbsp;Winds&nbsp;(Gold)",
                        "Rain&nbsp;of&nbsp;Blood&nbsp;(Diamond)",
                        "Race&nbsp;for&nbsp;the&nbsp;Throne&nbsp;(Samurai)",
                        "Age&nbsp;of&nbsp;Enlightenment&nbsp;(Lotus)",
                        "Destroyer&nbsp;War&nbsp;(Celestial)",
                        "Age&nbsp;of&nbsp;Conquest&nbsp;(Emperor)",
                        "A&nbsp;Brother's&nbsp;Destiny&nbsp;(Ivory&nbsp;Edition)",
                        "A&nbsp;Brother's&nbsp;Destiny&nbsp;(Twenty&nbsp;Festivals)",
                        "Onyx Edition",
                        "Shattered&nbsp;Empire",
                    ]
                },
                {"Format": ["Modern", "Obsidian Hand", "Big Deck"]},
                {"Misc": ["Not&nbsp;Legal&nbsp;(Proxy)", "Unreleased"]},
            ]
        case "printing.rarity":
            return list(mappings.RARITY_MAPPING.values())
        case "type":
            return list(mappings.TYPE_MAPPING.values())
        case "deck":
            return list(mappings.DECK_MAPPING.keys())
        case "clan":
            return list(mappings.CLAN_MAPPING.values())
        case "printing.set:printing.rarity":
            return [
                {
                    "Clan War (Imperial)": {
                        "Pre-Imperial Edition": ["Fixed"],
                        "Imperial Edition": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Shadowlands": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Forbidden Knowledge": ["Common", "Rare", "Uncommon"],
                        "Emerald Edition": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Battle of Beiden Pass": ["Fixed"],
                        "Anvil of Despair": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Crimson and Jade": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Obsidian Edition": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Time of the Void": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Scorpion Clan Coup 1": ["Common", "Fixed", "Uncommon"],
                        "Scorpion Clan Coup 2": ["Common", "Uncommon"],
                        "Scorpion Clan Coup 3": ["Common", "Fixed", "Uncommon"],
                        "Promotional&ndash;Imperial": ["Promo"],
                        "Promotional–Imperial": ["Promo"],
                    }
                },
                {
                    "The Hidden Emperor (Jade)": {
                        "Jade Edition": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Hidden Emperor 1": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Hidden Emperor 2": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Hidden Emperor 3": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Hidden Emperor 4": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Hidden Emperor 5": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Hidden Emperor 6": ["Common", "Fixed", "Rare", "Uncommon"],
                        "The Dark Journey Home": [
                            "Common",
                            "Fixed",
                            "Rare",
                            "Uncommon",
                        ],
                        "Pearl Edition": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Siege of Sleeping Mountain": ["Fixed"],
                        "Honor Bound": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Ambition's Debt": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Fire &amp; Shadow": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Top Deck Booster Pack": ["Fixed"],
                        "Heroes of Rokugan": ["Fixed"],
                        "Soul of the Empire": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Storms Over Matsu Palace": ["Fixed"],
                        "The War of Spirits": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Promotional&ndash;Jade": ["Promo"],
                        "Promotional–Jade": ["Promo"],
                        "Promotional&ndash;CWF": ["Promo"],
                    }
                },
                {
                    "Four Winds (Gold)": {
                        "Gold Edition": ["Common", "Fixed", "Rare", "Uncommon"],
                        "A Perfect Cut": ["Common", "Fixed", "Rare", "Uncommon"],
                        "An Oni's Fury": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Dark Allies": ["Common", "Fixed", "Rare", "Uncommon"],
                        "L5R Experience": ["Fixed"],
                        "Broken Blades": ["Common", "Fixed", "Rare", "Uncommon"],
                        "1,000 Years of Darkness": ["Fixed"],
                        "The Fall of Otosan Uchi": [
                            "Common",
                            "Fixed",
                            "Rare",
                            "Uncommon",
                        ],
                        "Heaven & Earth": ["Common", "Uncommon"],
                        "Heaven &amp; Earth": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Winds of Change": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Promotional&ndash;Gold": ["Promo"],
                    }
                },
                {
                    "Rain of Blood (Diamond)": {
                        "Diamond Edition": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Training Grounds": ["Fixed"],
                        "Reign of Blood": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Hidden City": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Wrath of the Emperor": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Dawn of the Empire": ["Fixed"],
                        "Web of Lies": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Enemy of My Enemy": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Code of Bushido": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Promotional&ndash;Diamond": ["Promo"],
                    }
                },
                {
                    "Age of Enlightenment (Lotus)": {
                        "Lotus Edition": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Path of Hope": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Drums of War": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Training Grounds 2": ["Fixed"],
                        "Test of Enlightenment": ["Fixed"],
                        "Rise of the Shogun": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Khan's Defiance": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Tomorrow": ["Fixed"],
                        "The Truest Test": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Promotional&ndash;Lotus": ["Promo"],
                        "Crab vs. Lion": ["Fixed"],
                    }
                },
                {
                    "Race for the Throne (Samurai)": {
                        "Samurai Edition": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Stronger Than Steel": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Test of the Emerald and Jade Championships": ["Fixed"],
                        "Honor's Veil": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Words and Deeds": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Samurai Edition Banzai": ["Rare"],
                        "The Heaven's Will": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Glory of the Empire": ["Common", "Fixed", "Rare", "Uncommon"],
                        "The Imperial Gift 1": ["Fixed"],
                        "Death at Koten": ["Fixed"],
                        "Promotional&ndash;Samurai": ["Fixed", "Promo"],
                        "Promotional–Samurai": ["Promo"],
                    }
                },
                {
                    "The Destroyer War (Celestial)": {
                        "Celestial Edition": ["Common", "Fixed", "Rare", "Uncommon"],
                        "The Imperial Gift 2": ["Fixed"],
                        "Path of the Destroyer": [
                            "Common",
                            "Fixed",
                            "Rare",
                            "Uncommon",
                        ],
                        "The Harbinger": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Celestial Edition 15th Anniversary": [
                            "Common",
                            "Fixed",
                            "Promo",
                            "Rare",
                            "Uncommon",
                        ],
                        "The Plague War": ["Common", "Fixed", "Rare", "Uncommon"],
                        "The Imperial Gift 3": ["Fixed"],
                        "Battle of Kyuden Tonbo": ["Fixed"],
                        "Empire at War": ["Common", "Fixed", "Rare", "Uncommon"],
                        "The Dead of Winter": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Before the Dawn": ["Common", "Fixed", "Rare", "Uncommon"],
                        "War of Honor": ["Fixed"],
                        "Forgotten Legacy": ["Fixed"],
                        "Second City": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Promotional&ndash;Celestial": ["Fixed", "Promo"],
                        "Promotional–Celestial": ["Promo"],
                    }
                },
                {
                    "Age of Conquest (Emperor)": {
                        "Emperor Edition": [
                            "Common",
                            "Fixed",
                            "Premium",
                            "Rare",
                            "Uncommon",
                        ],
                        "Embers of War": ["Common", "Fixed", "Rare", "Uncommon"],
                        "The Shadow's Embrace": ["Fixed"],
                        "Seeds of Decay": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Honor and Treachery": ["Fixed"],
                        "Emperor Edition Gempukku": ["Fixed"],
                        "Torn Asunder": ["Common", "Rare", "Uncommon"],
                        "Coils of Madness": ["Fixed", "Premium"],
                        "Gates of Chaos": ["Common", "Rare", "Uncommon"],
                        "Aftermath": ["Common", "Rare", "Uncommon"],
                        "Promotional&ndash;Emperor": ["Fixed", "Promo"],
                        "Promotional–Emperor": ["Promo"],
                        "Emperor Edition Demo Decks": ["Fixed"],
                    }
                },
                {
                    "A Brother's Destiny (Ivory)": {
                        "A Matter of Honor": ["Fixed"],
                        "Ivory Edition": [
                            "Common",
                            "Fixed",
                            "Premium",
                            "Rare",
                            "Uncommon",
                        ],
                        "The Coming Storm": ["Common", "Premium", "Rare", "Uncommon"],
                        "Siege: Heart of Darkness": ["Fixed"],
                        "A Line in the Sand": ["Common", "Premium", "Rare", "Uncommon"],
                        "The New Order": ["Common", "Premium", "Rare", "Uncommon"],
                        "The Currency of War": ["Fixed"],
                        "Promotional&ndash;Twenty Festivals": ["Promo"],
                        "Twenty Festivals": [
                            "Common",
                            "Fixed",
                            "Premium",
                            "Rare",
                            "Uncommon",
                        ],
                        "Thunderous Acclaim": ["Common", "Rare", "Uncommon"],
                        "Siege: Clan War": ["Fixed"],
                        "Evil Portents": ["Common", "Premium", "Rare", "Uncommon"],
                        "The Blackest Storm": ["Common", "Fixed", "Rare", "Uncommon"],
                        "Promotional&ndash;Ivory": ["Fixed", "Promo"],
                    }
                },
                {
                    "Onyx Edition": {
                        "Hidden Forest War": ["Fixed"],
                        "Onyx Edition": ["Fixed"],
                        "Rise of Jigoku": ["Fixed"],
                        "Road to Ruin": ["Fixed"],
                        "Rise of Otosan Uchi": ["Fixed"],
                        "Promotional&ndash;Onyx": ["Promo"],
                    }
                },
                {
                    "Shattered Empire": {
                        "Gathering Storm": ["Fixed"],
                        "Chaos Reigns I": ["Fixed"],
                        "Promotional&ndash;Shattered Empire": ["Promo"],
                    }
                },
                {
                    "Special": {
                        "Oracle of the Void": ["None"],
                        "Cubic Zirconia Edition": ["Fixed"],
                    }
                },
            ]
        case _:
            logger.error("Unknown lookup %s", query["lookup"])
            return []


class QueryParams(TypedDict):
    querystring: str
    table: str
    sort: list[dict[str, dict[str, str]]]
    size: str
    from_: str


class SearchQuery(TypedDict):
    q: str
    filter_by: str
    query_by: str
    sort_by: str
    per_page: str
    page: str


FilterBy = dict[str, Any]


def get_query_params(params: dict[str, Any]) -> tuple[str, str]:
    querystring = "*"
    filters: list[str] = []
    for key, value in params.items():
        match key:
            case "field_title" | "querystring":
                querystring = value
            case "field_keywords":
                if isinstance(value, list):
                    filters.extend([f"keywords:=[{x}]" for x in value])
                else:
                    filters.append(f"keywords:=[{value}]")
            case "field_clan":
                if isinstance(value, list):
                    filters.extend([f"clan:=[{x}]" for x in value])
                else:
                    filters.append(f"clan:=[{value}]")
            case "field_legality":
                if isinstance(value, list):
                    filters.extend(
                        [f"legality:=[{x.replace('&nbsp;', ' ')}]" for x in value]
                    )
                else:
                    filters.append(f"legality:=[{value.replace('&nbsp;', ' ')}]")

    return querystring, " && ".join(filters)


def get_search_params(body: bytes) -> SearchQuery:
    """b'querystring=hitomi&table=l5r&sort=%5B%7B%22title.keyword%22%3A%7B%22order%22%3A%22asc%22%7D%7D%5D&size=50&from=0'
    b'type_printing_set=select&field_printing_set=Chaos%20Reigns%20I&table=l5r&sort=%5B%7B%22title.keyword%22%3A%7B%22order%22%3A%22desc%22%7D%7D%5D&size=50&from=0'
    {'type_title': 'text', 'field_title': 'Gusai ', 'table': 'l5r', 'sort': [{'title.keyword': {'order': 'asc'}}], 'size': '50', 'from': '0'}
    """
    decoded_params = {}
    decoded_body = body.decode("utf-8")
    for param in decoded_body.split("&"):
        key, value = param.split("=")
        decoded_params[key] = urllib.parse.unquote(value)
        if key == "sort":
            decoded_params[key] = json.loads(decoded_params[key])

    logger.info(decoded_params)

    querystring, filters = get_query_params(decoded_params)

    search_query = SearchQuery(
        q=querystring,
        filter_by=filters,
        query_by="formattedtitle",
        sort_by="formattedtitle:asc",
        limit=decoded_params["size"],
        offset=decoded_params["from"],
    )

    logger.info(search_query)

    return search_query


def convert(hit: dict) -> dict:
    return {
        "_index": "l5r",
        "_type": "oracle-l5r_type",
        "_id": f"cardid={hit['document']['cardid']}.0",
        "_score": None,
        "_ignored": ["honor"],
        "_source": hit["document"],
        "sort": [hit["document"]["formattedtitle"]],
    }


@app.get("/oracle-fetch")
async def oracle_fetch(table: str, cardid: str):
    search_query = {
        "q": cardid,
        "query_by": "cardid",
        "sort_by": "formattedtitle:asc",
    }

    search_results = collection.documents.search(search_query)

    logger.info(search_results)
    if not (found_elements := search_results["found"]):
        return {}

    hits = search_results["hits"]

    return convert(hits[0])["_source"]


@app.post("/search")
async def search(request: Request):
    search_query = get_search_params(await request.body())

    search_results = collection.documents.search(search_query)

    logger.info(search_results)
    found_elements = search_results["found"]
    hits = search_results["hits"]

    return {
        "took": 1,
        "timed_out": False,
        "_shards": {"total": 1, "successful": 1, "skipped": 0, "failed": 0},
        "hits": {
            "total": found_elements,
            "max_score": None,
            "hits": [convert(x) for x in hits],
        },
    }


typesense_client: typesense.Client
collection: typesense.collection.Collection


def main():
    logging.basicConfig(level=logging.INFO)

    import uvicorn

    global typesense_client, collection

    typesense_client = typesense.Client(
        {
            "api_key": "xyz",
            "nodes": [
                {"host": "localhost", "port": "8108", "protocol": "http"},
            ],
        }
    )
    logger.info("Connected to Typesense")

    collection = typesense_client.collections["l5r"]
    logger.info(collection.retrieve())

    uvicorn.run(app, host="0.0.0.0", port=8000)
