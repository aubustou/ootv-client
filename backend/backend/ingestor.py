from __future__ import annotations

import argparse
import logging
import re
import shutil
from pathlib import Path
from typing import TypedDict

import lxml.etree as ET
import typesense

from .mappings import (
    CLAN_MAPPING,
    DECK_MAPPING,
    EXTENSION_MAPPING,
    LEGALITY_MAPPING,
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

IMAGE_FOLDER = Path(r"E:/L5R/L5R/L5R CCG Image Packs/")
OUTPUT_FOLDER = Path(r"E:/L5R/L5R/Oracle/")

import PIL.Image as Image


def get_image_path(
    card_id: str, image_name: str, edition_acronym_: str, number: str, index: int
) -> None:
    output_folder = OUTPUT_FOLDER / edition_acronym_ / number
    details_path = output_folder / f"printing_{card_id}_{index}_details.jpg"
    select_path = output_folder / f"printing_{card_id}_{index}_select.jpg"

    if details_path.exists() and select_path.exists():
        return None

    if not (path := next(IMAGE_FOLDER.rglob(f"{image_name}.*"), None)):
        if not (
            path := next(IMAGE_FOLDER.rglob(f"{image_name.replace('_', '')}.*"), None)
        ):
            logger.warning("Image %s not found", image_name)
            breakpoint()
            return None

    output_folder.mkdir(parents=True, exist_ok=True)

    # Convert to JPG
    image = Image.open(path)
    if image.mode == "RGBA":
        image = image.convert("RGB")
    image.save(details_path)

    # Resize to 150*210
    image.thumbnail((150, 210))
    image.save(select_path)


NUMBER_PATTERN = re.compile(r"(\d+)")


def get_printing(xml_item: ET.Element, card_id: str) -> list[dict[str, str]]:
    """Get the printing information of a card. Example with Goju Hitomi"""

    xml_printings = xml_item.findall("image")
    if not (xml_rarity := xml_item.find("rarity")):
        rarity = "f"
    else:
        rarity = xml_rarity.text

    printings = []
    for index, xml_printing in enumerate(xml_printings, start=1):
        edition_acronym = xml_printing.attrib["edition"]

        if not (edition := EXTENSION_MAPPING.get(edition_acronym)):
            continue

        image_name = Path(xml_printing.text).stem

        number = NUMBER_PATTERN.search(image_name).group(1)
        logger.info("Processing printing %s from edition %s", number, edition)

        get_image_path(card_id, image_name, edition_acronym, number, index)

        printing = {
            "set": [edition],
            "printingid": f"{index }",
            "artist": [""],
            "artnumber": [""],
            "number": [number],
            "rarity": [RARITY_MAPPING[rarity]],
            "text": [""],
            "printimagehash": [f"{edition_acronym}/{number}"],
        }
        printings.append(printing)

    return printings


TOKEN_REPLACEMENTS = [
    ("[BOW]", ":bow:"),
    ("[FAVOR]", ":favor:"),
]
PAY_PATTERN = re.compile(r"\[PAY ([\d*]+)\]")


def convert_text(text: str, card_type: str) -> tuple[str, list[str]]:
    if card_type in {"Personality", "Sensei"}:
        parts = text.split("<br>", maxsplit=1)
        if len(parts) == 2:
            keywords_, text = parts
        else:
            text = ""
            keywords_ = parts[0]
        keywords = keywords_.split("&#8226;")
    else:
        keywords = []

    for token, replacement in TOKEN_REPLACEMENTS:
        text = text.replace(token, replacement)

    if "[PAY " in text:
        text = PAY_PATTERN.sub(r":g\1:", text)

    text = text.strip().removeprefix("<br>").strip()

    cleaned_keywords: list[str] = []
    for keyword in keywords:
        # Remove HTML tags
        keyword = re.sub(r"<[^>]+>", "", keyword)
        keyword = keyword.strip()
        if keyword:
            cleaned_keywords.append(keyword)

    return text, cleaned_keywords


def xml_to_dict(xml_item: ET.Element) -> dict[str, str]:
    """Convert an XML element into a dictionary. Example with Goju Hitomi"""
    card_type = xml_item.attrib["type"]
    if card_type not in {"holding", "personality", "sensei"}:
        return {}

    legalities = []
    has_onyx = False
    for legality in xml_item.findall("legal"):
        legality_text = legality.text
        if legality_text in {"onyx", "shattered_empire"}:
            has_onyx = True
        if legality := LEGALITY_MAPPING.get(legality_text):
            legalities.append(legality)

    if not has_onyx:
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

    text, keywords = convert_text(xml_item.find("text").text, card_type)
    printings = get_printing(xml_item, card_id)

    card = {
        "printingprimary": str(printings[0]["printingid"]),
        "imagehash": printings[0]["printimagehash"][0],
        "title": [card_name],
        "formattedtitle": card_name,
        "printing": printings,
        "legality": legalities,
        "type": [card_type],
        "cardid": card_id,
        "puretexttitle": card_name,
        "deck": [card_deck],
        "text": [text],
        "keywords": keywords,
    }
    match card_type:
        case "Holding":
            if (xml_gold_production := xml_item.find("gold_production")) is not None:
                gold_production = xml_gold_production.text
            else:
                gold_production = ""

            card.update(
                {
                    "clan": [],
                    "cost": [xml_item.find("cost").text],
                    "production": [gold_production],
                }
            )
        case "Personality":
            card.update(
                {
                    "clan": [CLAN_MAPPING[x.text] for x in xml_item.findall("clan")],
                    "force": [xml_item.find("force").text],
                    "chi": [xml_item.find("chi").text],
                    "ph": [xml_item.find("personal_honor").text],
                    "honor": [xml_item.find("honor_req").text],
                    "cost": [xml_item.find("cost").text],
                }
            )
        case "Sensei":
            if "All Clans" in keywords:
                clans = list(CLAN_MAPPING.values())
            else:
                clans = [x.removesuffix(" Clan") for x in keywords]
            card.update(
                {
                    "clan": clans,
                    "production": [xml_item.find("gold_production").text],
                    "startinghonor": [xml_item.find("starting_honor").text],
                    "strength": [xml_item.find("province_strength").text],
                }
            )

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
                "sort": True,
            },
            {
                "name": "title",
                "type": "string[]",
            },
            {
                "name": "cardid",
                "type": "string",
            },
            {"name": "keywords", "type": "string[]", "facet": True},
            {"name": "clan", "type": "string[]", "facet": True},
            {"name": "legality", "type": "string[]", "facet": True},
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
