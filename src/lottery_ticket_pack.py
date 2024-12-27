from recipient import Recipient
from lottery_ticket import LotteryTicket


class LotteryTicketPack:
    recipients: list[Recipient]
    tickets: dict[str, list[LotteryTicket]]

    def __init__(
        self, recipients: list[Recipient], tickets: dict[str, list[LotteryTicket]]
    ) -> None:
        self.recipients = recipients
        self.tickets = tickets

    def __str__(self) -> str:
        return "\n".join(
            [
                f"{game_name}: {', '.join([str(ticket) for ticket in tickets])}"
                for game_name, tickets in self.tickets.items()
            ]
        )
