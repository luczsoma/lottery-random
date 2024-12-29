from lottery_game_definition import FieldDefinition
from random_org_api import RandomOrgApi


class LotteryTicket:
    numbers: list[set[int]]

    def __init__(self, numbers: list[set[int]]) -> None:
        self.numbers = numbers

    def __str__(self) -> str:
        return f"[{' | '.join([', '.join([str(number) for number in sorted(field)]) for field in self.numbers])}]"

    @staticmethod
    def generate_random(
        fields: list[FieldDefinition], random_org_api: RandomOrgApi
    ) -> "LotteryTicket":
        return LotteryTicket(
            [
                random_org_api.get_unique_true_random_integers(
                    field.n, field.min, field.max
                )
                for field in fields
            ]
        )
