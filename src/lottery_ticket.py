from lottery_game_definition import FieldDefinition
from random_org_api import RandomOrgApi


class LotteryTicket:
    numbers: list[set[int]]

    def __init__(self, numbers: list[set[int]]) -> None:
        self.numbers = numbers

    def __str__(self) -> str:
        return f"[{' | '.join([', '.join(sorted(list([str(number) for number in drawing_set]))) for drawing_set in self.numbers])}]"

    @staticmethod
    def generate_random(
        drawing_sets: list[FieldDefinition], random_org_api: RandomOrgApi
    ) -> "LotteryTicket":
        return LotteryTicket(
            [
                random_org_api.get_true_random_integers(
                    drawing_set.n, drawing_set.min, drawing_set.max
                )
                for drawing_set in drawing_sets
            ]
        )
