from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path
from typing import TypedDict

import lxml.etree as ET
import typesense

from .mappings import (
    CLAN_MAPPING,
    DECK_MAPPING,
    EXTENSION_MAPPING,
    RARITY_MAPPING,
    TYPE_MAPPING,
)

logger = logging.getLogger(__name__)

client: typesense.Client


def init_client() -> None:
    global client
    client = typesense.Client(
        {
            "nodes": [
                {
                    "host": "somosierra.flu",
                    "port": "8108",
                    "protocol": "http",
                }
            ],
            "api_key": "xyz",
            "connection_timeout_seconds": 2,
        }
    )


"""
<cards version="2024/3/30 Onyx Oracle Edition">	<!--"Oct 4, 2015 Kamisasori no Kaisho (Complete), Nov 28, 2017 Kolat 1.3.4">-->
	<card id="AD092" type="strategy">
		<name>A Chance Meeting</name>
		<rarity>u</rarity>
		<edition>AD</edition><image edition="AD">images/cards/AD/AD092.jpg</image>
		<legal>open</legal>
		<text><![CDATA[<b>Battle:</b> One of your Personalities in this battle challenges an opposing Personality. If the challenged Personality refuses the challenge, that personality becomes dishonored, and all of his or her Followers bow. If the challenged Personality accepts the challenge, the duel's winner gains Honor equal to the number of cards focused by both players, and the loser is destroyed.]]></text>
		<cost>0</cost>
		<focus>3</focus>
	</card>
	<card id="AD081" type="region">
		<name>Akodo Fields</name>
		<rarity>u</rarity>
		<edition>AD</edition><image edition="AD">images/cards/AD/AD081.jpg</image>
		<legal>open</legal>
		<legal>jade</legal>
		<text><![CDATA[<B>Limited:</B> Target one of your Followers in play and pay Gold equal to the Follower's Force. For the rest of the game, the Follower is Elite, contributes its Force to its army's total during the Resolution Segment of battle even if its Personality is bowed, and is immune to Fear.]]></text>
	</card>
    <card id="KYD022" type="personality">
		<name>Goju Hitomi - exp3</name>
		<rarity>f</rarity>
		<edition>KYD</edition><image edition="KYD">images/cards/KYD/KYD022.jpg</image>
		<edition>AD</edition><image edition="AD">images/cards/AD/AD081.jpg</image>
		<legal>open</legal>
		<clan>dragon</clan>
		<clan>ninja</clan>
		<text><![CDATA[<B>Dragon Clan Samurai. Ninja. Tattooed. Experienced 3 Mirumoto Hitomi. Unique.</B> Hitomi may attach the Obsidian Hand without Gold cost. <BR>Hitomi may cast Kihos as though she were a Shugenja. Kihos cast in this way produce Ninja effects instead of Spell effects. <BR><B>Limited:</B> Once per turn, get a Tattoo or Kiho card from your Fate deck and put it in your hand. Shuffle your deck.]]></text>
		<force>5</force>
		<chi>5</chi>
		<personal_honor>1</personal_honor>
		<cost>15</cost>
		<honor_req>-</honor_req>
	</card>
"""


NUMBER_PATTERN = re.compile(r"(\d+)")


def get_printing(xml_item: ET.Element) -> list[dict[str, str]]:
    """Get the printing information of a card. Example with Goju Hitomi"""
    xml_printings = xml_item.findall("image")
    if not (xml_rarity := xml_item.find("rarity")):
        rarity = "f"
    else:
        rarity = xml_rarity.text

    printings = []
    for index, xml_printing in enumerate(xml_printings, start=1):
        if not (edition := EXTENSION_MAPPING.get(xml_printing.attrib["edition"])):
            continue

        number = NUMBER_PATTERN.search(Path(xml_printing.text).stem).group(1)

        printing = {
            "set": [edition],
            "printingid": f"{index }",
            "artist": [""],
            "artnumber": [""],
            "number": [number],
            "rarity": [RARITY_MAPPING[rarity]],
            "text": [""],
            "printimagehash": ["ae/bf"],
        }
        printings.append(printing)

    return printings


def xml_to_dict(xml_item: ET.Element) -> dict[str, str]:
    """Convert an XML element into a dictionary. Example with Goju Hitomi"""
    card_type = xml_item.attrib["type"]
    if card_type != "personality":
        return {}

    legalities = xml_item.findall("legal")
    if not any(x.text in {"onyx", "shattered_empire"} for x in legalities):
        return {}

    for deck, values in DECK_MAPPING.items():
        if card_type in values:
            card_deck = deck
            break
    else:
        raise KeyError("Deck not found")

    card_name = xml_item.find("name").text
    logger.info("Processing card %s", card_name)

    card_id = xml_item.attrib["id"]
    card_type = TYPE_MAPPING[xml_item.attrib["type"]]

    force = xml_item.find("force").text
    chi = xml_item.find("chi").text
    personal_honor = xml_item.find("personal_honor").text
    cost = xml_item.find("cost").text
    honor_req = xml_item.find("honor_req").text

    clans = [CLAN_MAPPING[x.text] for x in xml_item.findall("clan")]

    text = xml_item.find("text").text
    keywords = []

    printings = get_printing(xml_item)

    card = {
        "clan": clans,
        "force": [force],
        "deck": [card_deck],
        "printingprimary": "1",
        "chi": [chi],
        "imagehash": "ae/bf",
        "title": [card_name],
        "formattedtitle": card_name,
        "printing": printings,
        "text": [text],
        "cardid": card_id,
        "keywords": keywords,
        "ph": [personal_honor],
        "type": [card_type],
        "honor": [honor_req],
        "puretexttitle": card_name,
        "cost": [cost],
    }

    return card


