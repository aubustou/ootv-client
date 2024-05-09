from __future__ import annotations

import argparse
import logging

import lxml.etree as ET
import typesense

client: typesense.Client


def init_client() -> None:
    global client
    client = typesense.Client(
        {
            "nodes": [
                {
                    "host": "localhost",
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
"""


def create_collection(documents: ET.tree) -> None:
    """Turn a XML schema into a Typesense schema"""
    schema = {
        "name": "l5r",
        "fields": [
            {"name": "id", "type": "string",},
            {"name": "type", "type": "string", "facet": True},
            {"name": "name", "type": "string",},
            {"name": "rarity", "type": "string", "facet": True},
            {"name": "edition", "type": "string", "facet": True},
            {"name": "image", "type": "string",},
            {"name": "legal", "type": "string", "facet": True},
            {"name": "cost", "type": "int32", "facet": True},
            {"name": "focus", "type": "int32", "facet": True},
        ],
        "default_sorting_field": "id",
    }
    try:
        client.collections.create(schema)
    except typesense.exceptions.ObjectAlreadyExists:
        logging.info("Collection already exists")


def main():
    parser = argparse.ArgumentParser(description="Ingest data into Typesense")
    parser.add_argument(
        "data_file",
        type=str,
        help="Path to the file containing the data to be ingested",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    init_client()


if __name__ == "__main__":
    main()
