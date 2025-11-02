#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from azure.communication.email import EmailClient
from azure.core.credentials import AzureKeyCredential
from datetime import datetime, timezone

from config import Config
from lottery_ticket_pack import LotteryTicketPack
from lottery_ticket import LotteryTicket
from random_org_api import RandomOrgApi


class LotteryRandom:
    config: Config = Config()
    random_org_api = RandomOrgApi(config.random_org_api_key)
    azure_email_client = EmailClient(
        config.azure_email_endpoint, AzureKeyCredential(config.azure_email_key)
    )

    def validate_lottery_ticket_pack_filter(
        self,
        lottery_ticket_pack_filter: set[str] | None,
    ) -> None:
        if lottery_ticket_pack_filter is not None:
            lottery_ticket_pack_names = [
                p.name for p in self.config.lottery_ticket_pack_definitions
            ]
            missing = [
                name
                for name in lottery_ticket_pack_filter
                if name not in lottery_ticket_pack_names
            ]
            if len(missing) > 0:
                raise RuntimeError(
                    f"Lottery ticket pack not found for following entries in lottery ticket pack filter: {", ".join(missing)}"
                )

    def create_lottery_ticket_packs(
        self, lottery_ticket_pack_filter: set[str] | None
    ) -> list[LotteryTicketPack]:
        return [
            LotteryTicketPack(
                lottery_ticket_pack_definition.recipients,
                dict(
                    [
                        (
                            game_name,
                            [
                                LotteryTicket.generate_random(
                                    self.config.lottery_game_definitions[
                                        game_name
                                    ].fields,
                                    self.random_org_api,
                                )
                                for _ in range(element.number_of_random_tickets)
                            ]
                            + element.permanent_tickets,
                        )
                        for (
                            game_name,
                            element,
                        ) in lottery_ticket_pack_definition.elements.items()
                    ]
                ),
            )
            for lottery_ticket_pack_definition in self.config.lottery_ticket_pack_definitions
            if lottery_ticket_pack_filter is None  # no filtering needed
            or lottery_ticket_pack_definition.name in lottery_ticket_pack_filter
        ]

    def send_lottery_ticket_pack(self, lottery_ticket_pack: LotteryTicketPack) -> None:
        for recipient in lottery_ticket_pack.recipients:
            subject = f"Lottery numbers for {recipient.name}"

            plainTextContent = f"""{subject}

{lottery_ticket_pack}

Timestamp: {datetime.now(timezone.utc).strftime('%Y/%m/%d %H:%M:%S')} (UTC)

This email was sent you by {self.config.sender_name} ({self.config.sender_email}) using https://github.com/luczsoma/lottery-random.
"""

            message = {  # type: ignore
                "content": {
                    "subject": subject,
                    "plainText": plainTextContent,
                },
                "recipients": {
                    "to": [
                        {
                            "address": recipient.email,
                            "displayName": recipient.name,
                        }
                    ]
                },
                "senderAddress": self.config.sender_email,
            }

            self.azure_email_client.begin_send(message)  # type: ignore

    def run(self, lottery_ticket_pack_filter: set[str] | None = None) -> None:
        self.validate_lottery_ticket_pack_filter(lottery_ticket_pack_filter)

        for lottery_ticket_pack in self.create_lottery_ticket_packs(
            lottery_ticket_pack_filter
        ):
            self.send_lottery_ticket_pack(lottery_ticket_pack)


def main() -> None:
    parser = ArgumentParser(
        prog="lottery-random",
        description="lottery-random is a true random lottery ticket generator with the help of the random.org API. It emails you true random numbers for the configured lottery ticket packs via Azure Communication Services.",
    )
    parser.add_argument(
        "-f",
        "--lottery-ticket-pack-filter",
        action="extend",
        nargs="+",
        type=str,
        required=False,
    )
    args = parser.parse_args()

    lottery_ticket_pack_filter: set[str] | None = (
        set(args.lottery_ticket_pack_filter)
        if args.lottery_ticket_pack_filter is not None
        else None
    )

    LotteryRandom().run(lottery_ticket_pack_filter)


if __name__ == "__main__":
    main()