class Printing(TypedDict):
    """
    {
        "set": [
            "1,000 Years of Darkness"
        ],
        "printingid": "1",
        "artist": [
            "William O'Connor"
        ],
        "artnumber": [
            "3048"
        ],
        "number": [
            "22"
        ],
        "rarity": [
            "Fixed"
        ],
        "text": [
            "Hitomi may attach the Obsidian Hand without Gold cost.<br>Hitomi may cast Kihos as though she were a Shugenja. Kihos cast in this way produce Ninja effects instead of Spell effects.<br>Limited: Once per turn, get a Tattoo or Kiho card from your Fate deck and put it in your hand. Shuffle your deck."
        ],
        "printimagehash": [
            "ae/bf"
        ]
    }
    """

    set: list[str]
    printingid: str
    artist: list[str]
    artnumber: list[str]
    number: list[str]
    rarity: list[str]
    text: list[str]
    printimagehash: list[str]


class ExpectedCard(TypedDict):
    """
    {
                        "clan": [
                            "Dragon"
                        ],
                        "force": [
                            "5"
                        ],
                        "@SequenceNumber": "0000",
                        "deck": [
                            "Dynasty"
                        ],
                        "printingprimary": "1",
                        "chi": [
                            "5"
                        ],
                        "imagehash": "ae/bf",
                        "title": [
                            "Goju Hitomi"
                        ],
                        "formattedtitle": "Goju Hitomi &#149; Experienced 3KYD",
                        "printing": [
                            {
                                "set": [
                                    "1,000 Years of Darkness"
                                ],
                                "printingid": "1",
                                "artist": [
                                    "William O'Connor"
                                ],
                                "artnumber": [
                                    "3048"
                                ],
                                "number": [
                                    "22"
                                ],
                                "rarity": [
                                    "Fixed"
                                ],
                                "text": [
                                    "Hitomi may attach the Obsidian Hand without Gold cost.<br>Hitomi may cast Kihos as though she were a Shugenja. Kihos cast in this way produce Ninja effects instead of Spell effects.<br>Limited: Once per turn, get a Tattoo or Kiho card from your Fate deck and put it in your hand. Shuffle your deck."
                                ],
                                "printimagehash": [
                                    "ae/bf"
                                ]
                            }
                        ],
                        "text": [
                            "Attaches The Obsidian Hand ignoring Gold cost.<br>Hitomi may perform Kiho actions as if she were a Shugenja, and when she performs a Kiho action, it is considered a Ninja action instead of a Kiho action when targeting it and resolving its effects.<br><b>Limited:</b> Search your Fate deck for a Tattoo or Kiho Strategy and put it in your hand."
                        ],
                        "@timestamp": "2022-05-23T15:37:41.250121",
                        "cardid": 2850,
                        "keywords": [
                            "<b>Experienced 3KYD Mirumoto Hitomi</b>",
                            "<b>Unique</b>",
                            "Dragon Clan",
                            "Ninja",
                            "Samurai",
                            "Tattooed"
                        ],
                        "ph": [
                            "1"
                        ],
                        "type": [
                            "Personality"
                        ],
                        "honor": [
                            "-"
                        ],
                        "puretexttitle": "Goju Hitomi - exp3KYD",
                        "cost": [
                            "15"
                        ]
                    },
    """

    clan: list[str]
    force: list[str]
    deck: list[str]
    printingprimary: str
    chi: list[str]
    imagehash: str
    title: list[str]
    formattedtitle: str
    printing: list[Printing]
    text: list[str]
    cardid: int
    keywords: list[str]
    ph: list[str]
    type: list[str]
    honor: list[str]
    puretexttitle: str
    cost: list[str]


def create_collection(documents: ET.tree, overwrite: bool = True) -> None:
    """Turn a XML schema into a Typesense schema"""
    schema = {
        "name": "l5r",
        "fields": [
            {"name": "id", "type": "int32", "facet": True},
            {"name": "type", "type": "string[]", "facet": True},
            {
                "name": "formattedtitle",
                "type": "string",
            },
            # {"name": "rarity", "type": "string", "facet": True},
            # {"name": "edition", "type": "string", "facet": True},
            # {"name": "image", "type": "string",},
            # {"name": "legal", "type": "string", "facet": True},
            # {"name": "cost", "type": "int32", "facet": True},
            # {"name": "focus", "type": "int32", "facet": True},
        ],
    }
    try:
        client.collections.create(schema)
        logging.info("Collection %s created", schema["name"])
    except typesense.exceptions.ObjectAlreadyExists:
        logging.info("Collection %s already exists", schema["name"])
        if overwrite:
            logging.info("Overwriting collection %s", schema["name"])
            client.collections[schema["name"]].delete()
            client.collections.create(schema)
            logging.info("Collection %s created", schema["name"])

    for card in documents.findall("card"):
        card_dict = xml_to_dict(card)

        if not card_dict:
            continue

        try:
            client.collections[schema["name"]].documents.create(card_dict)
            logging.info("Document %s created", card_dict["formattedtitle"])
        except typesense.exceptions.ObjectAlreadyExists:
            logging.info("Document %s already exists", card_dict["formattedtitle"])


def main():
    parser = argparse.ArgumentParser(description="Ingest data into Typesense")
    parser.add_argument(
        "database",
        type=Path,
        help="Path to the file containing the data to be ingested",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    init_client()

    with open(args.database) as f:
        xml = ET.parse(f)

    root = xml.getroot()
    create_collection(root)


if __name__ == "__main__":
    main()
