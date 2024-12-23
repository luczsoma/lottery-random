#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
from datetime import datetime, timezone
from json import load
from time import sleep

from requests import post

from jsonschema import validate
from azure.communication.email import EmailClient
from azure.core.credentials import AzureKeyCredential


class LotteryRandom:
    def __init__(self):
        self.config = self.parse_config()
        self.azure_email_client = EmailClient(
            self.config["azure_email_endpoint"],
            AzureKeyCredential(self.config["azure_email_key"]),
        )
        self.random_org_api_url = "https://api.random.org/json-rpc/2/invoke"
        self.last_random_org_api_call = None

    def parse_config(self):
        """Parses and returns the configuration

        Throws ValidationException or SchemaException if the configuration or the schema is not valid.
        """
        with open("config.json") as config_json_file, open(
            "config.schema.json"
        ) as config_schema_file:
            config = load(config_json_file)
            config_schema = load(config_schema_file)
            validate(config, config_schema)
            return config

    def get_sorted_true_random_integer_sequences(self, n, length, min, max):
        """Returns n sets of true random integer sequences

        Each sequence is with length length,
        and each number within the sequence is between min and max.
        """
        # max. 10 requests / sec
        if self.last_random_org_api_call is not None:
            diff_microseconds = (
                self.last_random_org_api_call - datetime.now(timezone.utc)
            ).microseconds
            if diff_microseconds < 100 * 1000:
                sleep(diff_microseconds / 1000)

        self.last_random_org_api_call = datetime.now(timezone.utc)

        response = post(
            self.random_org_api_url,
            json={
                "id": "",
                "jsonrpc": "2.0",
                "method": "generateIntegerSequences",
                "params": {
                    "apiKey": self.config["random_org_api_key"],
                    "n": n,
                    "length": length,
                    "min": min,
                    "max": max,
                    "replacement": False,
                },
            },
        ).json()

        if "result" in response:
            return [sorted(x) for x in response["result"]["random"]["data"]]
        else:
            raise RuntimeError(f"random.org API error: {response['error']['message']}")

    def validate_lottery_ticket_packs(self):
        """Throws error if a lottery ticket pack references a game which is not defined"""
        lottery_game_names = [
            x["game_name"] for x in self.config["lottery_game_definitions"]
        ]

        for lottery_ticket_pack in self.config["lottery_ticket_packs"]:
            for element in lottery_ticket_pack["elements"]:
                if element["game_name"] not in lottery_game_names:
                    raise ValueError(
                        f"Error in config.json: game \"{element['type_name']}\" is not defined"
                    )

    def sum_tickets_per_game(self):
        """Returns a dictionary with the summary of tickets for each game type

        Keys are game type names, values are the sum of the random tickets needed for that game.
        """
        tickets_per_game = {}

        for lottery_ticket_pack in self.config["lottery_ticket_packs"]:
            for element in lottery_ticket_pack["elements"]:
                game_name = element["game_name"]
                number_of_random_tickets = element["number_of_random_tickets"]

                if game_name in tickets_per_game:
                    tickets_per_game[game_name] += number_of_random_tickets
                else:
                    tickets_per_game[game_name] = number_of_random_tickets

        return tickets_per_game

    def generate_random_filled_drawing_sets_per_game(self, tickets_per_game):
        """Returns a dictionary with randomly generated drawing sets for each game

        In order to minimize random.org API calls, we summarize the number of tickets of each games needed.
        Instead of looping through each item in the lottery_ticket_packs, and calling the API
        for each drawing_set for each game for each element for each pack, we iterate through lottery_game_definitions
        and call it only for each summarized drawing_set for each game.
        """
        random_filled_drawing_sets_per_game = {}

        for game_name in tickets_per_game:
            game_definition = next(
                x
                for x in self.config["lottery_game_definitions"]
                if x["game_name"] == game_name
            )

            filled_drawing_sets = []

            for drawing_set in game_definition["drawing_sets"]:
                filled_drawing_set = self.get_sorted_true_random_integer_sequences(
                    tickets_per_game[game_name],
                    drawing_set["n"],
                    drawing_set["min"],
                    drawing_set["max"],
                )

                filled_drawing_sets.append(filled_drawing_set)

            random_filled_drawing_sets_per_game[game_name] = filled_drawing_sets

        return random_filled_drawing_sets_per_game

    def fill_lottery_ticket_packs_by_drawing_sets(self, filled_drawing_sets_per_game):
        """Returns lottery ticket packs filled with random tickets

        Copies and extends the config attribute's each lottery_ticket_packs member's
        each elements member with a tickets: [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]
        """
        filled_lottery_ticket_packs = deepcopy(self.config["lottery_ticket_packs"])

        for lottery_ticket_pack in filled_lottery_ticket_packs:
            for element in lottery_ticket_pack["elements"]:
                element["random_tickets"] = []
                filled_drawing_sets_of_game = filled_drawing_sets_per_game[
                    element["game_name"]
                ]

                for i in range(element["number_of_random_tickets"]):
                    current_ticket = []

                    for filled_drawing_set_of_game in filled_drawing_sets_of_game:
                        current_drawing_set = filled_drawing_set_of_game.pop(0)
                        current_ticket.append(current_drawing_set)

                    element["random_tickets"].append(current_ticket)

        return filled_lottery_ticket_packs

    def merge_random_and_permanent_tickets(self, random_filled_lottery_ticket_packs):
        """Merges permanent numbers to random numbers, and returns the merged set."""
        merged_lottery_ticket_packs = deepcopy(random_filled_lottery_ticket_packs)

        for lottery_ticket_pack in merged_lottery_ticket_packs:
            for element in lottery_ticket_pack["elements"]:
                element["tickets"] = (
                    element["random_tickets"] + element["permanent_tickets"]
                )

        return merged_lottery_ticket_packs

    def fill_lottery_ticket_packs(self):
        """Fills all lottery tickets with random numbers, merges permanent numbers to them,
        then returns them in the same way as the configuration file is nested within lottery_ticket_packs.
        """
        tickets_per_game = self.sum_tickets_per_game()
        random_filled_drawing_sets_per_game = (
            self.generate_random_filled_drawing_sets_per_game(tickets_per_game)
        )
        random_filled_lottery_ticket_packs = (
            self.fill_lottery_ticket_packs_by_drawing_sets(
                random_filled_drawing_sets_per_game
            )
        )
        merged_lottery_ticket_packs = self.merge_random_and_permanent_tickets(
            random_filled_lottery_ticket_packs
        )

        return merged_lottery_ticket_packs

    def stringify_lottery_ticket_packs(self, filled_tickets):
        """Adds a filled lottery ticket to string

        Copies and extends the filled_tickets with an as_string value.
        """
        stringified_lottery_ticket_packs = deepcopy(filled_tickets)

        for lottery_ticket_pack in stringified_lottery_ticket_packs:
            joined_tickets_per_game = []
            for element in lottery_ticket_pack["elements"]:
                game_name = element["game_name"]
                tickets = element["tickets"]

                joined = (
                    "["
                    + "], [".join(
                        [
                            " | ".join(
                                [
                                    ", ".join([str(x) for x in drawing_set])
                                    for drawing_set in ticket
                                ]
                            )
                            for ticket in tickets
                        ]
                    )
                    + "]"
                )

                joined_tickets_per_game.append(f"{game_name}: {joined}")

            lottery_ticket_pack["as_string"] = "\n".join(joined_tickets_per_game)

        return stringified_lottery_ticket_packs

    def email_stringified_lottery_ticket_packs(self, stringified_lottery_ticket_packs):
        """Sends the stringified tickets to the provided addresses in the configuration file"""
        email_from = self.config["email_from"]

        for lottery_ticket_pack in stringified_lottery_ticket_packs:
            for email_to in lottery_ticket_pack["email_to"]:
                subject = f"Lottery numbers for {email_to["name"]}"

                plainTextContent = f"""{subject}

{lottery_ticket_pack["as_string"]}

Timestamp: {datetime.now(timezone.utc).strftime('%Y/%m/%d %H:%M:%S')} (UTC)

This email was sent you by {email_from['name']} ({email_from['email']}) using https://github.com/luczsoma/lottery-random.
"""

                message = {
                    "content": {
                        "subject": subject,
                        "plainText": plainTextContent,
                    },
                    "recipients": {
                        "to": [
                            {
                                "address": email_to["email"],
                                "displayName": email_to["name"],
                            }
                        ]
                    },
                    "senderAddress": "lottery-random@luczsoma.hu",
                }

                self.azure_email_client.begin_send(message)

    def run(self):
        self.validate_lottery_ticket_packs()
        filled_tickets = self.fill_lottery_ticket_packs()
        stringified_tickets = self.stringify_lottery_ticket_packs(filled_tickets)
        self.email_stringified_lottery_ticket_packs(stringified_tickets)


LotteryRandom().run()
