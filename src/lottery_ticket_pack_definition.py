from collections import Counter
from lottery_game_definition import LotteryGameDefinition
from recipient import Recipient
from lottery_ticket import LotteryTicket


class LotteryTicketPackDefinitionElement:
    number_of_random_tickets: int
    permanent_tickets: list[LotteryTicket]

    def __init__(
        self,
        number_of_random_tickets: int,
        permanent_tickets: list[LotteryTicket],
    ) -> None:
        self.number_of_random_tickets = number_of_random_tickets
        self.permanent_tickets = permanent_tickets

    def validate(
        self, game_name: str, lottery_game_definitions: dict[str, LotteryGameDefinition]
    ) -> None:
        lottery_game_definition = lottery_game_definitions.get(game_name)
        if lottery_game_definition is None:
            raise RuntimeError(
                f'Invalid lottery ticket pack element: no game definition named "{game_name}"'
            )

        if self.number_of_random_tickets == 0 and len(self.permanent_tickets) == 0:
            raise RuntimeError(
                f'Invalid lottery ticket pack element for game "{game_name}": no tickets'
            )

        for permanent_ticket in self.permanent_tickets:
            if len(permanent_ticket.numbers) != len(lottery_game_definition.fields):
                raise RuntimeError(
                    f'Invalid lottery ticket pack element for game "{game_name}":'
                    "at least one permanent ticket does not have as many fields as it should"
                )

            for field, field_definition in zip(
                permanent_ticket.numbers, lottery_game_definition.fields
            ):
                if len(field) != field_definition.n:
                    raise RuntimeError(
                        f'Invalid lottery ticket pack element for game "{game_name}":'
                        "at least one permanent ticket's at least one field does not have as many numbers as it should"
                    )

                for number in field:
                    if number < field_definition.min:
                        raise RuntimeError(
                            f'Invalid lottery ticket pack element for game "{game_name}":'
                            f"{number} should be greater than or equal to {field_definition.min}"
                        )
                    if number > field_definition.max:
                        raise RuntimeError(
                            f'Invalid lottery ticket pack element for game "{game_name}":'
                            f"{number} should be less than or equal to {field_definition.max}"
                        )


class LotteryTicketPackDefinition:
    name: str
    recipients: list[Recipient]
    elements: dict[str, LotteryTicketPackDefinitionElement]

    def __init__(
        self,
        name: str,
        recipients: list[Recipient],
        elements: dict[str, LotteryTicketPackDefinitionElement],
    ) -> None:
        self.name = name
        self.recipients = recipients
        self.elements = elements

    def validate(
        self, lottery_game_definitions: dict[str, LotteryGameDefinition]
    ) -> None:
        if len(self.recipients) == 0:
            raise RuntimeError(
                "Invalid lottery ticket pack definition: at least one definition has no recipients"
            )

        emails_of_duplicate_recipients = [
            email
            for email, number_of_occurrence in Counter(
                [r.email for r in self.recipients]
            ).items()
            if number_of_occurrence > 1
        ]
        if len(emails_of_duplicate_recipients) > 0:
            raise RuntimeError(
                f"Duplicate recipients: {[", ".join(emails_of_duplicate_recipients)]}"
            )

        if len(self.elements) == 0:
            raise RuntimeError(
                "Invalid lottery ticket pack definition: at least one definition has no elements"
            )

        self.validate_elements(lottery_game_definitions)

    def validate_elements(
        self, lottery_game_definitions: dict[str, LotteryGameDefinition]
    ) -> None:
        for game_name, element in self.elements.items():
            element.validate(game_name, lottery_game_definitions)
