#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timezone
from azure.communication.email import EmailClient
from azure.core.credentials import AzureKeyCredential

from config import Config
from lottery_ticket_pack import LotteryTicketPack
from lottery_ticket import LotteryTicket
from random_org_api import RandomOrgApi


class LotteryRandom:
    config: Config = Config()
    azure_email_client = EmailClient(
        config.azure_email_endpoint, AzureKeyCredential(config.azure_email_key)
    )
    random_org_api = RandomOrgApi(config.random_org_api_key)

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
                "senderAddress": "lottery-random@luczsoma.hu",
            }

            self.azure_email_client.begin_send(message)  # type: ignore

    def run(self) -> None:
        lottery_ticket_packs = [
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
        ]

        for lottery_ticket_pack in lottery_ticket_packs:
            self.send_lottery_ticket_pack(lottery_ticket_pack)


if __name__ == "__main__":
    LotteryRandom().run()
