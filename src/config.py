from json import load
from typing import Any
from jsonschema import validate
from collections import Counter

from lottery_game_definition import LotteryGameDefinition, FieldDefinition
from lottery_ticket_pack_definition import (
    Recipient,
    LotteryTicketPackDefinition,
    LotteryTicketPackDefinitionElement,
)
from lottery_ticket import LotteryTicket


class Config:
    random_org_api_key: str
    azure_email_endpoint: str
    azure_email_key: str
    sender_email: str
    sender_name: str
    lottery_game_definitions: dict[str, LotteryGameDefinition]
    lottery_ticket_pack_definitions: list[LotteryTicketPackDefinition]

    def __init__(self) -> None:
        with open("config.json") as config_file, open(
            "config.schema.json"
        ) as config_schema_file:
            config = load(config_file)
            config_schema = load(config_schema_file)
            validate(config, config_schema)

            self.random_org_api_key = config["random_org_api_key"]
            self.azure_email_endpoint = config["azure_email_endpoint"]
            self.azure_email_key = config["azure_email_key"]
            self.sender_email = config["sender_email"]
            self.sender_name = config["sender_name"]

            self.lottery_game_definitions = self.validate_lottery_game_definitions(
                config["games"]
            )

            self.lottery_ticket_pack_definitions = (
                self.validate_lottery_ticket_pack_definitions(
                    config["ticket_packs"],
                    self.lottery_game_definitions,
                )
            )

    def validate_lottery_game_definitions(
        self, config_lottery_game_definitions: Any
    ) -> dict[str, LotteryGameDefinition]:
        names_of_duplicate_game_definitions = [
            game_name
            for game_name, number_of_occurrence in Counter(
                [g["name"] for g in config_lottery_game_definitions]
            ).items()
            if number_of_occurrence > 1
        ]
        if len(names_of_duplicate_game_definitions) > 0:
            raise RuntimeError(
                f"Duplicate game definitions: {[", ".join(names_of_duplicate_game_definitions)]}"
            )

        lottery_game_definitions = dict(
            [
                (
                    str(lottery_game_definition["name"]),
                    LotteryGameDefinition(
                        [
                            FieldDefinition(field["n"], field["min"], field["max"])
                            for field in lottery_game_definition["fields"]
                        ],
                    ),
                )
                for lottery_game_definition in config_lottery_game_definitions
            ]
        )

        for name, definition in lottery_game_definitions.items():
            definition.validate(name)

        return lottery_game_definitions

    def validate_lottery_ticket_pack_definitions(
        self,
        config_lottery_ticket_pack_definitions: Any,
        lottery_game_definitions: dict[str, LotteryGameDefinition],
    ) -> list[LotteryTicketPackDefinition]:
        names_of_duplicate_lottery_ticket_pack_definitions = [
            lottery_ticket_pack_definition_name
            for lottery_ticket_pack_definition_name, number_of_occurrence in Counter(
                [p["name"] for p in config_lottery_ticket_pack_definitions]
            ).items()
            if number_of_occurrence > 1
        ]
        if len(names_of_duplicate_lottery_ticket_pack_definitions) > 0:
            raise RuntimeError("Duplicate entry for at least one lottery ticket pack")

        for lottery_ticket_pack_definition in config_lottery_ticket_pack_definitions:
            names_of_duplicate_games_in_elements = [
                game_name
                for game_name, number_of_occurrence in Counter(
                    [e["game"] for e in lottery_ticket_pack_definition["elements"]]
                ).items()
                if number_of_occurrence > 1
            ]
            if len(names_of_duplicate_games_in_elements) > 0:
                raise RuntimeError(
                    "Duplicate entry for at least one game in at least one lottery ticket pack"
                )

        lottery_ticket_pack_definitions = [
            LotteryTicketPackDefinition(
                lottery_ticket_pack_definition["name"],
                [
                    Recipient(recipient["email"], recipient["name"])
                    for recipient in lottery_ticket_pack_definition["recipients"]
                ],
                dict(
                    [
                        (
                            str(pack["game"]),
                            LotteryTicketPackDefinitionElement(
                                pack["number_of_random_tickets"],
                                [
                                    LotteryTicket([set(field) for field in ticket])
                                    for ticket in pack["permanent_tickets"]
                                ],
                            ),
                        )
                        for pack in lottery_ticket_pack_definition["elements"]
                    ]
                ),
            )
            for lottery_ticket_pack_definition in config_lottery_ticket_pack_definitions
        ]

        for lottery_ticket_pack_definition in lottery_ticket_pack_definitions:
            lottery_ticket_pack_definition.validate(lottery_game_definitions)

        return lottery_ticket_pack_definitions
